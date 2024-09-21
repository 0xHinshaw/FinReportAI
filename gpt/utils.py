import sys
sys.path.append('/home/llmapi/finreport')
from pydantic import BaseModel, Field
from langchain_core.prompts.chat import ChatMessagePromptTemplate
# from configs import logger, log_verbose
from typing import (
    Literal,
    Optional,
    Callable,
    Generator,
    Dict,
    Tuple,
    Any,
    Awaitable,
    Union,
    List,
)
from sentence_transformers import SentenceTransformer
import requests
import json
import numpy as np
import math
import re


# class History(BaseModel):
#     """
#     对话历史
#     可从dict生成，如
#     h = History(**{"role":"user","content":"你好"})
#     也可转换为tuple，如
#     h.to_msy_tuple = ("human", "你好")
#     """
#     role: str = Field(...)
#     content: str = Field(...)

#     def to_msg_tuple(self):
#         return "ai" if self.role=="assistant" else "human", self.content

#     def to_msg_template(self, is_raw=True) -> ChatMessagePromptTemplate:
#         role_maps = {
#             "ai": "assistant",
#             "human": "user",
#         }
#         role = role_maps.get(self.role, self.role)
#         if is_raw: # 当前默认历史消息都是没有input_variable的文本。
#             content = "{% raw %}" + self.content + "{% endraw %}"
#         else:
#             content = self.content

#         return ChatMessagePromptTemplate.from_template(
#             content,
#             "jinja2",
#             role=role,
#         )

#     @classmethod
#     def from_data(cls, h: Union[List, Tuple, Dict]) -> "History":
#         if isinstance(h, (list,tuple)) and len(h) >= 2:
#             h = cls(role=h[0], content=h[1])
#         elif isinstance(h, dict):
#             h = cls(**h)

#         return h

from concurrent.futures import ThreadPoolExecutor, as_completed
import os

thread_pool = ThreadPoolExecutor(os.cpu_count())


def run_in_thread_pool(
    func: Callable,
    params: List[Dict] = [],
    pool: ThreadPoolExecutor = None,
):
    """
    在线程池中批量运行任务，并将运行结果以生成器的形式返回。
    请确保任务中的所有操作是线程安全的，任务函数请全部使用关键字参数。
    """
    tasks = []
    pool = ThreadPoolExecutor(os.cpu_count())

    for kwargs in params:
        thread = pool.submit(func, **kwargs)
        tasks.append(thread)
    results = []
    for obj in as_completed(tasks):
        results.append(obj.result())
    return results


class RetrivalTableContent:
    @staticmethod
    def search_docs_by_content(query_input, index_name):
        query_dsl = {
            "query": {
                "match": {
                    "content": {
                        "query": query_input,
                        "analyzer": "my_analyzer",
                    }
                }
            },
            "size": 50,
        }

        res = requests.get(
            url="http://10.13.14.16:9200/{}/_search".format(index_name),
            json=query_dsl,
        )
        retrival_datas = []

        try:
            for item in json.loads(res.content)["hits"]["hits"]:
                retrival_datas.append(
                    {
                        "content": item["_source"]["content"],
                        # "vector": item["_source"]['vector'],
                        # "year": item["_source"]["year"],
                        # "quarter": item["_source"]["quarter"],
                        # "company": item["_source"]["company"],
                        # "indicator": item["_source"]["indicator"],
                        # "value": item["_source"]["value"],
                        # "excel_name": item["_source"]["excel_name"],
                    }
                )
        except:
            pass

        return retrival_datas

    @staticmethod
    def rescore(retrival_datas, query_input, topk):
        model = SentenceTransformer("/home/llmapi/finreport/embed_model/m3e-base")
        embeddings_1 = model.encode([query_input])
        embeddings_2 = model.encode(
            [retrival_data["content"] for retrival_data in retrival_datas]
        )
        similarity = embeddings_1 @ embeddings_2.T
        scores = np.array(similarity[0])
        for i, retrival_data in enumerate(retrival_datas):
            retrival_data["score"] = scores[i]
        retrival_datas = sorted(retrival_datas, key=lambda x: x["score"], reverse=True)
        return retrival_datas[:topk]

    @staticmethod
    def search_docs_by_keywords(query_json, index_name):
        query_dsl = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"content": query_json["company"]}},
                        {"match_phrase": {"year": query_json["year"]}},
                        {"match_phrase": {"indicator": query_json["indicator"]}},
                        {"match_phrase": {"quarter": query_json["quarter"]}},
                    ]
                }
            },
        }
        res = requests.get(
            url="http://10.13.14.16:9200/{}/_search".format(index_name),
            json=query_dsl,
        )
        retrival_datas = []
        try:
            for item in json.loads(res.content)["hits"]["hits"]:
                if item["_source"]["value"] != "--" and query_json["indicator"]==item["_source"]["indicator"]:
                    import re
                    match = re.search(r'\(([^)]+)\)(?!.*\))', item["_source"]["indicator"])
                    if match:
                        retrival_datas.append(item["_source"]["content"]+match.group(1))
                    else:
                        # 默认单位是万元
                        retrival_datas.append(item["_source"]["content"]+'万元')
        except:
            pass

        return retrival_datas


