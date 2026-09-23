# Geo_data_cleaning_skill

地质（地球化学）Excel 数据清洗 **Skill**：自动探查表结构 → 只问关键问题 → 标准化年龄列并合并关联表 → 输出清洗结果。

整个流程按「极简 Token」设计：探查报告压到 6–8 行、提问一次只问 1 个、结尾只报文件路径与行列变化，避免把 DataFrame 内容刷进对话。

## 目录结构

```
Geo_data_cleaning_skill/
├── README.md
└── Geo_data_cleaning_skill/
    ├── skill.md                  # Skill 定义（角色、铁律、工作流）
    ├── package.py                # 打包成 zip，方便分发
    ├── requirements.txt          # 依赖清单
    └── scripts/
        ├── data_profiler.py      # 数据探查，生成极简摘要
        ├── data_cleaner.py       # 清洗主流程
        ├── merge_helper.py       # 关联表左连接
        ├── requirement_engine.py # 生成/收集需求问题
        └── report_generator.py   # HTML 清洗报告
```

## 环境要求

- Python 3.8+
- 安装依赖：

```bash
pip install -r Geo_data_cleaning_skill/requirements.txt
```

依赖内容：`pandas>=2.0.0`、`openpyxl>=3.1.0`、`xlrd>=2.0.0`、`numpy>=1.24.0`。

## 安装为 Skill

把 `Geo_data_cleaning_skill` 文件夹整个放进所用 Agent 的 skills 目录，例如：

- Claude Code：`~/.claude/skills/geo-data-cleaning-skill/`
- Codex：`~/.codex/skills/geo-data-cleaning-skill/`

要分发给别人时，在 `Geo_data_cleaning_skill` 目录下运行 `python package.py`，会生成 `geo_data_cleaning_skill_v1.0_YYYYMMDD.zip`。

## 使用方法

### 方式一：作为 Skill 使用（推荐）

在对话里直接说「帮我清洗这个地质数据：`某文件.xlsx`」，Agent 会按 `skill.md` 里定义的四步走：

1. **探查**：输出 `data_profiler.py` 生成的摘要（主表行数、年龄列、地理列、缺失 Top3、重复行、关联表数量）。
2. **提问**：一次只问 1 个问题，选项形如 `[1/2]`。
3. **清洗**：按你的回答执行，完成后只报输出路径与行列变化。
4. **完成**：不再额外输出总结或建议。

### 方式二：直接在代码里调用

`data_cleaner.py` 使用相对导入，请以包的形式调用（在 `Geo_data_cleaning_skill` 目录下运行）：

```python
# 在 Geo_data_cleaning_skill 目录下运行
from scripts.data_profiler import GeoDataProfiler
from scripts.data_cleaner import GeoDataCleaner

path = r"D:\data\geochem.xlsx"

# 1) 探查
prof = GeoDataProfiler(path)
prof.load_all_sheets()
prof.detect_main_sheet()
prof.profile_main()
prof.profile_other_sheets()
print(prof.generate_report())

# 2) 清洗
cleaner = GeoDataCleaner(
    path,
    requirements={"age_choice": "Age", "merge_sheets": "是"},
    profile={"main_sheet": prof.main_sheet, "age_columns": prof.profile["age_columns"]},
)
cleaner.run_clean()
print(cleaner.get_report())
print(cleaner.save_output())
```

也可以只做探查：

```bash
python Geo_data_cleaning_skill/scripts/data_profiler.py 数据.xlsx
```

## 清洗规则

| 步骤 | 实现位置 | 规则 |
| --- | --- | --- |
| 读表探查 | `GeoDataProfiler` | 读取全部 Sheet，探查时每表只取前 1000 行以省内存 |
| 识别主表 | `detect_main_sheet()` | 列名含 `samp_id` 或 `sample` 的表为主表，否则取第一个 Sheet |
| 字段识别 | `profile_main()` | 自动识别年龄列（含 `age`）与地理列（含 `lat`/`lon`/`long`），统计缺失值与重复行 |
| 年龄标准化 | `clean_age()` | `Ga` → ×1000 转 Ma；`Ma` 保留；纯数字直接转 float；无法解析记 `NaN`，结果写入新列 `cleaned_age_Ma` |
| 关联表合并 | `merge_sheets()` | 以 `samp_id` 为键左连接；该表无此列时，退回使用第一个含 `id` 的列 |
| 输出 | `save_output()` | 默认输出 `原文件名_cleaned.xlsx`，工作表名 `Cleaned_Main` |

## 输出结果

- Excel：`原文件名_cleaned.xlsx`（工作表 `Cleaned_Main`），清洗过程不修改原始文件。
- 文本报告：`GeoDataCleaner.get_report()` 返回原始/清洗后的行列数与操作清单。
- HTML 报告：`ReportGenerator(original_df, cleaned_df, log).generate_html(path)` 可生成含行列对比与操作列表的 HTML 报告（需自行调用，主流程不会自动生成）。

## 常见问题

### 1. 提示 `No module named 'pandas'`

依赖没装好，重新执行：`pip install -r Geo_data_cleaning_skill/requirements.txt`。

### 2. 提示 `attempted relative import with no known parent package`

`data_cleaner.py` 用的是相对导入。请在 `Geo_data_cleaning_skill` 目录下运行，并按 `from scripts.data_cleaner import GeoDataCleaner` 的方式导入，不要直接双击运行该脚本。

### 3. 读取 `.xls` 报错

旧版 Excel 需要 `xlrd>=2.0.0`（已在依赖里）。仍失败的话，先用 Excel 另存为 `.xlsx` 再处理。

### 4. 主表识别错了

主表判定只认列名里的 `samp_id` / `sample`。可以在调用时直接传入正确的 Sheet 名，例如 `profile={"main_sheet": "Sheet2"}`。

### 5. 年龄列没有标准化

检查列名是否含 `age`（大小写不敏感）；也可以在 `requirements` 里用 `age_choice` 显式指定列名。

### 6. 关联表没并进来

合并键优先用 `samp_id`，找不到时退回第一个含 `id` 的列；两张表都没有可用键时该表会被跳过。

### 7. 输出文件在哪？

默认输出到原文件同目录，文件名为 `原文件名_cleaned.xlsx`。

## 已知限制

1. **仅支持 Excel**：输入为 `.xlsx` / `.xls`，不支持 CSV、Shapefile 等格式。
2. **探查是抽样**：探查阶段每表只读前 1000 行，缺失值/重复行统计基于该样本；清洗阶段才加载全量数据。
3. **合并键固定**：除 `samp_id` 外只做一次「含 id 列」的回退匹配，多键、多对多关系不支持。
4. **年龄列取平均的分支目前不可用**：`clean_age()` 中 `age_choice == '平均值'` 的分支调用了一个在其上游分支内定义的函数，会抛 `NameError`。请直接指定具体年龄列，或自行修复该分支。
5. **地理列只做识别**：目前只统计经纬度列，不做坐标校验、去重或转换。
6. **数据安全**：清洗在本地进行，但请自行确认输入数据的存放与分享是否合规。

## 许可

未附许可证文件。如需他人合法复用，建议补充 MIT / Apache-2.0 等许可证。
