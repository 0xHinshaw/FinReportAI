from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
from config import Config
import json
import jieba
import glob
import pandas as pd

config = Config()

def tokenizer_ch(text):
    words = jieba.lcut(text)
    return words

def sentence_similarity(sent1:str, sents:list):
    # Get sentence similarity values between sent1 and all sentences in list sents.
    vectorizer = TfidfVectorizer(tokenizer=tokenizer_ch)
    X = vectorizer.fit_transform([sent1] + sents)
    similarity = cosine_similarity(X[0], X[1:])
    return similarity[0]

def clustering(phrases, threshold=0.7):
    """
    The function `clustering` performs agglomerative clustering on a list of phrases using TF-IDF
    vectorization and cosine similarity, and then groups the phrases based on the clusters formed.
    
    :param phrases: The `phrases` parameter in the `clustering` function is a list of entities
    representing the phrases that you want to cluster based on their similarity. Each string in the list
    corresponds to a phrase that you want to analyze and group into clusters
    :param cluster_res_directory: the directory path where the clustering results will be saved in JSON format. 
    :param threshold: The `threshold` parameter in the `clustering` function represents the similarity
    threshold for clustering the phrases. It is used to determine when two phrases should be grouped
    together in the same cluster based on their similarity. If the cosine similarity between two phrases
    is above the threshold value, they will be considered part
    :return: The function `clustering` returns a dictionary `clustered_phrases` where each key is a
    phrase from the input `phrases` list, and the corresponding value is the representative phrase for
    the cluster that the key phrase belongs to.
    """
    # Vectorize the phrases
    vectorizer = TfidfVectorizer(tokenizer=tokenizer_ch)
    X = vectorizer.fit_transform(phrases)
    # similarity_matrix = cosine_similarity(X)
    # Agglomerative clustering
    agg_cluster = AgglomerativeClustering(n_clusters=None, metric='cosine', linkage='average', distance_threshold=1-threshold)
    cluster_labels = agg_cluster.fit_predict(X.toarray())
    # cluster_labels = agg_cluster.fit_predict(similarity_matrix)

    # Group phrases based on clusters
    clustered_phrases = {}
    label_dict = {}
    count = 0
    for label, phrase in zip(cluster_labels, phrases):
        if label not in label_dict.keys():
            label_dict[label] = [phrase]
            clustered_phrases[phrase] = phrase
        else:
            count += 1
            label_dict[label].append(phrase)
            clustered_phrases[phrase] = label_dict[label][0]
    print(count)
    
    return clustered_phrases

def _valid_dict(lc):
    # Check if output from gpt is in valid form.
    def valid_string(s):
        return s.replace('\n', '') != ''
    return isinstance(lc, dict) and set(lc.keys()) == {"A", "关系", "B"} and lc['关系'] in {
        "并列", "递进", "因果", "转折", "让步", "时间顺序", "条件", "举例", "目的", "假设", "逻辑推理"} and \
            valid_string(lc["A"]) and valid_string(lc["B"])

def process_error_lc(data):
    """
    The function `process_error_lc` processes a list of dictionaries by removing invalid entries from
    the 'logicchain' key.
    
    :param data: List of dictionaries, each contains a key 'logicchain' whose value should be list of dictionaries,
                but could be wrong.
    :return: The function `process_error_lc` is returning the modified `data` after processing the logic
    chains within it. The logic chains are checked for validity using the `valid_dict` function, and any
    invalid logic chains are removed from the data. The function then returns the updated data.
    """
    try:
        for p in data:
            if isinstance(p['logicchain'], list):
                for lc in p['logicchain'][:]:
                    if _valid_dict(lc):
                        continue
                    else:
                        p['logicchain'].remove(lc)
            elif _valid_dict(p['logicchain']):
                p['logicchain'] = [p['logicchain']]
            else:
                p['logicchain'] = []
    except:
        for _, p in data.iterrows():
            if isinstance(p['logicchain'], list):
                for lc in p['logicchain'][:]:
                    if _valid_dict(lc):
                        continue
                    else:
                        p['logicchain'].remove(lc)
            elif _valid_dict(p['logicchain']):
                p['logicchain'] = [p['logicchain']]
            else:
                p['logicchain'] = []
    return data

