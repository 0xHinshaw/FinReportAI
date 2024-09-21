import os, tqdm
import json
import re
import itertools
import networkx as nx
from pylab import mpl
from pyltp import SentenceSplitter, Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller

model_path ='/data/shenyuge/model/ltp_data_v3.4.0/'
user_dict = '/data/shenyuge/model/vocab/all.txt'

#Load all data from local
segmentor = Segmentor(model_path+"cws.model",user_dict)
# 词性标注
postagger = Postagger(model_path+"pos.model")
# 句法分析
parser = Parser(model_path+"parser.model")

# Nouns_list = ["并列","时间顺序","举例"]
# Adjectives_list = ["并列", "转折"]
# Verbs_list = ["并列", "因果", "举例", "条件", "假设"]
# Adverbs_list = ["递进", "转折", "让步", "条件", "假设"]
# Conjunctions_list=["并列", "递进", "因果", "让步", "条件", "假设"]
# temp_list = [Nouns_list,Adjectives_list,Verbs_list,Adverbs_list,Conjunctions_list]


def find_common_elements(list1, list2):
    """找出两个列表中的相同元素"""
    # 将列表转换为集合
    set1 = set(list1)
    set2 = set(list2)
    # 使用交集操作找出相同的元素
    common_elements = set1.intersection(set2)
    # 返回相同元素的列表
    return list(common_elements)
# 输出可能结果的字典：
# for i in range(len(temp_list)):
#     for j in range(i+1,len(temp_list)):
#         print('"'+str(i)+""+str(j)+'"'+":")
#         print(find_common_elements(temp_list[i],temp_list[j]))
#         print('"'+str(j)+""+str(i)+'"'+":")
#         print(find_common_elements(temp_list[i],temp_list[j]))

n_list = ["ni","nl","ns","nt","nz","nd","nh","n","b","r","ws"]
Adj_list = ["a"]
V_list = ["v"]
Adv_list = ["d"]
Con_list = ["c"]
all_list = n_list+Adj_list+Adv_list+V_list+Con_list
temp_list2 = [n_list,Adj_list,V_list,Adv_list,Con_list]

