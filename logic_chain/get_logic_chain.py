import json, os, glob
import pandas as pd
from cluster import clustering, process_error_lc
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib

def get_graph(df,entity_dict):
    """
    This function creates a graph representation of data from a DataFrame using entity dictionaries.
    
    :param df: The `df` parameter is likely a pandas DataFrame containing information about papers,
    entities, relations, and sentence indices. The function `get_graph` seems to create a graph
    representation based on this DataFrame and an `entity_dict` mapping entities to their corresponding
    IDs. The graph structure includes the paper category and
    :param entity_dict: An entity dictionary that maps entity IDs to their corresponding names
    :return: The function `get_graph` returns a graph object containing the category of the paper and a
    list of quadruples. Each quadruple consists of an entity A, a relation, an entity B, and a list of
    sentence indices.
    """
    graph = {"category":df.iloc[0]["paper category"],"quadruples": []}
    df.groupby(by=["A", "B", "relation"]).apply(lambda x: graph["quadruples"].append(
        [entity_dict[x.iloc[0]["A"]], x.iloc[0]["relation"], entity_dict[x.iloc[0]["B"]], list(x["sentence index"])]))
    return graph

# 数据结构：第一层：list【文章所有段落】，第二层：dict【单个段落内容】，第三层：“logicchain”：list【段落中关键句的逻辑关系】，第四层：dict：三元组
# 第一步：构建df，column = [sentence_index,key_content,key_words,A,B,relation]

def produce_quadruples(json_path, output_path, cluster_res_path, kw2idx_path, write_to_file=True):
    """
    The function `produce_quadruples` reads data from a JSON file, processes it, performs mapping based
    on clustering results, groups the data, and outputs the result as a JSON file containing quadruples.
    
    :param json_path: The `json_path` parameter in the `produce_quadruples` function is the file path to
    the JSON file that contains the data you want to process and convert into quadruples. 
    :param output_path: The `output_path` parameter in the `produce_quadruples` function is the file
    path where the output JSON file will be saved after processing the data. 
    :return: The function `produce_quadruples` returns a list of dictionaries containing the category
    and quadruples for each group in the input data.
    """
    if not json_path.endswith('.json'):
        dfs = []
        for file in glob.glob(f'{json_path}/**/*.json', recursive=True):
            dfs.append(pd.read_json(file).explode("logicchain",ignore_index = True))
        k1 = pd.concat(dfs)
    else:
        k1 = pd.read_json(json_path).explode("logicchain",ignore_index = True)
    k1 = process_error_lc(k1)
    k1["logicchain_A"] = k1["logicchain"].str["A"]
    k1["logicchain_B"] = k1["logicchain"].str["B"]
    k1["logicchain_relation"] = k1["logicchain"].str["关系"]
    k1.dropna(subset=["logicchain_A", "logicchain_B", "logicchain_relation"], inplace = True)
    # print()
    # clustering_result = {}
    with open(cluster_res_path, 'r', encoding='utf-8') as f:
        clustering_result = json.load(f)
        f.close()
    def apply_map(group):
        group_name = group.name
        map_dict = clustering_result.get(group_name, group_name)
        logica = group["logicchain_A"].map(map_dict)
        logicb = group["logicchain_B"].map(map_dict)
        return pd.DataFrame({
            "logicchain_A":logica,
            "logicchain_B":logicb,
            "logicchain_relation":group["logicchain_relation"],
            "sentence index":group["sentence index"],
            "keywords":group['keywords']
        })
    k2 = k1.groupby("paper category").apply(apply_map).reset_index().drop(columns = ["level_1"])

    # get sentence indices with same relationship
    k3 = k2.groupby(['paper category', 'logicchain_A', 'logicchain_B', 'logicchain_relation']).agg(list).reset_index()
    result = {}
    pick_columns = ["logicchain_A","logicchain_relation","logicchain_B","sentence index"]
    for group in k3.groupby("paper category"):
        result[group[0]] = result.get(group[0], []) + group[1][pick_columns].values.tolist()

    # Get keyword to indices mapping
    k4 = k2[['keywords', 'sentence index']].explode('keywords', ignore_index=True)
    k4 = k4.groupby('keywords').agg(set)
    k4.to_json(kw2idx_path, orient='index')

    if write_to_file:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            print("转换成功")
        except Exception as e:
            print("转换失败")
        print("结束")
    else:
        return group[0], group[1][pick_columns].values.tolist()

