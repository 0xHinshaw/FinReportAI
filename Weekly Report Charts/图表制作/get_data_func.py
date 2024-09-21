import json
import matplotlib.pyplot as plt
import pandas as pd
from dateutil import parser
from datetime import datetime, timedelta
import re
from matplotlib.ticker import FormatStrFormatter
from matplotlib.font_manager import FontProperties
import numpy as np
from iFinDPy import THS_iFinDLogin,THS_HistoryQuotes,THS_Trans2DataFrame,THS_iFinDLogout,THS_EDBQuery,THS_BasicData

def standardize_date_format(date_string):
    parsed_date = parser.parse(date_string)
    # 格式化日期
    formatted_date = parsed_date.strftime("%Y-%m-%d")
    return formatted_date

def get_sorted_gainers_by_industry(codes,start_date,end_date,):
    THS_iFinDLogin("dgzq828","329804")
    res = THS_Trans2DataFrame(THS_BasicData(codes,"ths_int_chg_ratio_stock",f"{start_date},{end_date},106")).sort_values(by="ths_int_chg_ratio_stock",ascending=False)
    THS_iFinDLogout() 
    companies = get_company_by_code(list(res["thscode"]),excel_path="/home/luzhenye/data/iFind/同花顺指数/全部A股申万三级行业分类.xlsx")
    return companies,list(res["ths_int_chg_ratio_stock"])

def get_code_by_company(company,excel_path = "/home/luzhenye/data/iFind/同花顺指数/沪深A股所属申万三级行业.xlsx",df = None):
    if isinstance(company,str):
        if df is None:
            with open(excel_path,"rb") as file:
                df = pd.read_excel(file)
            code = df[df.iloc[:,1]==company].iloc[0,0]
        else:
            code = df[df.iloc[:,1]==company].iloc[0,0]
    elif isinstance(company,list):
        if df is None:
            with open(excel_path,"rb") as file:
                df = pd.read_excel(file)
        df.set_index(df.columns[1],inplace=True)
        code = list(df.loc[company,"证券代码"])
    else:
        raise "请输入字符串或列表"
    return code

def get_company_by_code(code,excel_path = "/home/luzhenye/data/iFind/同花顺指数/沪深A股所属申万三级行业.xlsx",df = None):
    if isinstance(code,str):
        if df is None:
            with open(excel_path,"rb") as file:
                df = pd.read_excel(file)
            company = df[df.iloc[:,0]==code].iloc[0,1]
        else:
            company = df[df.iloc[:,0]==code].iloc[0,1]
    elif isinstance(code,list):
        if df is None:
            with open(excel_path,"rb") as file:
                df = pd.read_excel(file)
        df.set_index(df.columns[0],inplace=True)
        company = list(df.loc[code,"证券名称"])
    else:
        raise "请输入字符串或列表"
    return company


def process_time_format(date_string):
    """处理所有的时间字符串，转为datetime格式

    Args:
        date_string (_type_): _description_

    Returns:
        _type_: _description_
    """
    parsed_date = parser.parse(date_string)
    return parsed_date

def get_sub_industry(level_1):
    """输入申万一级行业，得到所有下属的三级行业列表

    Args:
        level_1 (_type_): _description_

    Returns:
        _type_: _description_
    """
    result =[]
    with open("/home/luzhenye/PythonProject/图表制作/sw_industry_classification.json","r",encoding="utf-8") as file:
        sw_industry_classification = json.load(file)
    for key in sw_industry_classification[level_1].keys():
        result+=sw_industry_classification[level_1][key]
    return result

def get_company_level_3_industry(company):
    """获取公司对应的申万三级行业类别

    Args:
        company (_type_): 公司名

    Returns:
        _type_: 返回申万三级行业
    """
    with open("/home/luzhenye/data/iFind/同花顺指数/沪深A股所属申万三级行业.xlsx","rb") as file:
        df = pd.read_excel(file)
        category = df[df.iloc[:,1]==company].iloc[0,2]
    return category

def get_companies_in_level_3_industry(industry):
    """输入申万三级行业名称，得到对应三级行业中包含的企业。
    Args:
        industry (_type_): _description_
    Returns:
        _type_: _description_
    """
    with open("/home/luzhenye/data/iFind/同花顺指数/沪深A股所属申万三级行业.xlsx","rb") as file:
        df = pd.read_excel(file)
        companies = list(df[df.iloc[:,2]==industry].iloc[:,1])
    return companies

def get_companies_in_level_1_industry(industry):
    """输入申万一级行业名称，得到对应一级行业中包含的企业。

    Args:
        industry (_type_): _description_

    Returns:
        _type_: _description_
    """
    sub_industry_list = get_sub_industry(industry)
    with open("/home/luzhenye/data/iFind/同花顺指数/沪深A股所属申万三级行业.xlsx","rb") as file:
        df = pd.read_excel(file)
        companies = list(df[df.iloc[:,2].apply(lambda x: x in sub_industry_list)].iloc[:,1])
    return companies

def get_indicator_data(excel_path, parse_dates=False, header=None, index_col=None, date=None, columns=None, fluctuation=False, start_date=None, end_date=None):
    df = pd.read_excel(excel_path, parse_dates=parse_dates, header=header, index_col=index_col)
    df = df.sort_index()
    df = df.fillna(method='ffill')
    # print(df.columns)
    final_list =[]
    if columns is not None:
        select_columns = ["" for i in columns]
        for col_index,column in enumerate(columns):
            for df_column in df.columns:
                if re.search(f"{column}", f"{df_column}"):
                    select_columns[col_index]=df_column
                    break
        for col_index,col in enumerate(select_columns):
            if col == "":
                print(f"您需要的{columns[col_index]}数据无法在excel中找出")
            else:
                final_list.append(columns[col_index])
        select_columns = [i for i in select_columns if i != ""]
    else:
        select_columns = df.columns
        final_list = select_columns
    if fluctuation:
        start_date  = process_time_format(start_date)- timedelta(days=1)
        df = df.loc[process_time_format(str(start_date)):process_time_format(end_date), select_columns]
        y_list = list((df.iloc[-1] - df.iloc[0]) / df.iloc[0] * 100)
    else:
        y_list = list(df.loc[process_time_format(date), select_columns])
    # print(df)
    return final_list,y_list