import docx2txt
import regex as re
import json
import DataErrorDetection as ded
import os
import ReadContent as RC
from ContentNode import CN
from get_key_list import get_key_list
from keycontent_extra import get_keycontent

# 获取用户输入的文件路径
file_path = input("请输入Word文档的路径(格式为：xx\\xx\\xx 即可)：")

# 将用户输入的文件路径转换为Python可以处理的格式

print("file_path =" + file_path)

# 目录与正文的标题可能存在格式上的问题，比如多一个空格或者少一个：
def title_sub(title):
    """替换标题中的空格为\s*，用于之后的正则表达式匹配

    Args:
        title (str): 标题

    Returns:
        str : 调整后的标题
    """
    result = re.sub(" ",r"\\s*",title)
    return result

def get_first_match(patterns,text):
    """进行多个pattern的匹配，返回最先匹配上的pattern

    Args:
        patterns (list): 由pattern组成的列表
        text (str): 用于匹配的文本内容

    Returns:
        str : 最先匹配上的pattern
    """
    # 初始化变量
    first_match = None
    min_start = float('inf')

    # 遍历模式列表，找到最先匹配成功的模式
    for pattern in patterns:
        match = re.search(pattern, text)
        if match and match.start() < min_start:
            first_match = pattern
            min_start = match.start()
    return first_match

def node2json(node_list, text,key_list):
    """根据node结构，匹配每个节点所属的文本内容，并提取关键句，生成json

    Args:
        node_list (list): node组成的列表
        text (str): 用于匹配的文本内容
        key_list (list): 可能的关键句列表，由文章粗体字构成。

    Returns:
        list: 返回一个list，包含node节点转换成的字典。
    """
    index = 0
    for index, sub_node in enumerate(node_list):
        # 使用正则表达式提取文本
        if index != len(node_list)-1:
            pattern = "({})(?:\s*[\n。：])(\n?.*?)((\n.*?)*)({}.*?)(?:\n)".format(title_sub(sub_node.title), title_sub(node_list[index + 1].title))
            match = re.search(pattern, text)
            # print("{}:".format(sub_node.title)+str(len(match.groups())))
            if match:
                sub_node.content = match.group(2)
                if re.search(r"(\s*\*|\s*^（[0-9]）)",match.group(2)):# 查看周报内是否存在子标题
                    if get_first_match([r"\*",r"（[0-9]）"],match.group(2)) == r"（[0-9]）" :
                        pattern_sub = r"(（[0-9]）.*?)(?:\n)"
                        sub_match = re.findall(pattern_sub,match.group(2)+match.group(3))
                    else:
                        pattern_sub = r"\*.*?(?=\n)"
                        sub_match = re.findall(pattern_sub, match.group(2)+match.group(3))
                    sub_node_list = []
                    for sub_index,sub_title in enumerate(sub_match):
                        sub_node_list.append(CN(sub_title,key_list))
                        sub_node.link(sub_node_list[sub_index])
                        node_list.insert(index+sub_index+1,sub_node_list[sub_index])
                    sub_node.content = ""
            else:
                print("文件内容{}匹配存在问题，需要检查".format(title_sub(sub_node.title)))

        else: # 最后一个node匹配到以回车结尾。
            pattern = "({})(?:\s*[\n。：])(\n?.*?)((\n.*?)*)(?:\n)".format(title_sub(sub_node.title))
            match = re.search(pattern, text)
            # print("{}:".format(sub_node.title)+str(len(match.groups())))
            if match :
                sub_node.content = match.group(2)
                if re.search(r"(\*|（[0-9]）)", match.group(2), re.DOTALL):
                    if get_first_match([r"\*",r"（[0-9]）"],match.group(2)) == r"（[0-9]）" :
                        pattern_sub = r"(（[0-9]）.*?)(?:\n)"
                        sub_match = re.findall(pattern_sub, match.group(2) + match.group(3))
                    else:
                        pattern_sub = r"\*.*?(?=\n)"
                        sub_match = re.findall(pattern_sub, match.group(2) + match.group(3))
                    sub_node_list = []
                    for sub_index, sub_title in enumerate(sub_match):
                        sub_node_list.append(CN(sub_title,key_list))
                        sub_node.link(sub_node_list[sub_index])
                        node_list.insert(index + sub_index + 1, sub_node_list[sub_index])
                    sub_node.content = ""
            else:
                print("文件内容{}匹配存在问题，需要检查".format(title_sub(sub_node.title)))

    data = [i.to_json() for i in node_list if i.father_node is None]
    return data


def txt2json(file_path,key_list):
    """txt文件，分析结构并转化为json

    Args:
        file_path (str): 文件路径
        key_list (list): 粗体词或句子组成的列表，作为可能的关键句和关键词用于之后的匹配。
    """
    # 使用 os 库获取文件名
    file_name = os.path.basename(file_path)

    # 使用正则表达式提取文件名中的标题
    pattern_title = r"(.*?)\.txt"
    match_title = re.search(pattern_title, file_name)

    if match_title:
        title = match_title.group(1)
    else:
        print("未找到指定的文件")

    # 读取 txt 文件
    with open(file_path, 'r', encoding="utf-8") as file:
        text = file.read()

    # 读取文本内的标题
    content_list = RC.process(file_path)
    node_list = []
    old_index = [0] # 缓存上一个节点的索引

    for index, sub_title in enumerate(content_list):
        node_list.append(CN(sub_title,key_list))
        if node_list[index].n > node_list[old_index[-1]].n: # 标题与上一个标题级别对比
            node_list[old_index[-1]].link(node_list[index]) # 连接子节点
            old_index.append(index) # 更新缓存的节点
        else:
            while len(old_index) != 0:
                if node_list[index].n <= node_list[old_index[-1]].n: # 当前标题级别高于缓存中的node标题级别时
                    old_index.pop() # 删除缓存中最后一个dode，直到当前标题级别是缓存中最低的一个，或者缓存已被删空。
                else:
                    break
            if len(old_index) == 0:
                old_index.append(index) # 如果缓存中没有node，则添加当前的node进缓存。
            else:
                node_list[old_index[-1]].link(node_list[index]) 
                old_index.append(index)
    node_list.insert(0,CN("投资要点：",key_list))
    data = {
        "title": ded.process(title),
        "content": "",
        "keycontent": "",
        "subtitle": node2json(node_list, text,key_list)
    }

    # 将字典转换为JSON格式并保存到文件中
    json_file_path = os.path.join(os.path.dirname(file_path), title + '.json')
    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("转换成功")
    except Exception as e:
        print("转换失败")


# 使用os.listdir()函数列出文件夹中的内容
def dir2json(folder_path):
    """深度优先遍历文件夹，将所有txt文件都转化成json。

    Args:
        folder_path (str): 文件夹路径
    """
    # 生成txt文件
    if os.path.isdir(folder_path):
        docx2txt.process(folder_path)
    else:
        print("未找到指定文件夹")
        return

    # 遍历文件夹中的内容
    contents = os.listdir(folder_path)

    for item in contents:
        # 构建完整路径
        item_path = os.path.join(folder_path, item)
        # 检查当前项是文件还是文件夹
        if os.path.isdir(item_path):
            print("文件夹:", item)
            dir2json(item_path)
        elif os.path.splitext(item)[1] == ".docx":  # 筛选文件类型,注意”.“
            print("docx文件:", item)
            key_list = get_key_list(item_path)
            txt_path = os.path.join(folder_path, os.path.splitext(item)[0] + ".txt")
            txt2json(txt_path,key_list)

# dir2json(file_path)

