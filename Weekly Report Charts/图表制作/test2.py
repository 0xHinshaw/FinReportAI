from datetime import timedelta
from get_data_func import *
from plot_table import sw_level_1_industry_gains

if __name__ == '__main__':
    start_date = "2023-06-10"
    start_date  = process_time_format(start_date)- timedelta(days=1)
    sw_level_1_industry_gains("/home/luzhenye/data/png/test/test.png",start_date="2023-11-6",end_date="2023-11-10")
    # THS_iFinDLogin("dgzq828","329804")
    # res = THS_BasicData("801180.SL","ths_shhk_szhk_int_net_buy_amount_stock","2024-6-10,2024-6-19")
    # THS_iFinDLogout() 
    # print(res)