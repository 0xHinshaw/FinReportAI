import fitz
from PythonProject.招股说明书.extra_text_size import extract_Content_size
from pathlib import Path
import re
from PythonProject.招股说明书.zgsms_node import zgsms_node
import os
import json
from get_f_node import get_f_node
from get_node_content import get_node_content, content_detect


def get_toc_mode(page):
    """对某个目录对应的page进行分析，获取目录的制表符。

    Args:
        page (_type_): 目录所在的page

    Returns:
        str : 目录对应的制表符
    """
    text = page.get_text("text", flags=11)
    # 打印匹配结果
    match = re.findall(r'(\S)\1{3,}', text)
    # 如果找到匹配项，则打印匹配的内容
    if match:
        match = ["\\"+i for i in match]
        if len(set(match)) != 1:
            return "".join(set(match))
        else:
            return match[0]
    else:
        print("未找到目录样式匹配项")

# 创建文件夹
def mkdir(path:str):
    """若路径文件夹不存在，则创建文件夹

    Args:
        path (str): 目标路径
    """
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)

def get_feature(s) -> tuple:
    """fitz库可以解析某一个字符的字体大小等信息。

    Args:
        s : fitz读取到的字符

    Returns:
        tuple : 字符对应的（大小，字体）
    """
    return (s["size"],s["font"])

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

def multi_cata2json(pdf_path):
    """对于多目录文件，会根据目录先拆分文件，对每个目录做结构分析和内容匹配，之后再拼接起来最后对各个标题里的内容做调整。

    Args:
        pdf_path (str): 文件路径
    """
    path = Path(pdf_path).expanduser()
    doc = fitz.open(path)
    toc_page = []
    header_size, content_size = extract_Content_size(doc)
    for index, page in enumerate(doc):
        blocks = page.get_text("dict", flags=11)["blocks"]
        for b in blocks: 
            for l in b["lines"]:
                line_text = ""
                for s in l["spans"]:
                    if s["text"] != "":  
                        feature = get_feature(s)
                        if not feature in header_size: # 提取非页脚页眉内容
                            line_text += s["text"]
                if line_text != "":
                    if re.fullmatch(r"目\s*?录\s*?", line_text): # 识别出目录则记录下目录所在的page
                        toc_page.append(index)
                        print("本文内含有目录，在第{}页".format(toc_page))
    toc_page.append(index) # 此时index代表文件的总页数
    all_node = zgsms_node(title=os.path.basename(pdf_path).split(".")[0])
    for index,i in enumerate(toc_page): # 分别读取不同目录对应的文件内容
        if index != len(toc_page)-1:
            text_list = []
            page = doc.load_page(i)
            toc_mode = get_toc_mode(page)
            for p in range(i,toc_page[index+1]):
                page = doc.load_page(p)
                blocks = page.get_text("dict", flags=11)["blocks"]
                for b in blocks:  
                    for l in b["lines"]:  
                        line_text = ""
                        for s in l["spans"]:
                            if s["text"] != "": 
                                feature = get_feature(s)
                                if not feature in header_size: # 提取非页脚页眉内容
                                    line_text += s["text"]
                        if line_text != "":
                            text_list.append(line_text)
            text = "\n".join(text_list)
            f_node = get_f_node(text, "目录{}".format(index + 1), toc_mode) # 生成文件节点框架
            temp_node = zgsms_node(title=text) # 只是为了让text成为可变变量，并无实际含义
            get_node_content(f_node,temp_node,toc_mode)
            all_node.link(f_node)
    f_node_modify(all_node)
    json_file_path = os.path.join(
        os.path.dirname(pdf_path) + "\\json\\" + os.path.basename(pdf_path).split(".")[0] + '.json')
    try:
        mkdir(os.path.join(os.path.dirname(pdf_path) + "\\json\\"))
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(all_node.to_json(), f, ensure_ascii=False, indent=4)
        print("转换成功")
    except Exception as e:
        print("转换失败")
    print("结束")




