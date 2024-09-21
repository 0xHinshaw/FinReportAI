import pandas as pd
import json

def get_data_frame(file_name, sheet_name):
    """
    Read Excel file into a Pandas DataFrame.

    Args:
        file_name (str): The name of the Excel file (without extension).
        sheet_name (str): The name of the sheet within the Excel file.

    Returns:
        pandas.DataFrame: The DataFrame containing data from the specified Excel sheet.
    """
    return pd.read_excel(f"{file_name}.xlsx", sheet_name)

def create_data_structure(df):
    """
    Create a nested data structure from the DataFrame.

    Args:
        df (pandas.DataFrame): DataFrame containing data.

    Returns:
        dict: Nested data structure representing the contents of the DataFrame.
    """
    key = df['title']
    content = df['content']
    subtitle = df['subtitle']
    keycontent = df['keycontent']
    title_dict = {k: [] for k in key}
    index_dict = {k: [] for k in key}

    for i, k in enumerate(key):
        title_dict[key[i]].append(subtitle[i])
        index_dict[key[i]].append(i)

    contents = {}
    content_list = []
    for i, k in enumerate(subtitle):
        content_dict = {
            'title': k,
            'content': content[i],
            'keycontent': keycontent[i],
            'subtitle': []
        }
        content_list.append(content_dict)
        contents[k] = content_dict

    contents[df['document'][0]] = {
        'document': df['document'][0],
        'investmentpoints': df['investmentpoints'][0],
        'keypoints': df.get('keypoints', [None])[0],
        'subtitle': []
    }

    iter_dict = iter(title_dict.items())
    first_key, first_value = next(iter_dict)
    result = contents[first_key]
    for subtitle in first_value:
        result["subtitle"].append(contents[subtitle])

    result['subtitle'] = add_subtitles(result['subtitle'], title_dict, contents)

    return result

def add_subtitles(subtitle_data, title_dict, contents):
    """
    Recursively add subtitles to the nested data structure.

    Args:
        subtitle_data (list): List of dictionaries representing subtitles.
        title_dict (dict): Dictionary mapping titles to their subtitles.
        contents (dict): Dictionary containing all content information.

    Returns:
        list: Updated list of dictionaries with added subtitles.
    """
    for index, title in enumerate(subtitle_data):
        if title['title'] in title_dict:
            for subtitle in title_dict[title['title']]:
                subtitle_data[index]['subtitle'].append(contents[subtitle])

            add_subtitles(subtitle_data[index]['subtitle'], title_dict, contents)
    return subtitle_data

def save_data_to_json(data, file_name):
    """
    Save data to a JSON file.

    Args:
        data (dict): Data to be saved.
        file_name (str): Name of the JSON file to be saved.
    """
    with open(f"{file_name}_{sheet_name}.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

def process_excel_to_json(file_name, sheet_name):
    """
    Process Excel data and save it to a JSON file.

    Args:
        file_name (str): The name of the Excel file (without extension).
        sheet_name (str): The name of the sheet within the Excel file.
    """
    df = get_data_frame(file_name, sheet_name)
    results=[]
    for document in df['document'].unique():
        df_for_one_doc=df[df['document']==document].reset_index()
        result = create_data_structure(df_for_one_doc)
        results.append(result)
    json_data = json.dumps(results, ensure_ascii=False, indent=2)
    save_data_to_json(results, file_name)
    print(json_data)

# Example usage:
name = "/project/siyucheng/files/reportResearch/业绩综述"
sheet_name = "2023三季度"
process_excel_to_json(name, sheet_name)