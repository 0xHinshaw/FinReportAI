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

logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
log_file_path=f'/home/luzhenye/PythonProject/gpt/logs/原文-问题模板生成{datetime.now().strftime("%Y-%m-%d %H:%M")}.log'
file_handler = logging.FileHandler(log_file_path)
# 创建并设置日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# 将文件处理器添加到 Logger
logger.addHandler(file_handler)

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
    input_dir = "/home/luzhenye/data/json/text_tamplate_new"
    questions_list = """
    [ <company><year>年的营业总收入是多少？请分析其增速与去年相比的变化。
    <company><year>年归属于上市公司股东的净利润是多少？与去年相比，净利润增速如何？请解释增长的原因。
    <company><year>年第四季度单季度的营业总收入是多少？请分析其增速与去年相比的变化。
    <company><year>年第四季度单季度归属于上市公司股东的净利润是多少？与上季度相比，净利润增速如何？请解释增长的原因。

    <company><year>年的主要经济指标表现如何？请特别关注营业总收入和归属于上市公司股东的净利润，并分析其增长情况。
    <company><year>年第四季度单季度的主要经济指标表现如何？请特别关注营业总收入和归属于上市公司股东的净利润，并分析其增长情况。
    <company><year>年的股东回报情况如何？请分析特别分红的影响以及投资者对此的反应。
    <company><year>年第四季度单季度的股东回报情况如何？请分析特别分红的影响以及投资者对此的反应。

    <company><year>年的主要销售客户情况是怎样的？请关注前五名客户销售额和关联方销售额，并分析客户结构对业绩的影响。
    <company><year>年第四季度单季度的主要销售客户情况是怎样的？请关注前五名客户销售额和关联方销售额，并分析客户结构对业绩的影响。
    <company><year>年的主要供应商情况如何？请特别关注前五名供应商采购额和关联方采购额，并分析供应商结构对成本的影响。
    <company><year>年第四季度单季度的主要供应商情况如何？请特别关注前五名供应商采购额和关联方采购额，并分析供应商结构对成本的影响。

    <company><year>年基酒的设计产能是多少？
    <company><year>年的现有产能和实际产量有何不同？为什么会有这样的差异？
    基酒的新增产能是如何释放的？对公司产能有何影响？
    请解释产能计算标准中的“设计产能”和“实际产能”的计量单位以及计算方法。
    产能释放过程中可能遇到的风险有哪些？公司是否采取了相应的风险管理措施？
    对于<year>年的产能报告，您是否有任何疑问或建议？

    <company><year>年的现金流状况如何？请分析公司的经营、投资和筹资活动对现金流的影响，并评估公司的偿债能力和财务稳健性。
    <company><year>年的营销费用和财务费用分别是多少？与去年相比，有何变化？请解释变化的原因。
    请分析公司的盈利能力，包括毛利率、净利率、期间费用率等指标。并分析其变化趋势及影响因素。

    <company><year>年的品牌价值排名如何？请对品牌价值排名的变化进行分析。
    <company><year>年的市值稳定在多少？与去年相比，市值有何变化？请解释变化的原因。
    <company><year>年第四季度的品牌价值排名如何？请对品牌价值排名的变化进行分析。
    <company><year>年第四季度的市值稳定在多少？与上季度相比，市值有何变化？请解释变化的原因。

    <company><year>年的全年业绩达到了哪些规划目标？请列举并解释公司对<year+1>年的规划目标。
    请回答<company><year>年全年酒未来发展渠道的重点方向。
    您认为公司管理层对产能规划和投资的执行情况如何？存在哪些挑战？
    环境与社会责任在公司产能规划中扮演着怎样的角色？与实际产能情况是否相关？
    如何评估公司未来产能扩张的潜力？您认为有哪些因素可能影响这种扩张的实现？]
    """
    try:
        file_path = os.path.join(input_dir,file_name) # 选中其中一个文件
        save_json_path = os.path.join("/home/luzhenye/data/json/p-q-template",os.path.basename(file_path))
        # extract text
        if os.path.exists(save_json_path):
            return
        with open(file_path,"r",encoding="utf-8") as file:
            data_json = json.load(file)
        sub_text_list = [i for i in data_json['original_text'].split("\t") if i != ""]
        sub_template_list = [i for i in data_json['processed'].split("\t") if i != ""]
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
                        logger.error(f" 段落 {text} 发生错误：{e} ")
                        break
            final_result.append({"paragraph":text,"questions":result["questions"]})
        with open(save_json_path,"w",encoding="utf-8") as file :
            json.dump(final_result, file,ensure_ascii=False, indent=4)
        logger.info(f"{file_name} 处理完成")
    except Exception as e :
        logger.error(f"{file_name} 文件遇到{e}问题")
        return

if __name__ == "__main__":
    input_dir = "/home/luzhenye/data/json/text_tamplate_new"
    file_names = os.listdir(input_dir)
    num_threads = 8  # You can adjust this based on your system's capabilities
    # # # Process PDF files using multi-threading
    error_files = []
    # for file_name in file_names:
    #     error_files.append(process_json(file_name))
    with ProcessPoolExecutor(max_workers=num_threads) as executor:
        error_files = list(tqdm(executor.map(process_json, file_names), total=len(file_names)))
    print(error_files) 




