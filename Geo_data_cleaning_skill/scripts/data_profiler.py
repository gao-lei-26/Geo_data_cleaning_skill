import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

class GeoDataProfiler:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.sheets = {}
        self.profile = {}
        self.main_sheet = None

    def load_all_sheets(self) -> Dict[str, pd.DataFrame]:
        """读取所有Sheet，只读前1000行以节省内存"""
        xls = pd.ExcelFile(self.file_path)
        for sheet in xls.sheet_names:
            self.sheets[sheet] = pd.read_excel(self.file_path, sheet_name=sheet, nrows=1000)
        return self.sheets

    def detect_main_sheet(self) -> str:
        for name, df in self.sheets.items():
            cols = df.columns.str.lower()
            if any('samp_id' in c or 'sample' in c for c in cols):
                self.main_sheet = name
                return name
        self.main_sheet = list(self.sheets.keys())[0]
        return self.main_sheet

    def profile_main(self) -> Dict[str, Any]:
        df = self.sheets[self.main_sheet]
        results = {
            'sheet_name': self.main_sheet,
            'rows': len(df),
            'columns': len(df.columns),
            'column_list': list(df.columns),
            'age_columns': [c for c in df.columns if 'age' in c.lower()],
            'geo_columns': [c for c in df.columns if 'lat' in c.lower() or 'lon' in c.lower() or 'long' in c.lower()],
            'missing_counts': df.isna().sum().to_dict(),
            'duplicates': int(df.duplicated().sum())
        }
        self.profile = results
        return results

    def profile_other_sheets(self) -> Dict[str, Any]:
        other = {}
        for name, df in self.sheets.items():
            if name == self.main_sheet:
                continue
            other[name] = {
                'rows': len(df),
                'columns': list(df.columns),
                'sample_id_col': [c for c in df.columns if 'samp_id' in c.lower()]
            }
        self.profile['other_sheets'] = other
        return other

    def generate_report(self) -> str:
        """生成极度精简的探查报告（节省Token）"""
        p = self.profile
        lines = []
        lines.append("📊 探查摘要:")
        lines.append(f"- 主表: {p['sheet_name']} ({p['rows']}行)")
        lines.append(f"- 年龄列: {', '.join(p['age_columns']) if p['age_columns'] else '无'}")
        lines.append(f"- 地理列: {', '.join(p['geo_columns'][:3]) if p['geo_columns'] else '无'}")
        
        # 只列出缺失值最多的前3列
        missing_items = [(col, cnt) for col, cnt in p['missing_counts'].items() if cnt > 0]
        if missing_items:
            missing_items.sort(key=lambda x: -x[1])
            top_missing = missing_items[:3]
            lines.append("- 主要缺失 (Top3): " + ", ".join([f"{col}({cnt})" for col, cnt in top_missing]))
            if len(missing_items) > 3:
                lines.append(f"  (其余 {len(missing_items)-3} 列有缺失)")
        
        lines.append(f"- 重复行: {p['duplicates']}")
        lines.append(f"- 关联表: {len(p.get('other_sheets', {}))} 个")
        
        return "\n".join(lines)

# 命令行快速测试
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python data_profiler.py <excel_file>")
        sys.exit(1)
    profiler = GeoDataProfiler(sys.argv[1])
    profiler.load_all_sheets()
    profiler.detect_main_sheet()
    profiler.profile_main()
    profiler.profile_other_sheets()
    print(profiler.generate_report())