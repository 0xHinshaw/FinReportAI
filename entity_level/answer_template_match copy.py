import os
import json
import re
import logging
import difflib

# Set up logging
def setup_logging(log_file):
    # Setup logging configuration
    logging.basicConfig(level=logging.DEBUG,  # Change to DEBUG to get more information
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(log_file, 'w', 'utf-8'),
                                  logging.StreamHandler()])

def split_text_template(template,text):
    template =  re.sub(r"\s","",template)
    text = re.sub(r"\s","",text)
    template_sentences = re.split(r'([，,。;；])', template)
    text_sentences = re.split(r'([，,。;；])', text)
    template_sentences = [i.strip() for i in template_sentences if not re.fullmatch(r"[，,。;；]+",i) and i != ""]
    text_sentences = [i.strip() for i in text_sentences if not re.fullmatch(r"[，,。;；]+",i) and i != ""]
    if len(text_sentences) == len(template_sentences):
        return {"text_sentences":text_sentences,"template_sentences":template_sentences}
    else:
        return None

# def find_matching_part(sentence, template):
#     # Define the patterns to match the placeholders in the template
#     patterns = {
#         r"公司": "<公司>",
#         r"\d{4}年?": "<年份>",
#         r"\d+\.\d+亿元|\d+亿元": "<精确数据>",
#         r"同比增长": "<定性表述>",
#         r"\d+(?:\.\d+)?%": "<百分比>"
#     }

#     # Convert sentence to template-like format
#     converted_sentence = sentence

#     for pattern, replacement in patterns.items():
#         converted_sentence = re.sub(pattern, replacement, converted_sentence)
#     print("sentence:", converted_sentence, "template sentence:", template)

#     match = difflib.SequenceMatcher(None, converted_sentence, template).find_longest_match()

#     return converted_sentence[match.a:match.a + match.size]


def match_entities_sentence_template(entities,template_sentences,template_dir,text_template_dict):
    if isinstance(entities,dict):
        if 'sentence' not in entities.keys():
            raise KeyError('sentence not in entities keys')
        if entities["subentity"] != []:
            match_entities_sentence_template(entities["subentity"],template_sentences,template_dir,text_template_dict)
        entity = entities
        # Access the "sentence" key for each entity
        sentence = re.sub(r"\s","",entity['sentence']) # Strip to remove leading/trailing whitespace  
        sub_sentence_list = re.split(r'([，,。;；])', sentence)
        all_elements_list =  [i for i in sub_sentence_list if  i != ""]
        need_search_sentences_list =  [i for i in sub_sentence_list if not re.fullmatch(r"[，,。;；]+",i) and i != ""]
        select_templates = []
        for need_search_sentence in need_search_sentences_list:
            try:
                match_sentence= difflib.get_close_matches(need_search_sentence,text_template_dict["text_sentences"], n=3, cutoff=0.6)[0]
                select_template_index = text_template_dict["text_sentences"].index(match_sentence)
                select_templates.append(text_template_dict["template_sentences"][select_template_index])
            except:
                select_templates.append(need_search_sentence)
            
        elements_start_index = all_elements_list.index(need_search_sentences_list[0])
        elements_end_index = all_elements_list.index(need_search_sentences_list[-1],elements_start_index)
        select_elements = all_elements_list[elements_start_index:elements_end_index+1]
        select_elements = [i for i in select_elements if re.fullmatch(r"[，,。;；]+",i)]
        match_template = select_templates[0]
        for index,i in enumerate(select_elements):
            match_template += i+select_templates[index+1]
        log_message = (f"Sentence: {sentence}\n"
                    f"Matching Template Part: { match_template}\n")
        entity["sentence_template"] =  match_template
        logging.info(log_message)
    elif isinstance(entities,list):
        for entity in entities[:]:
            try:
                match_entities_sentence_template(entity,template_sentences,template_dir,text_template_dict)
            except KeyError:
                entities.remove(entity)

def process_files(data_dir, template_dir):
    
    # List all files in the data directory
    for data_filename in os.listdir(data_dir):
        if data_filename.endswith('_kw.json'):
            # Construct full file path
            data_file_path = os.path.join(data_dir, data_filename)
            
            logging.debug(f"Processing data file: {data_file_path}")
            
            try:
                with open(data_file_path, 'r', encoding='utf-8') as data_file:
                    data_content = json.load(data_file)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logging.error(f"Error reading JSON file {data_file_path}: {e}")
                continue  
            
            # Find the corresponding template file in the template directory
            template_filename = data_filename.replace('_kw', '')
            template_file_path = os.path.join(template_dir, template_filename)
            # sentenses = tree_traversal_extract_sentences(data_content)
            
            if os.path.exists(template_file_path):
                logging.debug(f"Template file found: {template_file_path}")
                try:
                    # Read the content of the template file
                    with open(template_file_path, 'r', encoding='utf-8') as template_file:
                        template_content = json.load(template_file)
                        template = template_content.get('processed', '')
                        text = template_content.get('original_text', '')
                        # logging.debug(f"Template content loaded: {template}")
                    text_template_dict = split_text_template(template,text)
                    if text_template_dict is not None:    # TODO； check if here is the error 
                        pass
                    else:
                        logging.error(f"{template_file_path}模板数据有问题，需要重新生成原文模板。")
                        continue
                    # Process each sentence and find the matching template part
                    # log the matching part
                    template_sentences = template.split("。")
                    template_sentences = [template_sentence.strip() for template_sentence in template_sentences if template_sentence.strip()]
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    logging.error(f"Error reading template file {template_file_path}: {e}")
            else:
                logging.warning(f"Template file for {template_filename} not found.")
            for item in data_content[:]:
                # Access the "entities" key and loop through each entity
                for entity in item['entities'][:]:
                    try:
                        match_entities_sentence_template(entity,template_sentences,template_dir,text_template_dict )
                    except KeyError:
                        item['entities'].remove(entity)
            with open(data_file_path,"w",encoding="utf-8") as file:
                json.dump(data_content, file, ensure_ascii=False, indent=4)
                    

# Define the directories
data_directory = '/data/shenyuge/lingyue-data-process/白酒点评报告'
template_directory = '/data/shenyuge/lingyue-data-process/白酒点评报告/text_template'

# Setup logging
setup_logging('/data/shenyuge/lingyue-data-process/entity_level/logs/answer_template_match2.log')

# Process the files
process_files(data_directory, template_directory)


# data_directory = '/home/shenyuge/lingyue-data-process/白酒点评报告'