import pdfplumber
import pandas as pd

def tail_not_space_char(page_chars):
    i = -1
    while page_chars[i].get('text').isspace():
        i = i - 1
        # print(page_chars[i].get('text'), i)
    return page_chars[i]
 
 
# 返回列表最头部的非空字符
def head_not_space_char(page_chars):
    i = 0
    while page_chars[i].get('text').isspace():
        i += 1
        # print(page_chars[i].get('text'), i)
    return page_chars[i]


# 将pdf表格数据抽取到文件中
def extract_tables_from_pdf(input_file_path, output_path):
    print("========================================表格抽取开始========================================")
    # 读取pdf文件，保存为pdf实例
    pdf = pdfplumber.open(input_file_path)
 
    # 存储每个页面最底部字符的y0坐标
    y0_bottom_char = []
    # 存储每个页面最底部表格中最底部字符的y0坐标
    y0_bottom_table = []
    # 存储每个页面最顶部字符的y1坐标
    y1_top_char = []
    # 存储每个页面最顶部表格中最顶部字符的y1坐标
    y1_top_table = []
    # 存储所有页面内的表格文本
    text_all_table = []
    # 访问每一页
    print("1===========开始抽取每页顶部和底部字符坐标及表格文本===========1")
    for page in pdf.pages:
        # table对象，可以访问其row属性的bbox对象获取坐标
        table_objects = page.find_tables()
        text_table_current_page = page.extract_tables()
        if text_table_current_page:
            text_all_table.append(text_table_current_page)
            # 获取页面最底部非空字符的y0
            y0_bottom_char.append(tail_not_space_char(page.chars).get('y0'))
            # 获取页面最底部表格中最底部字符的y0，table对象的bbox以左上角为原点，而page的char的坐标以左下角为原点，可以用page的高度减去table对象的y来统一
            y0_bottom_table.append(page.bbox[3] - table_objects[-1].bbox[3])
            # 获取页面最顶部字符的y1
            y1_top_char.append(head_not_space_char(page.chars).get('y1'))
            # 获取页面最顶部表格中最底部字符的y1
            y1_top_table.append(page.bbox[3] - table_objects[0].bbox[1])
    print("1===========抽取每页顶部和底部字符坐标及表格文本结束===========1")
 
    # 处理跨页面表格，将跨页面表格合并，i是当前页码，对于连跨数页的表，应跳过中间页面，防止重复处理
    print("2===========开始处理跨页面表格===========2")
    i = 0
    while i < len(text_all_table):
        # print("处理页面{0}/{1}".format(i+1, len(text_all_table)))
        # 判断当前页面是否以表格结尾且下一页面是否以表格开头，若都是则说明表格跨行，进行表格合并
        # j是要处理的页码，一般情况是当前页的下一页，对于连跨数页情况，也可以是下下一页,跨页数为k
        # 若当前页是最后一页就不用进行处理
        if i + 1 >= len(text_all_table):
            break
        j = i + 1
        k = 1
        # 要处理的页为空时退出
        while text_all_table[j]:
            if y0_bottom_table[i] <= y0_bottom_char[i] and y1_top_table[j] >= y1_top_table[j]:
                # 当前页面最后一个表与待处理页面第一个表合并
                if len(text_all_table[j][0][0])==len(text_all_table[i][-1][0]):
                    text_all_table[i][-1] = text_all_table[i][-1] + text_all_table[j][0]
                    text_all_table[j].pop(0)
                # 如果待处理页面只有一个表，就要考虑下下一页的表是否也与之相连
                if not text_all_table[j] and j + 1 < len(text_all_table) and text_all_table[j + 1]:
                    k += 1
                    j += 1
                else:
                    i += k
                    break
            else:
                i += k
                break
    print("2===========处理跨页面表格结束===========2")
 
 
    # 保存excel
    print("3===========转换表格列表为markdown格式，写入txt文件===========3")
    markdown_table_list = []
    for page_num, page in enumerate(text_all_table):
        for table_num, table in enumerate(page):
            # print("处理表格页面{0}/表格{1}".format(page_num, table_num))
            if table:
                # print(table)
                table_df = pd.DataFrame(table)
                markdown_table = table_df.to_markdown(index=False)
                markdown_table_list.append(markdown_table)
    # 将 Markdown 表格保存到文件
    with open(output_path, "w", encoding="utf-8") as f:
        for i, markdown_table in enumerate(markdown_table_list):
            # f.write(f"Table {i+1}:\n{markdown_table}\n\n")
            f.write(markdown_table + "\n\n\n")

    print("3===========保存表格到excel结束===========3")
    print("========================================表格抽取结束========================================")
 

def extract_text_from_pdf(input_file_path, output_path):
    return ''
if __name__ == "__main__":
    # from pprint import pprint

    # kb_file = KnowledgeFile(filename="test.txt", knowledge_base_name="samples")
    # # kb_file.text_splitter_name = "RecursiveCharacterTextSplitter"
    # docs = kb_file.file2docs()
    # pprint(docs[-1])

    # docs = kb_file.file2text()
    # pprint(docs[-1])

    # 抽取表格功能测试
    input_file = "/data/llmapi/finreport/2024-04-03：贵州茅台：贵州茅台2023年年度报告.pdf"
    output_path = "/data/shenyuge/lingyue-data-process/pdflux/2024-04-03：贵州茅台：贵州茅台2023年年度报告.txt"
 
    extract_tables_from_pdf(input_file, output_path)