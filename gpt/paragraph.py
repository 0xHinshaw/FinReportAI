import os
from docx import Document
from docx2txt import process

def extract_paragraphs_from_docx(input_file):
    """
    从 .docx 文件中提取字数大于等于 30 的所有段落,并保存到同名的 .txt 文件中。
    在遇到"目 录"关键词时,停止提取文本。
    
    参数:
    input_file (str) - .docx 文件路径
    """
    # 获取文件名和文件夹路径
    file_name = os.path.basename(input_file)
    output_folder = os.path.dirname(input_file)
    
    # 构建输出文件路径
    output_file = os.path.join(output_folder, os.path.splitext(file_name)[0] + ".txt")
    
    try:
        # 转换 .docx 文件为文本
        text = process(input_file)
        
        # 提取段落,并过滤字数小于 30 以及遇到"目 录"关键词时停止提取
        paragraphs = []
        for line in text.split('\n'):
            if '目' in line and '录' in line:
                break
            if len(line.strip()) >= 30:
                paragraphs.append(line.strip())
        
        # 创建 Document 对象
        print("正在创建 Document 对象...")
        doc = Document(input_file)
        print("Document 对象创建成功")
        
        # 提取所有段落(不包括目录,且长度大于50个字符)
        print("正在提取段落...")
        doc_paragraphs = []
        for i, p in enumerate(doc.paragraphs):
            if not p.style.name.startswith('Heading') and len(p.text.strip()) >= 50:
                doc_paragraphs.append(p.text.strip())
        
        # 合并两个函数提取的段落
        all_paragraphs = paragraphs + doc_paragraphs
        full_text = "\n\n".join([f"段落：\n{p}" for p in all_paragraphs])
        
        # 将段落文本写入 .txt 文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_text)
        
        print(f"文件已成功转换并保存至: {output_file}")
        print(f"总共提取出 {len(all_paragraphs)} 个段落")
    except Exception as e:
        print(f"转换过程中出现错误: {e}")

# 使用示例
# extract_paragraphs_from_docx(r"C:\Users\P3516\Desktop\switch\（可公开）次高端白酒行业深度报告：势能向上，成长可期.docx")