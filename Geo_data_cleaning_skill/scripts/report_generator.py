from datetime import datetime

class ReportGenerator:
    def __init__(self, original_df, cleaned_df, log):
        self.original = original_df
        self.cleaned = cleaned_df
        self.log = log

    def generate_html(self, output_path=None):
        html = f"""
        <html><head><meta charset="UTF-8"><title>清洗报告</title>
        <style>body{{font-family:Arial;margin:40px}}</style>
        </head><body>
        <h1>🧹 清洗报告</h1>
        <p>时间: {datetime.now()}</p>
        <table border="1">
        <tr><th>指标</th><th>清洗前</th><th>清洗后</th></tr>
        <tr><td>行数</td><td>{len(self.original)}</td><td>{len(self.cleaned)}</td></tr>
        <tr><td>列数</td><td>{len(self.original.columns)}</td><td>{len(self.cleaned.columns)}</td></tr>
        </table>
        <h2>操作</h2><ul>{"".join(f"<li>{l}</li>" for l in self.log)}</ul>
        </body></html>
        """
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
        return html