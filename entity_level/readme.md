# 实体提取流程&代码

1. **实体层及和问题引导.ipynb**: Extract all entities from each paragraph of the document. Specify the sentence and question related to the entity. Then formulate a tree structure of all entities.
2. **模板生成.py**: Generate a template for each paragraph in document with GPT 4o.
3. **点评报告-问题列表模板.py**: Given question list, for each paragraph, find the list of question that could be answered within that paragraph.


# 实体层及和问题引导

This script processes a `.docx` file to extract paragraphs, identify entities within those paragraphs, and generate questions and levels related to those entities using the GPT-4 model. The results are saved in a JSON file.

## Dependencies

The script requires the following Python libraries:
- `requests`
- `json`
- `ast`
- `os`
- `paragraph` (specifically, `extract_paragraphs_from_docx` function)

## Functions

### 1. `get_response_gpt4(content)`

Fetches a response from the GPT-4 model for a given input.

**Arguments:**
- `content` (str): The input content/question for the GPT-4 model.

**Returns:**
- `str`: The response from the GPT-4 model.

**Example:**
```python
response = get_response_gpt4("What is the capital of France?")
print(response)  # Should print the GPT-4's response
```

### 2. `get_entity_ques_list(paragraphs)`

Extracts entities, related sentences, and questions from a given paragraph using the GPT-4 model.

**Arguments:**
- `paragraphs` (str): The input paragraph.
    - previous prompt: 请根据我给出的上述段落，提取出其中的实体（识别和分类文本中的组织、个人、行业、地点、货币、交易、证券、法律等关键信息）和提到实体的相关语句，实体不要提取具体数值,实体的提取尽量细致一些，实体尽可能多一些，假设只知道段落主题而并不知道段落内容，而是通过问题引导来完成段落的写作，给出得到相关语句可能会问到的问题，使得问题能够引导出相关句子，问题不要包含具体时间，年份，问题不应出现倾向和定性说法，问题可以包含具体地点和行业，主要体现作者的思路和逻辑，并以json的形式返回[{{{{{{'entity': '','sentence': '', 'question': ''}}}}, {{{{'entity': '','sentence': '', 'question': ''}}}}}}],除了这个json信息其余的不要返回。
    - new prompt with graph RAG: 

    > -Goal- 
    Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and format a relationship tree to indicate connections among entities in paragraph.

    > -Steps-
    > 1. Identify all entities. For each identified entity, extract the following information:
    > - entity_name: Name of the entity, capitalized
    > - entity_type: One of the following types: [行业，板块，公司名称，品牌，产品，时间点，事件，市场表现，报表数据，营收情况，增长下降百分比，投资策略，风险评估]
    > - entity_description: 段落中与此entity相关的语句
    > - entity question: A question in Chinese to which entity_description can answer.
    > Format each entity as [{"entity":<entity_name>, > "entity_type":<entity_type>, "sentence": <entity_description>, "question": <entity_question>}]

    > 2. From the entities identified in step 1, identify levels of all entities. High level entities are entities that are more conclusive, while low level entities are more detailed.
    For each high level entity, find subentites from lower level entities that belongs to (included in) that entity.
    Format all entities (in Chinese) in tree format {"entitity": <entitity A>, "subentities": [{"entitity": <entity B>, "subentities":[...]}, {"entitity": <entity C>, "subentities":[...]}, ...]}

    > 3. Append all entries from step 1 into entity tree in step 2 and return output in json format. 
    [{"entitity": <entitity A>, "entity_type":<entity_type>, "sentence": <entity_description>, "question": <entity_question>}, "subentities": [{"entitity": <entity B>, "entity_type":<entity_type>, "sentence": <entity_description>, "question": <entity_question>}, "subentities":[...]}, {"entitity": <entity C>, "entity_type":<entity_type>, "sentence": <entity_description>, "question": <entity_question>}, "subentities":[...]}, ...]}, {...}]

    > Output only json format for step 3 of the answer.
    > ##################################
    > - texts: 
    > {texts}
        

