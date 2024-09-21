import os
import json
import pandas as pd
import logging
from pathlib import Path
# import openpyxl

# 配置日志
logging.basicConfig(filename='/home/luzhenye/PythonProject/gpt/excel转json/logs/comparison_json_excel.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_json_data(json_file_path):
    """Load JSON data from a given file path."""
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data
    
    
def load_excel_data(excel_file_path, sheet_names):
#     wb = openpyxl.load_workbook(excel_path)
#     sheet_names = wb.sheetnames
    # 获取所有工作表的名称
    xl = pd.ExcelFile(excel_file_path)
    data_frames = {}
    for sheet_name in sheet_names:
        if sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)
            data_frames[sheet_name] = df
    return data_frames


def validate_json_format(json_data, expected_keys):
    """
    Validate if JSON data has the correct format according to the GPT prompt requirements.
    """
    valid = True
    for item in json_data:
        for key in expected_keys:
            if key not in item:
                logging.error(f"Missing key '{key}' in JSON item: {item}")
                valid = False
            # if key == 'classification' and item[key] == '':
            #     item[key] = '--'
            if key == 'year-on-year' and item[key] == '':
                item[key] = '--'
    if valid:
        logging.info("All JSON items have the correct format.")
    else:
        logging.error("JSON format validation failed.")
    return valid

def compare_data(json_data, excel_data):
    for sheet_name, json_items in json_data.items():
        if sheet_name in excel_data:
            df = excel_data[sheet_name]
            for json_item in json_items:
                match = df[df['indicator'] == json_item['indicator']]
                if not match.empty:
                    for field in ['year', 'value', 'year-on-year']:
                        excel_val = str(match.iloc[0][field])
                        json_val = str(json_item[field])
                        if excel_val != json_val:
                            logging.info(f"Mismatch in {sheet_name} for {json_item['indicator']} {field}: Excel has {excel_val}, JSON has {json_val}")
                else:
                    logging.info(f"Indicator {json_item['indicator']} not found in {sheet_name} of Excel.")
        else:
            logging.info(f"Sheet {sheet_name} not found in Excel.")

def load_all_json_files(root_dir):
    all_data = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    data = load_json_data(file_path)
                    all_data.append((file_path, data))
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON from {file_path}: {str(e)}")
                except Exception as e:
                    logging.error(f"Error loading data from {file_path}: {str(e)}")
    return all_data

def main(excel_dir, json_dir):
    expected_format = ['year','quarter', 'company', 'indicator', 'value', 'year-on-year','unit']  #'classification', 'date'
    all_json_data = load_all_json_files(json_dir)
    for json_file_path, json_data in all_json_data:
        if validate_json_format(json_data['data'], expected_format):
            excel_file = os.path.join(excel_dir, Path(json_file_path).stem + '.xlsx')
            if os.path.exists(excel_file):
                excel_data = load_excel_data(excel_file, json_data.keys())
                compare_data(json_data, excel_data)
            else:
                logging.error(f"Excel file {excel_file} does not exist.")

if __name__ == "__main__":
    excel_dir = "/home/luzhenye/data/excel/定期报告"
    json_dir = "/home/luzhenye/data/json/定期报告"
    main(excel_dir, json_dir)
