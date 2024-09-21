import os
import fitz
import pdfplumber
from tqdm import tqdm
import shutil

def crop_header_footer(input_pdf, output_pdf):
    """
    裁剪PDF文件的页眉和页脚。

    :param input_pdf: 输入PDF文件的路径
    :param output_pdf: 输出PDF文件的路径
    :return: 无
    """
    pdf_document = fitz.open(input_pdf)
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        # 创建页眉和页脚的矩形区域
        header_rect = fitz.Rect(0, 0, page.rect.width, 70)
        footer_rect = fitz.Rect(0, page.rect.height - 70, page.rect.width, page.rect.height)
        # 绘制白色矩形以覆盖页眉和页脚
        page.draw_rect(header_rect, fill=(1, 1, 1))  # 使用白色填充页眉区域
        page.draw_rect(footer_rect, fill=(1, 1, 1))  # 使用白色填充页脚区域
    pdf_document.save(output_pdf)
    pdf_document.close()


def extract_covered_text(input_pdf, output_path):
    """
    提取PDF中被覆盖的页眉页脚区域的文本内容，并保存到文件中。

    :param input_pdf: 输入PDF文件的路径
    :param output_path: 输出文本文件的路径
    :return: 无
    """
    covered_text = ""
    with pdfplumber.open(input_pdf) as pdf:
        for page in tqdm(pdf.pages, desc="Extracting covered text"):
            header_rects = [fitz.Rect(0, 0, page.width, 70)]
            footer_rects = [fitz.Rect(0, page.height - 70, page.width, page.height)]
            bboxes = header_rects + footer_rects
            for bbox in bboxes:
                text_instances = page.within_bbox(bbox).extract_text()
                covered_text += text_instances + '\n'
    # 将结果保存到指定文件中
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(covered_text)


def not_within_bboxes(obj, bboxes):
    """
    检查对象是否位于任何边界框内。

    :param obj: PDF对象
    :param bboxes: 边界框列表
    :return: 如果对象不在任何边界框内则返回True，否则返回False
    """
    def obj_in_bbox(_bbox):
        v_mid = (obj["top"] + obj["bottom"]) / 2
        h_mid = (obj["x0"] + obj["x1"]) / 2
        x0, top, x1, bottom = _bbox
        return (h_mid >= x0) and (h_mid < x1) and (v_mid >= top) and (v_mid < bottom)

    return not any(obj_in_bbox(__bbox) for __bbox in bboxes)


def extract_text_except_tables(output_pdf, output_path):
    """
    从PDF中提取除表格以外的文本内容，并保存到文件中。

    :param output_pdf: 输出PDF文件的路径
    :param output_path: 输出文本文件的路径
    :return: 提取除表格以外的文本内容
    """
    text_except_tables = ""
    with pdfplumber.open(output_pdf) as pdf:
        for page in tqdm(pdf.pages, desc="Filtering text"):
            bboxes = [
                table.bbox
                for table in page.find_tables(
                    table_settings={
                        "vertical_strategy": "explicit",
                        "horizontal_strategy": "explicit",
                        "explicit_vertical_lines": page.curves + page.edges,
                        "explicit_horizontal_lines": page.curves + page.edges,
                    }
                )
            ]
            text_except_tables += page.filter(lambda obj: not_within_bboxes(obj, bboxes)).extract_text() + '\n'
    # 将结果保存到指定文件中
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text_except_tables)


def remove_covered_text(input_text_path, covered_text_path, output_path):
    """
    从输入文本中删除被覆盖的页眉页脚区域的内容，并保存到文件中。

    :param input_text_path: 输入文本文件的路径
    :param covered_text_path: 覆盖文本文件的路径
    :param output_path: 输出文本文件的路径
    :return: 无
    """
    with open(input_text_path, 'r', encoding='utf-8') as input_file:
        input_text = input_file.readlines()
    with open(covered_text_path, 'r', encoding='utf-8') as covered_file:
        covered_text = covered_file.readlines()
    # 逐行遍历covered_text中的内容，并在输入文本中删除匹配到的行
    cleaned_text = []
    for line in input_text:
        if line not in covered_text:
            cleaned_text.append(line)
    # 将结果保存到指定文件中
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(cleaned_text)


