import glob
import json

with open('/data/shenyuge/lingyue-data-process/logic_chain/keywords.json', 'r') as f:
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
    return sentence_keywords

def add_keywords(data):
    if 'sentence' in data:
        data['keywords'] = get_sentence_keywords(data['sentence'])
    if 'subentity' in data:
        for sub in data['subentity']:
            add_keywords(sub)
            if 'keywords' in data:
                # data['keywords'] = set(data['keywords'])
                data['keywords'] = set(data['keywords']).union(sub.get('keywords', set()))
            else:
                data['keywords'] = sub.get('keywords', set())

def set_to_list(entity):
    if 'keywords' in entity:
        entity['keywords'] = list(entity['keywords'])
    if 'subentity' in entity:
        for sub in entity['subentity']:
            set_to_list(sub)

for file in glob.glob('/data/shenyuge/lingyue-data-process/白酒点评报告/*.json'):
    struct = json.load(open(file, 'r'))
    f.close()
    for para in struct:
        for entity in para['entities']:
            add_keywords(entity)
    for para in struct:
        for entity in para['entities']:
            set_to_list(entity)
    json.dump(struct, open(file[:-5] + '_kw.json', 'w'), ensure_ascii=False, indent=4)