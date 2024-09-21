import fitz  # PyMuPDF
import os
import shutil


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


# 源文件夹和目标文件夹路径
source_folder = r"C:\Users\hnkfl\Downloads\公司公告问题文件及脚本\blankfile"
destination_folder = r"C:\Users\hnkfl\Downloads\公司公告问题文件及脚本\scanned"

# 执行脚本
move_scanned_pdfs(source_folder, destination_folder)

# 打印完成消息
print("扫描的PDF文件已移动到'scanned'文件夹。")
