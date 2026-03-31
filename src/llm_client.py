import requests
import json
# 导入合约解析和知识库模块
from contract_parser import ContractParser
from knowledge_base_builder import KnowledgeBaseBuilder


class LocalLLMClient:
    def __init__(self, api_url="http://localhost:1234/v1"):
        self.api_url = api_url

    # 基础分析方法（保留原有能力，支持自定义prompt）
    def analyze_contract(self, contract_code: str, custom_prompt: str = None) -> str:
        # 优先使用传入的自定义prompt，没有则用默认prompt
        if custom_prompt:
            prompt = custom_prompt
        else:
            # 严格按照 Qwen 模型要求格式化 prompt
            prompt = f"""<|im_start|>user
你是一个智能合约安全审计专家，请分析以下Solidity代码，找出所有安全漏洞，并按要求格式输出：

代码：
{contract_code}

请按照以下格式回答：
1. 漏洞类型
2. 漏洞位置
3. 漏洞描述
4. 修复建议
<|im_end|>
<|im_start|>assistant
"""

        # 完善请求 payload（关键参数不能缺）
        payload = {
            "model": "qwen2.5-coder-7b-instruct",  # 必须和服务器返回的模型ID完全一致
            "prompt": prompt,
            "temperature": 0.2,  # 控制输出随机性，0.1-0.7 适合审计场景
            "max_tokens": 2000,  # 限制输出长度，避免截断
            "stop": ["<|im_end|>"]  # 告诉模型遇到这个符号就停止生成
        }

        # 发送请求并解析结果
        try:
            response = requests.post(f"{self.api_url}/completions", json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["text"].strip()
        except Exception as e:
            return f"请求失败: {str(e)}"


# 增强版LLM客户端，整合合约解析+RAG检索
class EnhancedLLMClient(LocalLLMClient):
    def __init__(self, api_url="http://localhost:1234/v1"):
        super().__init__(api_url)
        # 初始化合约解析器和知识库
        self.parser = ContractParser()
        self.kb = KnowledgeBaseBuilder()

    def analyze_contract_enhanced(self, contract_code: str) -> str:
        # 1. 解析合约结构，提取函数、变量等信息
        parsed_contract = self.parser.parse_contract(contract_code)

        # 2. 基于合约函数名，检索相关漏洞知识库
        # 提取所有函数名生成检索关键词，提升匹配精度
        search_keywords = " ".join([func['name'] for func in parsed_contract.get('functions', [])])
        # 检索最相关的2条漏洞知识
        relevant_vulns = self.kb.search(search_keywords, n_results=2)

        # 3. 拼接检索到的漏洞知识，作为上下文
        vuln_context = ""
        if relevant_vulns.get('documents') and len(relevant_vulns['documents'][0]) > 0:
            for i, doc_content in enumerate(relevant_vulns['documents'][0]):
                vuln_meta = relevant_vulns['metadatas'][0][i]
                vuln_context += f"\n【相关漏洞参考 {i+1}】\n漏洞名称：{vuln_meta['title']}\n漏洞原理：{doc_content}\n修复方案：{vuln_meta['fix']}\n"

        # 4. 构建增强版Prompt，严格符合Qwen格式要求
        enhanced_prompt = f"""<|im_start|>user
你是一个专业的智能合约安全审计专家。请结合合约结构信息、漏洞参考知识，分析以下Solidity代码，找出所有安全漏洞，输出专业审计报告。

【合约结构化信息】
{json.dumps(parsed_contract, indent=2, default=str)}

【相关漏洞参考知识】
{vuln_context}

【待审计的合约代码】
{contract_code}

请严格按照以下格式输出审计结果：
1. 漏洞类型
2. 漏洞位置（函数/变量名）
3. 漏洞详细描述
4. 风险等级（高/中/低）
5. 完整修复代码
6. 参考漏洞依据
<|im_end|>
<|im_start|>assistant
"""

        # 调用父类方法，传入增强后的prompt
        return self.analyze_contract(contract_code, custom_prompt=enhanced_prompt)


# 测试代码
if __name__ == "__main__":
    # 测试用的高危重入漏洞合约
    test_contract = """
pragma solidity ^0.8.0;
contract VulnerableBank {
    mapping(address => uint) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint _amount) public {
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        // 高危：先转账，后更新余额，存在经典重入漏洞
        (bool success, ) = msg.sender.call{value: _amount}("");
        require(success, "Transfer failed");
        balances[msg.sender] -= _amount;
    }
}
    """

    # 1. 测试基础版分析
    print("===== 基础版分析结果 =====")
    base_client = LocalLLMClient()
    print(base_client.analyze_contract(test_contract))

    print("\n===== 增强版分析结果（合约解析+RAG知识库） =====")
    # 2. 测试增强版分析
    enhanced_client = EnhancedLLMClient()
    enhanced_result = enhanced_client.analyze_contract_enhanced(test_contract)
    print(enhanced_result)