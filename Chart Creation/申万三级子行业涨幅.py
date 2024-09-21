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

def sw_level_3_industry_gains(industry,save_path,start_date,end_date):
    column_list = get_sub_industry(industry)
    data_excel_path = "/home/luzhenye/data/iFind/同花顺指数/申万行业指数三级行业指数.xlsx"
    column_list,y_list = get_indicator_data(data_excel_path, parse_dates=[0], header=1, index_col=0,
                            fluctuation=True, start_date=start_date, end_date=end_date,
                            columns=column_list)
    _,y_300 = get_indicator_data("/home/luzhenye/data/iFind/同花顺指数/沪深300指数.xlsx",parse_dates=[0],header=1, index_col=0,fluctuation=True, start_date=start_date, end_date=end_date)
    column_list+=["沪深300"]
    y_list+=y_300
    get_bar(column_list, y_list, save_path,mark="沪深300")


if __name__ == '__main__':
    sw_level_3_industry_gains("食品饮料",save_path = '/home/luzhenye/data/png/test/test.png',start_date="2023-11-06",end_date="2023-11-10")
    

