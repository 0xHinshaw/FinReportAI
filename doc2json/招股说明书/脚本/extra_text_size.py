import fitz
from pathlib import Path


def extract_Content_size(doc):
    """提取正文的字体大小，小于正文字体的被视为页码，页眉，注释等"""
    feature_num = {}
    headers_size = []
    text_rate = {}
    page_num = 0
    for index,page in enumerate(doc):
        page_num +=1
        if index ==0 :
            continue
        page_rate = {}
        blocks = page.get_text("dict", flags=11)["blocks"]
        for b in blocks:  # iterate through the text blocks
            for l in b["lines"]:  # iterate through the text lines
                for s in l["spans"]:
                    if s["text"] != " ":  # iterate through the text spans
                        font = s["font"]
                        size = s["size"]
                        feature = (size,font)
                        if feature in feature_num.keys():
                            feature_num[feature]+= len(s["text"])
                        else:
                            feature_num[feature] = 1
                        page_rate[feature] = 1
        for i in page_rate.keys():
            if i in text_rate.keys():
                text_rate[i] += 1
            else:
                text_rate[i] = 1
    # 使用max函数找到值最大的项
    most_key = max(feature_num, key=feature_num.get)
    for i in text_rate.keys():
        if i < most_key:
            if text_rate[i]/page_num >= 0.9 :
                headers_size.append(i)
    # print(f" Header: {headers_size}"+f" Content: {most_key}")
    return headers_size,most_key

# extract_Content_size(doc)
# print()