def get_lengths(quadruples:dict):
    """
    The function `get_lengths` takes a dictionary of quadruples, builds a graph, performs depth-first
    search to find the end-to-end logic chains and returns a list of tuples
    containing the paths and their lengths.
    
    :param quadruples: A dictionary containing quadruples where each quadruple consists of four
    elements: entity_a, relationship, entity_b, and an sentence indices. Output from product_quadruples. 
    The function `get_lengths` takes this dictionary as input and returns a list of tuples where each tuple 
    contains a path and its length.
    :type quadruples: dict
    :return: The `get_lengths` function returns a list of tuples, where each tuple contains a path (list
    of nodes) and the length of that path in the graph represented by the input quadruples.
    """
    graph = {}  # Adjacency list representation of the graph
    is_head = {}
    global_visit = set()
    # Build the graph
    for entity_a, relationship, entity_b, _ in quadruples:
        global_visit.add(entity_a)
        global_visit.add(entity_b)
        if entity_a not in graph:
            graph[entity_a] = []
        graph[entity_a].append((relationship, entity_b))
        # find out all starting nodes.
        is_head[entity_a] = is_head.get(entity_a, True)
        is_head[entity_b] = False

    heads = [h for h in is_head.keys() if is_head[h]]
    # print(heads)
    # path_lengths = []
    def dfs(node, visited):
        if node in global_visit:
            global_visit.remove(node)
        if node not in graph.keys():
            return [([node], 1)]
        visited.add(node)
        path_lengths = []
        for _, neighbor in graph[node]:
            # print(graph[node])
            # print('node {} with neighbors {}'.format(node, neighbor))
            if neighbor not in visited:
                visited.add(neighbor)
                path_lengths.extend([([node]+path_c, 1+i) for path_c, i in dfs(neighbor, visited)])
            else:
                # visited.remove(node)
                return [([node, neighbor], 2)]
        visited.remove(node)
        return path_lengths
    
    # Start DFS from each node to find the longest chain
    # longest_chain_length = 0
    result = []
    for node in heads:
        visited = set()
        result.extend(dfs(node, visited))
    while len(global_visit) > 0:
        node = global_visit.pop()
        # node = 'C'
        global_visit.add(node)
        result.extend(dfs(node, set()))
    return result

def category_lengths(quadurple_path):
    """
    The function `category_lengths` reads data from a JSON file, processes it to get lengths of
    quadruples in different categories, and returns the results along with the paths.
    
    :param quadurple_path: It looks like the code snippet you provided is a Python function that reads
    data from a JSON file specified by the `quadurple_path` parameter, processes the data, and returns a
    dictionary containing category lengths and a list of paths
    :return: The function `category_lengths` returns a tuple containing two elements:
    1. `category_res`: a dictionary where keys are category names and values are NumPy arrays of lengths
    extracted from quadruples in each category.
    2. `paths`: a list of paths extracted from quadruples in all categories.
    """
    with open(quadurple_path, 'r', encoding='utf-8') as f:
        merged = json.load(f)
        f.close()
    category_res = {}
    paths = []
    for category in merged:
        result = get_lengths(category['quadruples'])
        category_res[category['category']] = np.array([r[1] for r in result])
        paths.extend([r[0] for r in result])
    return category_res, paths

def draw_histgrams(category_res:dict):
    """
    The function `draw_histgrams` creates subplots of histograms for logic chain lengths in different
    categories.
    
    :param category_res: A dictionary where the keys represent different categories and the values are
    lists of data points corresponding to each category
    :type category_res: dict
    """
    fig, axis = plt.subplots(2,3,sharex=True)
    axis = axis.flatten()
    for i, category in enumerate(category_res.keys()):
        sns.histplot(category_res[category], ax=axis[i], label=str(category))
        axis[i].set(ylabel="Count")
    fig.tight_layout()
    fig.legend()
    fig.suptitle("Histgrams for Logic Chain Lengths")
    plt.show()
    
def construct_entity2path_dict(output_path):
    # Construct entity -> path dictionary
    _, paths = category_lengths(output_path)
    entity2path = {}
    for path in paths:
        for p in path:
            entity2path[p] = entity2path.get(p, []) + [path]
    return entity2path

if __name__ == '__main__':
    json_path = "/data/shenyuge/lingyue-data-process/logic_chain/gpt_result.json"
    output_path = "/data/shenyuge/lingyue-data-process/logic_chain/merge_result.json"
    produce_quadruples(json_path, output_path)
    category_res, paths = category_lengths(output_path)
    # print(category_res)
    # draw_histgrams(category_res)
    entity2path = construct_entity2path_dict(paths)
    print(len([ep for ep in entity2path if len(entity2path[ep])>1]))
    