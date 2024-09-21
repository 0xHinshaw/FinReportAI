class log_node():
    def __init__(self, keyword="", sentenceindex=None, similar_index=None, merged_logic_chain=None):
        self.keyword = keyword
        self.sentenceindex = sentenceindex if sentenceindex is not None else []
        self.similar_index = similar_index if similar_index is not None else []
        self.merged_logic_chain = merged_logic_chain if merged_logic_chain is not None else []

    def to_json(self):
        return {"keyword": self.keyword,
         "sentenceindex": self.sentenceindex,
         "similar indeces": self.similar_index,
        "merged logic chain": self.merged_logic_chain
        }
