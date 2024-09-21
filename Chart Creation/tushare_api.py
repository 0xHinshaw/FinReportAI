import tushare as ts

pro = ts.pro_api('2fbd06f20dd7df2ef71b08f77848e462e2f930108d696d837c8f295a')

#获取20230705当日所有申万行业指数的ts_code,name,open,close,vol,pe,pb数据
df = pro.sw_daily(trade_date='20230705', fields='ts_code,name,open,close,vol,pe,pb')
print(df)