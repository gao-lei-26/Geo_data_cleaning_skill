import pandas as pd

def merge_sheets(main_df: pd.DataFrame, other_dfs: dict, on_col: str = 'samp_id') -> pd.DataFrame:
    result = main_df.copy()
    for name, df in other_dfs.items():
        if on_col in df.columns:
            result = result.merge(df, on=on_col, how='left', suffixes=('', f'_{name}'))
        else:
            possible = [c for c in df.columns if 'id' in c.lower()]
            if possible:
                result = result.merge(df, left_on=on_col, right_on=possible[0], how='left', suffixes=('', f'_{name}'))
    return result