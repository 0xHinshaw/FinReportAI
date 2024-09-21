from logic_chain import log_node
from get_logic_chain import construct_entity2path_dict
import json
import glob

keyword_path = r"/data/shenyuge/lingyue-data-process/logic_chain/keywords.json"
data_path = r"/data/shenyuge/lingyue-data-process/logic_chain/multi_process_test"
merged_path = r"/data/shenyuge/lingyue-data-process/logic_chain/merge_result.json"
with open(keyword_path,"r",encoding="utf-8") as file:
    keyword = json.load(file)

lst = []
entity2keyword = {}
keyword2entity = {}
idx2entity = {}
# entity2idx = {}

def sentence_idx_to_entity(merged_path):
    """
    The function `sentence_idx_to_entity` maps sentence index to the keywords the sentence contains.
    
    :param merged_path: path of the file after logic chain merge
    """
    with open(merged_path, 'r', encoding='utf-8') as f:
        merged = json.load(f)
        f.close()
    for m in merged:
        # Get all sentence indices
        for quad in m['quadruples']:
            for si in quad[3]:
                idx2entity[si] = idx2entity.get(si, set()) | {quad[0], quad[2]}
            # entity2idx[m[0]] = entity2idx.get(m[0], set()) & {si}
            # entity2idx[m[2]] = entity2idx.get(m[2], set()) & {si}

def keyword2sentence(data):
    """
    The function `keyword2sentence` processes data to create a mapping from any keyword to the entities from which
    the sentences contain the keyword, updating dictionaries and generating JSON objects.
    
    :param data: It seems like the `data` parameter is being used in the `keyword2sentence` function,
    but the actual content of the `data` parameter is missing in the provided code snippet. Could you
    please provide an example or description of the `data` parameter so that I can assist you further
    with
    """

    # Update dict globally
    global lst
    global entity2keyword, keyword2entity
    global idx2entity

    # Facilitate idx2entity mapping for jumping pad.
    sentence_idx_to_entity(merged_path)
    def maintain_dict(inter, dat):
        si = dat['sentence index']
        for A in idx2entity.get(si, []):
            entity2keyword[A] = entity2keyword.get(A, set()) | {inter}
            keyword2entity[inter] = keyword2entity.get(inter, set()) | {A}
    for large_factor in keyword.keys():
        # Get keywords from different topics
        for small_factor in keyword[large_factor].keys():
            result = {
                "topic" : small_factor,
                "keywords" : []
            }
            for i in keyword[large_factor][small_factor]:
                result["keywords"].append(log_node(keyword=i))
                for dat in data :
                    intersection = set(dat["keywords"]) & set(keyword[large_factor][small_factor])
                    if intersection:
                        result["keywords"][-1].sentenceindex.append(dat['sentence index'])
                        for inter in intersection:
                            maintain_dict(inter, dat)
            for index,node in enumerate(result["keywords"]):
                result["keywords"][index] = node.to_json()
                sentences_index = node.sentenceindex
                sentences = [data[i-1]["keycontent"] for i in sentences_index]

            lst.append(result)

def tag_mapping(data_path, kw2entity_path, entity2kw_path, entity2chain_path):
    """
    The function `tag_mapping` reads JSON data from a specified path, processes the data using
    `keyword2sentence` function, and then saves the results in JSON files at specified paths.
    
    :param data_path: The `data_path` parameter is the file path to the JSON file containing the data
    that needs to be processed
    :param kw2entity_path: The `kw2entity_path` parameter in the `tag_mapping` function is the file path
    where the mapping of keywords to entities will be saved in JSON format
    :param entity2kw_path: The `entity2kw_path` parameter in the `tag_mapping` function is the file path
    where the mapping of entities to keywords will be saved as a JSON file. This file will contain the
    mapping of entities to their corresponding keywords after processing the data
    :param entity2path_path: The `entity2path_path` parameter in the `tag_mapping` function is a file
    path where the function will write the mapping of entities to paths in JSON format. This mapping
    will be constructed by the `construct_entity2path_dict` function
    """
    if data_path.endswith('.json'):
        with open(data_path,"r",encoding="utf-8") as file:
            data = json.load(file)
            file.close()
        keyword2sentence(data)
    else:
        for file in glob.glob('/data/shenyuge/lingyue-data-process/logic_chain/multi_process_test/**/*.json', recursive=True):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                f.close()
            keyword2sentence(data)
    for v in keyword2entity:
        keyword2entity[v] = list(keyword2entity[v])
    for v in entity2keyword:
        entity2keyword[v] = list(entity2keyword[v])
    
    with open(kw2entity_path, 'w', encoding='utf-8') as f:
        json.dump(keyword2entity, f, ensure_ascii=False, indent=4)
    with open(entity2kw_path, 'w', encoding='utf-8') as f:
        json.dump(entity2keyword, f, ensure_ascii=False, indent=4)
    construct_entity2path_dict(entity2chain_path)

if __name__ == '__main__':
    with open(data_path,"r",encoding="utf-8") as file:
        data = json.load(file)
        file.close()
    keyword2sentence(data)
    # for file in glob.glob('/data/shenyuge/lingyue-data-process/logic_chain/multi_process_test/**/*.json', recursive=True):
    #     with open(file, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         f.close()
    #     keyword2sentence(data)
    print(lst)
    for v in keyword2entity:
        keyword2entity[v] = list(keyword2entity[v])
    for v in entity2keyword:
        entity2keyword[v] = list(entity2keyword[v])
    with open("/data/shenyuge/lingyue-data-process/logic_chain/keyword_to_entity.json", 'w', encoding='utf-8') as f:
        json.dump(keyword2entity, f, ensure_ascii=False, indent=4)
