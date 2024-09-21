import re
import os
import json
import DataErrorDetection as ded

def process(file_path):
    """提取文件中的目录，根据标题级别构造初步的文章结构

    Args:
        file_path (str): 文件路径

    Returns:
        list : 目录标题组成的list，文章无目录则返回None
    """

    # 读取 txt 文件
    with open(file_path, 'r',encoding="utf-8") as file:
        text = file.read()

    # 使用正则表达式提取文本
    pattern = "(?:\n)(目\s+?录.*?)(插图目录.*?\n)(?=\n)"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        content_list = match.group(1).split("\n")
        content_list = [i.split("\t")[0] for i in content_list]
        content_list = [item for item in content_list if item.strip()]
        # image_list = match.group(2).split("\n")
        # image_list = [i.split("\t")[0] for i in image_list]
        return content_list[1:]
    else:
        print("文件匹配错误，没有目录")