def process_pdf(input_pdf, output_folder):
    """
    处理PDF文件。

    :param input_pdf: 输入PDF文件的路径
    :param output_folder: 输出文件夹的路径
    :return: 无
    """
    # 生成输出文件的路径
    base_name = os.path.basename(input_pdf)
    output_pdf = os.path.join(output_folder, base_name.replace('.pdf', '_cropped.pdf'))
    covered_text_path = os.path.join(output_folder, base_name.replace('.pdf', '_covered_text.txt'))
    final_output_path = os.path.join(output_folder, base_name.replace('.pdf', '.txt'))

    # 原有的处理流程
    crop_header_footer(input_pdf, output_pdf)
    extract_text_except_tables(output_pdf, final_output_path)
    extract_covered_text(input_pdf, covered_text_path)
    remove_covered_text(final_output_path, covered_text_path, final_output_path)

    # 删除临时文件
    os.remove(output_pdf)
    os.remove(covered_text_path)


def is_scanned_page(page):
    """
    检查页面是否是扫描页。

    :param page: 页面对象
    :return: 如果是扫描页返回True，否则返回False
    """
    # 通过分析文本长度来检查页面是否是扫描的
    text = page.get_text()
    return len(text.strip()) < 50  # 用于扫描页检测的阈值


def analyze_pdf(file_path, destination_folder):
    """
    分析给定PDF文件是否包含扫描页，并将包含扫描页的文件移动到目标文件夹。

    :param file_path: PDF文件的路径
    :param destination_folder: 目标文件夹的路径
    :return: 如果文件包含扫描页则返回True，否则返回False
    """
    try:
        # 打开PDF文件
        doc = fitz.open(file_path)

        # 遍历每一页
        for page in doc:
            if is_scanned_page(page):
                # 如果找到扫描页，则关闭文档并返回True
                doc.close()
                return True

        # 如果没有找到扫描页，则关闭文档
        doc.close()

    except Exception as e:
        # 处理处理过程中可能发生的任何异常
        print(f"处理文件时发生错误 {file_path}: {e}")

    return False


def move_scanned_pdfs(source_folder, destination_folder):
    """
    将源文件夹中包含扫描页的PDF文件移动到目标文件夹。

    :param source_folder: 源文件夹的路径
    :param destination_folder: 目标文件夹的路径
    :return: 无
    """
    # 如果目标文件夹不存在，则创建它
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 遍历源文件夹及其子目录
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            # 检查文件是否为PDF
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root, file)
                # 分析PDF文件，并移动包含扫描页的文件
                if analyze_pdf(file_path, destination_folder):
                    shutil.move(file_path, os.path.join(destination_folder, file))


def main():
    input_folder = r"C:\Users\hnkfl\Desktop\ocr\111"  # 输入文件夹路径
    output_folder = r"C:\Users\hnkfl\Desktop\ocr\111"  # 输出文件夹路径

    # 如果输出文件夹不存在，则创建它
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有PDF文件
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.pdf'):
            input_pdf = os.path.join(input_folder, file_name)
            process_pdf(input_pdf, output_folder)

    # 源文件夹和目标文件夹路径
    source_folder = r"C:\Users\hnkfl\Downloads\公司公告问题文件及脚本\blankfile"
    destination_folder = r"C:\Users\hnkfl\Downloads\公司公告问题文件及脚本\scanned"

    # 执行脚本
    move_scanned_pdfs(source_folder, destination_folder)

    # 打印完成消息
    print("扫描的PDF文件已移动到'scanned'文件夹。")

if __name__ == "__main__":
    main()
