from extractkey import get_sentence_keywords
from cluster import sentence_similarity
from bert_util import get_similarity
from gptapi import call_llm_api, get_sent_logic
from utils import timeit
import json, re
import pandas as pd
import numpy as np
from config import Config

config = Config()
TOP_N = 5

json_path = config.json_directory
with open(config.kw2idx_path, 'r', encoding='utf-8') as f:
    kw2index = json.load(f)
api_key = config.api_key
data = pd.read_pickle(config.total_data_path)


def merge_logic_chains(user_input, input_logic_chain, similar_sentences, similar_logic_chains):
    # Call GPT api to optimize user input base on similar sentences from database.
    # Should return (answer_sentence, answer_logic_chain)
    prompt_template = """假设一个金融语言模型能够自动分析输入文字，提取关键内容和逻辑链，并在数据库中匹配相应的句子以优化现有文字。
    现有文字为：“{0}”，现有逻辑链为{1}，已匹配到以下句子：{2}。首先，请识别这些句子涉及的行业和包含的金融要素。
    然后，基于这些行业信息、金融要素及句子中的逻辑链:{3}，优化现有句子的逻辑链，使用优化后逻辑链修改现有文字并输出优化后的句子。
    这个新句子应整合所有相关内容而不引入额外信息，并确保所包含的逻辑链元素全部来源于提供的逻辑链。最后，请输出这个句子及其使用的逻辑链，
    按字典格式输出：{{'sentence':'{{}}', 'chains': {{}}}}。注意：回答须用中文且直接相关，
    只输出仿写的句子和逻辑链即可，不需要输出行业和金融要素，生成的逻辑链格式为{{"A":,"关系":,"B":}}，不得包含非必要文本。最后不要加任何的总结性的陈述！"""
    prompt = prompt_template.format(user_input, input_logic_chain, similar_sentences, similar_logic_chains)
    response = call_llm_api(prompt,api_key)
    pattern = r"({)(.*)(})"
    match = re.search(pattern,response,re.DOTALL)
    if match:
        result = match.group()
        result = re.sub("，",",",result)
        #result = re.sub("}}","}",result)
        print('================',result)
        temp = eval(result)
        return temp["sentence"],temp["chains"]
    else:
        return merge_logic_chains(user_input, input_logic_chain, similar_sentences, similar_logic_chains)

def format_logic_chain(logic_chain:list):
    # Change logic chain format to dict representation.
    logic_chain_res = {}
    for chain in logic_chain:
        # Each chain with format {"A":"entity A", '关系':'relation 1', 'B':'entity b'}
        logic_chain_res[chain["A"]] = logic_chain_res.get(chain['A'], []) + [(chain['关系'], chain["B"])]
    return logic_chain_res

def get_entity_paper_mapping(sentences:pd.DataFrame):
    """
    This function takes a DataFrame of sentences and creates a mapping of entities to the sentences and
    papers they appear in.
    
    :param sentences: The function `get_entity_paper_mapping` takes a DataFrame `sentences` as input.
    :type sentences: pd.DataFrame
    :return: A dictionary mapping entities to a set of sentences and a set of paper titles where the
    entities appear in the provided DataFrame. {Entity: {'sentences': set(), 'paper title': set()}}
    """
    res = {}
    for _, row in sentences.iterrows():
        for lc in row['logicchain']:
            A, B = lc['A'], lc['B']
            res[A] = res.get(A, {'sentences': set(), 'paper': set()})
            res[A]['sentences'].add(row['sentence index'])
            res[A]['paper'].add(row['paper title'])
            res[B] = res.get(B, {'sentences': set(), 'paper': set()})
            res[B]['sentences'].add(row['sentence index'])
            res[B]['paper'].add(row['paper title'])
    return res

@timeit
def output_logic_chain(user_input):
    """
    The function `output_logic_chain` processes user input to find similar sentences and logic chains,
    merges them with the input logic chain, and returns the merged answer sentence and logic chains.
    
    :param user_input: The `output_logic_chain` function takes a user input as a parameter and performs
    a series of operations to generate an answer sentence, a current logic chain, and a total logic
    chain
    :return: The function `output_logic_chain` returns the merged answer sentence, the current logic
    chain for the answer, and the total logic chain from similar sentences.
    """

    keywords = get_sentence_keywords(user_input)
    indices = set()
    for keyword in keywords:
        indices = indices.union(set(kw2index[keyword]['sentence index'])) 

    pick_columns = ['sentence index', 'keycontent', 'logicchain', 'paper title']
    sentences = data[data['sentence index'].isin(indices)][pick_columns].groupby(['sentence index', 'keycontent', 'paper title']).agg(list).reset_index()
    sentences = sentences.drop_duplicates(['keycontent']).reset_index()
    similarity = get_similarity(user_input, sentences['keycontent'].to_list())
    
    # get TOP_N most similar sentences
    topn = np.argsort(similarity)[::-1][:TOP_N]
    similar_sentences = sentences.iloc[topn]['keycontent'].to_list()
    similar_logic_chains = sentences.iloc[topn]['logicchain'].to_list()
    similar_logic_chains = [a for b in similar_logic_chains for a in b]

    # Map each entity to its corresponding sentence and paper
    entity_paper_mapping = get_entity_paper_mapping(sentences.iloc[topn])

    # Get total logic chain
    logic_chain_total = format_logic_chain(similar_logic_chains) 
    
    input_logic_chain = get_sent_logic(user_input)
    answer_sentence, answer_logic_chain = merge_logic_chains(user_input, input_logic_chain, similar_sentences, similar_logic_chains)
    logic_chain_curr = format_logic_chain(answer_logic_chain) # Current logic chain

    # return the merged answer and merged logic chain
    return answer_sentence, logic_chain_curr, logic_chain_total, entity_paper_mapping

if __name__ == '__main__':
    user_input = "2004年以来，白酒销量有什么趋势？" #User question.
    answer_sentence, logic_chain_curr, logic_chain_total, entity_paper_mapping = output_logic_chain(user_input)
    # print('With user input: {}, the merged sentence is {}, logic chain is {}'.format(user_input, answer_sentence, logic_chain_res))
    print('With user input: {}, the merged sentence is {}, logic_chain_curr is {}, logic_chain_total is {}'.format(user_input, answer_sentence, logic_chain_curr,logic_chain_total))
    