import re
from get_title_mode import get_title_mode
from PythonProject.招股说明书.zgsms_node import zgsms_node
import logging
# 配置日志记录器
logging.basicConfig(filename='my_program.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_f_node(text:str, file_name:str, toc_mode:str):
    """识别目录以生成文件节点

    Args:
        text (str): 文件内容
        file_name (str): 文件名字
        toc_mode (str): 目录制表符

    Returns:
        zgsms_node: 只有title属性的文件节点
    """
    # 使用正则表达式提取目录
    pattern = r"(\n\s*本?册?目\s*?录\s*?\n)(.*[{}]{}\s*\n*[1234567890]{})".format(toc_mode,"{2,}","{1,4}")
    match = re.search(pattern, text, re.DOTALL)
    if match:
        content_list = match.group(2).split("\n")
        content_list = [i for i in content_list if i != ""]
        f_node = list2node(file_name,content_list,toc_mode)
        return f_node
    else:
        logging.info("文件没有目录")
        return None
    
def list2node(file_name,toc_list,toc_mode,mode_func = get_title_mode):
    """用于将目录内容转化成节点

    Args:
        file_name (str): 文件名字
        toc_list (list): 按行读取的目录列表
        toc_mode (str): 制表符
        mode_func (func): 识别标题格式的函数，可自行替换使得某几个类型的标题被识别同一个类型，从而划分成同级标题. Defaults to get_title_mode.

    Returns:
        zgsms_node : 文件节点
    """
    # 根据目录生成需要的
    f_node = zgsms_node(title=f"{file_name}") # 生成文件节点
    node_list = [f_node]
    parent_node_index = {} # 用于缓存不同级别的最新一个标题
    toc_level = [] # 缓存标题级别
    level = 0 # 初始化最新标题级别
    text = ""
    status = False
    for index,i in enumerate(toc_list):
        mode = mode_func(i) # 获取当前的标题格式类型
        if mode is not None:
            if mode in toc_level:
                level = toc_level.index(mode)
            else:
                toc_level.append(mode) # 缓存
                level = toc_level.index(mode)
            status = True # 用于判定是否开始拼接标题，由于缩进问题，可能导致同一个标题被拆分在不同的行。
        if re.search(f"[{toc_mode}]{'{3,}'}\s*\n?$|[1234567890XVI]+\s?\n?$",i): # 是否以制表符或数字结尾。
            if mode is not None: # 和上一个if结合判断是否是完整的标题
                node_list.append(zgsms_node(title=re.split(r"[{}]{}|[1234567890XVI]+\s?\n?$".format(toc_mode,'{3,}'),i)[0]))
                if level != 0: # 判断是否存在父节点
                    node_list[parent_node_index[level-1]].link(node_list[-1]) # 让父节点连接到此标题
                    parent_node_index[level] = len(node_list)-1 # 更新该级别标题
                else:
                    f_node.link(node_list[-1]) # 让文件节点连接到此标题
                    parent_node_index[level] = len(node_list)-1  # 更新该级别标题
                status = False 
                continue
            if status: # 非完整的标题，如果status为true则说明需要拼接到上一行。
                text += re.split(r"[{}]".format(toc_mode),i)[0] # 拼接
                node_list.append(zgsms_node(title=re.split(r"[{}]{}|[1234567890XVI]+\s?\n?$".format(toc_mode,'{3,}'),text)[0]))
                if level != 0:
                    node_list[parent_node_index[level-1]].link(node_list[-1]) # 让父节点连接到此标题
                    parent_node_index[level] = len(node_list)-1  # 更新该级别标题
                else:
                    f_node.link(node_list[-1]) # 让文件节点连接到此标题
                    parent_node_index[level] = len(node_list)-1  # 更新该级别标题
                text = ""
                status = False
                continue
        if status:  # 不以制表符或数字结尾，说明标题还未拼接完成
            text+="\n"+i # 拼接标题
    return f_node