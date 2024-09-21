# Doc2JSON_投资策略

本项目旨在提供一种简单而有效的方法，用于将投资策略文件从文档（doc）格式转换为JSON格式。

## 使用方法

1. **准备数据**：
   准备好要转换的Excel文件，其中应该包含以下列：

   1. **title**：标题列，包含主要内容的标题信息。
   2. **content**：内容列，包含主要内容的具体内容信息。
   3. **subtitle**：副标题列，包含主要内容的副标题信息。
   4. **keycontent**：关键内容列，包含主要内容的关键内容信息，如粗体字部分。
   5. **document**：文档列，指示内容所属的文档标题。
   6. **investmentpoints**：投资要点列，包含投资相关的重点信息。
   7. **keypoints**：关键投资要点列，包含与投资要点内容相关的关键信息（如粗体字）。

   确保Excel文件中的上述列包含了所需的数据信息，以便程序能够正确地读取和转换数据。

2. **配置文件路径**：
   在代码中，设置正确的文件路径和工作表名称，以便程序能够正确地读取Excel文件。

3. **执行代码**：
   运行`process_excel_to_json`函数，将Excel数据处理并转换为JSON格式。

4. **保存结果**：
   转换完成后，程序将生成一个JSON文件，其中包含了转换后的数据。

## 主要函数说明

- `get_data_frame`：读取Excel文件并将其转换为Pandas DataFrame格式。
- `create_data_structure`：根据DataFrame创建一个嵌套的数据结构，以便表示文档内容的层次结构。
- `add_subtitles`：递归地向数据结构中添加副标题，以构建完整的层次结构。
- `save_data_to_json`：将数据保存为JSON文件。
- `process_excel_to_json`：执行完整的Excel到JSON转换流程。

## 示例

以下是使用示例：

```python
name = "/project/siyucheng/files/reportResearch/投资策略"
sheet_name = "2023三季度"
process_excel_to_json(name, sheet_name)
```

在这个示例中，将名为“2023三季度”的工作表中的数据从Excel文件转换为JSON格式，并将其保存在指定的文件路径中。