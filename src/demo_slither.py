from slither_analyzer import SlitherAnalyzer
from report_generator import SlitherReportGenerator


def demo_slither_analysis():
    """演示Slither分析功能"""
    print("=" * 60)
    print("Slither静态分析演示")
    print("=" * 60)

    test_contract = """
pragma solidity ^0.8.0;

contract ReentrancyVulnerable {
    mapping(address => uint) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint _amount) public {
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        (bool success, ) = msg.sender.call{value: _amount}("");
        require(success, "Transfer failed");
        balances[msg.sender] -= _amount;
    }
}

contract UncheckedReturn {
    function test(address payable _to) public payable {
        _to.send(msg.value);
    }
}

contract IntegerOverflow {
    function add(uint256 a, uint256 b) public pure returns (uint256) {
        return a + b;
    }
}
    """

    analyzer = SlitherAnalyzer()
    print("\n1. 分析合约代码...")
    result = analyzer.analyze_contract_code(test_contract, "vulnerable.sol")

    print("\n2. Slither分析结果:")
    print("-" * 60)
    print(analyzer.get_findings_summary(result))

    print("\n3. 详细JSON输出:")
    print("-" * 60)
    import json
    print(json.dumps(result, indent=2, default=str))

    return result


def demo_full_report_generation():
    """演示完整的Slither + LLM报告生成"""
    print("\n" + "=" * 60)
    print("Slither + LLM 完整报告生成演示")
    print("=" * 60)

    test_contract = """
pragma solidity ^0.8.0;

contract SimpleStore {
    uint public value;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function set(uint _value) public {
        require(msg.sender == owner, "Only owner can set");
        value = _value;
    }

    function get() public view returns (uint) {
        return value;
    }
}
    """

    report_generator = SlitherReportGenerator()

    print("\n1. 开始生成深度审计报告...")
    print("   - 执行Slither静态分析")
    print("   - 使用LLM解释发现的问题")
    print("   - 生成HTML报告")

    report = report_generator.generate_slither_report(
        test_contract,
        "SimpleStore.sol"
    )

    print("\n2. 报告生成完成!")
    print("-" * 60)
    print(f"Slither分析: {'成功' if report['slither_analysis'].get('success') else '失败'}")
    print(f"发现数量: {len(report['llm_explanations'])}")
    print(f"HTML报告: {'已生成' if report['html_report'] else '未生成'}")

    if report['llm_explanations']:
        print("\n3. LLM分析结果预览:")
        print("-" * 60)
        for idx, item in enumerate(report['llm_explanations'][:2], 1):
            finding = item['finding']
            print(f"\n[{idx}] {finding['title']} ({finding['severity']})")
            print(f"    类型: {finding['type']}")
            print(f"    LLM分析: {item['explanation'][:150]}...")

    output_file = "demo_report.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report['html_report'])
    print(f"\n4. HTML报告已保存到: {output_file}")

    return report


def demo_multiple_findings():
    """演示处理多个发现"""
    print("\n" + "=" * 60)
    print("演示多漏洞合约分析")
    print("=" * 60)

    complex_contract = """
pragma solidity ^0.8.0;

contract ComplexVulnerabilities {
    mapping(address => uint) balances;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdrawAll() public {
        uint bal = balances[msg.sender];
        require(bal > 0);
        (bool success, ) = msg.sender.call{value: bal}("");
        require(success);
        balances[msg.sender] = 0;
    }

    function transfer(address to, uint amount) public {
        require(balances[msg.sender] >= amount);
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }

    function setOwner(address newOwner) public {
        owner = newOwner;
    }

    function getBalance(address a) public view returns (uint) {
        return balances[a];
    }
}
    """

    report_gen = SlitherReportGenerator()
    report = report_gen.generate_slither_report(complex_contract, "Complex.sol")

    if report['slither_analysis'].get('success'):
        summary = report['slither_analysis']['summary']
        print(f"\n发现总结:")
        print(f"  总问题数: {summary['total_issues']}")
        print(f"  严重: {summary['critical']}")
        print(f"  高危: {summary['high']}")
        print(f"  中危: {summary['medium']}")
        print(f"  低危: {summary['low']}")

        if report['llm_explanations']:
            print(f"\n前3个问题的LLM分析:")
            for idx, item in enumerate(report['llm_explanations'][:3], 1):
                print(f"\n{idx}. {item['finding']['title']}")
                print(f"   {item['explanation'][:200]}...")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 Slither集成演示脚本")
    print("=" * 60)

    try:
        demo_slither_analysis()
        print("\n")
        demo_full_report_generation()
        print("\n")
        demo_multiple_findings()

        print("\n" + "=" * 60)
        print("✅ 所有演示完成!")
        print("=" * 60)
        print("\n提示:")
        print("1. Slither分析器会自动运行Slither工具并解析结果")
        print("2. 生成的报告包含Slither发现和LLM专家解释")
        print("3. 可以直接在Streamlit应用中体验完整功能")
        print("4. 运行 'streamlit run app.py' 启动Web界面")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {str(e)}")
        print("\n请确保:")
        print("1. 已安装Slither: pip install slither-analyzer")
        print("2. Slither可执行文件在系统PATH中")
        print("3. 已安装所需依赖: pip install -r requirements.txt")
