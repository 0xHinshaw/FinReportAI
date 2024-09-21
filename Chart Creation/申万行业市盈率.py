import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from iFinDPy import THS_iFinDLogin,THS_HistoryQuotes,THS_Trans2DataFrame,THS_iFinDLogout,THS_EDBQuery,THS_BasicData

THS_iFinDLogin("dgzq828","329804")
res = THS_Trans2DataFrame(THS_BasicData("801120.SL","ths_pe_ttm_index","2024-6-19,100,100"))
THS_iFinDLogout() 
print(res)