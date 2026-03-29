import requests
import json

class LocalLLMClient:
    def __init__(self, api_url="http://localhost:1234/v1"):
        self.api_url = api_url

    def analyze_contract(self, contract_code: str) -> str:
        # 1. 严格按照 Qwen 模型要求格式化 prompt（必须包含分隔符）
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

        # 2. 完善请求 payload（关键参数不能缺）
        payload = {
            "model": "qwen2.5-coder-7b-instruct",  # 必须和服务器返回的模型ID完全一致
            "prompt": prompt,
            "temperature": 0.2,  # 控制输出随机性，0.1-0.7 适合审计场景
            "max_tokens": 2000,  # 限制输出长度，避免截断
            "stop": ["<|im_end|>"]  # 告诉模型遇到这个符号就停止生成
        }

        # 3. 发送请求并解析结果
        try:
            response = requests.post(f"{self.api_url}/completions", json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["text"].strip()
        except Exception as e:
            return f"请求失败: {str(e)}"

# 测试代码
if __name__ == "__main__":
    client = LocalLLMClient()
    # 替换为你的Solidity测试代码
    test_contract = """
pragma solidity ^0.8.0;
contract Test {
    uint256 public balance;
    function withdraw() public {
        payable(msg.sender).transfer(balance);
        balance = 0;
    }
}
"""
    print("分析结果：")
    print(client.analyze_contract(test_contract))