import pandas as pd
import numpy as np

def is_number(value):
    '''
    检查输入值是否为数字。

    参数:
    - value: 待检查的值。

    返回:
    - True: 如果值是数字。
    - False: 如果值不是数字。
    '''
    try:
        float(value)
        return True
    except ValueError:
        return False

def find_gross_margin(file_path):
    '''
    从指定的 Excel 文件中查找并输出毛利率数据。

    参数:
    - file_path: Excel 文件路径。

    输出:
    - 每个具体条目及其对应的毛利率，以文本格式输出。
    '''
    # 加载 Excel 文件
    xls = pd.ExcelFile(file_path)
    
    # 遍历文件中的所有 sheets
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # 遍历每行
        for i, row in df.iterrows():
            gross_margin_column_index = None  # 用于追踪包含毛利率的列索引
            
            # 遍历每列
            for j, cell in enumerate(row):
                cell_str = str(cell)
                
                # 当单元格内容仅为"毛利率（%）"时
                if pd.notna(cell) and cell_str.strip() == '毛利率（%）':
                    gross_margin_column_index = j  # 记录包含毛利率的列索引
                    break  # 找到后立即跳出循环
            
            if gross_margin_column_index is not None:
                # 对于每个包含毛利率的单元格，打印其值
                col_values = df.iloc[:, gross_margin_column_index][1:]  # 获取该列下方所有单元格的值
                for idx, value in col_values.items():
                    if is_number(value):  # 检查是否是数字
                        numeric_value = pd.to_numeric(value, errors='coerce')  # 尝试将文本转换为数字
                        if not np.isnan(numeric_value):  # 检查是否不是NaN
                            row_name = df.iloc[idx, 0]  # 假设行名在第一列
                            print(f"{row_name}: {numeric_value}%")


def gm_main():
    '''
    主函数，用于运行整个脚本。
    '''
    # 指定 Excel 文件路径
    file_path = r'C:\Users\P3516\Desktop\ai coding\LLM\tables\2018-03-28：贵州茅台2017年年度报告.xlsx'
    find_gross_margin(file_path)

# 调用主函数
if __name__ == "__main__":
    gm_main()