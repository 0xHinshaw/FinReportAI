import re
import DataErrorDetection as ded

def content_modify(content:str):
    """修改输出的json中的content内容，解决一部分pdf转txt带来的缩进换行问题。

    Args:
        content (str): 节点中的content

    Returns:
        str: 返回修正好的content
    """
    result = re.sub(r"\s\n", r"", content)# 当content中的空格连着回车时，删除这种组合。
    return result

class zgsms_node():
    def __init__(self, title="", content="", subtitle=None, keycontent=""):
        # 初始化节点
        self.title = title
        self.content = content
        self.subtitle = subtitle if subtitle is not None else [] # 这一步是解决list是可变变量带来的问题。
        self.keycontent = keycontent
        self.parent_node = None
        self.child_node = []

    def link(self,node):
        """连接子节点

        Args:
            node (gsgg_node): 子节点
        """
        self.child_node.append(node)
        node.parent_node = self

    def to_json(self):
        if len(self.child_node) == 0:
            return {
                "title": ded.process(self.title),
                "content": self.content,
                "subtitle": self.subtitle,
                "keycontent": self.title  # 确保 keycontent 是 title 的值
            }
        else:
            return {
                "title": ded.process(self.title),
                "content": self.content,
                "subtitle": [i.to_json() for i in self.child_node],
                "keycontent": self.title  # 确保 keycontent 是 title 的值
            }
