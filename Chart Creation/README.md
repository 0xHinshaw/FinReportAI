# 图表制作文件说明

## 文件：
### get_data_func.py 包含用于提取数据的函数

- get_code_by_company （证券名称转证券代码）
```python
get_code_by_company(company,
    excel_path = "/home/luzhenye/data/iFind/同花顺指数/沪深A股所属申万三级行业.xlsx",
    df = None)
```
输入证券名称，返回证券代码，支持字符串和列表格式的输入，输出对应格式  
默认只支持沪深A股的证券，如果需要全部A股，将excel_path改为"/home/luzhenye/data/iFind/同花顺指数/全部A股申万三级行业分类.xlsx"  


- get_company_by_code （证券代码转证券名称）
```python
get_company_by_code(code,
    excel_path = "/home/luzhenye/data/iFind/同花顺指数/沪深A股所属申万三级行业.xlsx",
    df = None)
```
输入证券代码，返回证券名称，支持字符串和列表格式的输入，输出对应格式  
默认只支持沪深A股的证券，如果需要全部A股，将excel_path改为"/home/luzhenye/data/iFind/同花顺指数/全部A股申万三级行业分类.xlsx"  
  
  
- process_time_format （处理时间字符串）
```python
process_time_format(date_string)
```
处理所有的时间字符串，转为datetime格式

- get_sub_industry （获取申万一级行业所包含的申万三级行业）
```python
get_sub_industry(level_1)
```
输入申万一级行业，得到所有下属的三级行业列表，只支持字符串输入，输出列表

- get_company_level_3_industry （获取公司对应的申万三级行业类别）
```python
get_company_level_3_industry(company)
```
获取公司对应的申万三级行业类别，只支持字符串输入，输出字符串

- get_companies_in_level_3_industry （获取三级行业中包含的公司）
```python
get_companies_in_level_3_industry(industry)
```
输入申万三级行业名称，得到对应三级行业中包含的公司列表。

- get_companies_in_level_1_industry （获取一级行业中包含的公司）
```python
get_companies_in_level_1_industry(industry)
```
输入申万一级行业名称，得到对应一级行业中包含的公司列表。

### plot_func.py 包含用于作图的函数
### plot_table.py 包图表制作函数
- sw_level_3_industry_gains()
```python
sw_level_3_industry_gains(industry,save_path,start_date,end_date,column_list = None)
```
输入申万一级行业名称，得到对应的三级行业涨幅柱状图，save_path为图片保存地址，start_date为起始日期，end_date为结束日期。
指定三级行业列表可以输入column_list
- sw_level_1_industry_gains()
```python
sw_level_1_industry_gains(save_path,start_date,end_date,mark ="沪深300")
```
获取一级行业涨幅柱状图，save_path为图片保存地址，start_date为起始日期，end_date为结束日期，mark为特殊颜色标记的行业
