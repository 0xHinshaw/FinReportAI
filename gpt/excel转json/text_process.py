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
from inspect import classify_class_attrs

def detect_quarter(str_list,defualt_quarter):
    for str_item in str_list:
        str_item = re.sub("\s","",str_item)
        match = re.search(r"第[一二三四]季",str_item)
        if match:
            return match.group()+"度"
        if re.search(r"[\(（]?1月?[\-~]3[\)）]?月",str_item):
            return "第一季度"
        if re.search(r"[\(（]?4月?[\-~]6[\)）]?月",str_item):
            return "第二季度"
        if re.search(r"[\(（]?7月?[\-~]9[\)）]?月",str_item):
            return "第三季度"
        if re.search(r"[\(（]?10月?[\-~]12[\)）]?月",str_item):
            return "第四季度"
        if re.search(r"[\(（]?1月?[\-~]6[\)）]?月",str_item):
            return "半年"
        if re.search(r"[\(（]?7月?[\-~]12[\)）]?月",str_item):
            return "下半年"
        if re.search(r"1月1日",str_item):
            return "年初"
        if re.search(r"12月31日",str_item):
            return "年末"
        if re.search(r"同期",str_item):
            if defualt_quarter != "全年" and defualt_quarter != "半年":
                defualt_quarter = "第" + defualt_quarter + "度"
        if re.search(r"[\(（]?7月?[\-~]12[\)）]?月",str_item):
            return "下半年"
        if re.search(r"(年度末?)|(年末)",str_item):
            return "年末"
        if defualt_quarter == "三季":
            if re.search(r"(年初至(.*?)期末)",str_item):
                return "前" + defualt_quarter + "度"
            if  re.search(r"(期初)",str_item):
                return "第" + defualt_quarter + "度初"
        if  re.search(r"(期初)",str_item):
                return "年初"
        if re.search(r"(年初至(.*?)期末)",str_item) is None:
            if defualt_quarter == "全年":
                if  re.search(r"(期末)",str_item):
                    return "年末"
            elif defualt_quarter == "半年" :
                if  re.search(r"(期末)",str_item):
                    return "半年末"
            else :
                if  re.search(r"(期末)",str_item):
                    return "第" + defualt_quarter + "度末"
    if defualt_quarter != "全年" and defualt_quarter != "半年":
        defualt_quarter = "第" + defualt_quarter + "度"
    return defualt_quarter

def detect_adjustment(str_list):
    for str_item in str_list:
        match = re.search(r"(调整后)|(调整前)",str_item)
        if match:
            return "-" + match.group()
    return ""

def classification_transfer(classification):
    if classification == "--":
        return ""
    else :
        return str("-"+classification)
    

def detect_year(str_list,defualt_year):
    for str_item in str_list:
        match = re.search(r"[0-9]{4}",str_item)
        if match:
            return match.group()
        if re.search(r"(本期)|(本报告期)|(当期)|(本年)",str_item):
            return defualt_year
        if re.search(r"(上期)|(去年)|(上年)",str_item):
            return str(int(defualt_year) - 1)
    return None

def process_unit(str_list,table_unit):
    for str_item in str_list:
        match = re.search(r"[（\(][个十百千万亿元吨公斤股\/\%]+[\)）]",str_item)
        if match:
            return match.group()
    return table_unit
        
def detect_unit(indicator):
    pass
    
   

def process_date(date,indicator,classification,table_name,defualt_year,defualt_quarter):
    year = detect_year([date,classification,indicator,table_name],defualt_year)
    if not year:
        year = defualt_year
    quarter = detect_quarter([date,classification,indicator,table_name],defualt_quarter)
    return year,quarter

def text2json(text,company,table_name,defualt_year,defualt_quarter,table_unit):
    text = re.sub(r"[\|]","",text)
    res = {"table_name":table_name,"data":[]}
    line_list = text.split("\n")
    num_clumns = 5
    for line in line_list:
        line = re.sub(r"\s+","\t",line.strip())
        if line.startswith("indicator"):
            num_clumns = len(line.split("\t"))
            indicator_index = line.split("\t").index("indicator")
            classification_index = line.split("\t").index("classification")
            value_index = line.split("\t").index("value")
            date_index = line.split("\t").index("date")
            year_on_year_index = line.split("\t").index("year-on-year")
            continue
        if len(line.split("\t")) != num_clumns or line.startswith("table") or line.startswith("...") :
            print(line)
            continue
        else:
            date = line.split("\t")[date_index].strip()
            classification = classification_transfer(line.split("\t")[classification_index].strip())
            indicator = line.split("\t")[indicator_index].strip()
            whether_adjustment = detect_adjustment([classification])
            unit = process_unit([indicator,classification],table_unit)
            year,quarter = process_date(date,indicator,classification,table_name,defualt_year,defualt_quarter)
            res["data"].append(
                {
                "year":year,
                "quarter":quarter,
                "company":company,
                "indicator":str(indicator+classification+whether_adjustment),
                "value":line.split("\t")[value_index].strip().replace("不适用","--"),
                "year-on-year":line.split("\t")[year_on_year_index].strip().replace("不适用","--"),
                "unit":unit
                }
            )
    return res