def read_json(file_path):
    """读取json文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        json_dict = json.load(f)
    return json_dict


def json2sentences(json_dict, sentences):
    if isinstance(json_dict["subtitle"],list) :
        if json_dict["sentences"] != "":
            print("出现特例")
        for dic in json_dict["subtitle"]:
            sentences = json2sentences(dic,sentences)
    else:
        for i in json_dict["sentences"]:
            sentences.append(i)
    return sentences

def select_words(postags, words):
    exclude_tag = {'d', 'e', 'o', 'wp', 'q', 'u', 'c'}
    # exclude_tag = {'wp'}
    new_words = [w for (i, w) in enumerate(words) if postags[i] not in exclude_tag and 
                 w not in {'是', '了', '的', '得'}]
    return new_words

def generate_prompt(postags,words,sent,arcs):
    """根据语法依存关系将部分语法关系依存的词语连接，生成prompt"""
    result = []
    chunk_index = {key: None for key in range(len(words))}
    n = 0
    for index,arc in enumerate(arcs):
        # if arc[1] in ["ATT","ADV","FOB","POB","IOB","VOB","CMP"]:#需要连接的语法关系
        if arc[1] in ["ATT","ADV"]:#需要连接的语法关系
            if chunk_index[index]:
                if chunk_index[index] > arc[0]-1:
                    chunk_index[index] = arc[0]-1
            else:
                if index < arc[0]-1 :
                    chunk_index[index] = arc[0]-1
                else:
                    if chunk_index[arc[0]-1]:
                        if chunk_index[arc[0]-1] > index:
                            chunk_index[arc[0]-1] = index
                    else:
                        chunk_index[arc[0] - 1] = index
    chunk_words = []
    while n < len(words):
        if chunk_index[n]:
            chunk_words.append("".join(words[n:chunk_index[n]+1]))
            n = chunk_index[n]+1
        elif postags[n] == "wp": #删除标点符号
            n=n+1
        else:
            chunk_words.append("".join(words[n:n+1]))
            n+=1
    # 连接完毕生成prompt,5句话问一次更好
    chunk_words = select_words(postags, chunk_words)
    # prompt = '在‘{}’这句话中，{}中是否存在两个词之间,注意是列表中的词，存在列表["并列", "递进", "因果", "转折", "让步", "时间顺序", "条件", "举例", "目的", "假设", "逻辑推理"]中的一个关系,请注意要是列表中的关系，'.format(sent,chunk_words)
    prompt = '现有两个表：词汇表:{}；逻辑表：["并列", "递进", "因果", "转折", "让步", "时间顺序", "条件", "举例", "目的", "假设", "逻辑推理"]。从‘{}’这句话中分析，词汇表中是否存在两个词之间，存在逻辑表中的某个逻辑关系，'.format(chunk_words, sent)
    return ""+prompt+""
    # for j in list(itertools.combinations(index_tag, 2)):
    #     if len(prompt_dict[str(j[0][1])+str(j[1][1])]) != 0:
    #         print("‘{}‘和’{}‘是否存在{}中某一种关系？".format(words[j[0][0]],words[j[1][0]],prompt_dict[str(j[0][1])+str(j[1][1])]))

# def read_json_dir(folder_path):
#     if not os.path.isdir(folder_path):
#         print("未找到指定文件夹")
#         return
#     # 遍历文件夹中的内容
#     contents = os.listdir(folder_path)
#     for item in contents:
#         # 构建完整路径
#         item_path = os.path.join(folder_path, item)
#         # 检查当前项是文件还是文件夹
#         if os.path.isdir(item_path):
#             print("文件夹:", item)
#             read_json(item_path)
#         elif os.path.splitext(item)[1] == ".json":  # 筛选文件类型,注意”.“
#             print("json文件:", item)
#             json_dict = read_json(item_path)
#             sentences = []
#             sentences = json2sentences(json_dict, sentences)
#             result = []
#             for sent in sentences:
#                 words = segmentor.segment(sent)
#                 postags = postagger.postag(words)
#                 arcs = parser.parse(words, postags)
#                 result.append(generate_prompt(postags, words, sent, arcs))
#             for i in result:
#                 print(i)

def json2prompt(json_path):
    json_dict = read_json(json_path)
    sentences = []
    sentences = json2sentences(json_dict, sentences)
    result = ["以下问题只输出字典结果，不用解释，不要复述"]
    for index,sent in enumerate(sentences):
        words = segmentor.segment(sent)
        postags = postagger.postag(words)
        arcs = parser.parse(words, postags)
        result.append(generate_prompt(postags, words, sent, arcs))
        if index%5 == 4:# 6个问题为一组较好
            result.append("以上问题，如果存在逻辑关系请用triplet的形式表达出来，比如{词1: ‘’, 关系: ‘’, 词2:},词1和词2必须来自表1，关系必须来自表2 请注意回答的完整性，如果不存在则回答空字典{}")
            result.append("以下问题只输出字典结果，不用解释，不要复述")
    for i in result:
        print(i)

def sents2prompt(sent):
    """
    This Python function generates a prompt based on the input sentence, utilizing segmentation,
    part-of-speech tagging, parsing, and prompt generation techniques.
    
    :param sent: Generates a prompt based on a given sentence. The function `sents2prompt` takes a 
    sentence as input and processes it to generate a question prompt. 
    :return: prompt string
    """
    question ="以下问题只输出字典结果，不用解释，不要复述： "
    words = segmentor.segment(sent)
    postags = postagger.postag(words)
    arcs = parser.parse(words, postags)
    question += generate_prompt(postags, words, sent, arcs)
    question += """以上问题，如果存在逻辑关系请用triplet list的形式表达出来，比如[{"A": 词1, "关系": 关系1, "B": 词2}, {A: 词3, "关系": 关系2, "B": 词4},...], 不要使用空格或换行符, 其中词1词2词3词4必须来自表1，关系1关系2且必须在列表：["并列", "递进", "因果", "转折", "让步", "时间顺序", "条件", "举例", "目的", "假设", "逻辑推理"]里面，不能是别的词，尽量准确描述，如果不存在则回答空字典{}"""

    return question

def save_prompt(json_path, output_path='/data/shenyuge/lingyue-data-process/logic_chain/prompts.json'):
    """
    The function `save_prompt` reads data from a JSON file, processes it to extract prompts from
    sentences, and saves the results to another JSON file.
    
    :param json_path: The `json_path` parameter in the `save_prompt` function is the file path to the
    JSON file that contains the data you want to process.
    :param output_path: The `output_path` parameter in the `save_prompt` function is the file path where
    the processed data will be saved. 
    """
    with open(json_path, 'r', encoding = 'utf-8') as f:
        data = json.load(f)
    # sentences = json2sentences(data, [])
    result = []
    # count = 0
    for item in tqdm.tqdm(data):
        sent = item['keycontent'].replace('\n', '')
        if len(sent) >= 25 and len(item['keywords']) > 0:
            # result.append({'sentence index': item['sentence index'], 'prompt': sents2prompt(sent)})
            item['prompt'] = sents2prompt(sent)
            result.append(item)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    json_path = '/data/shenyuge/lingyue-data-process/doc2json/output2.json'
    save_prompt(json_path)
    # with open('/data/shenyuge/lingyue-data-process/doc2json/output2.json', 'r', encoding = 'utf-8') as f:
    #     data = json.load(f)
    # # sentences = json2sentences(data, [])
    # result = []
    # count = 0
    # for item in tqdm.tqdm(data):
    #     sent = item['keycontent'].replace('\n', '')
    #     if len(sent) >= 25 and len(item['keywords']) > 0:
    #         # result.append({'sentence index': item['sentence index'], 'prompt': sents2prompt(sent)})
    #         item['prompt'] = sents2prompt(sent)
    #         result.append(item)
    # with open('/data/shenyuge/lingyue-data-process/logic_chain/prompts.json', 'w', encoding='utf-8') as f:
    #     json.dump(result, f, ensure_ascii=False, indent=4)

# def get_tag_index(pos,lsts):
#     for index, lst in enumerate(lsts):
#         if pos in lst:
#             return index
#     print("词性超出范围，请检查")


# // [
# //     {
# //         "Topic": "topic1",
# //         "keywords": [
# //             {   "keyword": "keyword1",
# //                 "sentenceindex": {1,2,3,4,5},
# //                 "similar indeces": [(1,2), (2,3), (1,3)], //假如123像
# //                 "merged logic chain": [logic123, logic4, logic5]
# //             },
# //             {   "keyword": "keyword2",
# //                 "sentenceindex": {6,7,8,9,10},
# //                 "similar indeces": [(6,7), (7,8), (6,8)], //假如678像
# //                 "merged logic chain": [logic678, logic9, logic10]
# //             }
# //         ]
# //     }
# // ]



# import pandas as pd

# # 计算节点图的距离：
# def get_node_distance(G,source,target1,pr=False):
#     distance = nx.shortest_path_length(G, source=source, target=target1)
#     if pr:
#         print("'%s'与'%s'在依存句法分析图中的最短距离为:  %s" % (source, target1, distance))
#     return distance


# #  分词 cws、词性 pos、命名实体标注 ner、语义角色标注 srl、依存句法分析 dep、语义依存分析树 sdp、语义依存分析图 sdpg
# # 分词

# sample = r"C:\Users\78666\Desktop\行业周报\已完成\（可公开）食品饮料行业双周报（20231113-20231126）：茅台再次发放特别分红，持续关注动销、成本等关键指标.json"
# json2prompt(sample)


# 可视化语法依存关系
# rely_id = [arc[0]for arc in arcs]  # 提取依存父节点id
# relation = [arc[1] for arc in arcs]  # 提取依存关系
# heads = ['Root' if id == 0 else words[id-1] for id in rely_id]  # 匹配依存父节点词语
#
# # for i in range(len(words)):
# #     print(parser_mean[str(format(relation[i]))] + '(' + words[i] + ', ' + heads[i] + ')')
#
# # 利用networkx绘制句法分析结果
#
# mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
# G = nx.Graph()  # 建立无向图G
#
# # 添加节点
# for word in words:
#     G.add_node(word)
#
# G.add_node('Root')
#
# # 添加边
# for i in range(len(words)):
#     G.add_edge(words[i], heads[i],relationship = relation[i])
# pos = nx.spring_layout(G)
# nx.draw(G, pos, with_labels=True)
# edge_labels = nx.get_edge_attributes(G, 'relationship')
# nx.draw_networkx_edge_labels(G ,pos,edge_labels=edge_labels)
#
# # nx.draw(G, with_labels=True)
# plt.savefig("undirected_graph.png")

# 命名实体识别
# recognizer = NamedEntityRecognizer(model_path+"ner.model")
# netags = recognizer.recognize(words, postags)
# netags_str = '\t'.join(netags)
# print()

