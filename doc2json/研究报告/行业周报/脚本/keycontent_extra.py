import re
def get_keycontent(content,key_list):
    """检查content内容开头是否是粗体内容，是则被视为关键内容。

    Args:
        content ( str): 段落内容
        key_list (list): 粗体内容列表

    Returns:
        str: 检测出的粗体内容，如果没有则返回""
    """
    for i in key_list:
        pattern = r"^\s*{}(.*?)".format(i)
        if re.search(pattern,content,re.DOTALL):
            return i
    return ""