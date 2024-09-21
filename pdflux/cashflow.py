from openpyxl import load_workbook
import pandas as pd
import json
import json

def find_cash_flow_statements(file_path):
    """
    Find cash flow statements in an Excel file.

    Args:
    - file_path (str): The path to the Excel file.

    Returns:
    - results (dict): A dictionary containing cash flow statements organized by target texts and sheet names.
    """
    target_texts = [
        "经营活动产生的现金流量净额",
        "销售商品、提供劳务收到的现金",
        "客户存款和同业存放款项净增加额",
        "向中央银行借款净增加额",
        "向其他金融机构拆入资金净增加额",
        "收到原保险合同保费取得的现金",
        "收到再保业务现金净额",
        "保户储金及投资款净增加额",
        "收取利息、手续费及佣金的现金",
        "拆入资金净增加额",
        "回购业务资金净增加额",
        "代理买卖证券收到的现金净额",
        "收到的税费返还",
        "收到其他与经营活动有关的现金",
        "经营活动现金流入小计",
        "购买商品、接受劳务支付的现金",
        "客户贷款及垫款净增加额",
        "存放中央银行和同业款项净增加额",
        "支付原保险合同赔付款项的现金",
        "拆出资金净增加额",
        "支付利息、手续费及佣金的现金",
        "支付保单红利的现金",
        "支付给职工以及为职工支付的现金",
        "支付的各项税费",
        "支付其他与经营活动有关的现金",
        "经营活动现金流出小计"
    ]
    results = {text: {} for text in target_texts}  # Initialize results dictionary

    try:
        xls = pd.ExcelFile(file_path)
        for sheet_name in xls.sheet_names:
            sheet = pd.read_excel(xls, sheet_name=sheet_name)
            # delete the blankspaces, "\n", and "NULL"
            sheet = sheet.apply(lambda x: x.astype(str).str.strip())
            sheet = sheet.replace('', '0')
            sheet = sheet.fillna(0)
            for target_text in target_texts:
                cash_flow_found = False
                for index, row in sheet.iterrows():
                    if target_text in row.values:
                        cash_flow_found = True
                        # Extract data after finding the target text
                        data = print_cash_flow_values(sheet, target_text)
                        results[target_text][sheet_name] = data
                        break
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return results

def print_cash_flow_values(sheet, target_text):
    """
    Extract cash flow values from a sheet based on the target text.

    Args:
    - sheet (DataFrame): The DataFrame representing the Excel sheet.
    - target_text (str): The target text to search for in the sheet.

    Returns:
    - data (dict): A dictionary containing extracted cash flow values.
    """
    data = {}
    for index, row in sheet.iterrows():
        # if target_text in row.values:
        if any(target_text.strip() == cell.strip() for cell in row.values):
            for col_index in range(1, len(row)):
                col_name = sheet.columns[col_index]
                value = row.iloc[col_index]
                data[col_name] = value
            break
    return data

def save_results_to_json(results, output_file):
    """
    Save results to a JSON file.

    Args:
    - results (dict): The dictionary containing cash flow statements.
    - output_file (str): The path to the output JSON file.
    """
    try:
        with open(output_file, 'w') as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=4)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results to {output_file}: {e}")

if __name__ == '__main__':
# 示例使用
    file_path = "/data/chengsiyu/data/公司公告/2018-08-02：贵州茅台2018年半年度报告.xlsx"

    output_file = "/data/chengsiyu/result/cash_flow_results2.json"
    results = find_cash_flow_statements(file_path)
    save_results_to_json(results, output_file)
