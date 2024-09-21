import os
import fitz
import pdfplumber
from tqdm import tqdm
'''
def process_pdf_files(folder_path):
    # 遍历文件夹中所有文件，跳过含有“英文”的文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf') and "英文" not in filename:
            pdf_path = os.path.join(folder_path, filename)
            try:
                main(pdf_path)  # 处理PDF文件，不关注返回值
            except Exception:
                pass  # 暂时忽略错误这个就行
'''
def extract_covered_text(input_pdf):
    # 提取被覆盖的页眉页脚区域文本内容，并保存到指定文件中
    covered_text = ""
    with pdfplumber.open(input_pdf) as pdf:
        for page in tqdm(pdf.pages, desc="Extracting covered text"):
            header_rects = [fitz.Rect(0, 0, page.width, 75)]
            footer_rects = [fitz.Rect(0, page.height - 75, page.width, page.height)]
            bboxes = header_rects + footer_rects
            for bbox in bboxes:
                text_instances = page.within_bbox(bbox).extract_text()
                covered_text += text_instances + '\n'
    # 将结果保存到指定文件中
    return covered_text

def not_within_bboxes(obj, bboxes):
    # 检查对象是否位于任何表格的边界框内
    def obj_in_bbox(_bbox):
        # 参见 https://github.com/jsvine/pdfplumber/blob/stable/pdfplumber/table.py#L404
        v_mid = (obj["top"] + obj["bottom"]) / 2
        h_mid = (obj["x0"] + obj["x1"]) / 2
        x0, top, x1, bottom = _bbox
        return (h_mid >= x0) and (h_mid < x1) and (v_mid >= top) and (v_mid < bottom)
    return not any(obj_in_bbox(__bbox) for __bbox in bboxes)

def extract_text_except_tables(output_pdf):
    # 提取PDF中除表格以外的文本内容，并保存到指定文件中
    text_except_tables = ""
    with pdfplumber.open(output_pdf) as pdf:
        for page in tqdm(pdf.pages, desc="Filtering text"):
            # 获取页面上的表格边界框
            bboxes = [
                table.bbox
                for table in page.find_tables(
                    table_settings={
                        "vertical_strategy": "lines",
                        "horizontal_strategy": "lines"
                    }
                )
            ]
            text_except_tables += page.filter(lambda obj: not_within_bboxes(obj, bboxes)).extract_text() + '\n'
    # 将结果保存到指定文件中
    return text_except_tables

def remove_covered_text(input_text, covered_text):
    # 从输入的文本中删除覆盖的页眉页脚区域文本内容，并保存到指定文件中
    input_text = input_text.split("\n")
    covered_text = covered_text.split("\n")
    # 逐行遍历covered_text中的内容，并在输入文本中删除匹配到的行
    cleaned_text = []
    for line in input_text:
        if line not in covered_text:
            cleaned_text.append(line)
    # 将结果保存到指定文件中
    return "\n".join(cleaned_text)

def process_pdf(input_pdf):
    text_except_tables = extract_text_except_tables(input_pdf)
    covered_text = extract_covered_text(input_pdf)
    text = remove_covered_text(text_except_tables, covered_text)
    return text
'''
def main():
    input_folder = "/data/chengsiyu/data/公司公告"
    output_folder = "/data/chengsiyu/result/txt/公司公告/test1"
    # 如果输出文件夹不存在，则创建它
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # 遍历输入文件夹中的所有PDF文件
    for root, dirs, files in os.walk(input_folder):
        for file_name in files:
            if file_name.endswith('.pdf'):
                input_pdf = os.path.join(root, file_name)
                process_pdf(input_pdf)

if __name__ == "__main__":
    main()
'''
