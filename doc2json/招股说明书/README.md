# 招股说明书结构分析
对招股说明书内容按标题结构进行提取，转换为json数据格式，支持pdf和txt格式的招股说明书，包括招股说明书，招股说明书摘要，招股说明书附录，招股意向书。
## 使用指南
txt文件使用file2json中的txt2json函数
```
from file2json import txt2json

txt_path = "dir_path/your_txt.txt"
file_name = os.path.splitext(os.path.basename(txt_path))[0] #文件名字
with open(txt_path, "r", encoding="utf-8") as f:
    text_except_tables = f.read() # 直接读取txt
title_list = first_titles(text_except_tables) # 获取一级标题
output_dir = os.path.dirname(txt_path) 输出json文件存放路径
txt2json(file_name, text_except_tables, title_list, output_dir=output_dir) # txt招股说明书转化为json
```
pdf文件使用file2json中的pdf2json函数
```
from file2json import pdf2json

pdf_path= "dir_path/your_pdf.pdf"
pdf2json(pdf_path) # pdf招股说明书转化为json
```
对于含有多个目录的pdf文件：
```
from multi_cata import multi_cata2json

pdf_path= "dir_path/your_pdf.pdf"
pdf2json(pdf_path) # 多目录pdf招股说明书转化为json
```
## 功能和特点
### pdf正文内容提取
提取pdf文件中除了页眉页脚和表格数据的内容。
### 文件目录提取
识别到目录后对目录进行解析，构造出初始文章结构。
### 无目录文件一级标题提取
对于没有目录的文件，会按照一般的一级目录格式进行一级标题提取。
### 标题内容匹配
使用目录标题或给定的标题，对文件内容进行匹配，生成初始的框架内容
### 多目录招股说明书结构分析
可以处理包含多个目录的招股说明书文件，如招股说明书摘要，找过说明书附录等
### 子标题检测
对于标题对应的内容进行子标题检测，查找是否有子标题，以及子标题结构构建，子标题内容匹配。

## 依赖
以下依赖用pip安装即可
- pymupdf = 1.24.1
- fitz = 0.0.1.dev2
- pdfplumber = 0.11.0

## 联系方式

