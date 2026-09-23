import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict
from .merge_helper import merge_sheets

class GeoDataCleaner:
    def __init__(self, file_path: str, requirements: Dict, profile: Dict):
        self.file_path = Path(file_path)
        self.requirements = requirements
        self.profile = profile
        self.df_main = None
        self.df_merged = None
        self.log = []
        self.original_shape = None

    def load_main(self):
        sheet = self.profile['main_sheet']
        # 加载全量数据用于清洗
        self.df_main = pd.read_excel(self.file_path, sheet_name=sheet)
        self.original_shape = self.df_main.shape

    @staticmethod
    def parse_age(val):
        """把年龄值统一解析为 Ma：Ga 乘 1000、Ma 保留、纯数字直接转换、无法解析记 NaN"""
        if pd.isna(val):
            return np.nan
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip()
        try:
            if 'Ga' in s:
                return float(s.replace('Ga', '').strip()) * 1000
            if 'Ma' in s:
                return float(s.replace('Ma', '').strip())
            return float(s)
        except ValueError:
            return np.nan

    def clean_age(self):
        age_choice = self.requirements.get('age_choice')

        if age_choice and age_choice in self.df_main.columns:
            self.df_main['cleaned_age_Ma'] = self.df_main[age_choice].apply(self.parse_age)
            self.log.append(f"年龄标准化: {age_choice} -> cleaned_age_Ma")

        elif age_choice == '平均值' and len(self.profile.get('age_columns', [])) > 1:
            # 计算多个年龄列的平均值
            age_cols = self.profile['age_columns']

            def row_mean(row):
                vals = [self.parse_age(v) for v in row if not pd.isna(v)]
                vals = [v for v in vals if not pd.isna(v)]
                return float(np.mean(vals)) if vals else np.nan

            self.df_main['cleaned_age_Ma'] = self.df_main[age_cols].apply(row_mean, axis=1)
            self.log.append("年龄标准化: 多个年龄列取平均 -> cleaned_age_Ma")

    def merge_other_sheets(self):
        if self.requirements.get('merge_sheets') == '是':
            xls = pd.ExcelFile(self.file_path)
            other_dfs = {}
            for name in xls.sheet_names:
                if name != self.profile['main_sheet']:
                    other_dfs[name] = pd.read_excel(self.file_path, sheet_name=name)
            self.df_merged = merge_sheets(self.df_main, other_dfs)
            self.log.append(f"已合并 {len(other_dfs)} 个关联表")
        else:
            self.df_merged = self.df_main.copy()

    def save_output(self, output_path=None):
        if output_path is None:
            stem = self.file_path.stem
            output_path = self.file_path.parent / f"{stem}_cleaned.xlsx"
        with pd.ExcelWriter(output_path) as writer:
            self.df_merged.to_excel(writer, sheet_name='Cleaned_Main', index=False)
        self.log.append(f"输出: {output_path}")
        return str(output_path)

    def get_report(self) -> str:
        lines = ["🧹 清洗结果:"]
        lines.append(f"原始: {self.original_shape[0]}行 x {self.original_shape[1]}列")
        lines.append(f"清洗后: {self.df_merged.shape[0]}行 x {self.df_merged.shape[1]}列")
        lines.append(f"操作: {', '.join(self.log)}")
        return '\n'.join(lines)

    def run_clean(self):
        self.load_main()
        self.clean_age()
        self.merge_other_sheets()
        return self.df_merged
