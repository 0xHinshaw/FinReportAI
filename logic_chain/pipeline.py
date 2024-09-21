from extractkey import process_json_files
from NER import save_prompt
from gptapi import add_logic_chain
from cluster import save_cluster_dict_to_file
from get_logic_chain import produce_quadruples
from tagging import tag_mapping
import glob, json, tqdm
from config import Config

# doc_json_directory = '/data/shenyuge/lingyue-data-process/doc2json'
# json_directory = '/data/shenyuge/lingyue-data-process/doc2json/output.json'
# prompt_directory = '/data/shenyuge/lingyue-data-process/logic_chain/prompts.json'
# gpt_output_dir = '/data/shenyuge/lingyue-data-process/logic_chain/multi_process_test'
# DATE_TIME = '2024-04-07 12:56'
# cluster_dict_dir='/data/shenyuge/lingyue-data-process/logic_chain/clustering_result.json'
# merge_res_dir = "/data/shenyuge/lingyue-data-process/logic_chain/merge_result.json"
# kw2entity_path = '/data/shenyuge/lingyue-data-process/logic_chain/keyword_to_entity.json'
# entity2kw_path = '/data/shenyuge/lingyue-data-process/logic_chain/entity_to_keyword.json'
# entity2chain_path = '/data/shenyuge/lingyue-data-process/logic_chain/entity_to_chain.json'

if __name__ == '__main__':
    config = Config()
    # Get all key contents from all json files, give unique keys, extract keywords included.
    # process_json_files(config.doc_json_directory, config.json_directory, write_to_file=True)
    
    # Process all key contents to append the prompt for chatGPT to extract logic chains from sentence. Save to json file
    # save_prompt(config.json_directory, config.prompt_directory)

    # Use chatGPT to extract logic chain for each sentence and append in json.
    # add_logic_chain(config.prompt_directory, config.gpt_output_dir)

    # Group all similar entities and substitude each entity with group representitive. Save mapping relation for further use.
    # save_cluster_dict_to_file(config.gpt_output_dir, config.cluster_dict_dir)

    # Merge logic chain entities useing the cluster dict generated above. 
    # Produce quadruples indicate each entity logic relation pair with its corresponding sentence indices.
    produce_quadruples(config.gpt_output_dir, config.merge_res_dir, config.cluster_dict_dir, config.kw2idx_path, False)
    
    # Create mapping relations among keywords, entities and logic chains.
    tag_mapping(config.merge_res_dir, config.kw2entity_path, config.entity2kw_path, config.entity2chain_path)