class RetrivalRelatedTableContent:
    def __init__(self) -> None:
        self.prompt = """请从用户输入中提取公司名、金融指标、年份、季度信息。请注意：
        1.季度信息只能填写："一季"，"二季"，"三季"，"四季"，半年则为"二季"，没有季度信息就填写"全年"。
        2.直接返回名称，不要输出其他多余的内容，输出json格式：
        [{{
            "company": str,
            "indicator": str,
            "year": str,
            "quarter": str,
            "yoy" : bool
        }},
        {{
            "company": str,
            "indicator": str,
            "year": str,
            "quarter": str,
            "yoy" : bool
        }},......]
        3.注意用户问题中的年份是文字时请转换成数字；当用户问到同比、与去年相比、前两年等类似信息时，注意也要抽取出来对应的年份。
        4.若用户需要单个季度的数据请，该季度前一个季度也应该抽取出来。
        5.当用户让分析增长情况时，'yoy'请返回true，否则返回false
        6.如果用户没有问及金融指标值相关信息，就认为是一个闲聊类问题，输出空json。
        用户输入：{}
        """
        self.map_dic = {
            '归属于上市公司股东的净利润':'归属母公司股东的净利润'
        }
        self.related_dic = {
            '营业总收入':"营业总收入同比增长率(%)",
            '归属母公司股东的净利润':'归属母公司股东的净利润同比增长率(%)'
        }

    @staticmethod
    def post_query(query: str):
        api_json = {
            "api_base_url": "https://api.kwwai.top/v1/",
            "api_key": "sk-QeiIJwcjqnhybuSeBbC0F27eEc0b42529a4410194b362bBb",
        }
        api_key = api_json["api_key"]
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "gpt-4-turbo",
            "temperature": 0.2,
            "messages": [{"role": "user", "content": query}],
        }
        response = requests.post(
            api_json["api_base_url"] + "chat/completions",
            headers=headers,
            json=data,
            timeout=200,
        )
        return response.json()["choices"][0]["message"]["content"]

    def getIntention(self, query: str):
        try:
            res = json.loads(
                RetrivalRelatedTableContent().post_query(self.prompt.format(query))
            )
        except:
            res = []
        # 将提取指标修正成标准指标
        for item_json in res:
            if item_json['indicator'] in self.map_dic.keys():
                item_json['indicator'] = self.map_dic[item_json['indicator']]
        for item_json in res:
            if item_json['indicator'] in self.related_dic.keys():
                res.append({
                    'company':item_json['company'],
                    'year':item_json['year'],
                    'quarter':item_json['quarter'],
                    'indicator':self.related_dic[item_json['indicator']],
                })
        return res

    def retrieval_keywords_related_info(self, extract_table_data):
        # 检索相关的计算指标
        query_dsl = {"query": {"match": {"目标指标": extract_table_data["indicator"]}}}
        try:
            response = json.loads(
                requests.get(
                    url="http://10.13.14.16:9200/{}/_search".format("指标公式"),
                    json=query_dsl,
                ).text
            )
        except:
            return [], ""
        res = [hit["_source"] for hit in response["hits"]["hits"]]
        if not len(res):
            return [], ""
        related_indicator = res[0]["所需指标"]
        computing_method = res[0]["公式"]
        related_indicator_contents = []
        for item in related_indicator:
            json_item = {
                "company": extract_table_data["company"],
                "year": extract_table_data["year"],
                "quarter": extract_table_data["quarter"],
                "indicator": item,
            }
            indicators = RetrivalTableContent().search_docs_by_keywords(
                json_item, "excel_indicators"
            )
            if not len(indicators):
                continue
                # return [], computing_method
            related_indicator_contents.append(indicators[0])
        computing_method = "{}={}".format(
            extract_table_data["indicator"], computing_method
        )
        return related_indicator_contents, computing_method

    def main(self, query):
        indicator_jsonl_need_retrival = self.getIntention(query)
        print(indicator_jsonl_need_retrival)
        indicator_value_list = run_in_thread_pool(
            RetrivalTableContent().search_docs_by_keywords,
            [
                {"query_json": item_json, "index_name": "excel_indicators"}
                for item_json in indicator_jsonl_need_retrival
            ],
        )
        res = []
        for indicator_values in indicator_value_list:
            if len(indicator_values):
                res += list(set(indicator_values))
        indicator_related_value_list = run_in_thread_pool(
            self.retrieval_keywords_related_info,
            [{"extract_table_data": i} for i in indicator_jsonl_need_retrival],
        )
        for indicator_related_values in indicator_related_value_list:
            if (
                not len(indicator_related_values[0])
                and indicator_related_values[1] == ""
            ):
                pass
            else:
                res += [
                    str(indicator_related_values[0])
                    + "  计算公式："
                    + indicator_related_values[1]
                ]
        prompt_table = ""
        if len(res):
            indicators_string = ""
            for item in res:
                indicators_string += item + "\n\n"
            prompt_table = "表格检索内容：\n\n{}\n表格检索出来的内容都是准确的。".format(
                indicators_string
            )
        return prompt_table


if __name__ == "__main__":
    prompt_table = RetrivalRelatedTableContent().main(
        "贵州茅台2023年第四季度的营业总收入是多少"
    )
    print(prompt_table)
