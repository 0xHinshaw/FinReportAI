import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from iFinDPy import THS_iFinDLogin,THS_HistoryQuotes,THS_Trans2DataFrame,THS_iFinDLogout,THS_EDBQuery,THS_BasicData,THS_HQ
import pickle
import pandas as pd
from plot_func import *

# 获取历史数据并存储
start_date = "2019-06-19"
end_date = "2024-06-20"
# THS_iFinDLogin("dgzq828","329804")
# res = THS_HQ('801010.SL,801030.SL,801040.SL,801050.SL,801080.SL,801110.SL,801120.SL,801130.SL,801140.SL,801150.SL,801160.SL,801170.SL,801180.SL,801200.SL,801210.SL,801230.SL,801710.SL,801720.SL,801730.SL,801740.SL,801750.SL,801760.SL,801770.SL,801780.SL,801790.SL,801880.SL,801890.SL,801950.SL,801960.SL,801970.SL,801980.SL','pe_ttm_index','','2019-06-20','2024-06-20')
# THS_iFinDLogout()
# res.data.to_pickle('/home/luzhenye/data/iFind/同花顺指数/hs300_pe_ttm_index.pkl')
# 读取 Pickle 文件
# df = pd.read_pickle('/home/luzhenye/data/iFind/同花顺指数/hs300_pe_ttm_index.pkl')
# print(df)
# print(res)

# 做折线图：
def sw_relative_hs_pe_ttm(start_date = "2019-06-19",end_date = "2024-06-20",save_path = "/home/luzhenye/data/png/test/test.png",
              average = True,legend = True,inx = '801120.SL'):
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

if __name__ == '__main__':
    sw_relative_hs_pe_ttm(start_date = "2019-06-19",end_date = "2024-06-20",save_path = "/home/luzhenye/data/png/test/test.png")

    
    