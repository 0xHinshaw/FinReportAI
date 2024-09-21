import os
import fitz
import pdfplumber
import shutil
from tqdm import tqdm

def process_pdf_files(folder_path):
    """
    Process PDF files in a folder, excluding files containing "英文" in their names.

    Args:
        folder_path (str): Path to the folder containing PDF files.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf') and "英文" not in filename:
            pdf_path = os.path.join(folder_path, filename)
            try:
                main(pdf_path)  # Process PDF files, ignoring return values
            except Exception:
                pass  # Temporary ignore errors

def crop_header_footer(input_pdf, output_pdf):
    """
    Crop header and footer from a PDF file and save the modified PDF.

    Args:
        input_pdf (str): Path to the input PDF file.
        output_pdf (str): Path to save the cropped PDF.
    """
    pdf_document = fitz.open(input_pdf)
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        # Create rectangles for header and footer
        header_rect = fitz.Rect(0, 0, page.rect.width, 75)
        footer_rect = fitz.Rect(0, page.rect.height - 75, page.rect.width, page.rect.height)
        # Draw white rectangles to cover header and footer
        page.draw_rect(header_rect, fill=(1, 1, 1))  # 使用白色填充页眉区域
        page.draw_rect(footer_rect, fill=(1, 1, 1))  # 使用白色填充页脚区域
    pdf_document.save(output_pdf)
    pdf_document.close()

def extract_covered_text(input_pdf, output_path):
    """
    Extract text covered by header and footer from a PDF file and save it to a text file.

    Args:
        input_pdf (str): Path to the input PDF file.
        output_path (str): Path to save the extracted text.
    """
    covered_text = ""
    with pdfplumber.open(input_pdf) as pdf:
        for page in tqdm(pdf.pages, desc="Extracting covered text"):
            header_rects = [fitz.Rect(0, 0, page.width, 75)]
            footer_rects = [fitz.Rect(0, page.height - 75, page.width, page.height)]
            bboxes = header_rects + footer_rects
            for bbox in bboxes:
                text_instances = page.within_bbox(bbox).extract_text()
                covered_text += text_instances + '\n'
    # Save the result to the specified file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(covered_text)

def not_within_bboxes(obj, bboxes):
    """
    Check if an object is not within any bounding box.

    Args:
        obj: Object to be checked.
        bboxes (list): List of bounding boxes.

    Returns:
        bool: True if the object is not within any bounding box, False otherwise.
    """
    def obj_in_bbox(_bbox):
        v_mid = (obj["top"] + obj["bottom"]) / 2
        h_mid = (obj["x0"] + obj["x1"]) / 2
        x0, top, x1, bottom = _bbox
        return (h_mid >= x0) and (h_mid < x1) and (v_mid >= top) and (v_mid < bottom)
    return not any(obj_in_bbox(__bbox) for __bbox in bboxes)

def extract_text_except_tables(output_pdf, output_path):
    """
    Extract text from a PDF file except text within tables and save it to a text file.

    Args:
        output_pdf (str): Path to the PDF file.
        output_path (str): Path to save the extracted text.
    """
    text_except_tables = ""
    with pdfplumber.open(output_pdf) as pdf:
        for page in tqdm(pdf.pages, desc="Filtering text"):
            bboxes = [
                table.bbox
                for table in page.find_tables(
                    table_settings={
                        "vertical_strategy": "explicit",
                        "horizontal_strategy": "explicit",
                        "explicit_vertical_lines": page.curves + page.edges,
                        "explicit_horizontal_lines": page.curves + page.edges,
                    }
                )
            ]
            text_except_tables += page.filter(lambda obj: not_within_bboxes(obj, bboxes)).extract_text() + '\n'
    # Save the result to the specified file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text_except_tables)

def remove_covered_text(input_text_path, covered_text_path, output_path):
    """
    Remove covered text from the input text and save the result to a file.

    Args:
        input_text_path (str): Path to the input text file.
        covered_text_path (str): Path to the file containing covered text.
        output_path (str): Path to save the cleaned text.
    """
    with open(input_text_path, 'r', encoding='utf-8') as input_file:
        input_text = input_file.readlines()
    with open(covered_text_path, 'r', encoding='utf-8') as covered_file:
        covered_text = covered_file.readlines()
    cleaned_text = []
    for line in input_text:
        if line not in covered_text:
            cleaned_text.append(line)
    # Save the result to the specified file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(cleaned_text)

def process_pdf(input_pdf, output_folder, error_folder, blank_folder):
    """
    Process a PDF file.

    Args:
        input_pdf (str): Path to the input PDF file.
        output_folder (str): Path to the folder to save output files.
        error_folder (str): Path to the folder to save error files.
        blank_folder (str): Path to the folder to save blank files.
    """
    base_name = os.path.basename(input_pdf)
    output_pdf = os.path.join(output_folder, base_name.replace('.pdf', '_cropped.pdf'))
    covered_text_path = os.path.join(output_folder, base_name.replace('.pdf', '_covered_text.txt'))
    final_output_path = os.path.join(output_folder, base_name.replace('.pdf', '.txt'))
    try:
        crop_header_footer(input_pdf, output_pdf)
        extract_text_except_tables(output_pdf, final_output_path)
        extract_covered_text(input_pdf, covered_text_path)
        remove_covered_text(final_output_path, covered_text_path, final_output_path)
        os.remove(output_pdf)
        os.remove(covered_text_path)
        if os.path.getsize(final_output_path) == 0:
            blank_pdf_path = os.path.join(blank_folder, base_name)
            shutil.copyfile(input_pdf, blank_pdf_path)
    except Exception as e:
        error_file_path = os.path.join(error_folder, base_name)
        shutil.copyfile(input_pdf, error_file_path)
        print(f"Error processing {input_pdf}: {str(e)}")
        return

def main():
    input_folder = "/data/financial_report_baijiu/公司公告"
    output_folder = "/data/chengsiyu/result/txt/公司公告/finalfile/"
    error_folder = "/data/chengsiyu/result/txt/公司公告/errorfile/"
    blank_folder = "/data/chengsiyu/result/txt/公司公告/blankfile/"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(error_folder):
        os.makedirs(error_folder)
    if not os.path.exists(blank_folder):
        os.makedirs(blank_folder)
    for root, dirs, files in os.walk(input_folder):
        for file_name in files:
            if file_name.endswith('.pdf'):
                input_pdf = os.path.join(root, file_name)
                process_pdf(input_pdf, output_folder, error_folder, blank_folder)

if __name__ == "__main__":
    main()