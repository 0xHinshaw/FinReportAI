import DataErrorDetection as ded
import re
def title_modify(title,key_list):
    """标题的修正

    Args:
        title (str):标题
        key_list (list): 加粗内容组成的list

    Returns:
        str: 修正后的标题
    """
    title = ded.process(title)
    for i in key_list:
        pattern = r"^\s*{}".format(i)
        if re.search(pattern, title, re.DOTALL):
            if re.search(r"[：。]",i[-1]):
                i = i[:-1]
            return i
    else:
        title = re.split(r"[。：]",title)[0]
    return title
