import re
from PythonProject.招股说明书.zgsms_node import zgsms_node
from fuzzy_matching import fuzzy_match
from get_title_mode import get_content_title_mode, get_title_rank
from title_modify import title_modify
import logging
# 配置日志记录器
logging.basicConfig(filename='my_program.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_next_node(node, last=False):
    """获取节点的下一个节点，用于正则表达式匹配两个节点之间的内容。

    Args:
        node (zgsms_node): 当前节点
        last (bool): 是否是最后一个节点. Defaults to False.

    Returns:
        _type_: 下一个节点，无则返回None
    """
    if not last:
        if node.child_node != []:
            return node.child_node[0]
    if node.parent_node:
        node_index = node.parent_node.child_node.index(node)
        if node_index != len(node.parent_node.child_node) - 1:
            return node.parent_node.child_node[node_index + 1]
        else:
            return get_next_node(node.parent_node, True)
    return None


def get_node_f_name(node):
    """获取本文件的名字，用于log记录。

    Args:
        node (zgsms_node): 当前节点

    Returns:
        str : 当前节点对应的文件名字
    """
    if node.parent_node is None:
        return node.title
    else:
        result = get_node_f_name(node.parent_node)
    return result

def get_node_content(node, temp_node, toc_mode, log=True):
    """获取节点之间的内容

    Args:
        node (gsgg_node): 当前节点
        temp_node (zgsms_node): 临时的文件内容容器，用于让节点在匹配后删除已经匹配完的内容，不直接使用str是因为str是不可变变量。
        toc_mode (str): 制表符
        log (bool, optional): 是否记录log。 Defaults to True.
    """
    if node is None :
        return
    text = temp_node.title # 将容器中的文本内容提取。
    next_node = get_next_node(node) # 获取下一个节点
    if node.parent_node is None: # 判断是否是文件节点
        preface_node = zgsms_node(title="preface") # 插入preface节点存储文件第一个标题之前的内容。
        if next_node: # 如果存在下一个节点
            pattern = r"^(.*?)(\s*{}\s*\n)(?!.{})".format(title_modify(next_node.title),
                                                                            '{0,3}[' + toc_mode + ']{2}') 
            match = re.search(pattern, text, re.DOTALL) # 匹配文件开头到第一个标题之间的内容
            if match:
                content = match.group(1)
                preface_node.content = "\n" + content
                temp_node.title = "\n" + text[match.end() - len(match.group(2)) - 2:] # 删除已经匹配的内容
                node.child_node.insert(0,preface_node) 
                preface_node.parent_node = node 
            else:
                if log:
                    print("目录前的内容匹配失败,或内容为空：{}".format(node.title))
    else:
        if next_node: 
            pattern = r"(\s*{}\s*\n)(?!.{})(.*?)(\s*{}\s*\n)(?!.{})".format(title_modify(node.title),
                                                                                  '{0,3}[' + toc_mode + ']{2}',
                                                                                  title_modify(next_node.title),
                                                                                  '{0,3}[' + toc_mode + ']{2}')
            match = re.search(pattern, text, re.DOTALL) # 匹配两个节点之间的内容，并且标题附近不能存在制表符，防止匹配到目录
            if match:
                content = match.group(2)
                node.content = "\n"+content
                temp_node.title = "\n"+text[match.end() - len(match.group(3))-2:] # 删除已经匹配的内容
            else:
                pattern = r"(\s*{})(?:\s*?\n*?)(\s?\n?{})".format(title_modify(node.title), title_modify(next_node.title))
                match = re.search(pattern, text, re.DOTALL) # 未匹配到内容时检查是否是标题之间无内容
                if not match and node.parent_node is not None:
                    if node.title != "preface":
                        match = fuzzy_match(node.title,next_node.title,toc_mode,text) # 标题匹配失败，可能是目录标题和内容标题不一致，进行模糊匹配。
                        if match:
                            # print("模糊匹配成功："+str(node.title))
                            content = match.group(2)
                            node.content = "\n"+content
                            temp_node.title = "\n"+text[match.end() - len(match.group(2))-2:] # 删除已经匹配的内容
                        else:
                            if log:
                                logging.info("大目录内容匹配失败,或内容为空：{}".format(get_node_f_name(node))) # 模糊匹配失败
        else:
            pattern = r"(\s*{}\s*\n)(?!.{})(.*)".format(title_modify(node.title), toc_mode)
            match = re.search(pattern, text, re.DOTALL) #最后一个节点则从该标题匹配至文件结束。
            if match:
                content = match.group(2)
                node.content = "\n"+content
                temp_node.title = "\n"+text[match.end() - 1:] # 删除已经匹配的内容
            else:
                logging.info("目录内容未匹配成功：或该节点无内容{}".format(get_node_f_name(node)))
    if node.child_node != []:
        for i in node.child_node:
            get_node_content(i, temp_node, toc_mode) # 存在子节点则对子节点内容进行匹配。


def get_child_node_content(node,temp,node_list):
    """检测到content里还有子标题后，对子标题内容进行匹配

    Args:
        node (zgsms_node): 当前的子标题
        temp (zgsms_node):  临时的文件内容容器，用于让节点在匹配后删除已经匹配完的内容，不直接使用str是因为str是不可变变量。
        node_list (_type_): 识别出的子标题列表
    """
    node_index = node_list.index(node) # 在子标题列表中的索引
    if node_index != len(node_list)-1 : # 判断是否是最后一个子标题
        next_node = node_list[node_index+1] 
        pattern = r"({})(.+?)({})".format(title_modify(node.title),title_modify(next_node.title))
        match = re.search(pattern, temp.title, re.DOTALL) # 匹配两个子标题间的内容
        if match:
            node.content = match.group(2)
            temp.title = "\n" + temp.title[match.end() - len(match.group(3)) - 2:] # 删除已匹配的内容
        else:
            pattern = r"(\s?\n?{})(?:\s?\n?)({})".format(title_modify(node.title),title_modify(next_node.title))
            match = re.search(pattern, temp.title, re.DOTALL)
            if not match and node.parent_node is not None:
                print("子标题内容匹配失败：{}".format(node.title)) # 记录匹配失败
                pass
    else:
        match = re.search( r"({})(.*)".format(title_modify(node.title)),temp.title,re.DOTALL) # 最后一个子标题则匹配剩余的所有内容
        if match:
            node.content = match.group(2)
            temp.title = "\n" + temp.title[match.end() - len(match.group(2)) - 2:]
        else:
            print("子标题提取存在问题")


def modify_self_content(node):
    """匹配子标题后调整自身的内容

    Args:
        node (zgsms_node): 当前的节点
    """
    next_node = get_next_node(node)
    if next_node:
        pattern = r"({}\s?\n?)(.*?)(?:\n?\s?{})".format(title_modify(node.title), title_modify(next_node.title))
        match = re.search(pattern, node.title + node.content, re.DOTALL) # 匹配当前节点到下一个节点之间的内容
        if match:
            node.content = match.group(2) # 更新内容
        else:
            pattern = r"(\s?\n?{})(?:\s*?\n*?)({})".format(title_modify(node.title), title_modify(next_node.title))
            match = re.search(pattern, node.title + node.content, re.DOTALL)
            if not match and node.parent_node is not None:
                logging.info("modify_self_content匹配失败：{}".format(node.title)) # 记录问题
                pass
    else:
        print("程序有问题") # 检测到子标题但查不到下一个节点则说明程序出错

def content_detect(node,content):
    """检查content中是否还含有子标题

    Args:
        node (zgsms_node): 被检测的节点
        content (str): 检测内容
    """
    # 只做了结构上的检查，未对内容进行更改
    match = re.search(r"本?册?\s*目\s*录\s*\n",content)
    if match :
        content = content[:match.start()] # 如果内容中存在目录则删除
    title_list = [] # 子标题列表
    end_list = [] # 子标题结束位置
    rank_list = [] # 子标题的排序
    mode_list = [] # 子标题的格式
    mode, title, endpos = get_content_title_mode(content, only_mode=False)
    end_list.append(endpos)
    while mode is not None: # 循环匹配子标题直到不存在子标题。
        title_rank = get_title_rank(title)
        rank_list.append(title_rank)
        title_list.append(title)
        mode_list.append(mode)
        mode, title, endpos = get_content_title_mode(content[end_list[-1]:], only_mode=False)
        end_list.append(end_list[-1] + endpos)
    end_list[-1] = (len(content))
    for index, title in enumerate(title_list):# 遍历子标题列表，补全子标题
        if index != len(title_list) - 1:
            match = re.search(r"^\s?\n?(.+?)(?:[。：；\n]|{})".format(title_modify(title_list[index + 1])),
                              str(content[end_list[index]:end_list[index + 1]]),re.DOTALL) # 子标题的正则匹配，及截断逻辑
            if match:
                title_list[index] = title + match.group(1) 
            else:
                print("小标题匹配失败：" + title)
        else:
            match = re.search(r"^\s?\n?(.+?)(?:[。：；\n])",
                              str(content[end_list[index]:end_list[index + 1]]),re.DOTALL)
            if match:
                title_list[index] = title + match.group(1)
            else:
                match = re.search(r"^\s?\n?(.+?)(?:{})".format(content[-1]),
                                  str(content[end_list[index]:end_list[index + 1]]), re.DOTALL)
                if match:
                    title_list[index] = title + match.group(1)
                else:
                    print("小标题匹配失败：" + title)
    node_list = []
    temp_node = zgsms_node(title=str(node.title)) # 临时节点
    cache = [] # 缓存列表
    if title_list != []:
        for index, i in enumerate(title_list):
            node_list.append(zgsms_node(title=i))
            mode = mode_list[index]
            rank = rank_list[index]
            if cache == []:
                cache.append({"mode": mode, "rank": rank, "index": index})
                temp_node.link(node_list[index])
            else:
                latest_ache = cache[-1] # 上一个缓存的标题
                if rank == 1 : # 标题是从一开始则默认新建一个分级
                    cache.append({"mode": mode, "rank": rank, "index": index})
                    node_list[latest_ache["index"]].link(node_list[index])
                else:
                    status = True
                    for ache in cache[::-1] :
                        ache_index = cache.index(ache)
                        if mode == ache["mode"] and rank > ache["rank"] : # 当rank大于格式的上一个标题时才添加，避免添加错误
                            cache[ache_index] = {"mode": mode_list[index], "rank": rank_list[index], "index": index}
                            cache = cache[:ache_index+1]
                            status = False
                            if ache_index != 0 :
                                node_list[cache[ache_index-1]["index"]].link(node_list[index])
                            else:
                                temp_node.link(node_list[index])
                            break
                    if status:
                        cache.append({"mode": mode, "rank": rank, "index": index})
                        node_list[latest_ache["index"]].link(node_list[index])
    if node_list!=[]: # 新增的node数量不为0时
        # print("总共："+str(len(node_list)))
        temp1 = zgsms_node(title=content) # 临时节点，用于隔开当前检测节点，使得next_node函数正常运作
        for i in node_list:
            get_child_node_content(i,temp1,node_list) # 新增子节点的内容匹配填充
        for i in temp_node.child_node:
            node.link(i) # 连接新增节点
        modify_self_content(node) # 调整当前节点内容。



