from slither_analyzer import SlitherAnalyzer
from llm_client import EnhancedLLMClient
import json


class ReportGenerator:
    def generate_html_report(self, analysis_result, contract_code):
        """生成HTML格式的审计报告"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>智能合约审计报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .vulnerability {{ border: 1px solid #ccc; padding: 15px; margin: 10px 0; }}
                .high {{ border-left: 5px solid #d9534f; }}
                .medium {{ border-left: 5px solid #f0ad4e; }}
                .low {{ border-left: 5px solid #5cb85c; }}
            </style>
        </head>
        <body>
            <h1>智能合约安全审计报告</h1>
            <h2>合约代码</h2>
            <pre>{contract_code}</pre>
            <h2>审计结果</h2>
            {self._format_vulnerabilities(analysis_result)}
        </body>
        </html>
        """
        return html_template

    def _format_vulnerabilities(self, analysis_result):
        """格式化漏洞信息"""
        return str(analysis_result)


class SlitherReportGenerator(ReportGenerator):
    def __init__(self):
        super().__init__()
        self.slither = SlitherAnalyzer()
        self.llm = EnhancedLLMClient()

    def generate_slither_report(self, contract_code: str, contract_name: str = "contract.sol") -> dict:
        """生成基于Slither分析的完整审计报告"""
        report = {
            "slither_analysis": None,
            "llm_explanations": [],
            "html_report": ""
        }

        slither_result = self.slither.analyze_contract_code(contract_code, contract_name)
        report["slither_analysis"] = slither_result

        if not slither_result.get("success"):
            report["html_report"] = self._generate_error_report(slither_result)
            return report

        if not slither_result.get("findings"):
            report["html_report"] = self._generate_clean_report(contract_code)
            return report

        explanations = self._explain_findings_with_llm(slither_result)
        report["llm_explanations"] = explanations

        report["html_report"] = self._generate_html_with_slither(
            slither_result,
            explanations,
            contract_code
        )

        return report

    def _explain_findings_with_llm(self, slither_result: dict) -> list:
        """使用LLM解释Slither发现"""
        explanations = []
        findings = slither_result.get("findings", [])

        for finding in findings:
            locations = finding.get("locations", [])
            location_text = ""
            if locations:
                loc = locations[0]
                location_text = f"文件: {loc.get('filename', 'unknown')}, 行: {loc.get('start_line', 0)}-{loc.get('end_line', 0)}, 合约: {loc.get('contract', 'unknown')}"

            explanation_prompt = f"""<|im_start|>user
你是智能合约安全审计专家。请详细解释以下Slither检测到的问题：

【漏洞类型】: {finding['type']}
【漏洞标题】: {finding['title']}
【严重级别】: {finding['severity']}
【置信度】: {finding['confidence']}
【漏洞描述】: {finding['description']}
【位置信息】: {location_text}

请提供：
1. 漏洞的详细技术解释
2. 为什么这是一个安全问题
3. 可能的攻击场景
4. 具体的修复建议和代码示例
<|im_end|>
<|im_start|>assistant
"""

            explanation = self.llm.analyze_contract(contract_code="", custom_prompt=explanation_prompt)

            explanations.append({
                "finding": finding,
                "explanation": explanation
            })

        return explanations

    def _generate_html_with_slither(self, slither_result: dict, explanations: list, contract_code: str) -> str:
        """生成包含Slither分析和LLM解释的HTML报告"""
        summary = slither_result.get("summary", {})

        findings_html = ""
        for idx, item in enumerate(explanations, 1):
            finding = item["finding"]
            explanation = item["explanation"]

            severity_class = finding["severity"].lower()

            locations = finding.get("locations", [])
            location_text = ""
            if locations:
                loc = locations[0]
                location_text = f"{loc.get('filename', 'unknown')}:{loc.get('start_line', 0)}-{loc.get('end_line', 0)}"

            findings_html += f"""
            <div class="vulnerability {severity_class}">
                <h3>{idx}. [{finding['severity']}] {finding['title']}</h3>
                <p><strong>类型:</strong> {finding['type']}</p>
                <p><strong>位置:</strong> {location_text if location_text else 'N/A'}</p>
                <p><strong>置信度:</strong> {finding['confidence']}</p>
                <p><strong>描述:</strong> {finding['description']}</p>
                <hr>
                <h4>LLM专家分析:</h4>
                <pre>{explanation}</pre>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>智能合约审计报告 - Slither + LLM</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .summary {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin: 20px 0; }}
                .summary-card {{ background: white; padding: 15px; border-radius: 5px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .critical {{ border-left: 5px solid #8b0000; }}
                .high {{ border-left: 5px solid #d9534f; }}
                .medium {{ border-left: 5px solid #f0ad4e; }}
                .low {{ border-left: 5px solid #5cb85c; }}
                .informational {{ border-left: 5px solid #5bc0de; }}
                .vulnerability {{ background: white; padding: 20px; margin: 15px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                pre {{ background: #f8f9fa; padding: 15px; border-radius: 3px; overflow-x: auto; white-space: pre-wrap; }}
                .code {{ background: #2d2d2d; color: #f8f8f2; padding: 20px; border-radius: 5px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔒 智能合约安全审计报告</h1>
                <p>Powered by Slither静态分析 + LLM智能分析</p>
            </div>

            <div class="summary">
                <div class="summary-card">
                    <h2>{summary.get('total_issues', 0)}</h2>
                    <p>总问题数</p>
                </div>
                <div class="summary-card">
                    <h2 style="color: #8b0000;">{summary.get('critical', 0)}</h2>
                    <p>严重</p>
                </div>
                <div class="summary-card">
                    <h2 style="color: #d9534f;">{summary.get('high', 0)}</h2>
                    <p>高危</p>
                </div>
                <div class="summary-card">
                    <h2 style="color: #f0ad4e;">{summary.get('medium', 0)}</h2>
                    <p>中危</p>
                </div>
                <div class="summary-card">
                    <h2 style="color: #5cb85c;">{summary.get('low', 0)}</h2>
                    <p>低危</p>
                </div>
            </div>

            <h2>📋 审计发现</h2>
            {findings_html if findings_html else '<p>未检测到明显的安全问题</p>'}

            <h2>📝 合约代码</h2>
            <div class="code">
                <pre>{contract_code}</pre>
            </div>

            <footer style="margin-top: 40px; padding: 20px; background: #ecf0f1; text-align: center;">
                <p>报告生成时间: {self._get_current_time()}</p>
                <p>此报告由AI辅助生成，仅供参考</p>
            </footer>
        </body>
        </html>
        """
        return html

    def _generate_error_report(self, slither_result: dict) -> str:
        """生成错误报告"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>审计报告 - 错误</title></head>
        <body>
            <h1>审计失败</h1>
            <p>Slither分析错误: {slither_result.get('error', 'Unknown error')}</p>
            <pre>{slither_result.get('stderr', '')}</pre>
        </body>
        </html>
        """

    def _generate_clean_report(self, contract_code: str) -> str:
        """生成无漏洞的报告"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>审计报告</title></head>
        <body>
            <h1>✅ 审计完成 - 未发现问题</h1>
            <p>Slither静态分析未检测到已知的安全漏洞模式。</p>
            <p>注意: 这不意味着合约完全安全，仍需人工审核。</p>
            <h2>合约代码</h2>
            <pre>{contract_code}</pre>
        </body>
        </html>
        """

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    print("Slither Report Generator Module")

