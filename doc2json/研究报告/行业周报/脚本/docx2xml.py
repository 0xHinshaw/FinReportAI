import zipfile
import os
import re

def docx2xml(docx_file):
    """docx本质是包含多个组成要素的zip文件，通过加压缩zip获取其中的document.xml，可以提取到粗体文本信息，用于之后的关键词，关键句分析。

    Args:
        docx_file (str): docx文件路径

    Returns:
        str : document.xml所在的路径
    """
    # 使用 os 库获取文件名
    file_name = os.path.basename(docx_file)
    # 使用正则表达式提取文件名中的标题
    pattern_title = r"(.*?)\.docx"
    match_title = re.search(pattern_title, file_name)
    if match_title:
        title = match_title.group(1)
    else:
        print("未找到指定的文件")

    xml_file_path = os.path.join(os.path.dirname(docx_file), title + '.json')
    # 定义解压缩后的文件夹路径
    extracted_folder = os.path.join(os.path.dirname(docx_file),"extracted_folder" ,title )
    if not os.path.exists(extracted_folder):
        os.makedirs(extracted_folder)

    # 解压缩 DOCX 文件
    with zipfile.ZipFile(docx_file, 'r') as zip_ref:
        zip_ref.extractall(extracted_folder)

    # 获取 document.xml 文件路径
    xml_file = os.path.join(extracted_folder, 'word', 'document.xml')

    # 检查 document.xml 是否存在并打印其内容
    if os.path.exists(xml_file):
        print("docx2xml:转换成功")
        return xml_file
    else:
        print("docx2xml:\nDocument.xml file not found!")