# questions_list = """
# [
# - <company><year>年的营业总收入是多少？请分析其增速与去年相比的变化。
# - <company><year>年归属于上市公司股东的净利润是多少？与去年相比，净利润增速如何？请解释增长的原因。
# - <company><year>年的主要经济指标表现如何？请特别关注营业总收入和归属于上市公司股东的净利润，并分析其增长情况。
# - <company><year>年的股东回报情况如何？请分析特别分红的影响以及投资者对此的反应。
# - <company><year>年的主要销售客户情况是怎样的？请关注前五名客户销售额和关联方销售额，并分析客户结构对业绩的影响。
# - <company><year>年的主要供应商情况如何？请特别关注前五名供应商采购额和关联方采购额，并分析供应商结构对成本的影响。
# - <company><year>年第四季度单季度的营业总收入是多少？请分析其增速与去年相比的变化。
# - <company><year>年第四季度单季度归属于上市公司股东的净利润是多少？与上季度相比，净利润增速如何？请解释增长的原因。
# - <company><year>年第四季度单季度的主要经济指标表现如何？请特别关注营业总收入和归属于上市公司股东的净利润，并分析其增长情况。
# - <company><year>年第四季度单季度的股东回报情况如何？请分析特别分红的影响以及投资者对此的反应。
# - <company><year>年第四季度单季度的主要销售客户情况是怎样的？请关注前五名客户销售额和关联方销售额，并分析客户结构对业绩的影响。
# - <company><year>年第四季度单季度的主要供应商情况如何？请特别关注前五名供应商采购额和关联方采购额，并分析供应商结构对成本的影响。
# - <company><year>年的全年业绩达到了哪些规划目标？请列举并解释公司对<year+1>年的规划目标。
# - <company><year>年的治理效能如何？请分析董事会的运作情况以及对公司决策的影响。
# - 根据<company><year>年年度报告回答，<company>的产品生产工艺流程为？
# - <company>的产品原料采购模式是什么？
# - <company><year>年的品牌价值排名如何？请对品牌价值排名的变化进行分析。
# - <company><year>年的市值稳定在多少？与去年相比，市值有何变化？请解释变化的原因。
# - <year>年第四季度<company>的产品原料采购模式是什么？
# - <company><year>年第四季度的品牌价值排名如何？请对品牌价值排名的变化进行分析。
# - <company><year>年第四季度的市值稳定在多少？与上季度相比，市值有何变化？请解释变化的原因。
# - <company><year>年全年酒的销售渠道是什么？
# - <company><year> 年全年酒的销售模式是什么？
# - <company><year>年全年酒的销售渠道占比是多少？分析其未来趋势
# - <company><year>年全年酒的直销在销售渠道中的占比是多少？分析其未来趋势
# - <company><year>年全年酒的直营与批发的占比是多少，分析其未来趋势
# - 请回答<company><year>年全年酒未来发展渠道的重点方向
# - 根据<company><year>年年度报告回答，<company><year>年的公司经营模式为？
# - <company>的产品销售模式是什么？
# - <company><year>年四季度酒的销售渠道是什么？
# - <company><year>年四季度酒的销售模式是什么？
# - <company><year>年四季度酒的销售渠道占比是多少？分析其未来趋势
# - <company><year>年四季度酒的直销在销售渠道中的占比是多少？分析其未来趋势
# - <company><year>年四季度酒的直营与批发的占比是多少，分析其未来趋势
# - 请回答<company><year>年四季度酒未来发展渠道的重点方向
# - <company><year>年四季度的主要公司经营模式为？
# - <company><year>年的营销费用和财务费用分别是多少？与去年相比，有何变化？请解释变化的原因。
# - 请分析公司的盈利能力，包括毛利率、净利率、期间费用率等指标。并分析其变化趋势及影响因素。
# - <company><year>年的现金流状况如何？请分析公司的经营、投资和筹资活动对现金流的影响，并评估公司的偿债能力和财务稳健性。
# - 分析一下该公司<year>年的盈利能力，并分析原因。
# - <company><year> 年基酒的设计产能是多少？
# - <company>的产品生产工艺流程为？
# - 根据以上分类整理为以上格式请描述制酒车间的设计产能和实际产能情况
# - 制酒车间的设计产能和实际产能有何不同？为什么会有这样的差异？
# - 基酒的新增产能是如何释放的？对公司产能有何影响？
# - 请解释产能计算标准中的“设计产能”和“实际产能”的计量单位以及计算方法。
# - 上述现有产能中的实际产量在报告期内有何变化？对公司业绩有何影响？
# - 在建产能项目中，各项目的计划投资金额是否符合预期？为什么？
# - 您认为公司管理层对产能规划和投资的执行情况如何？存在哪些挑战？
# - 环境与社会责任在公司产能规划中扮演着怎样的角色？与实际产能情况是否相关？
# - 请比较现有产能和在建产能项目的投资回报率。哪个项目的潜在回报更高？
# - 产能释放过程中可能遇到的风险有哪些？公司是否采取了相应的风险管理措施？
# - 对于<year>年的产能报告，您是否有任何疑问或建议？
# - 如何评估公司未来产能扩张的潜力？您认为有哪些因素可能影响这种扩张的实现？]
# """

# 手动生成
# print(content)
# result = """

# """
# result = result.replace('\n', '')
# result = json.loads(result)
# with open(os.path.join("/home/luzhenye/PythonProject/gpt/p-q-template",os.path.basename(json_path)),"w",encoding="utf-8") as file :
#     json.dump(result, file,ensure_ascii=False, indent=4)
# result = get_response_gpt4(content)
