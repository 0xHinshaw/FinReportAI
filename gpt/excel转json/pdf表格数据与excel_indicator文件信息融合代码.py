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

all_table_data = []
company_name = "贵州茅台(600519.SH)"
report_types = ['半年报告提取/data/', '年度报告提取/data/', '24年第一季度报告提取/data/', '第三季度报告提取/data/',"23年一季报/data"] #
for report_dir in report_types:
    report_type = report_dir.split('/')[0][:-2]
    report_headname = company_name + '-' + report_type + '-'

    for table_dir in os.listdir(report_dir):
        if ".json" in table_dir:
            table_file = os.path.join(report_dir, table_dir)
            table_name=table_dir.split('.')[0]
            table_headname = report_headname + table_name
            table_data_collector = {}
            table_data_collector['excel_name'] = table_headname
            table_data_collector['indicators_json_list'] = []
            table_data = json.load(open(table_file, 'r'))['data']
            table_data_collector['indicators_json_list'] += table_data
            all_table_data.append(table_data_collector)


# excel_indicators_file = "/home/luzhenye/data/temp/indicators_yoy.json"
# excel_indicators = json.load(open(excel_indicators_file, 'r'))
# all_table_data += excel_indicators
save_json_path = "/home/luzhenye/data/temp/indicators_ours.json"

with open(save_json_path,"w",encoding="utf-8") as file :
    json.dump(all_table_data, file,ensure_ascii=False, indent=4)










