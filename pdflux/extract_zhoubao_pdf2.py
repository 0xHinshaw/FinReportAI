import fitz  # pip install pymupdf  
# TODO：fits 有缺陷，不能实现页眉和页脚的去除，排版比较乱
import os

def extract_text_from_pdf(pdf_path, output_dir):
    # 打开PDF文件
    doc = fitz.open(pdf_path)
    pdf_name = os.path.basename(pdf_path)
    txt_filename = os.path.splitext(pdf_name)[0] + '.txt'
    txt_path = os.path.join(output_dir, txt_filename)
    
    full_text = []
    
    # 处理每一页
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        
        page_text = []
        
        for block in blocks:
            if block['type'] == 0:  # 仅处理文本块
                # 对两栏布局进行处理
                block_texts = []
                for line in block['lines']:
                    line_text = ''.join([span['text'] for span in line['spans']])
                    block_texts.append(line_text)
                page_text.append('\n'.join(block_texts))
        
        # 将每页的文本添加到完整文本中
        full_text.append('\n'.join(page_text))
    
    # 将提取的文本保存到指定路径
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write('\n\n'.join(full_text))
    
    print(f"文本已保存到: {txt_path}")

# 示例用法
pdf_path = "/home/luzhenye/data/pdf/周报/食品饮料行业双周报（20240520-20240602）：政策优化，关注预期改善.pdf"
output_dir = "/home/shenyuge/lingyue-data-process/pdflux"
os.makedirs(output_dir, exist_ok=True)
extract_text_from_pdf(pdf_path, output_dir)