**Returns:**
- `list`: A list of dictionaries containing entities, related sentences, and questions.

**Example:**
```python
entities_questions = get_entity_ques_list("This is a sample paragraph.")
print(entities_questions)  # Should print the extracted entities and questions
```

### 3. `update_questions(data_dict, question_list)`

Updates the entity hierarchy with corresponding questions.

**Arguments:**
- `data_dict` (dict): The entity hierarchy data.
- `question_list` (list): A list of dictionaries containing entities and corresponding questions.

**Example:**
```python
data_dict = {"entity": "Company", "subentity": []}
question_list = [{"entity": "Company", "sentence": "This is a company.", "question": "What is a company?"}]
update_questions(data_dict, question_list)
print(data_dict)  # Should print the updated data_dict with questions
```

### 4. `get_entity_list_from_docx(input_file, output_json=None)`

Extracts entities and generates questions from a `.docx` file, saving the results in a JSON file.

**Arguments:**
- `input_file` (str): The path to the input `.docx` file.
- `output_json` (str, optional): The path to the output JSON file. If not provided, the output file will be saved in the same directory as the input file with a `.json` extension.

**Example:**
```python
get_entity_list_from_docx("/path/to/input.docx", "/path/to/output.json")
```

## Workflow

1. **Extract Paragraphs from `.docx` File:**
   - The `extract_paragraphs_from_docx` function is used to extract paragraphs from the input `.docx` file.

2. **Read Extracted Text:**
   - The extracted text is read from a `.txt` file.

3. **Process Each Paragraph:**
   - For each paragraph, the script attempts to extract entities and generate questions using the `get_entity_ques_list` function.
   - The extracted entities are structured into a hierarchical format using the GPT-4 model.
   - The `update_questions` function is used to integrate the questions into the entity hierarchy.

4. **Save Results:**
   - The results are saved in a JSON file. If the `output_json` argument is not provided, the output file is saved with the same name as the input file but with a `.json` extension.

## Example Usage

To run the script and process a `.docx` file:
```python
get_entity_list_from_docx("/home/shenyuge/lingyue-data-process/entity_level/（可公开）次高端白酒行业深度报告：势能向上，成长可期.docx")
```

## Error Handling

The script includes error handling to retry processing each paragraph up to three times in case of an exception. It logs the errors and continues processing the remaining paragraphs.

## Notes

- Ensure that the `extract_paragraphs_from_docx` function from the `paragraph` module is correctly implemented and available.
- The API key used in the `get_response_gpt4` function should be kept secure and not hard-coded in the script for production use.

This documentation should help in understanding the functionality and usage of the script.



# 模板生成

This script processes `.docx` files to extract text, identify entities, and generate neutral templates using the GPT-4 model. The results are saved in JSON files, and the script includes logging and error handling mechanisms.

## Dependencies

The script requires the following Python libraries:
- `requests`
- `json`
- `ast`
- `os`
- `re`
- `docx2txt`
- `tqdm`
- `logging`
- `datetime`
- `concurrent.futures`
- `sys`

## Functions

### 1. `setup_logging(log_file)`

Sets up the logging configuration.

**Arguments:**
- `log_file` (str): The path to the log file.

**Example:**
```python
setup_logging('/path/to/logfile.log')
```

### 2. `get_response_gpt4(content)`

Fetches a response from the GPT-4 model for a given input.

