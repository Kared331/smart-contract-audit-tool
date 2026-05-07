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
