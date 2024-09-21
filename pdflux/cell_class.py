# def modify_bbox(bbox):
#     for index,item in enumerate(bbox):
#         bbox[index] = round(item)
#     return bbox

class excel_cell():
    def __init__(self, x0, y0, x1, y1, row_index,column_index):
        # 初始化节点
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.column_index = column_index
        self.row_index = row_index
        self.parent_cell = None
        self.child_cell = []

    def merge(self,cell):
        """连接子单元格

        Args:
            node (gsgg_node): 子单元格
        """
        if self.parent_cell is None:
            self.child_cell.append(cell)
            cell.parent_cell = self
            self.update_xy(cell)
            cell.delete_xy()
        else :
            self.parent_cell.merge(cell)
    
    def update_xy(self,c):
        if c.x0 < self.x0:
            self.x0 = c.x0
        if c.y0 < self.y0:
            self.y0 = c.y0
        if c.x1 > self.x1:
            self.x1 = c.x1
        if c.y1 > self.y1:
            self.y1 = c.y1

    def delete_xy(self):
        self.x0 = 0
        self.y0 = 0
        self.y1 = 0
        self.x1 = 0

