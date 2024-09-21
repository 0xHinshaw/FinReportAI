# Financial Data Extraction from Excel Files

This Python script is used to extract specific financial data from Excel files. The script contains several functions that are used to extract different types of financial data based on the parameter provided.

## Functions

The script contains the following functions. Specific function readme can be found down in the document:

- `get_income_info()`: Extracts income information. (营业总收入总量, 营业总收入同比, 营业总收入季环比)
- `find_cash_flow_statements()`: Finds cash flow statements. (经营活动产生的现金流量净额)
- `get_net_profit()`: Extracts net profit. (归属于母公司股东的净利润总量, 归属于母公司股东的净利润同比, 归属于母公司股东的净利润季环比)
- `find_gross_margin()`: Finds gross margin. (毛利率)
- `get_revenue()`: Extract different ratios and profit. (销售费用率, 管理费用率, 财务费用率, 研发费用率, 净利润)

## Usage

The script is used by calling the `extract_data()` function with a file path and a parameter. The function reads the Excel file at the specified path and extracts the data based on the parameter.

Here is an example of how to use the script:

``` python
file_path = '/data/financial_report_baijiu/公司公告/tables/2018-03-28：贵州茅台2017年年度报告.xlsx'
print(extract_data(file_path, "销售费用率"))
```

In this example, the script reads the Excel file at the specified path and extracts the sales expense rate.

## Parameters

The `extract_data()` function only accepts the following parameters:

- 营业总收入总量
- 营业总收入同比
- 营业总收入季环比
- 归属于母公司股东的净利润总量
- 归属于母公司股东的净利润同比
- 归属于母公司股东的净利润季环比
- 毛利率
- 销售费用率
- 管理费用率
- 财务费用率
- 研发费用率
- 净利润
- 经营活动产生的现金流量净额

## 归属于母公司股东的净利润相关数据获取

假设用户只传入他所需要的指标名称，通过字典对应的函数，调用函数返回结果。

```python
    target_dict = {
            "同比":extra_year_on_year_data,
            "总量":extra_recent_data,
            "季度环比":extra_quarter_over_quarter_data
        }
```

### 使用指南

示例：

```python
from net_profit import get_net_profit

excel_path = "dir_name/2018-04-21：金徽酒2017年年度报告.xlsx"
print(get_net_profit(excel_path,"同比"))
```

输出结果为：

```  python
{'本期：': '252,961,361.81 ', '上期：': '221,865,803.02 ', '同比：': 0.1402}
```

### 功能和特点

#### 模糊匹配

为了应对表格的名字，列名，行名在不同文件下不统一，所以会以相对模糊的形式匹配出最有可能的那一个。

#### 表名匹配失败时，遍历表格

当未搜索到类似“合并利润表”时，会对所有表格的行列内容匹配“归属于母公司股东的净利润”相关内容，找到目标表格。


### 1. 年度营业收入分析（income.py）

这个项目提供了两个主要功能：

年度营业总收入分析：根据输入的财务报告文件，分析并计算当前年度与上一年度的营业总收入，并给出同比增长率。

季度环比增长率计算：根据输入的财务报告文件，计算每个季度的环比增长率。

#### 主要函数

- `analyze_income(file_path: str) -> Tuple[Optional[float], Optional[float], float]`

    **功能：** 分析给定财务报告文件中的年度营业总收入，并计算同比增长率。

    **参数：** `file_path`: str: 财务报告文件的路径。

    **返回值：** Tuple[Optional[float], Optional[float], float] - 包含当前年度营业总收入、前一年度营业总收入和同比增长率的元组。如果找不到收入数据，则返回 `None`。

- `analyze_quarterly_income(file_path: str) -> List[Tuple[str, float]]`

    **功能：** 分析给定财务报告文件中的季度营业总收入。

    **参数：** `file_path`: str - 财务报告文件的路径。

    **返回值：** `List[Tuple[str, float]]` - 包含每个季度的营业总收入的列表。每个元组包含季度名称和对应的营业总收入。

## Gross_income计算
这个脚本用于从一个给定的 Excel 文件中查找并提取毛利率数据。它能够识别包含"毛利率（%）"的单元格，并输出每个具体条目的毛利率。（假定所有“毛利率（%）”都是作为列名的单元格）

### 基本逻辑
1. **Excel 文件加载**：首先，脚本会加载指定的 Excel 文件。
   
2. **遍历 Sheets**：脚本会遍历文件中的所有 Sheets。

3. **查找毛利率所在单元格**：对于每个 Sheet，它会在每行中查找仅包含"毛利率（%）"的单元格。

4. **提取毛利率数据**：一旦找到包含"毛利率（%）"的单元格，脚本会提取该列下方的数据，并尝试将其转换为数字格式。

5. **输出结果**：最终，脚本会将每个具体条目以及其对应的毛利率以文本格式输出。

### 函数介绍
- **`is_number(value)`**：检查输入值是否为数字。
- **`find_gross_margin(file_path)`**：主要函数，用于查找并输出 Excel 文件中的毛利率数据。
- **`gm_main()`**：新添加的函数，用于运行整个脚本。

### 输入与输出
- **输入**：单个 Excel 文件路径。
- **输出**：每个具体条目及其对应的毛利率，以文本格式输出。

### 示例
- **输入文件**：2018-03-28：贵州茅台2017年年度报告.xlsx
- **输出结果**：
  - 酒类 : 89.83%
  - 茅台酒 : 92.82%
  - 其他系列酒 : 62.75%
  - 国内  : 89.9%
  - 国外  : 88.11%

## 费用率计算功能
这个脚本用于处理指定的 Excel 文件，提取其中的数据并计算相关费用率。它能够根据给定的列名或文本信息，从 Excel 文件中提取销售费用、管理费用、财务费用、研发费用、营业总收入和净利润数据，并计算对应的费用率。

### 基本逻辑
1. **处理 Excel 文件（`process_excel`函数）**：读取 Excel 文件，检查sheets中是否包含“合并利润表”关键字，如果存在则执行情况一的处理，否则执行情况二的处理。

2. **处理情况一（`process_case_one`函数）**：从上一步中定位到符合要求的sheet，检查是否存在指定的列名，并提取相关数据。如果存在数值列名（假设为“本期发生额”），则提取指定列名下的数据。
   
3. **计算各项费用率（`calculate_ratios`函数）**：根据提取的数据，计算销售费用率、管理费用率、财务费用率、研发费用率和净利率，并打印输出。

4. **处理情况二（`process_case_two`函数）**：遍历所有sheets检查是否存在指定的文本，然后定位到符合要求的sheet，并根据情况一处理。

### 函数介绍
- **`process_case_one(sheet)`**：处理情况一，提取指定列名的数据。
- **`calculate_ratios(result)`**：根据提取的数据计算各项费用率。
- **`process_case_two(sheet)`**：处理情况二，根据文本信息提取数据并调用情况一处理。
- **`process_excel(file_path)`**：处理 Excel 文件，提取数据并计算费用率。
- **`revenue_main()`**：主函数，用于运行整个脚本。

### 输入与输出
- **输入**：单个 Excel 文件路径。
- **输出**：计算出的销售费用率、管理费用率、财务费用率和净利率。

### 示例
- **输入文件**：2018-03-28：贵州茅台2017年年度报告.xlsx
- **输出结果**：
  - 销售费用率: 4.89%
  - 管理费用率: 7.73%
  - 财务费用率: -0.09%
  - 净利率: 47.50%
