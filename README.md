# Data Processing
## Background
We have different categories of documents, including 公司公告，招股说明书以及研究报告。They are in multiple formats: pdf, word and txt. These formats are, however, difficult for NLP analysis using computer programs The first part of this project thus aims to convert all these documents into json and preserve the structure of the original document. The output of the json will have the format of:
```json
[
    {
        "title": "Paragraph title",
        "content": "Paragraph Contents",
        "keycontent": "Important statements in the beginning of paragraph",
        "subtitle": [{},{},...]
    }
]
```
Each element in the subtitle contains the sub part of current paragraph.

In addition, for the second part, we also wrote function to extract logic chains from all key contents from the documents using chatGPT api, where each logic chain reveals certain relationship between 2 entities.

```json
[
    {
        "sentence index": 1, // unique sentence id starting from 1.
        "paper category": "<Category of the paper this sentence belongs to>",
        "paper title": "Title of the paper this sentence belongs to",
        "date": "Date when the paper was written or published",
        "keycontent": "<Key content>",
        "keywords": [
            "keyword 1",
            "keyword 2" // keywords of interest
        ],
        "logicchain": [
            {
                "A": "Entity A",
                "关系": "Relationship",
                "B": "Entity B"
            }, {}
        ]
    },{}
]
```

There are also methods written to combine similar logic chains, analyze logic chain properties and methods to locate specific logic chains using differnt criterias (keywords, entities, etc.).

## Introduction to Code
We keep separate document for each paper category. Please refer the following for detailed information.

- Part 1: Document to json.

    The scripts for different paper category are different. Each script is put in the directory `doc2json/<paper category>/json` with all readme files in `doc2json/<paper category>` for each paper category.

- Part 2: Extract and analyze logic chain

    All code and documents are located in the `logic_chain/` directory. Please refer to:
    [Logic Chain README.md](./logic_chain/README.md)