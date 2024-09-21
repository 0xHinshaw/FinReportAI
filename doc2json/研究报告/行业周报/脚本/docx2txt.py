import os
import subprocess
from docx import Document

def process(input):
    """将路径文件夹下的docx文件全部转化成txt文本

    Args:
        input (str): 要处理的文件夹路径
    """
    docx_name_list = os.listdir(input)
    for dn in docx_name_list:
        if not dn.endswith(".docx"):
            continue
        path1 = os.path.join(input, dn)
        output = os.path.splitext(dn)[0]
        output_path = os.path.join(input, output + ".txt")

        # 使用 pandoc 将 docx 转换为 txt
        subprocess.run(["pandoc", "-s", path1, "-o", output_path])

        # 读取并重新编码文件
        try:
            with open(output_path, 'rb') as file:
                content = file.read().decode("utf-8").encode("utf-8")
            with open(output_path, 'wb') as file:
                file.write(content)
        except IOError as err:
            print("I/O error: {0}".format(err))

# # 使用示例
# process("/path/to/your/docx/files")







