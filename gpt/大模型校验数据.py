import math
import pandas as pd
import openpyxl
import difflib
import re
import difflib
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

def get_response_gpt4(content):
    """ 获取gpt-4模型的回复

    Args:
        content (_type_): 给gpt-4的问题

    Returns:
        _type_: 模型的回答
    """
    # url = "https://gateway.ai.cloudflare.com/v1/05c43e30f91a115d8153715954fd70ee/lingyue-ai/openai/chat/completions"
    # url = "https://api.deepseek.com/chat/completions"
    url = "https://api.kwwai.top/v1/chat/completions"
    headers = {
        # "Authorization": "Bearer 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",
        # "Authorization": "Bearer sk-246e62fbd9cc4d12bd1cd65a5a532c06",
        "Authorization": "Bearer sk-QeiIJwcjqnhybuSeBbC0F27eEc0b42529a4410194b362bBb",
        "Content-Type": "application/json"
    }
    data = {
        # "model": "gpt-4-0613",
        # "model": "gpt-4o",
        # "model": "deepseek-chat",
        "model": "gpt-4o",
        "messages": [
            {
            "role": "user",
            "content": f"{content}"
            }
        ],
        "stream" : False
        }
        
    response = requests.post(url, json=data, headers=headers)
    # 假设 response.text 是一个字符串，内容是有效的JSON
    json_string = response.text
    # 将JSON字符串转换为字典
    data_json = json.loads(json_string)
    return data_json["choices"][0]["message"]["content"]

def text2json(text,company):
    text = re.sub(r"\|","",text)
    res = {"table_name":"","data":[]}
    line_list = text.split("\n")
    for line in line_list:
        if len(line.split("\t")) != 4 or line.startswith("row_name"):
            continue
        else:
            date = line.split("\t")[1].strip()
            year = re.search(r"([0-9]{4})",date)
            if year:
                year = year.group()
            else :
                year = ""
            match = re.search(r"([一二三]*?\s*季)|中",date)
            if re.search(r"([一二三]*?\s*季)|中",date):
                quarter = match.group()
            else:
                quarter = "全年"
            whether_adjustment = "--"
            if re.search("调整前",date):
                whether_adjustment = False
            if re.search("调整后",date):
                whether_adjustment = True
            res["data"].append(
                {
                "year":year,
                "quarter":quarter,
                "whether-adjustment":whether_adjustment,
                "company":company,
                "indicator":line.split("\t")[0].strip(),
                "value":line.split("\t")[2].strip(),
                "year-on-year":line.split("\t")[3].strip()
                }
            )
    return res


def get_data_json_from_gpt(table,company):
    prompt = "please read the following table and extract all data based on the given format: \n" +\
            "table name: \n" +\
            "row_name \t column name \t value \t 同比变化(%) \n"  +\
            "...  \t ... \t ... \t ... \n"  +\
            "...  \t ... \t ... \t ... \n"  +\
            "Please note that some row or column names need to be combined. If " +\
            "同比变化(%) doesn't exist, set value as '-'" + str(table) +\
            "Please output table only and strictly follow the above format!"
    res = get_response_gpt4(prompt)
    print(res)
    with open("/home/luzhenye/data/temp/output/主要会计数据.txt","w",encoding="utf-8") as file :
        file.write(res)
    return text2json(res,company),res

   


def save_num_data_from_excel(excel_path,save_json_path,company):
    wb = openpyxl.load_workbook(excel_path)
    # 获取所有工作表的名称
    sheet_names = wb.sheetnames[8:]
    df = pd.read_excel(excel_path, sheet_names[0])
    markdown_str = str(df.to_markdown(index=False))
    df.fillna('', inplace=True)
    # print(close_sheet, df)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    res,res_gpt = get_data_json_from_gpt(markdown_str,company)
    # 指定在以下列中所有行都必须非空
    with open(save_json_path,"w",encoding="utf-8") as file :
        json.dump(res, file,ensure_ascii=False, indent=4)

