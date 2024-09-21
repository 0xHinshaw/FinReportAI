import re


def process(text, symbols = ['@', '#', '$', "\\", "*" ,"（可公开）","\t","\n"]):
    """
    删掉文本中的"\","*"等转码时产生的错误
    text:输入文本
    error:错误的匹配项
    :return:清洗后的text
    """
    symbol_list = symbols
    for symbol in symbol_list:
        text = re.sub(re.escape(symbol), "", text)
    return text

