# Logic Chain Extraction & Analysis
This project establishs a pipeline to generate logic chains from json files.

## How to Use
With config specified, run `pipeline.py` to extract logic chain from all documents.

## Code Logic
1. Get all key contents from all json files, give unique keys, extract keywords included.
2. Process all key contents to append the prompt for chatGPT to extract logic chains from sentence. Save to json file
3. Use chatGPT to extract logic chain for each sentence and append in json.
4. Group all similar entities and substitude each entity with group representitive. Save mapping relation for further use.
5. Merge logic chain entities useing the cluster dict generated above. Produce quadruples indicate each entity logic relation pair with its corresponding sentence indices.
6. Create mapping relations among keywords, entities and logic chains.

## Mian Function Explaination
All json files for documents processed are stored under doc2json/\<catetory\>/json.

1. ``doc2json.extractkey.process_json_files``: extract all keycontents from json files, stored in the format of: 
    ```json
    {
            "sentence index": 1,
            "paper category": "",
            "paper title": "",
            "date": "",
            "keycontent": "...",
            "keywords": [
                "", ""
            ],
            "logicchain": []
    }
    ```
where sentence index is natural order of the keycontent and is unique for all sentences; paper category is the name of the category of the paper (公司深度报告，投资策略, etc); paper title is paper title; date is the date specified in some paper title, keywords are the keywords among given keyword list that appeare in this sentence.
- `directory`: directory that contains all json files from all category of interest. Must have category/json/ as subdirectories. In this case: ./doc2json.
- `output_path`: file name for result storage.
- `write_to_file`: wheather to write result into output_path or not.
**!Notice: If desired starting sentence index is not 1, must specify `global index` in `extractkey.py` file.**

2. ``gptapi.add_logic_chain_test``: Generate prompt and call ghatgpt api to look for logic chains between entities in every keycontent. Stored in the format of:
    ```json
    // File name: gpt_result.json
    [{
            "sentence index": 5,
            "paper category": "行业深度报告",
            "paper title": "政策强化信心，白酒复苏在途 白酒行业系列报告",
            "date": "",
            "keycontent": "高端白酒批价近期有所回暖，白酒批价有望企稳回升。",
            "keywords": [
                "回暖",
                "批价"
            ],
            "logicchain": [
                {
                    "A": "高端白酒批价",
                    "关系": "时间顺序",
                    "B": "近期有所回暖"
                },
                {
                    "A": "白酒批价",
                    "关系": "假设",
                    "B": "有望企稳"
                }
            ]
        }, {

        }]
    ```
where logicchain contains all triplets that indicates relationship between entities.
- `data`: output from `extractkey.process_json_files` or dictionary with similar structure as above. Could be `None` if `json_directory` is provided.
- `json_directory`: if `data` is not provided, read json contents from this directory and use it as main data.
- `output_path`: file name for result storage.
- `write_to_file`: wheather to write result into output_path or not.

3. `get_logic_chain`: Use clustering algorithm to detect entities that are similar within certain category. Group similar entities together and output json with format:
    ```json
    // File name: merge_result.json
    {   "category": "行业深度报告",
        "quadruples": [
            [
                "1-2月",
                "因果",
                "明显",
                [
                    32
                ]
            ],[
                "3）新品推广不及",
                "并列",
                "6）宏观经济下行风险",
                [
                    15,
                    33
                ]
            ]
        ]
    }
    ```
where the list indicates the sentences share the same logic relations.

4. `save_cluster_dict_to_file`: json directory -> `{"Entity": "Entity group representitive"}`
    reads JSON files from a directory, processes the data, extracts phrases
    from logic chains, clusters the phrases, and saves the clustering result dictionary to a JSON file.
    
    :param api_res_dir: The `api_res_dir` parameter in the `cluster_file` function is the directory path
    where the JSON files containing data are located. 
    :param cluster_res_dir: The `cluster_res_dir` parameter in the `cluster_file` function is the
    directory path where the clustering results will be saved in JSON format. 

