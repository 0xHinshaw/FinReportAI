import requests
import json
import ast
import os
import re
import docx2txt
from tqdm import tqdm
import logging
from logging import Logger
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor

# logger = logging.getLogger('my_logger')
# logger.setLevel(logging.DEBUG)
# log_file_path=f'/home/luzhenye/PythonProject/gpt/logs/原文-问题模板生成{datetime.now().strftime("%Y-%m-%d %H:%M")}.log'
# file_handler = logging.FileHandler(log_file_path)
# # 创建并设置日志格式
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)
# # 将文件处理器添加到 Logger
# logger.addHandler(file_handler)

def get_response_gpt4(content):
    """ 获取gpt-4模型的回复

    Args:
        content (_type_): 给gpt-4的问题

    Returns:
        _type_: 模型的回答
    """
    url = "https://gateway.ai.cloudflare.com/v1/05c43e30f91a115d8153715954fd70ee/lingyue-ai/openai/chat/completions"
    # url = "https://api.deepseek.com/chat/completions"
    # url = "https://api.kwwai.top/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        # "Authorization": "Bearer sk-246e62fbd9cc4d12bd1cd65a5a532c06",
        # "Authorization": "Bearer sk-QeiIJwcjqnhybuSeBbC0F27eEc0b42529a4410194b362bBb",
        "Content-Type": "application/json"
    }
    data = {
        # "model": "gpt-4-0613",
        # "model": "gpt-4",
        # "model": "deepseek-chat",
        "model": "gpt-4o",
        "messages": [
            {
            "role": "user",
            "content": f"{content}"
            }
        ],
        "stream" : False
        }
   
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()  # 确保HTTP请求成功
    json_string = response.text
    data_json = json.loads(json_string) # 直接尝试解析JSON
    return data_json["choices"][0]["message"]["content"]
   


def merge_short_strings(string_list):
    result = []
    temp = ""
    for index in range(len(string_list)):
        if len(temp)<300:
            temp += string_list[index] + "\n"
        else:
            result.append(temp)
            temp = string_list[index]
    if len(temp)<100:
        result[-1]+=temp
    else:
        result.append(temp)
    
    return result

def process_json(file_name):
    input_dir = "/data/shenyuge/data/industry"
    questions_list = """
    [   
        行业整体行情如何？
        行业的涨幅在所有行业中的排名如何？
        与同期主要指数的表现如何？
        哪些细分板块的表现优于主要指数？
        哪个细分板块的跌幅最小？
        不同细分板块的跌幅分布是怎样的？
        哪个细分板块的跌幅最大？
        近期有哪些重要的政策变化？
        这些政策变化如何影响市场预期？
        有哪些重要的市场指标值得关注？
        在长期的经济复苏进程中，需要关注哪些因素？
        哪些公司的业绩表现出较强的确定性？
        有哪些边际改善的机会？
        那些板块的业绩表现具有分化态势？
        有哪些风险需要注意？
    ]
    """
    try:
        file_path = os.path.join(input_dir,file_name) # 选中其中一个文件
        save_json_path = os.path.join("/data/shenyuge/data/industry/p-q-template",os.path.basename(file_path))
        # extract text
        if os.path.exists(save_json_path):
            return
        with open(file_path,"r",encoding="utf-8") as file:
            data_json = json.load(file)
        sub_text_list = [i for i in data_json['original_text'].split("\n") if i != ""]
        sub_template_list = [i for i in data_json['processed'].split("\n") if i != ""]
        if len(sub_template_list) != len(sub_text_list):
            return file_name
        final_result = []
        max_try = 5
        for text_index,text in tqdm(enumerate(sub_text_list)):
            try_num = 0
            while try_num < max_try:
                try :
                    questions_list = questions_list.replace('{', '<').replace('}', '>')
                    post_content ="原文：\n"+ text + "\n 模板：\n"+sub_template_list[text_index]+ f"\n问题列表：{questions_list}"+""" \n 上述是原文，模板和问题列表，原文和模板中的Q加数字代表的是某一季度，分析上面的的问题列表，哪些问题的能够在模板中找到答案，如果模板中的句子能够回答问题，请按照{ "questions":[[question, template_part], [question, template_part]]}的格式返回，格式中question代表能回答的具体问题，template_part则是上述模板中的截取出来可以回答问题的句子模板。
                    注意：
                    1、原文内容回答不了的问题不要加进去，如果该段落没有回答任何问题，则返回{"questions":[]}。
                    2、template_part应该截取到答案句，不要输出整个模板，不要截取的太长。
                    3、每个question对应一个template_part，template_part中的<>不要替换为具体数据。
                    4、不要改变我提供的json格式，
                    5、不要改变问题列表中的问题
                    6、只返回json数据就可以了,不要输出其他内容。以确保你输出的内容我可以直接读取"""
                    result = get_response_gpt4(post_content)
                    result = re.search(r"\{(.*)\}",result,re.DOTALL).group()
                    result = result.replace('\n', '')
                    result = json.loads(result)
                    if result is not None:
                        break
                except Exception as e :
                    try_num += 1
                    if try_num == 5:
                        print(f" 段落 {text} 发生错误：{e} ")
                        break
            final_result.append({"paragraph":text,"questions":result["questions"]})
        with open(save_json_path,"w",encoding="utf-8") as file :
            json.dump(final_result, file,ensure_ascii=False, indent=4)
        print(f"{file_name} 处理完成")
    except Exception as e :
        print(f"{file_name} 文件遇到{e}问题")
        return

if __name__ == "__main__":
    result = process_json('（可公开）食品饮料行业双周报（20240520-20240602）：政策优化，关注预期改善.json')