**Arguments:**
- `content` (str): The input content/question for the GPT-4 model.
    - previous prompt: 改变上文，涉及到举例时需将所有例子替换为<例子>，将其中的一些定性表述改为中性表达，如：'增长'，'下降','上升'，’提升‘等等改为'<定性表述>'，评价好坏的描述（良好，较好，不及，稳定，较差等等）改为<评价描述>, 提到褒贬的动词（提升，减少，振兴等）改为<改变>。替换后的文本需要完全看不出褒贬，让模板能够适用各种情况，请注意一些固定搭配和成语，请简化具体操作描述，将其改为更抽象的表达，如将具体信息mask为<具体操作>，将具体的经营模式，销售模式，采购模式，等模式内容替换为类似<经营模式的简短描述><销售模式的简短描述><采购模式的简短描述>等，注意替换带引号的整体内容只用一个标签概括。使得上述段落可以应用到其余公司或行业。将其中的、日期、年份、季度、月份、组织、项目、数量、个人、公司、产品、地点、时间、数值、货币、交易、证券、法律等具体信息，替换为<公司><产品><项目><数量><年份><季度><日期><精确数据><预测数据>这样的抽象标签。
    - current prompt with graphRAG:
        > - Goal: 你是一个金融分析师正在使用chatgpt创造业绩综述报告。Given a document paragraph, write a question prompt to let chatgpt output the paragraph similar to the input paragraph containing all entities extracted.

        > -Steps-
        > 1. Identify all entities. Append time information to each entity point if available. For each identified entity, extract the following information:
        > - entity_name: Name of the entity, capitalized
        > - entity_type: One of the following types: [行业，板块，公司名称，时间点，价格，品牌，产品，事件，市场表现，报表数据，营收情况，同比，环比，投资策略，风险评估]
        > - entity_value: the value/string for the specific entity.
        Export all entities in json format.
        > - year: 
        > - quarter:
        > - year-on-year: comparison value if applicable
        > - month-to-month: comparison value if applicable

        > 2. Suppose you have a structured json dataset <data> for all entities extracted above. Format a single question prompt such that chatgpt can use the prompt and the dataset to create the original paragraph. The prompt should: 
            - contain all entities extract from step 1;
            - state the background for the writing and articulate requirements;
            - use "{data}" string to substitude the entire dataset.
            - create concise analysis (200-300 words) for the data.

        > Output the question prompt string in Chinese from step 2 only.

        > #################
       >  texts:
        > （1）伊利股份
        > 公司2022Q4业绩亮眼，2023年开局稳健。单季度看，由于今年春节时间较早，在疫情全面放开后，去年12月起开始逐步备货，公司2022Q4业绩亮眼。2022Q4，公司实现营业收入293.10亿元，同比增长14.54%；实现归母净利润13.70亿元，同比增长80.10%。今年春节期间，送礼、走亲访友等消费场景逐步复苏回暖，公司礼赠等奶盒动销较好，今年一季度开局稳健。2023Q1，公司实现营业总收入334.41亿元，同比增长7.71%；实现归母净利润36.15亿元，同比增长2.73%。
        公司奶粉及奶制品业务增速亮眼，液态奶收入基于2022Q1高基数小幅下滑。公司在夯实传统液态奶的同时，近几年积极致力于多元化的业务布局，目前成效逐步显现。其中，奶粉及奶制品、冷饮产品业务均实现较快增长。2022年，公司液态奶/奶粉及奶制品/冷饮产品分别实现营业收入849.26亿元/262.60亿元/95.67亿元，同比分别增长0.02%/62.0%/33.6%。2023Q1，公司液态奶/奶粉及奶制品/冷饮产品分别实现营业收入217.41/74.43/37.94亿，同比分别下降2.6%/增长37.9%/增长35.7%。公司今年一季度液态奶增速下滑主要系春节提前备货，叠加去年同期高基数所致；奶粉与奶制品增速较快受益于澳优并表，而冷饮产品在推新与渠道扩展的推动下，业绩亦实现较快增长。


**Returns:**
- `str`: The response from the GPT-4 model, or `None` if an error occurs.

**Example:**
```python
response = get_response_gpt4("What is the capital of France?")
print(response)  # Should print the GPT-4's response
```

### 3. `merge_short_strings(string_list)`

Merges short strings in a list into longer strings to ensure each string has a minimum length.

**Arguments:**
- `string_list` (list): A list of strings to be merged.

**Returns:**
- `list`: A list of merged strings.