5. `produce_quadruples`: json with logic chains -> `[["entity a", "relationship", "entity b", [sentence indices]]]`
    performs mapping based on clustering results, groups the data, and outputs the result as a JSON file containing logic relations and sentences that contains this relation.

6. Create entity, keyword, logic chain mapping.
- entity_to_chain.json: keywords -> all logic chains (each chain is represented by a list).
    ```json
    {
        "多方积极性": [
            [
                "7、风险提示",
                "团购渠道",
                "持续扩张",
                "提高",
                "多方积极性"
            ],
            [
                "产能",
                "持续扩张",
                "提高",
                "多方积极性"
            ],
            [
                "公司净利率",
                "提高",
                "多方积极性"
            ],
            [
                "定向增发股份",
                "提高",
                "多方积极性"
            ],
            [
                "稳固经销渠道",
                "团购渠道",
                "持续扩张",
                "提高",
                "多方积极性"
            ]
        ],
        "预期\n": [
            [
                "7、风险提示",
                "团购渠道",
                "持续扩张",
                "预期\n",
                "行业竞争",
                "加剧"
            ],
            [
                "7、风险提示",
                "团购渠道",
                "持续扩张",
                "预期\n",
                "行业竞争",
                "加剧"
            ],
            [
                "产能",
                "持续扩张",
                "预期\n",
                "行业竞争",
                "加剧"
            ],
            [
                "产能",
                "持续扩张",
                "预期\n",
                "行业竞争",
                "加剧"
            ],
            [
                "稳固经销渠道",
                "团购渠道",
                "持续扩张",
                "预期\n",
                "行业竞争",
                "加剧"
            ],
            [
                "稳固经销渠道",
                "团购渠道",
                "持续扩张",
                "预期\n",
                "行业竞争",
                "加剧"
            ]
        ]
    }
    ```

- entity_to_keyword.json: entity -> all keywords that appeared in the sentences where specified entity is present.
    ```json
    {
        "第二轮": [
            "走势",
            "政府"
        ],
        "第三轮": [
            "走势"
        ],
        "我国白酒行业": [
            "生产",
            "预收账款",
            "三公消费",
            "阶段",
            "收入",
            "发展",
            "社会",
            "管理",
            "国家",
            "竞争",
            "中国",
            "批价",
            "增速",
            "产业",
            "走势",
            "市场",
            "战略",
            "全国",
            "政府"
        ], ...
    }
    ```

- keyword_to_entity.json: keyword -> all entities that are relavent to the keyword.
    ```json
    {
        "走势": [
            "SW食品饮料行业指数整体上涨2.50%",
            "2004年以来",
            "2009年初-2014年底",
            "走势相对弱势",
            "受",
            "近期受我国宏观经济数据、美国CPI以及人民币走势等因素影响",
            "反复、北向资金流出、市场流传的限酒令",
            "食品饮料行业",
            "11月22日-11月26日,SW食品饮料行业指数整体上涨2.50%",
            "跑赢同期沪深300指数约3.11个百分点",
            "关注",
            "市场走势较为低迷",
            "信心、市场情绪、终端需求等指标",
            "第三轮",
            "7月8日",
            "沪深300指数",
            "跑赢沪深300指数",
            "4轮牛市",
            "第一轮",
            "中报业绩",
            "2004年-2008年底",
            "第二轮",
            "跌幅",
            "我国白酒行业",
            "走势相对强势",
            "SW食品饮料行业指数整体下跌3.66%",
            "跑输同期沪深300指数",
            "板块",
            "疫情",
            "因素",
            "扰动因素",
            "2015年初-2018年底",
            "跌幅在所有申万一级行业指数中位居首位",
            "渠道经销商",
            "约4.61个百分点",
            "11月22日-11月26日",
            "食品饮料行业细分板块",
            "SW食品饮料行业",
            "北向资金流出",
            "白酒周期",
            "较大波动",
            "11月15日-11月19日,SW食品饮料行业指数整体上涨3.15%,涨幅在所有申万一级行业指数中位居首位",
            "需求复苏进程",
            "行业"
        ], ...
    }
    ```