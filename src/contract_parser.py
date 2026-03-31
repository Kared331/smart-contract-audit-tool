from solcx import compile_source, install_solc
import json

class ContractParser:
    def __init__(self):
        # 安装并设置 Solidity 编译器版本
        install_solc('0.8.0')  # 选择一个常用版本

    def parse_contract(self, source_code: str):
        """
        解析 Solidity 源代码，提取结构信息
        """
        try:
            # 编译合约
            compiled = compile_source(source_code, output_values=['abi', 'bin', 'ast'])

            # 提取合约名称和接口
            contract_id = list(compiled.keys())[0]
            contract_interface = compiled[contract_id]

            # 提取 ABI（应用二进制接口）
            abi = contract_interface['abi']

            # 提取函数和事件
            functions = [item for item in abi if item['type'] == 'function']
            events = [item for item in abi if item['type'] == 'event']

            # 提取状态变量（从 AST 中提取，这里简化处理）
            # 实际项目中可以使用更复杂的 AST 遍历
            state_variables = self._extract_state_variables(source_code)

            return {
                'contract_name': contract_id.split(':')[-1],
                'functions': functions,
                'events': events,
                'state_variables': state_variables,
                'abi': abi
            }
        except Exception as e:
            return {'error': str(e)}

    def _extract_state_variables(self, source_code: str):
        """
        简化的状态变量提取（基于关键字匹配）
        实际项目建议使用更精确的 AST 解析
        """
        import re
        # 匹配类似 "uint public balance;" 的模式
        pattern = r'(uint|int|string|address|bool|bytes\d*|mapping\s*$$[^)]*$$\s*\w+)\s+(public|private|internal|external)?\s*(\w+)\s*;'
        matches = re.findall(pattern, source_code)
        variables = []
        for match in matches:
            var_type = match[0]
            var_name = match[2]
            variables.append({'type': var_type, 'name': var_name})
        return variables

# 测试代码
if __name__ == "__main__":
    test_code = """
    contract VulnerableBank {
        mapping(address => uint) public balances;
        uint public totalDeposits;

        event Deposit(address indexed user, uint amount);

        function deposit() public payable {
            balances[msg.sender] += msg.value;
            totalDeposits += msg.value;
            emit Deposit(msg.sender, msg.value);
        }
    }
    """

    parser = ContractParser()
    result = parser.parse_contract(test_code)
    print(json.dumps(result, indent=2, default=str))
