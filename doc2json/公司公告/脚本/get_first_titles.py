import re


class TitleRegex:
    # 定义第一级标题的正则表达式
    LEVEL_ONE_REGEX = [
        r"^第[一二三四五六七八九十]+\章",
        r"^第[一二三四五六七八九十]+\节",
        r"^[一二三四五六七八九十]+\、"
    ]

    # 定义其他主要标题的正则表达式
    MAIN_TITLE_REGEX = [
        r"重要内容提示：",
        r".{0,8}声明",
        r"特别提示",
        r"目\s*录",
        r"重要提示"
    ]


def extract_primary_titles(text):
    primary_titles = []

    # 遍历文本的每一行
    for line in text.split('\n'):
        # 匹配每一种标题的正则表达式
        matched_titles = [regex for regex in TitleRegex.LEVEL_ONE_REGEX if re.search(regex, line)]

        # 如果当前行匹配到了标题正则表达式，则添加到列表中
        if matched_titles:
            primary_titles.extend(matched_titles)

    # 根据优先级确定最终的第一级标题
    for regex in TitleRegex.LEVEL_ONE_REGEX:
        for title in primary_titles:
            if title.startswith(regex):
                # 提取匹配到的行作为最终的标题内容
                extracted_title = [line for line in text.split('\n') if re.search(title, line)]
                # 筛选出不包含连续多个句点的标题
                filtered_titles = [title for title in extracted_title if "........" not in title]
                # 筛选出不包含引号或右括号的标题
                filtered_titles = [title for title in filtered_titles if "\"" not in title and "”" not in title]
                return filtered_titles, text  # 返回标题和文本内容

    # 如果没有匹配到任何标题，则返回空列表
    return [], text  # 返回空列表和文本内容


def extract_main_titles(text):
    main_titles = []

    # 提取每种正则表达式的第一个匹配文本
    title_positions = {}  # 记录每个标题的位置
    for regex in TitleRegex.MAIN_TITLE_REGEX:
        matches = re.finditer(regex, text)
        for match in matches:
            title = match.group()
            # 检查匹配的文本是否独立存在
            if text.count(title) == 1:
                # 检查匹配的文本所在行是否只包含这个文本
                line = re.search(r'.*' + re.escape(title) + r'.*', text)
                if line and line.group().strip() == title:
                    main_titles.append(title)
                    title_positions[title] = match.start()

    # 根据标题在文本中的位置进行排序
    main_titles = sorted(main_titles, key=lambda title: title_positions[title])

    return main_titles


def first_titles(text):
    # 提取第一级标题和主要标题
    primary_titles, text = extract_primary_titles(text)
    main_titles = extract_main_titles(text)

    # 合并提取的标题
    titles = main_titles + primary_titles

    return titles