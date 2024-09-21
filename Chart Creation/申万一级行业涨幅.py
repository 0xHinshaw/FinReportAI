import matplotlib.pyplot as plt
import pandas as pd
from dateutil import parser
from datetime import datetime
import re
from matplotlib.ticker import FormatStrFormatter
import numpy as np
from matplotlib.font_manager import FontProperties
from get_data_func import *
from plot_func import *

if __name__ == "__main__":
    column_list = [
    "农林牧渔", "煤炭", "石油石化", "钢铁", "有色金属",
    "电子", "家用电器", "食品饮料", "纺织服饰", "轻工制造",
    "医药生物", "公用事业", "交通运输", "房地产", "商贸零售",
    "社会服务", "综合", "建筑材料", "建筑装饰", "电力设备",
    "国防军工", "计算机", "通信", "银行", "非银金融", "传媒",
    "机械设备", "汽车", "美容护理", "环保", "基础化工"
    ]
    column_list,y_list = get_indicator_data("/home/luzhenye/data/iFind/同花顺指数/申万行业指数一级行业.xlsx", parse_dates=[0], header=1, index_col=0,
                            fluctuation=True, start_date="2023/11/5", end_date="2023/11/10",
                            columns=column_list)
    # y_list = get_indicator_data("/home/luzhenye/data/excel/同花顺/申万行业指数一级行业.xlsx", parse_dates=[0], header=1, index_col=0,
    #                         date="2023/11/10",
    #                         columns=industry_list)
    _,y_300 = get_indicator_data("/home/luzhenye/data/iFind/同花顺指数/沪深300指数.xlsx",parse_dates=[0],header=1, index_col=0,fluctuation=True, start_date="2024/5/19", end_date="2024/5/31")
    column_list+=["沪深300"]
    y_list+=y_300
    get_bar(column_list, y_list, '/home/luzhenye/data/png/test/test.png',mark="沪深300")
    # print(y_list)
    # print(len(industry_list))
    # print(len(y_list))
    # get_bar(df,'/home/luzhenye/data/png/test/sales_data.png')

