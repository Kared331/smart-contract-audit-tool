import chromadb
from chromadb.config import Settings
import json

class KnowledgeBaseBuilder:
    def __init__(self, persist_directory="./chroma_db"):
        self.client = chromadb.PersistentClient(settings=Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        self.collection = self.client.get_or_create_collection("vulnerabilities")

    def add_vulnerability(self, vuln_data):
        """
        添加漏洞记录到知识库
        vuln_data 格式：
        {
            "id": "reentrancy_001",
            "title": "重入攻击",
            "description": "在外部调用前未更新状态...",
            "code_example": "contract Example { ... }",
            "fix": "使用 Checks-Effects-Interactions 模式"
        }
        """
        self.collection.add(
            documents=[vuln_data['description']],
            metadatas=[{
                "title": vuln_data['title'],
                "code_example": vuln_data['code_example'],
                "fix": vuln_data['fix']
            }],
            ids=[vuln_data['id']]
        )

    def search(self, query, n_results=3):
        """
        检索相关漏洞
        """
        results = self.collection.query(
            query_embeddings=None,  # 使用内置的嵌入模型
            query_texts=[query],
            n_results=n_results
        )
        return results

# 测试：添加一些漏洞示例
if __name__ == "__main__":
    kb = KnowledgeBaseBuilder()

    # 示例漏洞数据
    # 示例漏洞数据（原2个 + 新增2个，共4个）
# 完整漏洞列表（原2个+新增2个）
vulnerabilities = [
    {
        "id": "reentrancy_001",
        "title": "重入攻击",
        "description": "在外部调用前未更新状态，允许攻击者重复调用函数提取资金。",
        "code_example": "function withdraw(uint amount) public { require(balance[msg.sender] >= amount); msg.sender.call{value: amount}(\"\"); balance[msg.sender] -= amount; }",
        "fix": "先更新状态，再进行外部调用（Checks-Effects-Interactions）"
    },
    {
        "id": "integer_overflow_001",
        "title": "整数溢出",
        "description": "算术运算超出变量类型范围，导致意外行为。",
        "code_example": "uint8 a = 255; a = a + 1; // 溢出为 0",
        "fix": "使用 SafeMath 库或 Solidity 0.8+ 的内置溢出检查"
    },
    {
        "id": "access_control_001",
        "title": "访问控制缺失",
        "description": "敏感函数没有适当的权限检查，任何人都可以调用。",
        "code_example": "function changeOwner(address newOwner) public { owner = newOwner; }",
        "fix": "添加onlyOwner修饰符或适当的权限检查"
    },
    {
        "id": "timestamp_dependency_001",
        "title": "时间戳依赖",
        "description": "合约逻辑依赖于block.timestamp，可能被矿工操纵。",
        "code_example": "require(block.timestamp > startTime);",
        "fix": "避免在关键逻辑中使用时间戳，或使用更安全的时间源"
    }
]  

for vuln in vulnerabilities:
    kb.add_vulnerability(vuln)

    # 测试检索
    results = kb.search("合约中资金被重复提取")
    print("检索结果：")
    for i, doc in enumerate(results['documents'][0]):
        print(f"\n结果 {i+1}:")
        print(f"标题: {results['metadatas'][0][i]['title']}")
        print(f"描述: {doc}")
        print(f"修复: {results['metadatas'][0][i]['fix']}")
