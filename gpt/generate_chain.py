from extractkey import get_sentence_keywords
from cluster import sentence_similarity
from bert_util import get_similarity
import pickle, glob, json
import pandas as pd
import numpy as np

TOP_N = 5

json_path = '/data/shenyuge/lingyue-data-process/logic_chain/multi_process_test'
with open('/data/shenyuge/lingyue-data-process/logic_chain/keyword_to_index.json', 'r', encoding='utf-8') as f:
    kw2index = json.load(f)
# with open('/data/shenyuge/lingyue-data-process/logic_chain/total_data.pickle') as f:
data = pd.read_pickle('/data/shenyuge/lingyue-data-process/logic_chain/total_data.pickle')
# dfs = []
# for file in glob.glob(f'{json_path}/**/*.json', recursive=True):
#     dfs.append(pd.read_json(file).explode("logicchain",ignore_index = True))
#     with open(file, 'r', encoding='utf-8') as f:
#         records = json.load(f)
#         f.close()
#     for r in records:
#         r['keycontent'] = r['keycontent'].replace('\n', '')
#     with open(file, 'w', encoding='utf-8') as f:
#         json.dump(records, f,ensure_ascii=False,indent=4)
# data = pd.concat(dfs)
# data.to_pickle('/data/shenyuge/lingyue-data-process/logic_chain/total_data.pickle')

def merge_logic_chains(user_input, similar_sentences, similar_logic_chains):
    # Should return (answer_sentence, answer_logic_chain)
    pass

def output_logic_chain(user_input):
    """
    This function takes user input, identifies keywords in a sentence, retrieves similar sentences from
    a dataset, calculates similarity scores, and returns the most similar sentences along with their
    corresponding logic chains after merging.
    
    :param user_input: It looks like the `output_logic_chain` function is designed to process user input
    and retrieve relevant information based on keywords and similarity scores. The function seems to
    involve extracting keywords from a sentence, finding similar sentences from a dataset, calculating
    similarity scores, and merging logic chains
    :return: The function `output_logic_chain` returns the merged answer sentence and a dictionary
    containing the merged logic chains.
    """
    keywords = get_sentence_keywords(sent1)
    indices = set()
    for keyword in keywords:
        indices = indices.union(set(kw2index[keyword]['sentence index'])) 

    sentences = data[data['sentence index'].isin(indices)].drop_duplicates(['keycontent']).reset_index()
    similarity = get_similarity(sent1, sentences['keycontent'].to_list())
    # similarity = sentence_similarity(sent1, sentences['keycontent'].to_list())
    topn = np.argsort(similarity)[::-1][:TOP_N]
    similar_sentences = sentences.iloc[topn]['keycontent']
    similar_logic_chains = sentences.iloc[topn]['logicchain']

    answer_sentence, answer_logic_chain = merge_logic_chains(user_input, similar_sentences, similar_logic_chains)
    logic_chain_res = {}
    for chain in answer_logic_chain:
        # Each chain with format 
        logic_chain_res[chain["A"]] = (chain['关系'], chain["B"])
    # return the merged answer and merged logic chain
    return answer_sentence, logic_chain_res

if __name__ == '__main__':
    user_input = "2020年之后，白酒的销量呈现什么趋势？" #User question.
    answer_sentence, logic_chain_res = output_logic_chain(user_input)
    