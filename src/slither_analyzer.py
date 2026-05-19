import json
import subprocess
import os


class SlitherAnalyzer:
    def __init__(self):
        self.slither_path = "slither"

    def analyze_contract_file(self, contract_path: str) -> dict:
        """分析合约文件并返回Slither的JSON输出"""
        if not os.path.exists(contract_path):
            return {"error": f"Contract file not found: {contract_path}"}

        try:
            cmd = [
                self.slither_path,
                contract_path,
                "--json", "-"
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and result.stdout:
                slither_output = json.loads(result.stdout)
                return self._parse_slither_output(slither_output)
            else:
                return {
                    "error": "Slither analysis failed",
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
        except subprocess.TimeoutExpired:
            return {"error": "Slither analysis timeout"}
        except json.JSONDecodeError:
            return {"error": "Failed to parse Slither JSON output"}
        except Exception as e:
            return {"error": f"Analysis error: {str(e)}"}

    def analyze_contract_code(self, contract_code: str, contract_name: str = "contract.sol") -> dict:
        """直接分析合约代码（通过临时文件）"""
        import tempfile

        temp_dir = tempfile.mkdtemp()
        contract_path = os.path.join(temp_dir, contract_name)

        try:
            with open(contract_path, 'w', encoding='utf-8') as f:
                f.write(contract_code)

            return self.analyze_contract_file(contract_path)
        finally:
            if os.path.exists(contract_path):
                os.remove(contract_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

    def _parse_slither_output(self, slither_data: dict) -> dict:
        """解析Slither的JSON输出为结构化数据"""
        results = {
            "success": True,
            "contract": slither_data.get("files", ["unknown"]),
            "summary": {
                "total_issues": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "informational": 0
            },
            "findings": []
        }

        if "results" not in slither_data:
            return results

        for detector in slither_data.get("results", []):
            if not isinstance(detector, dict):
                continue

            detector_type = detector.get("check", "unknown")
            detector_title = detector.get("title", "Unknown Issue")
            severity = self._normalize_severity(detector.get("impact", "Informational"))

            for finding in detector.get("findings", []):
                if not isinstance(finding, dict):
                    continue

                finding_data = {
                    "type": detector_type,
                    "title": detector_title,
                    "severity": severity,
                    "description": finding.get("description", ""),
                    "confidence": finding.get("confidence", "Medium"),
                    "locations": []
                }

                for element in finding.get("elements", []):
                    if isinstance(element, dict):
                        loc = element.get("source_mapping", {})
                        location = {
                            "filename": loc.get("filename", "unknown"),
                            "start_line": loc.get("start_line", 0),
                            "end_line": loc.get("end_line", 0),
                            "contract": element.get("name", "unknown")
                        }
                        finding_data["locations"].append(location)

                results["findings"].append(finding_data)
                results["summary"]["total_issues"] += 1

                if severity == "Critical":
                    results["summary"]["critical"] += 1
                elif severity == "High":
                    results["summary"]["high"] += 1
                elif severity == "Medium":
                    results["summary"]["medium"] += 1
                elif severity == "Low":
                    results["summary"]["low"] += 1
                else:
                    results["summary"]["informational"] += 1

        return results

    def _normalize_severity(self, impact: str) -> str:
        """将Slither的impact级别标准化"""
        impact_map = {
            "Critical": "Critical",
            "High": "High",
            "Medium": "Medium",
            "Low": "Low",
            "Informational": "Informational"
        }
        return impact_map.get(impact, "Informational")

    def get_findings_summary(self, slither_result: dict) -> str:
        """生成Slither发现的摘要文本"""
        if not slither_result.get("success"):
            return f"Slither分析失败: {slither_result.get('error', 'Unknown error')}"

        summary = slither_result.get("summary", {})
        findings = slither_result.get("findings", [])

        if not findings:
            return "Slither未检测到任何问题。"

        summary_text = f"""
=== Slither分析摘要 ===
总问题数: {summary.get('total_issues', 0)}
- Critical: {summary.get('critical', 0)}
- High: {summary.get('high', 0)}
- Medium: {summary.get('medium', 0)}
- Low: {summary.get('low', 0)}
- Informational: {summary.get('informational', 0)}

详细发现:
"""
        for idx, finding in enumerate(findings, 1):
            locations = finding.get("locations", [])
            loc_str = ""
            if locations:
                loc = locations[0]
                loc_str = f" (行 {loc.get('start_line', 0)}-{loc.get('end_line', 0)}, 合约: {loc.get('contract', 'unknown')})"

            summary_text += f"""
{idx}. [{finding['severity']}] {finding['title']}{loc_str}
   类型: {finding['type']}
   描述: {finding['description'][:200]}{'...' if len(finding['description']) > 200 else ''}
   置信度: {finding['confidence']}
"""

        return summary_text


if __name__ == "__main__":
    print("Slither Analyzer Module")
