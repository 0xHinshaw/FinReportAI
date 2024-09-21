import re
import DataErrorDetection as ded
from title_modify import title_modify
from keycontent_extra import get_keycontent
class CN():
    def __init__(self, title,key_list = None):
        """初始化目录节点

        Args:
            title (str): 标题
            key_list (list): 粗体内容组成的列表，用于判断标题所属内容是否含有加粗句子。 Defaults to None.
        """
        pattern = r"(^\d\.?)(\d\.?)?(\d\.?)?(\d\.?)?"
        match = re.search(pattern, title, re.DOTALL)
        self.title = title_modify(title,key_list)
        if match:
            self.n = len([i for i in match.groups() if i is not None])
        else:
            self.n = None
        self.key_list = key_list
        self.father_node = None
        self.son_node = []
        self.keycontent = ""
        self.content = ""
        self.subtitle = ""

    def link(self,node):
        """用于连接父标题与子标题

        Args:
            node (node): 子节点（self是父节点）
        """
        self.son_node.append(node)
        node.father_node = self

    def to_json(self):
        """将递归地将bode结构转化成json所需的字典形式。

        Returns:
            dict: 包含title，content，keycontent，subtitle属性的字典
        """
        if len(self.son_node) == 0:
            return {"title": ded.process(self.title), "content": ded.process(self.content), "keycontent": get_keycontent(ded.process(self.content),self.key_list),
                    "subtitle": self.subtitle}
        else:
            return {"title": ded.process(self.title), "content": ded.process(self.content), "keycontent": get_keycontent(ded.process(self.content),self.key_list),
                    "subtitle": [i.to_json() for i in self.son_node]}