**Example:**
```python
merged_strings = merge_short_strings(["short1", "short2", "long enough"])
print(merged_strings)  # Should print the merged list of strings
```

### 4. `main_processing_function()`

Processes the log file to identify paragraphs that need to be reprocessed, generates neutral templates using GPT-4, and saves the results in JSON files.

**Arguments:**
- None

**Example:**
```python
main_processing_function()
```

## Workflow

1. **Setup Logging:**
   - The `setup_logging` function is used to configure logging.

2. **Read and Process Log File:**
   - The script reads a log file to identify paragraphs that need to be reprocessed.

3. **Extract Text from `.docx` Files:**
   - The script uses `docx2txt` to extract text from `.docx` files.

4. **Generate Neutral Templates:**
   - For each paragraph, the script generates a neutral template using the `get_response_gpt4` function.
   - The script ensures that each paragraph is processed up to a maximum of five attempts in case of errors.

5. **Save Results:**
   - The results are saved in JSON files.

## Example Usage

To run the script and process the `.docx` files:
```python
setup_logging('/path/to/logfile.log')
main_processing_function()
```

## Error Handling

The script includes error handling to retry processing each paragraph up to five times in case of an exception. It logs the errors and continues processing the remaining paragraphs.

# 报告-问题 模板

This script processes JSON files containing original and processed text to identify which questions can be answered by the processed text using the GPT-4 model. The results are saved in JSON files, and the script includes logging and error handling mechanisms.

## Dependencies

The script requires the following Python libraries:
- `requests`
- `json`
- `ast`
- `os`
- `re`
- `docx2txt`
- `tqdm`
- `logging`
- `datetime`
- `concurrent.futures`

## Functions

### 1. `get_response_gpt4(content)`

Fetches a response from the GPT-4 model for a given input.

