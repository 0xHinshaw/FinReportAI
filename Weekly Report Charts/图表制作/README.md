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

- sw_pe_ttm()
```python
sw_pe_ttm(start_date = "2019-06-19",end_date = "2024-06-20",save_path = "/home/luzhenye/data/png/test/test.png",
              average = True,legend = True,inx = '801120.SL')
```
获取申万一级行业的折线图，默认为食品饮料，目前只有近5年的数据，后续补充，inx 用于指定一级行业。

- sw_relative_hs_pe_ttm()
```python
sw_relative_hs_pe_ttm(start_date = "2019-06-19",end_date = "2024-06-20",save_path = "/home/luzhenye/data/png/test/test.png",
              average = True,legend = True,inx = '801120.SL',indicator = "相对沪深300的PE")
```
用于画出申万一级行业相对沪深300指数的PE折线图，修改inx画出不同的图，average、legend分别处理平均线和图片上方的图例。

- top_gainers_by_industry(codes)
```python
top_gainers_by_industry(codes,save_path = "/home/luzhenye/data/png/test/test.png",start_date="2023-11-06",
                            end_date="2023-11-10",top_num=8)
```
输入股票代码的列表，获取股票涨幅榜图，top_num用于指定前多少的榜单,支持输入负数，以获取跌幅榜图。

- baijiu_price()
```python
 baijiu_price(product = "国窖1573",
    start_date = "2023-01-14",
    end_date = "2023-7-14",
    save_path = "/home/luzhenye/data/png/test/test.png",excel_path ="/home/luzhenye/data/iFind/白酒产品价格.xlsx")
```
输入白酒产品名字，获取白酒的价格折线图。目前只有如下产品：[批发参考价:五粮液:普五(八代)(52度):500ml,批发参考价:酱香茅台:茅台1935(53度):500ml,批发参考价:飞天茅台:22年飞天(散)(53度):500ml,批发参考价:飞天茅台:十五年(53度):500ml,批发参考价:飞天茅台:20年飞天(散)(53度):500ml,批发参考价:泸州老窖:国窖1573(52度):500ml]

- indicator_price()
```python
indicator_price(indicator = "豆粕市场价",
    start_date = "2019-07-29",
    end_date = "2023-07-29",
    save_path = "/home/luzhenye/data/png/test/test.png",excel_path ="/home/luzhenye/data/iFind/食品饮料相关经济数据.xlsx")
```
输入指标名字，获取指标的折线图。目前只有如下指标：[生产资料价格:大豆(黄豆),现货价:豆粕,现货价格:白砂糖:长沙:产地广西,现货价:玻璃,现货价:大麦:全国均价,啤酒:产量:累计值,啤酒:产量:当月值,现货均价:铝锭(华南):佛山,出厂价:包装纸:瓦楞纸:140g,平均价:生鲜乳(原奶):主产区,平均批发价:猪肉,全国:生猪存栏]

