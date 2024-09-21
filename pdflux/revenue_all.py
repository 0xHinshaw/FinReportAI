import pandas as pd

def process_case_one(sheet):
    '''
    处理情况一：检查是否存在指定的列名，并提取相关数据。

    输入:
    - sheet: 包含数据的 DataFrame。

    输出:
    - 包含销售费用、管理费用、财务费用、研发费用、营业总收入和净利润的字典。
    '''
    # 检查是否存在指定的列名
    required_rows = ["销售费用", "管理费用", "财务费用", "研发费用", "营业总收入", "净利润"]
    if sheet.empty:
        print("DataFrame为空")
        return
    
    result = {}
    
    # 检查第一行的第二个单元格是否包含“附注”，确定数据列的位置
    note_column_index = None
    if "附注" in str(sheet.iloc[0, 1]).strip().lower():
        note_column_index = 1
    
    # 数据应当在第二列，即列索引为 1
    value_column_index = 1 if note_column_index != 1 else 2
    
    for row_name in required_rows:
        # 在当前 sheet 中查找包含指定文本的行
        found = False
        for index, row in sheet.iterrows():
            if row_name in str(row[0]):  # 第一列的单元格包含行名
                # 获取对应的数值
                value = str(row[value_column_index]).strip()
                
                # 检查数值是否为空，如果为空且不是“附注”列，就跳过该列
                if not value and value_column_index != note_column_index:
                    continue
                
                # 转换为数字（去除逗号并尝试转换为浮点数）
                try:
                    value = float(value.replace(",", ""))
                except ValueError:
                    value = None
                
                # 存储结果
                result[row_name] = value
                found = True
                break
        
        if not found:
            result[row_name] = None
    
    return result



def calculate_ratios(result):
    '''
    根据提取的数据计算各项费用率。

    输入:
    - result: 包含提取数据的字典。

    输出:
    - ratios: 包含各项费用率的字典。
    '''
    # 计算各项费用率
    ratios = {}
    
    # 计算销售费用率
    if result["销售费用"] is not None and result["营业总收入"] != 0:
        ratios["销售费用率"] = result["销售费用"] / result["营业总收入"] * 100
    else:
        ratios["销售费用率"] = None
    
    # 计算管理费用率
    if result["管理费用"] is not None and result["营业总收入"] != 0:
        ratios["管理费用率"] = result["管理费用"] / result["营业总收入"] * 100
    else:
        ratios["管理费用率"] = None
    
    # 计算财务费用率
    if result["财务费用"] is not None and result["营业总收入"] != 0:
        ratios["财务费用率"] = result["财务费用"] / result["营业总收入"] * 100
    else:
        ratios["财务费用率"] = None
    
    # 计算研发费用率
    if result["研发费用"] is not None and result["营业总收入"] != 0:
        ratios["研发费用率"] = result["研发费用"] / result["营业总收入"] * 100
    else:
        ratios["研发费用率"] = None
    
    # 计算净利率
    if result["净利润"] is not None and result["营业总收入"] != 0:
        ratios["净利率"] = result["净利润"] / result["营业总收入"] * 100
    else:
        ratios["净利率"] = None
    
    # 打印比率
    for key, value in ratios.items():
        if value is not None:
            print(f"{key}: {value:.2f}%")
    
    return ratios

def process_case_two(sheet):
    '''
    处理情况二：检查是否存在指定的文本，并根据情况一处理。

    输入:
    - sheet: 包含数据的 DataFrame。

    输出:
    - 包含提取数据的字典。
    '''
    required_texts = ["销售费用", "营业总收入", "净利润"]
    found_texts = set()
    for text in required_texts:
        found = False
        for index, value in sheet.stack().items():
            if text in str(value):
                found_texts.add(text)
                found = True
                break
        if not found:
            return None
    
    if set(required_texts) == found_texts:
        return process_case_one(sheet)

def process_excel(file_path):
    '''
    处理 Excel 文件，提取数据并计算费用率。

    输入:
    - file_path: Excel 文件路径。

    输出:
    - 包含提取数据的字典。
    '''
    # 读取 Excel 文件
    xls = pd.ExcelFile(file_path)
    
    # 遍历所有 sheet
    found = False
    for sheet_name in xls.sheet_names:
        sheet = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        # 检查是否包含“合并利润表”关键字
        if "合并利润表" in sheet_name:
            found = True
            result = process_case_one(sheet)
            if result:
                # 计算费用率
                calculate_ratios(result)
                return result
    
    if not found:
        for sheet_name in xls.sheet_names:
            sheet = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            result = process_case_two(sheet)
            if result:
                # 计算费用率
                calculate_ratios(result)
                return result


def main():
    # 指定 Excel 文件夹路径
    folder_path = r'C:\Users\P3516\Desktop\ai coding\LLM\tables'
    # 遍历文件夹中的所有文件
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing file: {file_path}")
            result = process_excel(file_path)
            if result:
                print(result)


if __name__ == "__main__":
    main()

