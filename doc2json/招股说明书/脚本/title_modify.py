import re
def title_modify(title):
    """调整标题，用于re正则匹配

    Args:
        title (str): 标题

    Returns:
        str : 调整后的标题
    """
    temp = list(title)
    for ind, char in enumerate(temp):
        result = re.sub(r"[\s\n]", "", char) # 清除所有标题中的空格和回车
        result = re.sub(r"[的与之和及]", r".?", result) # 常见的标题错误
        result = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', r".?", result) # 所有标点符号替换，防止标点符号出现问题
        temp[ind] = result
    temp = [i for i in temp if i != ""]
    result = "\s*?\n*?".join(temp) # 在字符中插入空格和回车的匹配，解决文本内容可能存在的缩进换行问题。
    return result