import os, re
import json
from config import Config

config = Config()
# 全局变量，用于跟踪句子编号
global_index = 1

# 定义关键词字典
with open(config.keywords_path, 'r') as f:
    keyword_dict = json.load(f)

def get_sentence_keywords(sentence):
    """
    This Python function extracts keywords from a sentence based on a predefined dictionary of keywords
    and their associated values.
    
    :param sentence: The function `get_sentence_keywords` takes a sentence as input and returns a list
    of keywords present in the sentence based on a predefined `keyword_dict`. The `keyword_dict` is not
    defined in the code snippet provided, so you would need to define it before using the function
    :return: The function `get_sentence_keywords` returns a list of keywords that are found in the input
    sentence, based on the values in the `keyword_dict` dictionary.
    """
    sentence_keywords = set()
    for keyword, values in keyword_dict.items():
        for key, value in values.items():
            for v in value:
                if v in sentence:
                    sentence_keywords.add(v)
    return list(sentence_keywords)

def add_next_content(sentence, sub, threshold=22):
    """
    This Python function `add_next_content` takes a sentence and a dictionary `sub` as input, and
    appends additional content from the `sub` dictionary until the total length of the sentence reaches
    a specified threshold.
    
    :param sentence: The `sentence` parameter is a string that represents the current content that you
    want to add more content to
    :param sub: The `sub` parameter is a dictionary that contains information about a particular subject
    or topic. It may have the following keys:
    :param threshold: The `threshold` parameter in the `add_next_content` function represents the
    maximum length that the `sentence` should have after adding content from the `sub`. If the length of
    the `sentence` is less than the `threshold`, additional content from the `sub` will be added until
    the `, defaults to 22 (optional)
    :return: The function `add_next_content` returns the updated `sentence` after appending additional
    content from the `sub` dictionary until the length of the `sentence` reaches the specified
    `threshold`.
    """
        # sentence = sub['title'] + ':' + sentence
    if len(sentence) < threshold:
        next_contents = sub.get('content', '').split('。')
        i = 1
        while len(sentence) < threshold and i < len(next_contents):
            sentence += next_contents[i]
            i += 1
    return sentence
    

def extract_keycontent(block, folder, title):
    """
    The function `extract_keycontent` recursively extracts key content from a nested block structure and
    returns a list of dictionaries containing relevant information such as sentence index, paper
    category, paper title, date, key content, keywords, and logic chain.
    
    :param block: The `block` parameter in the `extract_keycontent` function seems to represent a block
    of content from a document. It contains information such as the title, subtitle, key content, and
    possibly other details related to the content. The function recursively processes this block and its
    sub-blocks to extract key
    :param folder: Folder is a variable that represents the category or folder where the paper is
    stored. It could be a string indicating the category or folder name
    :param title: The `title` parameter in the `extract_keycontent` function represents the title of a
    paper or document from which key content needs to be extracted
    :return: The function `extract_keycontent` returns a list of dictionaries, where each dictionary
    represents information about a specific sentence extracted from the input block. The information
    includes the sentence index, paper category, paper title, date, key content of the sentence,
    keywords extracted from the sentence, and an empty logic chain.
    """
    global global_index
    # nonlocal global_index
    date = re.findall(r'(\d{8}-\d{8})|(\d{4}-\d{2}-\d{2})', title)
    date = ''.join(date[0]) if date != [] else ""
    if len(block['subtitle']) == 0 and str(block.get('keycontent', '')).strip().lower() in ["nan", '']:
        sentence = block['title']
        sentence = add_next_content(sentence, block)
        sentence = sentence.replace('\n', '')
        res = [{"sentence index": global_index,
                "paper category": folder,
                "paper title": title,
                "date": date,
                "keycontent": sentence,
                "keywords": get_sentence_keywords(sentence),
                "logicchain": []}]
        global_index += 1
        return res
    
    elif len(block['subtitle']) == 0:
        sentence = block['keycontent']
        sentence = add_next_content(sentence, block)
        entence = sentence.replace('\n', '')
        res = [{"sentence index": global_index,
                "paper category": folder,
                "paper title": title,
                "date": date,
                "keycontent": sentence,
                "keywords": get_sentence_keywords(sentence),
                "logicchain": []}]
        global_index += 1
        return res
    
    else:
        all_results = []
        if str(block.get('keycontent', "nan")).strip().lower() not in ['nan', '']:
            sentence = block['keycontent']
            sentence = add_next_content(sentence, block)
            entence = sentence.replace('\n', '')
            all_results.append({"sentence index": global_index,
                    "paper category": folder,
                    "paper title": title,
                    "date": date,
                    "keycontent": sentence,
                    "keywords": get_sentence_keywords(sentence),
                    "logicchain": []})
            global_index += 1
        for sub in block['subtitle']:
            all_results += extract_keycontent(sub, folder, title)
        return all_results


    # for sub in block['subtitle']:
    #     keycontent = sub.get("keycontent", "")
    #     if isinstance(keycontent, float):  # 如果是浮点数，则转换为字符串
    #         keycontent = str(keycontent)
    #     if keycontent and keycontent.strip().lower() != "nan":  # 检查是否为非空字符串且不是 "nan"
    #         # for sentence in keycontent.split("。"):
    #         # sentence = keycontent
    #         sentence = keycontent.strip()  # 去除首尾空白字符
    #         if sentence:  # 检查是否为空
    #             #如果keycontent太短，加上本节title和下面的句子
    #             if len(sentence) < 20 and sub['content'].strip().lower() != "nan":
    #                 sentence = add_next_content(sentence, sub)
    #             sentence_keywords = get_sentence_keywords(sentence)
    #             result = {
    #                 "sentence index": global_index,
    #                 "paper category": folder,
    #                 "paper title": title,
    #                 "date": "",
    #                 "keycontent": sentence,
    #                 "keywords": list(sentence_keywords),  # 将 set 转换为 list
    #                 "logicchain": []
    #             }
    #             all_results.append(result)
    #             global_index += 1
        # result = extract_keycontent(sub, folder, title, all_results)
        # all_results.append(result)
    # return all_results + extract_keycontent(sub, folder, title)

