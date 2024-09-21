import difflib
from get_data_func import *
import json
import matplotlib.pyplot as plt
import pandas as pd
from dateutil import parser
from datetime import datetime, timedelta
import re
from matplotlib.ticker import FormatStrFormatter
from matplotlib.font_manager import FontProperties
import numpy as np
from plot_func import*

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
if __name__ == '__main__':
    indicator_price()