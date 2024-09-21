from datetime import datetime
import os

class Config:
    def __init__(self):
        parent_path = os.path.dirname(__file__)
        self.parent_path = parent_path
        # self.doc_json_directory = self.parent_path + '/doc2json'
        self.json_directory = self.parent_path + '/multi_process_test'
        self.prompt_directory = self.parent_path + '/prompts.json'
        self.gpt_output_dir = self.parent_path + '/multi_process_test'
        self.cluster_dict_dir= self.parent_path + '/clustering_result.json'
        self.merge_res_dir = self.parent_path + '/merge_result.json'
        self.kw2entity_path = self.parent_path + '/keyword_to_entity.json'
        self.kw2idx_path = self.parent_path + '/keyword_to_index.json'
        self.entity2kw_path = self.parent_path + '/entity_to_keyword.json'
        self.entity2chain_path = self.parent_path + '/entity_to_chain.json'
        self.keywords_path = self.parent_path + '/keywords.json'
        self.total_data_path = self.parent_path + '/total_data.pickle'

        START_TIME = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.log_file_path = self.parent_path + f'/logs/log_file_for_{START_TIME}.log'
        self.error_file_path = self.parent_path + '/error_file'

        self.api_key = 'sk-QeiIJwcjqnhybuSeBbC0F27eEc0b42529a4410194b362bBb'