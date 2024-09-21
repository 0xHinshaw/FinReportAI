# 周报结构分析
对周报内容按粗体标题结构进行提取，转换为json数据格式，支持docx格式的周报。
## 使用指南
输入docx周报所在文件夹，使用"周报脚本"中的dir2json函数
```
from 周报脚本 import dir2json

dir_path = "word_dir_path" # 周报的文件夹位置
dir2json(dir_path) # 将遍历文件夹下的docx文件，并转化成json格式。放在文件所在位置的json文件夹中。
```

## 功能和特点
### word粗体字识别
将word文档改成压缩文件格式后提取其中的document.xml对其中的加粗文本进行提取。
### 粗体关键句识别
对每段内容的开头和粗体内容列表比对，从而识别段落开头的关键句。
### 子标题检测
对于标题对应的内容进行子标题检测，查找是否有子标题，以及子标题结构构建，子标题内容匹配。

## 依赖
以下依赖用pip安装即可
- regex = 2023.12.25 
- python-docx = 1.1.0
还需要使用conda安装：pandoc
- conda install -c conda-forge pandoc
## 联系方式

