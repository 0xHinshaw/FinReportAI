# 导入解析xml的库
import re
import xml.dom.minidom as xdom
import DataErrorDetection as ded
from docx2xml import docx2xml

def get_wp(wt):
    """寻找当前文本所在的<w:p>节点

    Args:
        wt (_type_): 文本节点

    Returns:
        _type_: 所在的<w:p>节点
    """
    wp = wt.parentNode
    while wp.nodeName != "w:p":
        wp = wp.parentNode
    return wp

def get_key_list(docx_file):
    """获取一个粗体字内容组成的list

    Args:
        docx_file (str): docx文件路径

    Returns:
        list : 关键内容组成的list
    """
    # 加载文档
    xml_path = docx2xml(docx_file)
    xp = xdom.parse(xml_path)
    # 获取文档根节点
    root=xp.documentElement
    # 获取body节点们
    bodys = root.getElementsByTagName("w:body")
    # 因为getElements返回多个对象，我们只有一个
    body = bodys[0]
    key_list = []
    # 检索粗体字，作为可能的标题列表，关键词保存
    for i,ele in enumerate(body.childNodes):
        # 找到包含w:t的标签,可能是多个
        wts = ele.getElementsByTagName("w:t")
        if len(wts) != 0:
            b_list = [wts[0]]
            sub_text = ""
            for wt in wts: # 循环
                if len(wt.parentNode.getElementsByTagName("w:b")) !=0 :
                    if get_wp(wt) == get_wp(b_list[0]):
                        sub_text += wt.childNodes[0].data
                    else:
                        match = re.search(r"(^\s*行业周观点：)(.*?。)", sub_text, re.DOTALL)
                        if not match:
                            key_list.append(sub_text)
                        else:
                            key_list.append(match.group(1))
                            key_list.append(match.group(2))
                        b_list = [wt]
                        sub_text = wt.childNodes[0].data
            if sub_text != "" :
                key_list.append(sub_text)

    key_list = sorted(list(set([ded.process(i) for i in key_list if i != ""])),key=len,reverse=True)
    return key_list