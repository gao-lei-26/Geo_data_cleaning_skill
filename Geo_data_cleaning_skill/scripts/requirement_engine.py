from typing import Dict, List

class GeoRequirementEngine:
    def __init__(self, profile: Dict):
        self.profile = profile
        self.questions = []
        self.answers = {}

    def generate_questions(self) -> List[Dict]:
        """生成极简问题，每次只问1个核心问题"""
        qs = []
        age_cols = self.profile.get('age_columns', [])
        if age_cols:
            # 只保留年龄选择这一个核心问题
            options = age_cols.copy()
            if len(age_cols) > 1:
                options.append('平均值')
            qs.append({
                'id': 'age_choice',
                'text': f'年龄列 [{",".join(age_cols)}] 用哪个？[1={age_cols[0]}]' + (f' [2=平均值]' if len(age_cols) > 1 else ''),
                'type': 'choice',
                'options': options
            })
        
        other_sheets = self.profile.get('other_sheets', {})
        if other_sheets:
            qs.append({
                'id': 'merge_sheets',
                'text': f'合并关联表？[1=是] [2=否]',
                'type': 'choice',
                'options': ['是', '否']
            })
        
        self.questions = qs
        return qs

    def parse_answers(self, answer_dict: Dict) -> Dict:
        self.answers.update(answer_dict)
        return self.answers

    def get_summary(self) -> str:
        lines = ["📋 需求确认:"]
        for k, v in self.answers.items():
            lines.append(f"  {k}: {v}")
        return '\n'.join(lines)