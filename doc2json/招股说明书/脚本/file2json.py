import os
import re
from PythonProject.招股说明书.zgsms_node import zgsms_node
import os
import json
import fitz
from get_node_content import get_node_content, content_detect, get_child_node_content, get_next_node,get_node_f_name
from get_f_node import get_f_node
from get_first_titles import first_titles
from pdffinal import process_pdf
import logging

# 配置日志记录器,修改日志路径可在filename中修改。
logging.basicConfig(filename='my_program.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fullwidth_to_halfwidth(s:str) -> str:
    """将字符串中的全角数字转换为半角数字

    Args:
        s (str): 输入的text内容

    Returns:
        str: 统一数字字体后的text
    """
    result = ""
    for char in s:
        code = ord(char)
        if 0xFF10 <= code <= 0xFF19:  # 全角数字的Unicode编码范围
            code -= 0xFEE0  # 转换为半角数字的Unicode编码
        result += chr(code)
    return result


def mkdir(path:str):
    """若路径文件夹不存在，则创建文件夹

    Args:
        path (str): 目标路径
    """
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)

def f_node_modify(node:zgsms_node):
    """递归文件节点进行子标题的检测和构建

    Args:
        node (zgsms_node): 公司公告的内容节点
    """
    if node is None:
        return
    if node.child_node != []: # 当子节点为空时才进行检测。
        for i in node.child_node:
            f_node_modify(i)
    else:
        if re.search(r"^\s*本?册?目\s*录",node.title) is None:
            content_detect(node,str(node.content))

def title_list2f_node(file_name:str,title_list:list):
    """通过给定的标题列表构建最外层的文件

    Args:
        file_name (str): 指定文件名
        title_list (list): 指定标题列表

    Returns:
        f_node (gsgg_node): 输出公司公告文件节点
    """
    f_node = zgsms_node(title = "{}".format(file_name))
    for title in title_list:
        f_node.link(zgsms_node(title=title))
    return f_node

def txt2json(file_name:str,text:str,title_list:list,toc_mode=None, output_dir=None):
    """将txt文件内容解析成json格式。

    Args:
        file_name (_type_): 文件名
        text (_type_): txt中的内容
        title_list (_type_): 一级标题列表
        toc_mode (_type_, optional): 目录的制表符. Defaults to None.
        output_dir (_type_, optional): 输出的文件路径. Defaults to None.
    """
    # logging.info(file_name)
    # 使用传入的 text_except_tables 参数
    text = fullwidth_to_halfwidth(text)
    if text == "" :
        logging.info("文件内容为空："+file_name)
    pattern = r"\n\s*本?册?目\s*?录\s*?\n"
    match = re.search(pattern, text, re.DOTALL) # 检测是否存在目录
    if match:
        toc_start = match.start()
        if toc_mode is None:
            match = re.findall(r'(\S)\1{5,}', text[toc_start:toc_start+100])
            # 检测是否存在制表符
            if match:
                match = ["\\" + i for i in match]
                if len(set(match)) != 1:
                    toc_mode = "".join(set(match))
                else:
                    toc_mode = match[0]
                f_node = get_f_node(text,file_name, toc_mode) # 有目录和制表符，提取目录中的标题结构来生成文件节点
                temp1 = zgsms_node(title=text) 
                get_node_content(f_node,temp1, toc_mode)
            else:
                toc_mode = "@" # 没有制表符则默认为@，不影响后续的使用
                f_node = title_list2f_node(file_name, title_list)
        else:
            # 如果有给定的制表符则按给定的制表符运行
            f_node = title_list2f_node(file_name,title_list)  
    else:
        # 未识别到目录按照给定的标题列表生成文件节点
        toc_mode= "@"
        f_node = title_list2f_node(file_name, title_list)
    if f_node is None:
        # 若文件节点为空则出现问题，文件生成终止，并记录log信息。
        logging.info("f_node 节点为空"+file_name)
        return
    temp1 = zgsms_node(title=text) # temp1只是为了让text成为可变变量，并无实际含义
    get_node_content(f_node,temp1, toc_mode) # 获取标题对应内容
    f_node_modify(f_node) # 检测内容是否含有子标题
    if title_list == []:
        # 整个文件都没有标题，记录信息以供查询
        logging.info("文件无标题：" + file_name)
        f_node = zgsms_node(title=file_name,content=text)
    if output_dir is None:
        output_dir = os.getcwd()  # 如果没有指定输出目录，默认为当前工作目录
    json_file_path = os.path.join(output_dir,file_name+".json")  
    try: # 创建输出目录
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(f_node.to_json(), f, ensure_ascii=False, indent=4)
        logging.info("转换成功:{}".format(get_node_f_name(f_node))) # 转换成功则记录
    except Exception as e:
        logging.info("转换失败:{}".format(get_node_f_name(f_node))) # 转换失败记录


def pdf2json(file_path):
    """pdf公司公告文件处理为json格式

    Args:
        file_path (str): pdf文件路径
    """
    text_except_tables = process_pdf(file_path) # pdf文件内容提取
    file_name = os.path.splitext(os.path.basename(file_path))[0] # 文件名
    title_list = first_titles(text_except_tables) # 文件一级标题
    txt2json(file_name,text_except_tables,title_list)