**Arguments:**
- `content` (str): The input content/question for the GPT-4 model.
    - prompt: "原文：\n"+ text + "\n 模板：\n"+sub_template_list[text_index]+ f"\n问题列表：{questions_list}"+""" \n 上述是原文，模板和问题列表，原文和模板中的Q加数字代表的是某一季度，分析上面的的问题列表，哪些问题的能够在模板中找到答案，如果模板中的句子能够回答问题，请按照{ "questions":[[question, template_part], [question, template_part]]}的格式返回，格式中question代表能回答的具体问题，template_part则是上述模板中的截取出来可以回答问题的句子模板。
                    注意：
                    1、原文内容回答不了的问题不要加进去，如果该段落没有回答任何问题，则返回{"questions":[]}。
                    2、template_part应该截取到答案句，不要输出整个模板，不要截取的太长。
                    3、每个question对应一个template_part，template_part中的<>不要替换为具体数据。
                    4、不要改变我提供的json格式，
                    5、不要改变问题列表中的问题
                    6、只返回json数据就可以了,不要输出其他内容。以确保你输出的内容我可以直接读取"

**Returns:**
- `str`: The response from the GPT-4 model.

**Example:**
```python
response = get_response_gpt4("What is the capital of France?")
print(response)  # Should print the GPT-4's response
```

### 2. `merge_short_strings(string_list)`

Merges short strings in a list into longer strings to ensure each string has a minimum length.

**Arguments:**
- `string_list` (list): A list of strings to be merged.

**Returns:**
- `list`: A list of merged strings.

**Example:**
```python
merged_strings = merge_short_strings(["short1", "short2", "long enough"])
print(merged_strings)  # Should print the merged list of strings
```

### 3. `process_json(file_name)`

Processes a JSON file to identify which questions can be answered by the processed text using the GPT-4 model. The results are saved in JSON files.

**Arguments:**
- `file_name` (str): The name of the JSON file to be processed.

**Example:**
```python
process_json('example.json')
```

## Workflow

1. **Setup Logging:**
   - The script includes commented-out logging setup. Uncomment and configure logging as needed.

2. **Fetch GPT-4 Response:**
   - The `get_response_gpt4` function sends a request to the GPT-4 API and returns the model's response.

3. **Merge Short Strings:**
   - The `merge_short_strings` function combines short strings into longer ones to ensure each string has a minimum length.

4. **Process JSON File:**
   - The `process_json` function reads a JSON file, extracts text, and generates questions and answers using the GPT-4 model. It ensures that each paragraph is processed up to a maximum of five attempts in case of errors.
   - The results are saved in a new JSON file.

## Example Usage

To run the script and process a specific JSON file:
```python
if __name__ == "__main__":
    result = process_json('（可公开）食品饮料行业双周报（20240520-20240602）：政策优化，关注预期改善.json')
```

## Error Handling

The script includes error handling to retry processing each paragraph up to five times in case of an exception. It logs the errors and continues processing the remaining paragraphs.

## Notes

- Ensure that the API key used in the `get_response_gpt4` function is kept secure and not hard-coded in the script for production use.
- Adjust the logging configuration as needed by uncommenting and configuring the logging setup section.

This documentation should help in understanding the functionality and usage of the script.


# Paragraph Topic
For extracting topic for all paragraphs, use following prompt:
-Goal-
Given a paragraph，select the most important and representative topic from the paragraph, make sure each topic encapsulates the main content and the length of the topic is no more than 10 characters. 
-Steps-
1. Read the text. If you find any of the following phrases:[投资要点, 业绩综述, 行业业绩综述, 白酒板块业绩表现, 啤酒板块业绩表现, 调味品板块业绩表现, 乳品板块业绩表现, 零食板块业绩表现, 投资策略 , 风险提示], select and output the matching phrases.
2. If the text does not contain any of the phrases mentioned above, select the most important and representative topic from the paragraph. Ensure each topic encapsulates the main content and is no more than 10 characters long.
3. Output the phrases in the following format: [phrase, phrase, phrase, phrase

##############################
-Examples-
##############################
Example 1:

Text:
投资要点：
食品饮料行业2023年业绩稳健增长，2024Q1归母净利润实现双位数增长。2023年SW食品饮料行业实现营业总收入10342.3亿元，同比增长6.9%；实现归母净利润2058.9亿元，同比增长16.9%。今年春节，居民走亲访友、外出旅游等意愿高涨，礼赠、宴席等消费场景向好，一定程度上带动了终端需求增加，行业2024Q1营收与归母净利润同比均实现了不同程度的增长。2024Q1，食品饮料行业实现营业总收入3129.1亿元，同比增长6.7%；实现归母净利润812.7亿元，同比增长16.0%。

投资策略：维持对行业的超配评级。白酒板块：从白酒企业公布的业绩数据来看，内部表现呈现分化。高端白酒确定性高，业绩稳健增长。次高端白酒商务宴席弱复苏，业绩表现分化。区域白酒受送礼、送亲访友、宴席等因素催化，业绩表现较好。二季度是白酒的消费淡季，酒企以控货挺价为主，后续需持续跟踪动销、库存等指标，长期需要进一步结合经济复苏进度等情况进行判断。标的方面，建议关注确定性强的高端白酒贵州茅台（600519）、五粮液（000858）与泸州老窖（000568）；次高端与区域白酒可以关注动销和库存表现较好的山西汾酒（600809）、古井贡酒（000596）等。大众品板块：大众品板块业绩表现延续分化态势。业绩具备确定性、存在边际改善预期、高性价比的板块可重点关注。啤酒板块关注旺季低基数下销量或回暖、成本下行等边际改善机会。调味品板块今年一季度业绩有所改善，可以重点关注餐饮消费力修复、成本等边际改善预期。乳品龙头动销良性，生鲜乳成本压力趋缓，需持续关注后续需求。零食公司今年春节动销超预期，多数龙头一季度业绩表现亮眼，板块具备一定景气性，持续关注改革红利。标的方面，可重点关注青岛啤酒（600600）、海天味业（603288）、伊利股份（600887）、三只松鼠（300783）等。

风险提示：原材料价格波动，产品提价不及预期，渠道开展不及预期，行业竞争加剧风险，食品安全风险等。
########################
Output:
[‘投资要点’,'行业业绩综述’,'投资策略','风险提示']

##############################
Example 2:

Text:
食品饮料行业2023年业绩稳健增长，2024Q1归母净利润实现双位数增长。2023年SW食品饮料行业实现营业总收入10342.3亿元，同比增长6.9%；实现归母净利润2058.9亿元，同比增长16.9%。今年春节，居民走亲访友、外出旅游等意愿高涨，礼赠、宴席等消费场景向好，一定程度上带动了终端需求增加，行业2024Q1营收与归母净利润同比均实现了不同程度的增长。2024Q1，食品饮料行业实现营业总收入3129.1亿元，同比增长6.7%；实现归母净利润812.7亿元，同比增长16.0%。
########################
Output:
['业绩综述']

##############################
Example 3:

Text:
1.食品饮料行业2023年与2024Q1业绩概述
1.1行业2023年业绩稳健增长，2024Q1归母净利润增速快于营收增速
食品饮料行业2023年业绩稳健增长，Q4营收增速环比回落。2023年SW食品饮料行业（申万食品饮料行业剔除B股，共125家样本公司，下同）实现营业总收入10342.3亿元，同比增长6.9%，增速同比下降0.7个百分点；实现归母净利润2058.9亿元，同比增长16.9%，增速同比增加4.5个百分点。单季度看，由于2024年春节较晚，备货错期使行业2023年四季度营收增速环比回落。2023Q4，食品饮料行业实现营业总收入2440.9亿元，同比增长1.9%，季环比下降4.8个百分点。利润端，受益于部分板块原材料成本下降、费用结构优化、一次性收益增加等因素影响，2023Q4食品饮料行业归母净利润增速快于营收增速。2023Q4，食品饮料行业实现归母净利润435.2亿元，同比增长23.6%，季环比增加7.5个百分点。
2024Q1食品饮料行业营业总收入实现个位数增长，归母净利润实现双位数增长。今年春节，居民走亲访友、外出旅游等意愿高涨，礼赠、宴席等消费场景向好，一定程度上带动了终端需求增加，行业2024Q1营收与归母净利润同比均实现了不同程度的增长。2024Q1，食品饮料行业实现营业总收入3129.1亿元，同比增长6.7%。在成本费用优化等背景下，行业归母净利润增速整体快于营收增速。2024Q1，食品饮料行业实现归母净利润812.7亿元，同比增长16.0%。
########################
Output:
['行业业绩概述']


##############################
Example 4:

Text:
2.白酒板块：业绩表现分化，高端白酒确定性强
2.1白酒板块2023年稳健收官，2024Q1业绩实现双位数增长
白酒板块2023年稳健收官。2023年，白酒板块（SW白酒剔除古井贡酒B，共20家样本公司，下同）实现营业总收入4121.1亿元，同比增长15.6%；实现归母净利润1551.5亿元，同比增长18.9%，全年稳健收官。分季度看，考虑到今年春节较晚，部分酒企去年四季度控货消化库存，叠加部分公司改革持续，2023Q4白酒营收季环比放缓。2023Q4，白酒板块实现营业总收入1009.5亿元，同比增长14.9%，增速季环比下降0.3个百分点。在费用优化下，2023Q4白酒板块实现归母净利润361.7亿元，同比增长18.7%，增速季环比增加0.8个百分点。
2024Q1白酒板块业绩实现双位数增长。作为疫后首个完全不受疫情影响的春节，居民返乡、出行等意愿高涨。在宴席等消费场景带动下，春节期间白酒动销整体良性，带动2024年一季度白酒板块业绩实现了双位数增长。2024Q1，白酒板块实现营业总收入1508.7亿元，同比增长14.7%；实现归母净利润619.9亿元，同比增长15.7%。
########################
Output:
['白酒板块业绩表现']