# def extract_deep_keycontent(subtitles, folder, title):
#     global global_index
#     all_results = []
#     for sub in subtitles:
#         keycontent = sub.get("keycontent", "")
#         if isinstance(keycontent, float):  # 如果是浮点数，则转换为字符串
#             keycontent = str(keycontent)
#         if keycontent and keycontent.strip().lower() != "nan":  # 检查是否为非空字符串且不是 "nan"
#             # for sentence in keycontent.split("。"):
#             # sentence = keycontent
#             sentence = keycontent.strip()  # 去除首尾空白字符
#             if sentence:  # 检查是否为空
#                 if len(sentence) < 20 and sub['content'].strip().lower() != "nan":
#                     sentence = sub['title'] + ':' + sentence
#                     next_contents = sub['content'].split('。')
#                     i = 1
#                     while len(sentence) < 22 and i < len(next_contents):
#                         sentence += next_contents[i]
#                         i += 1
#                     print(sentence)
#                 sentence_keywords = set()
#                 for keyword, values in keyword_dict.items():
#                     for key, value in values.items():
#                         for v in value:
#                             if v in sentence:
#                                 sentence_keywords.add(v)
#                 result = {
#                     "sentence index": global_index,
#                     "paper category": folder,
#                     "paper title": title,
#                     "date": "",
#                     "keycontent": sentence,
#                     "keywords": list(sentence_keywords),  # 将 set 转换为 list
#                     "logicchain": []
#                 }
#                 all_results.append(result)
#                 global_index += 1
#         # 递归提取更深层级的 keycontent
#         if "subtitle" in sub:
#             sub_results = extract_deep_keycontent(sub["subtitle"], folder, title)
#             all_results.extend(sub_results)
#     return all_results


def process_json_files(directory, output_path, write_to_file):
    """
    The function `process_json_files` reads JSON files from a directory, extracts key content, and
    optionally writes the results to an output file.
    
    :param directory: The `directory` parameter in the `process_json_files` function is the path to the
    directory where the JSON files are located. Must contain paper category as subdirectory.
    This function will search for JSON files within this directory and its subdirectories to process them
    :param output_path: The `output_path` parameter in the `process_json_files` function is the file
    path where the processed JSON data will be written to if the `write_to_file` parameter is set to
    `True`. This is the location where the function will save the results of processing the JSON files
    :param write_to_file: The `write_to_file` parameter in the `process_json_files` function is a
    boolean flag that determines whether the extracted results should be written to a file. If
    `write_to_file` is set to `True`, the extracted results will be written to the specified
    `output_path` file in JSON
    :return: The function `process_json_files` returns a list of results extracted from JSON files found
    in the specified directory. If the `write_to_file` parameter is set to `True`, the results are also
    written to a JSON file at the specified `output_path`.
    """
    global global_index
    all_results = []
    print(directory)
    for root, dirs, files in os.walk(directory):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            json_folder_path = os.path.join(folder_path, "json")
            if os.path.exists(json_folder_path):
                for json_file in os.listdir(json_folder_path):
                    if json_file.endswith(".json"):
                        file_path = os.path.join(json_folder_path, json_file)
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, dict):
                                data = [data]
                            for item in data:
                                # subtitle = item.get("subtitle", [])
                                result = extract_keycontent(item, folder, item.get("document", item.get('title', '')))
                                all_results.extend(result)
                                # 补充提取更深层级的 keycontent
                                # deep_results = extract_deep_keycontent(subtitle, folder, item.get("document", ""))
                                # all_results.extend(deep_results)
    # for result in all_results:
    #     print(result)
    if write_to_file:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=4)
    return all_results

if __name__ == '__main__':
    process_json_files(r"./doc2json", r"./doc2json/output.json", True)