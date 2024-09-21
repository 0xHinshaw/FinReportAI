# Doc2JSON_公司公告

本项目旨在提供一系列简单而有效的方法，用于处理不同格式的pdf文档，并将它们先转换为纯文本格式，再转换成JSON，以便后续处理和分析。以下是包含的工具以及它们的功能和使用说明。

## 1. PDF转TXT工具（pdf2txt_final.py）

### 功能介绍

这个工具用于处理公司公告中的PDF文件，将其转换为纯文本格式（TXT），以便后续处理和分析。

### 使用方法

1. 将待处理的公司公告PDF文件放入指定文件夹中。
2. 运行脚本，程序将自动处理PDF文件，并将结果保存在相应文件夹中。
   - 处理后成功提取内容的TXT文件将会被保存在`result/txt/公司公告/finalfile/`文件夹中。
   - 处理过程中出现错误的PDF文件将会被保存在`result/txt/公司公告/errorfile/`文件夹中。
   - 处理后的TXT文件为空的PDF文件将会被保存在`result/txt/公司公告/blankfile/`文件夹中。

### 主要函数说明

- `process_pdf_files`：遍历指定文件夹中的PDF文件，排除文件名中含有“英文”的文件。
- `crop_header_footer`：剪裁页眉和页脚。
- `extract_covered_text`：提取被页眉和页脚覆盖的文本。
- `not_within_bboxes`：检查对象是否不在任何边界框内。
- `extract_text_except_tables`：提取除去表格外的文本。
- `remove_covered_text`：删除被页眉页脚页码覆盖的文本。
- `process_pdf`：对单个PDF文件执行上述所有操作，并根据处理结果将其分类为正常文件、错误文件或空白文件。

### 注意事项

- 确保安装了所需的Python库，包括`fitz`、`pdfplumber`和`tqdm`。
- 空白文件是指处理后的文本文件为空的情况，多数是由于pdf为扫描件以及页眉页脚页码情况不一致所致，对于这些文件的处理请参照下面对应的解决方案。

## 2. 补充处理空白文件工具1（restartblank1_final.py）

### 功能介绍

这个工具用于处理公司公告中的PDF文件，特别处理扫描件以及没有页眉、页脚和页码的公司公告文件，以确保转换过程的准确性和完整性，并补充处理空白文件。

### 文件结构

- **input_dir**：存放待处理的 PDF 文件的文件夹路径。
- **output_dir**：存放处理后的 PDF 文件的文件夹路径。
- **covered_text_dir**：存放被覆盖的文本的文件夹路径。
- **mid_output_dir**：存放中间文本输出文件的文件夹路径。
- **final_output_dir**：存放最终文本输出文件的文件夹路径。
- **error_folder**：存放处理过程中出现错误的文件的文件夹路径。
- **scanned_pdf_dir**：存放扫描页 PDF 文件的文件夹路径。

### 使用方法

1. 将待处理的PDF文件放入指定的文件夹中。
2. 运行主函数，程序将自动处理PDF文件，并将结果保存在相应文件夹中。

### 主要函数说明

- `crop_header_footer`
- `extract_covered_text`
- `not_within_bboxes`
- `extract_text_except_tables`
- `remove_covered_text`

除上述函数外，补充下面函数：

- `is_scanned_page`：检测 PDF 文件中是否存在扫描页。
- `analyze_pdf`：分析 PDF 文件以确定是否存在扫描页。
- `move_scanned_pdfs`：移动扫描页 PDF 文件到指定文件夹。

### 注意事项

- 确保安装了所需的Python库，包括`PyMuPDF`、`pdfplumber`、`shutil`和`tqdm`。

## 3. 补充处理空白文件工具2（restartblank2_final.py）

### 功能介绍

这个工具用于处理公司公告中的PDF文件，特别处理不规则的页眉、页脚和页码，以确保转换过程的准确性和完整性，并补充处理空白文件。

### 文件结构

- **input_folder**：存放待处理的PDF文件的文件夹路径。
- **covered_text_path**：存放提取的被页眉和页脚覆盖的文本内容的文件路径。
- **final_output_path**：存放最终提取的文本内容的文件路径。

在处理过程中，会涉及以下临时文件路径：

- **file1_path**：最终提取的文本内容文件的路径，用于作为比较的第一个文件。
- **file2_path**：提取的被覆盖文本内容文件的路径，用于作为比较的第二个文件。
- **output_path**：清理后的文本内容输出文件的路径。

### 使用方法

1. 将需要处理的PDF文件放置在指定的输入文件夹中。
2. 运行主函数，程序将自动处理PDF文件，并将结果保存在相应文件夹中。

### 主要函数说明

- `crop_header_footer`
- `extract_covered_text`
- `not_within_bboxes`
- `extract_text_except_tables`

除上述函数外，补充下面函数：

- `remove_common_lines`：移除两个文件之间的共同行，并将结果保存到新文件中。

### 注意事项

- 确保安装了所需的Python库，包括`PyMuPDF`、`pdfplumber`和`tqdm`。
- 请确保输入文件夹中的PDF文件格式正确，以避免处理错误。

## 目录结构提取及内容匹配
### 使用指南
txt文件使用file2json中的txt2json函数，使用示例：
```python
from file2json import txt2json

txt_path = "dir_path/your_txt.txt"
file_name = os.path.splitext(os.path.basename(txt_path))[0] #文件名字
with open(txt_path, "r", encoding="utf-8") as f:
    text_except_tables = f.read() # 直接读取txt
title_list = first_titles(text_except_tables) # 获取一级标题
output_dir = os.path.dirname(txt_path) 输出json文件存放路径
txt2json(file_name, text_except_tables, title_list, output_dir=output_dir) # txt公司公告转化为json

```
pdf文件使用file2json中的pdf2json函数，使用示例：
```python
from file2json import pdf2json

pdf_path= "dir_path/your_pdf.pdf"
pdf2json(pdf_path) # pdf公司公告转化为json
```
### 功能和特点
#### 文件目录提取
识别到目录后对目录进行解析，构造出初始文章结构。
详见`get_f_node.py`
#### 模糊匹配
当目录标题和正文中的标题不一致时，会采取修改正文标题的方式进行模糊匹配。
详见`fuzzy_matching.py`
#### 标题内容匹配
使用目录标题或给定的标题，对文件内容进行匹配，生成初始的框架内容
详见`get_node_content.py`
#### 子标题检测
对于标题对应的内容进行子标题检测，查找是否有子标题，以及子标题结构构建，子标题内容匹配。
详见`get_node_content.py`
### 依赖
以下依赖用pip安装即可
- pymupdf = 1.24.1
- fitz = 0.0.1.dev2
- pdfplumber = 0.11.0