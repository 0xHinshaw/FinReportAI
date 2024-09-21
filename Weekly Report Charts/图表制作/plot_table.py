import difflib
import json
import matplotlib.pyplot as plt
import pandas as pd
from dateutil import parser
from datetime import datetime
import re
from matplotlib.ticker import FormatStrFormatter
from matplotlib.font_manager import FontProperties
from get_data_func  import *
from plot_func import *

def sw_level_3_industry_gains(industry,save_path,start_date,end_date,column_list  = None):
    start_date = standardize_date_format(start_date)
    end_date = standardize_date_format(end_date)
    if column_list is None:
        column_list = get_sub_industry(industry)
    data_excel_path = "/home/luzhenye/data/iFind/同花顺指数/申万行业指数三级行业指数.xlsx"
    column_list,y_list = get_indicator_data(data_excel_path, parse_dates=[0], header=1, index_col=0,
                            fluctuation=True, start_date=start_date, end_date=end_date,
                            columns=column_list)
    _,y_300 = get_indicator_data("/home/luzhenye/data/iFind/同花顺指数/沪深300指数.xlsx",parse_dates=[0],header=1, index_col=0,fluctuation=True, start_date=start_date, end_date=end_date)
    column_list+=["沪深300"]
    y_list+=y_300
    get_bar(column_list, y_list, save_path,mark="沪深300")

def sw_level_1_industry_gains(save_path,start_date,end_date,mark ="沪深300"):
    start_date = standardize_date_format(start_date)
    end_date = standardize_date_format(end_date)
    column_list = [
    "农林牧渔", "煤炭", "石油石化", "钢铁", "有色金属",
    "电子", "家用电器", "食品饮料", "纺织服饰", "轻工制造",
    "医药生物", "公用事业", "交通运输", "房地产", "商贸零售",
    "社会服务", "综合", "建筑材料", "建筑装饰", "电力设备",
    "国防军工", "计算机", "通信", "银行", "非银金融", "传媒",
    "机械设备", "汽车", "美容护理", "环保", "基础化工"
    ]
    column_list,y_list = get_indicator_data("/home/luzhenye/data/iFind/同花顺指数/申万行业指数一级行业.xlsx", parse_dates=[0], header=1, index_col=0,
                            fluctuation=True, start_date=start_date, end_date=end_date,
                            columns=column_list)
    _,y_300 = get_indicator_data("/home/luzhenye/data/iFind/同花顺指数/沪深300指数.xlsx",parse_dates=[0],header=1, index_col=0,fluctuation=True, start_date=start_date, end_date=end_date)
    column_list+=["沪深300"]
    y_list+=y_300
    get_bar(column_list, y_list, save_path,mark=mark)

# 做折线图：
def sw_pe_ttm(start_date = "2019-06-19",end_date = "2024-06-20",save_path = "/home/luzhenye/data/png/test/test.png",
              average = True,legend = True,inx = '801120.SL'):
    start_date = standardize_date_format(start_date)
    end_date = standardize_date_format(end_date)
    df = pd.read_pickle("/home/luzhenye/data/iFind/同花顺指数/all_pe_ttm_index.pkl")
    date_range = list(pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d'))
    for date in date_range:
        if date not in df.index:
            df.loc[date,:] = [None for i in df.columns]
    df = df.sort_index()
    df = df.fillna(method='ffill')
    df = df.loc[start_date:end_date,:]
    y_list = list(df[inx])
    x = df.index
    get_line(x,y_list,save_path=save_path,average = average,legend = legend,today=end_date[-5:],indicator="市盈率（PE，TTM）")

# 个股排行榜单
def top_gainers_by_industry(codes,save_path = "/home/luzhenye/data/png/test/test.png",start_date="2023-11-06",
                            end_date="2023-11-10",top_num=8):
    start_date = standardize_date_format(start_date)
    end_date = standardize_date_format(end_date)
    x,y = get_sorted_gainers_by_industry(codes,start_date=start_date,end_date=end_date)
    if top_num>0:
        get_bar(x[:top_num],y[:top_num],save_path=save_path)
    else :
        get_bar(x[top_num:][::-1],y[top_num:][::-1],save_path=save_path,sort=False)

def sw_relative_hs_pe_ttm(start_date = "2019-06-19",end_date = "2024-06-20",save_path = "/home/luzhenye/data/png/test/test.png",
              average = True,legend = True,inx = '801120.SL',indicator = "相对沪深300的PE"):
    start_date = standardize_date_format(start_date)
    end_date = standardize_date_format(end_date)
    df = pd.read_pickle("/home/luzhenye/data/iFind/同花顺指数/all_pe_ttm_index.pkl")
    date_range = list(pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d'))
    for date in date_range:
        if date not in df.index:
            df.loc[date,:] = [None for i in df.columns]
    df = df.sort_index()
    df = df.fillna(method='ffill')
    df = df.loc[start_date:end_date,:]
    y_list = list(df[inx]/df["000300.SH"])
    x = df.index
    get_line(x,y_list,save_path=save_path,average = average,legend = legend,today=end_date[-5:],indicator=indicator)

def baijiu_price(product = "国窖1573",
    start_date = "2023-01-14",
    end_date = "2023-7-14",
    save_path = "/home/luzhenye/data/png/test/test.png",excel_path ="/home/luzhenye/data/iFind/白酒产品价格.xlsx"):
    df = pd.read_excel(excel_path, header=0, index_col=0).iloc[:-1,:]
    date_range = list(pd.date_range(start=start_date, end=end_date))
    for date in date_range:
        if date not in df.index:
            df.loc[date,:] = [None for i in df.columns]
    df = df.sort_index()
    df = df.fillna(method='ffill')
    df = df.loc[process_time_format(start_date):process_time_format(end_date),:]
    select_columns =  difflib.get_close_matches(product, df.columns, n=3, cutoff=0.2)[0]
    y_list = list(df[select_columns])
    get_line(date_range,y_list,save_path=save_path,today=end_date[-5:],indicator=select_columns)

def indicator_price(indicator = "豆粕市场价",
    start_date = "2019-07-29",
    end_date = "2023-07-29",
    save_path = "/home/luzhenye/data/png/test/test.png",excel_path ="/home/luzhenye/data/iFind/食品饮料相关经济数据.xlsx"):
    df = pd.read_excel(excel_path, header=0, index_col=0).iloc[:-1,:]
    date_range = list(pd.date_range(start=start_date, end=end_date))
    for date in date_range:
        if date not in df.index:
            df.loc[date,:] = [None for i in df.columns]
    df = df.sort_index()
    df = df.fillna(method='ffill')
    df = df.loc[process_time_format(start_date):process_time_format(end_date),:]
    select_columns =  difflib.get_close_matches(indicator, df.columns, n=3, cutoff=0.2)[0]
    y_list = list(df[select_columns])
    get_line(date_range,y_list,save_path=save_path,today=end_date[-5:],indicator=select_columns)