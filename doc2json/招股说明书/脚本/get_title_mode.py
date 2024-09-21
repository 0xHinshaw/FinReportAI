import re
def  get_title_mode(title):
    """根据标题格式返回一个值，用于对不同格式的标题分级。
    想手动调整标题分级的情况可以调整返回的值。

    Args:
        title (str): 标题

    Returns:
        int : 代表格式的分类
    """
    if re.search(r"^\s*第[一二三四五六七八九十]{1,}章",title):
        return 3
    if re.search(r"^\s*[(（]?[一二三四五六七八九十]{1,}[)）]",title):
        return 1
    if re.search(r"^\s*[一二三四五六七八九十]{1,}\s*[、\.]",title):
        return 2
    if re.search(r"^\s*第[一二三四五六七八九十]{1,}节", title):
        return 3
    if re.search(r"^\s*第[1234567890]{1,}章",title):
        return 4
    if re.search(r"^\s*[(（]?[1234567890]{1,}[)）]",title):
        return 5
    if re.search(r"^\s*[1234567890]{1,}\s*[、\.]",title):
        return 6
    if re.search(r"^\s*第[1234567890]{1,}节", title):
        return 7
    if re.search(r"^\s*发行概况|^\s*发行人声明|^\s*重大事项提示|^\s*目\s*录|^\s*释\s*义|^\s*引\s*言|\s*正\s*文|\s*结\s*尾",title):
        return 3
    return None


def get_content_title_mode(content, only_mode=True):
    """在检测content内容是否包含标题的函数，返回检测出的第一个标题的格式和检测的结果。

    Args:
        content (str): 检测内容
        only_mode (bool, optional): 是否只返回标题格式分类. Defaults to True.

    Returns:
        _type_: 第一个匹配成功的标题的格式分类，第一个匹配成功的标题的内容，第一个匹配成功的标题的结束位置索引。
    """
    first_pattern = None
    first_match = None
    first_match_start = float('inf')
    first_match_end = 0
    patterns = [r"[\n\s:：]+[(（]?[一二三四五六七八九十]{1,}[)）]",
                r"[\n\s:：]+[一二三四五六七八九十]{1,}\s*[、\.]",
                r"[\n\s:：]+[(（][l1234567890]{1,2}[)）]",
                r"[\n\s:：]+[l1234567890]{1,2}\s*[、\.](?![1234567890])",
                r"\n\s*第[一二三四五六七八九十]{1,}章",
                r"\n\s*第[一二三四五六七八九十]{1,}节",
                r"\n\s*第[l1234567890]{1,2}章",
                r"\n\s*第[l1234567890]{1,2}节"
                r"\n\s*项目[l1234567890一二三四五六七八九十]{1,2}\s*[:：]",
                r"\n\s*附送[l1234567890一二三四五六七八九十]{1,2}\s*[:：]"]
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match and match.start() < first_match_start:
            first_match_start = match.start()
            first_match = match.group()
            first_match_end = match.end()
            first_pattern = patterns.index(pattern)
    if only_mode:
        return first_pattern
    return first_pattern, first_match, first_match_end

def get_title_rank(title):
    """将标题序号转化成数字，用于对比标题序号的先后，防止序号出错的情况。

    Args:
        title (str): 标题

    Returns:
        int: 标题序号
    """
    match = re.findall(r"[l1234567890一二三四五六七八九十百千]{1,3}", title)
    if match:
        return chinese_arabic_to_int(match[0])
    else:
        print("标题rank错误，请检查"+title)
        return 0
    pass


def chinese_arabic_to_int(s):
    """中文数字转化成阿拉伯数字

    Args:
        s (str): 中文数字

    Returns:
        _type_: 阿拉伯数字
    """
    # 中文数字与阿拉伯数字的映射
    num_map = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
               '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
               '十': 10, '百': 100, '千': 1000, '万': 10000,
               '亿': 100000000,"l":1}

    # 检查是否为纯阿拉伯数字
    if s.isdigit():
        return int(s)

    # 转换中文数字
    total = 0
    r = 1  # 表示单位：个十百千...
    for i in range(len(s) - 1, -1, -1):
        val = num_map.get(s[i])
        if val >= 10 and i == 0:  # 应对 '十三', '十四' 这类的情况
            if val > r:
                r = val
                total = total + val
            else:
                r = r * val
        elif val >= 10:
            if val > r:
                r = val
            else:
                r = r * val
        else:
            total = total + r * val
    return total