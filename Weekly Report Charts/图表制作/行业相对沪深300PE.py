import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from iFinDPy import THS_iFinDLogin,THS_HistoryQuotes,THS_Trans2DataFrame,THS_iFinDLogout,THS_EDBQuery,THS_BasicData,THS_HQ
import pickle
import pandas as pd
from plot_func import *

# 获取历史数据并存储
start_date = "2019-06-19"
end_date = "2024-06-20"
def sw_relative_hs_pe_ttm(start_date = "2019-06-19",end_date = "2024-06-20",save_path = "/home/luzhenye/data/png/test/test.png",
              average = True,legend = True,inx = '801120.SL',indicator = "相对沪深300的PE"):
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

if __name__ == '__main__':
    sw_relative_hs_pe_ttm(start_date = "2019-06-19",end_date = "2024-06-20",save_path = "/home/luzhenye/data/png/test/test.png",
                          indicator = "SW食品饮料行业相对沪深300的PE")
