import re
from get_title_mode import get_title_mode, get_content_title_mode
from title_modify import title_modify


def fuzzy_modify(title,window = None,index=None):
    """替换标题中部分内容为r".{0,n}"，以实现模糊匹配。

    Args:
        title (str): 传入的标题
        window (int, optional): 替换的窗口大小. Defaults to None.
        index (int, optional): 替换窗口的起始索引. Defaults to None.

    Returns:
        str : 调整后的标题
    """
    temp = list(title)
    for ind,char in enumerate(temp):
        result = re.sub(r"[\s\n]", "", char)
        result = re.sub(r"[的与之和情况及]", r".?", result) # 常错字符
        result = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5\\\*\?\n\.]', r".?", result)
        temp[ind] = result
    if index is not None:
        c = str(window+3)
        temp[index] = ".{}".format("{0,"+c+"}")
        if index+window+1 > len(temp)-1:
            temp[index+1:] = ""
        temp[index+1:index+window+1] = ""
    temp = [i for i in temp if i!=""]
    result = "\s*?\n*?".join(temp)
    return result

def fuzzy_match(title,next_title,toc_mode,text,windows = 2):
    """模糊匹配，解决目录中标题和内容标题不一致的情况，目前只能解决两个连续的标题之中一个存在错误的情况，如缺字多字，符号不对。
    只用于目录标题提取结果，不用于子标题检测结果。

    Args:
        title (str): 当前标题
        next_title (str): 下一个标题
        toc_mode (str): 制表符
        text (str): 用于匹配的文本内容
        windows (int, optional): 窗口大小. Defaults to 2.

    Returns:
        : 返回match
    """
    first_pattern, first_match, first_match_end = get_content_title_mode(text,only_mode=False)
    if first_match is None:
        return None
    t1 = get_title_mode(first_match)
    t1_r = get_title_mode(title)
    temp_t2 = re.sub(" ","",next_title)
    second_match = temp_t2[:8]
    match = re.search(r"(?:\n?\s*{})\s?\n?(.+?)(?:[。：；\n]|{})".format(first_match,title_modify(second_match)),text[:100], re.DOTALL)
    if t1 == t1_r and match:
        temp_t1 = first_match + match.group(1)
        pattern = r"(\s*{})(?!.{})(.*?)(?:{})(?!.{})".format(title_modify(temp_t1),
                                                             '{0,3}[' + toc_mode + ']{2}',
                                                             title_modify(second_match),
                                                             '{0,3}[' + toc_mode + ']{2}')
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match
    for window in range(1,windows+3):
        for index in range(len(next_title) - 1):
            pattern = r"(\s*{})(?!.{})(.*?)(?:{})(?!.{})".format(fuzzy_modify(title),
                                                                 '{0,3}[' + toc_mode + ']{2}',
                                                                 fuzzy_modify(next_title, window, index),
                                                                 '{0,3}[' + toc_mode + ']{2}')
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match
        for index in range(len(title)-1):
            pattern = r"(\s*{})(?!.{})(.*?)(?:{})(?!.{})".format(fuzzy_modify(title,window,index),
                                                                              '{0,3}[' + toc_mode + ']{2}',
                                                                              fuzzy_modify(next_title),
                                                                              '{0,3}[' + toc_mode + ']{2}')
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match