excel_path = "/home/luzhenye/data/excel/tables/2024-04-03：贵州茅台：贵州茅台2023年年度报告.xlsx" 
save_json_path = "/home/luzhenye/data/temp/output/主要会计数据.json"       
save_num_data_from_excel(excel_path,save_json_path,"贵州茅台")
# text = "Certainly! Here is the data extracted from the provided table, formatted as requested:\n\n### 主要会计数据\n```plaintext\nrow_name \t                                column_name \t                     value\n营业收入 \t                                    2023年 \t                         147,693,604,994.14\n营业收入 \t                                    2022年调整后 \t                 124,099,843,771.99\n营业收入 \t                                    2022年调整前 \t                 124,099,843,771.99\n营业收入 \t                                    本期比上年同期增减(%) \t         19.01\n营业收入 \t                                    2021年调整后 \t                 106,190,154,843.76\n营业收入 \t                                    2021年调整前 \t                 106,190,154,843.76\n归属于上市公司股东的净利润 \t                    2023年 \t                         74,734,071,550.75\n归属于上市公司股东的净利润 \t                    2022年调整后 \t                 62,717,467,870.12\n归属于上市公司股东的净利润 \t                    2022年调整前 \t                 62,716,443,738.27\n归属于上市公司股东的净利润 \t                    本期比上年同期增减(%) \t         19.16\n归属于上市公司股东的净利润 \t                    2021年调整后 \t                 52,435,506,622.16\n归属于上市公司股东的净利润 \t                    2021年调整前 \t                 52,460,144,378.16\n归属于上市公司股东的扣除非经常性损益的净利润 \t    2023年 \t                         74,752,564,425.52\n归属于上市公司股东的扣除非经常性损益的净利润 \t    2022年调整后 \t                 62,792,896,829.57\n归属于上市公司股东的扣除非经常性损益的净利润 \t    2022年调整前 \t                 62,791,872,697.72\n归属于上市公司股东的扣除非经常性损益的净利润 \t    本期比上年同期增减(%) \t         19.05\n归属于上市公司股东的扣除非经常性损益的净利润 \t    2021年调整后 \t                 52,556,464,900.24\n归属于上市公司股东的扣除非经常性损益的净利润 \t    2021年调整前 \t                 52,581,102,656.24\n经营活动产生的现金流量净额 \t                    2023年 \t                         66,593,247,721.09\n经营活动产生的现金流量净额 \t                    2022年调整后 \t                 36,698,595,830.03\n经营活动产生的现金流量净额 \t                    2022年调整前 \t                 36,698,595,830.03\n经营活动产生的现金流量净额 \t                    本期比上年同期增减(%) \t         81.46\n经营活动产生的现金流量净额 \t                    2021年调整后 \t                 64,028,676,147.37\n经营活动产生的现金流量净额 \t                    2021年调整前 \t                 64,028,676,147.37\n归属于上市公司股东的净资产 \t                    2023年末 \t                     215,668,571,607.43\n归属于上市公司股东的净资产 \t                    2022年末调整后 \t             197,480,041,239.46\n归属于上市公司股东的净资产 \t                    2022年末调整前 \t             197,506,672,396.00\n归属于上市公司股东的净资产 \t                    本期末比上年同期末增减(%) \t     9.21\n归属于上市公司股东的净资产 \t                    2021年末调整后 \t             189,511,713,508.90\n归属于上市公司股东的净资产 \t                    2021年末调整前 \t             189,539,368,797.29\n总资产 \t                                        2023年末 \t                     272,699,660,092.25\n总资产 \t                                        2022年末调整后 \t             254,500,826,096.02\n总资产 \t                                        2022年末调整前 \t             254,364,804,995.25\n总资产 \t                                        本期末比上年同期末增减(%) \t     7.15\n总资产 \t                                        2021年末调整后 \t             255,315,103,017.82\n总资产 \t                                        2021年末调整前 \t             255,168,195,159.90\n股本 \t                                            2023年末 \t                     1,256,197,800.00\n股本 \t                                            2022年末调整后 \t             1,256,197,800.00\n股本 \t                                            2022年末调整前 \t             1,256,197,800.00\n股本 \t                                            2021年末调整后 \t             1,256,197,800.00\n股本 \t                                            2021年末调整前 \t             1,256,197,800.00\n```"

