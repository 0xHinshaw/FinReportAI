import os
from datetime import datetime
import signal
import re
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pdfminer.converter import PDFPageAggregator
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTImage, LTLine, LTRect, LTChar, LTTextBoxHorizontal,LTTextContainer,LTFigure
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from tqdm import tqdm
import sys
#TODO luke 的版本
module_path = "/home/luzhenye/PythonProject/pdf表格提取"
sys.path.append(module_path)
from extract_tables import filter_elements_within_rect,group_rectangles,find_table_rect,mid_x,mid_y,get_char_element,sort_char_list,is_within_rect,group_by_y0

def extract_text_dianping_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        parser = PDFParser(file)
        document = PDFDocument(parser)

        # 创建资源管理器和参数
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        concat_result = []
        file_text = ""
        # 读取特定页面
        for page_index, page in enumerate(PDFPage.create_pages(document)):
            pdf_type = True
            interpreter.process_page(page)
            layout = device.get_result()
            vertical_list = []
            horizontal_list = []
            page_text_lines = []
            page_line_rects = []
            char_list = []
            page_height = page.mediabox[3] 
            page_width = page.mediabox[2]  
            left_rect = LTRect(
                        bbox=(30,0,200,page_height-75),linewidth=1)
            right_rect = LTRect(
                        bbox=(190,60,page_width,page_height-75),linewidth=1)
            all_rect =  LTRect(
                        bbox=(30,60,page_width,page_height-75),linewidth=1)
            for element in layout:
                    if isinstance(element, LTTextContainer):
                        get_char_element(element,char_list)
            char_list = sort_char_list(char_list)
            for element in layout:
                if isinstance(element, LTImage):
                    if is_within_rect(element,left_rect):
                        pdf_type = False
                        # print(f"Image found: {element.name}")
                    # You can add code here to further process the image.
                elif isinstance(element, LTFigure):
                    # LTFigure objects are containers for other LT* objects.
                    for image in element:
                        if isinstance(image, LTImage):
                            if is_within_rect(image,left_rect):
                                pdf_type = False
                                # print(f"Image found in figure: {image.name}")
            if not pdf_type:
                char_list = filter_elements_within_rect(char_list,right_rect)
                char_list = [text_char for text_char in char_list if 10.4<text_char.size<12]
            else:
                # pass
                char_list = filter_elements_within_rect(char_list,all_rect)
                char_list = [text_char for text_char in char_list if 10.4<text_char.size<12 or abs(text_char.size-14)<0.1]
                char_list = [text_char for text_char in char_list if text_char.get_text() != " "]
            char_dict = group_by_y0(char_list)
            temp_text = ""
            for key in sorted(char_dict.keys(),reverse=True):
                char_dict[key] = sorted(char_dict[key],key=lambda c :c.x0)
            text = []
            for key in sorted(char_dict.keys(),reverse=True):
                for text_char in char_dict[key]:
                    temp_text += text_char.get_text()
                text.append(temp_text)
                temp_text = ""
            file_text += "\n".join(text)
            file_text += "\n"
        return file_text

if __name__ == "__main__":
    extract_text_dianping_pdf("/home/shenyuge/lingyue-data-process/pdflux/食品饮料行业双周报（20240520-20240602）：政策优化，关注预期改善.pdf")

    