def save_cluster_dict_to_file(api_res_dir=config.json_directory, 
                 cluster_res_dir=config.cluster_dict_dir):
    """
    The function `cluster_file` reads JSON files from a directory, processes the data, extracts phrases
    from logic chains, clusters the phrases, and saves the clustering result dictionary to a JSON file.
    
    :param api_res_dir: The `api_res_dir` parameter in the `cluster_file` function is the directory path
    where the JSON files containing data are located. 
    :param cluster_res_dir: The `cluster_res_dir` parameter in the `cluster_file` function is the
    directory path where the clustering results will be saved in JSON format. 
    """
    phrases = set()
    for file in glob.glob(f'{api_res_dir}/**/*.json', recursive=True):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            f.close()
        process_error_lc(data)
        for item in data:
            # phrases.extend([lc['A'] for lc in item['logicchain']] + [lc['B'] for lc in item['logicchain']])
            for lc in item['logicchain']:
                phrases.add(lc['A'])
                phrases.add(lc['B'])
    clustered = clustering(phrases)
    with open(cluster_res_dir, 'r', encoding='utf-8') as f:
        origin = json.load(f)
    origin['公司公告'] = clustered
    with open(cluster_res_dir, 'w', encoding='utf-8') as f:
        json.dump(origin, f, ensure_ascii=False, indent=4)

if __name__== '__main__':
    sentence_similarity("你好我是开心小女孩", ["你好我是伤心小女孩", "你好我不是个小女孩哈哈哈被我骗了","哈哈哈哈我是开心小男孩"])
    save_cluster_dict_to_file()
    # import re
    # with open('/data/shenyuge/lingyue-data-process/logic_chain/gongsigonggao.txt', 'r', encoding='utf-8') as f:
    #     ss = f.read()
    #     re.sub(r"")
    #     ss = ss.replace('\"', '')
    # # cluster = re.search(r"(').+?('): (').+?(')", ss[:1000])
    # pattern = r"(')(.+?)(': ')(.+?)(')"

    # cluster = re.sub(pattern, lambda m: '\"' + m.group(2) + '\": \"' + m.group(4) + '\"', ss)

    # print("Output string:", cluster)

    # with open('./gpt_result.json', 'r', encoding='utf-8') as f:
    #     data = json.load(f)
    phrases = set()
    for file in glob.glob(f'{config.json_directory}/**/*.json', recursive=True):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            f.close()
        process_error_lc(data)
        for item in data:
            # phrases.extend([lc['A'] for lc in item['logicchain']] + [lc['B'] for lc in item['logicchain']])
            for lc in item['logicchain']:
                phrases.add(lc['A'])
                phrases.add(lc['B'])
#     phrases = [
#     "你好，世界！",
#     "我爱中国菜。",
#     "今天天气很好。",
#     "我们去爬山吧！",
#     "这是我的电话号码。",
#     "你想喝咖啡吗？",
#     "他想喝咖啡吗？",
#     "明天是个新的一天。",
#     "我喜欢唱歌和跳舞。",
#     "中秋节快乐！"
# ]
    clustered = clustering([p for p in phrases if len(p) > 3])
    import json
    with open(config.cluster_dict_dir, 'a', encoding='utf-8') as f:
        json.dump({"A":"B"}, f, ensure_ascii=False, indent=4)
        # origin = json.load(f)
        # json.dump(origin + clustered, f, ensure_ascii=False, indent=4)
    print(clustered)

# similarity_matrix = cosine_similarity(X)

# # DBSCAN clustering
# threshold = 0.8
# dbscan_cluster = DBSCAN(eps=1-threshold, min_samples=2, metric='precomputed')
# cluster_labels = dbscan_cluster.fit_predict(similarity_matrix)

# # Group phrases based on clusters
# clustered_phrases = {}
# for label, phrase in zip(cluster_labels, phrases):
#     if label not in clustered_phrases:
#         clustered_phrases[label] = []
#     clustered_phrases[label].append(phrase)

# # Output clustered phrases
# for label, phrases in clustered_phrases.items():
#     print(f"Cluster {label}: {phrases}")
