from pathlib import Path
import json
import requests
import json
import ast
import os
import re
from tqdm import tqdm
import openpyxl
import pandas as pd
import numpy as np

## 加载同花顺财务指标的json数据，返回格式为“年份-季度-公司名-指标名: 数值”
def load_table(table_dir: str, #'/data/financial_report_baijiu/公司公告/tables/'
               table_name: str # ths_table_name
               ):

    json_path = os.path.join(table_dir, table_name)
    df = json.load(json_path)

    return df

## 用同花顺数据校验 our data 的准确性
def check_with_facts_function (index_name: str, #年份-季度-公司名-指标名# 
                               our_value: float,
                               ths_table: json,
                               error_log_file='./index_value_err.log'): 

    ## 去掉指标数据里的逗号
    our_value_digit = our_value.replace(',', '')
    ths_value_digit = ths_value.replace(',', '')
    
    ## 检验 our data 是否属于 numeric value
    if not our_value_digit.isnumeric():
        raise Exception("当前并非数值")
        return None

    
    ## 若数值相同，则返回 our data, 若不同则返回 同花顺的数据，并保留record
    if our_value_digit == ths_value_digit:
    # ths_table = load_table()
    # if our_value == ths_table[index_name].replace(',', ''):
        # print('A')
        return our_value
    else:
        # print('B')
        error_log = open(error_log_file, 'w')
        error_log.write(index_name+'\t'+our_value+'\t'+ths_value+'\n')
        return ths_value
        


if __name__ == '__main__':

    index_name = '2024年-第一季度-贵州茅台-销售商品、提供劳务收到的现金'
    ours = "10,990"
    ths_value = "10,991"
    ths_table_name = '同花顺.xlsx'
    answer = check_with_facts_function(index_name, ours, ths_table_name)
    print(answer, type(answer))
