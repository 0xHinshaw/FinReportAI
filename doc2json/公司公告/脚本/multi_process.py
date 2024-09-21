import os
from multiprocessing import Pool
from file2json import pdf2json,txt2json
from get_first_titles import first_titles
import logging
import os
from tqdm import tqdm
data_list = os.listdir("/data/chengsiyu/result/txt/公司公告/finaltxt")
print(len(data_list))
json_list = os.listdir("/home/luzhenye/PythonProject/脚本/json")
print(len(json_list))
json_list = [os.path.basename(i).split(".json")[0]+".txt" for i in json_list]
fix_list = [i for i in data_list if i not in json_list]
# 配置日志记录器
logging.basicConfig(filename='my_program.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_txt_file(txt_path):
    file_name = os.path.splitext(os.path.basename(txt_path))[0]
    # logging.info(file_name)
    with open(txt_path, "r", encoding="utf-8") as f:
        text_except_tables = f.read()
    title_list = first_titles(text_except_tables)
    output_dir = os.path.dirname(txt_path)
    txt2json(file_name, text_except_tables, title_list, output_dir=output_dir)

def process_txt_files(txt_folder):
    """多进程处理文件夹中的所有txt文件"""
    txt_paths = [os.path.join(txt_folder, f) for f in os.listdir(txt_folder) if f.endswith('.txt')]
    test_paths = txt_paths[500:]

    # 使用多进程池处理所有PDF文件
    with Pool() as pool:
        pool.map(process_txt_file, test_paths)
    # 打印结果

def process_pdf_files(pdf_folder):
    """多进程处理文件夹中的所有PDF文件"""
    pdf_paths = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.endswith('.pdf')]

    # 使用多进程池处理所有PDF文件
    with Pool() as pool:
        pool.map(pdf2json, pdf_paths)
    # 打印结果

# 测试
# if __name__ == "__main__":
#     txt_folder = r'/home/luzhenye/PythonProject/脚本/txt'
#     # process_txt_files(txt_folder)
#     txt_list = os.listdir(txt_folder)
#     pbar = tqdm(txt_list)
#     for i in pbar:
#         pbar.set_description('Processing '+i)
#         process_txt_file(os.path.join(txt_folder, i))