import os
import fitz
import pdfplumber
from tqdm import tqdm

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
        # Draw white rectangles to cover the header and footer
        page.draw_rect(header_rect, fill=(1, 1, 1))  # Fill the header area with white color
        page.draw_rect(footer_rect, fill=(1, 1, 1))  # Fill the header area with white color
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
            # Get the bounding boxes of tables on the page
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

def remove_common_lines(file1_path, file2_path, output_path):
    """
    Remove common lines between two files and save the result to a new file.

    Args:
        file1_path (str): Path to the first file.
        file2_path (str): Path to the second file.
        output_path (str): Path to save the cleaned text.
    """
    # Read the content of file1
    with open(file1_path, 'r', encoding='utf-8') as file1:
        lines_file1 = file1.readlines()
    # 读取文件2中的内容
    with open(file2_path, 'r', encoding='utf-8') as file2:
        lines_file2 = file2.readlines()
    # Read the content of file2
    with open(output_path, 'w', encoding='utf-8') as output_file:
        for line in lines_file1:
            if line not in lines_file2:
                output_file.write(line)

def main():
    """
    Process PDF files and extract text, then remove common lines between the extracted text and covered text.
    """
    input_folder = "/data/chengsiyu/result/txt/公司公告/noheader/blankpdf/"  # Input PDF folder path
    # Iterate through all files in the folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            input_pdf = os.path.join(input_folder, filename)
            output_pdf = "/data/chengsiyu/result/txt/公司公告/solution2/output.pdf"  # Cropped PDF output path
            covered_text_path = "/data/chengsiyu/result/txt/公司公告/solution2/covered_text.txt"  # Covered text output path
            final_output_path = "/data/chengsiyu/result/txt/公司公告/noheader/resttxt/" + os.path.splitext(filename)[
                0] + ".txt"  # Final text output path
            crop_header_footer(input_pdf, output_pdf)
            extract_text_except_tables(input_pdf, final_output_path)
            extract_covered_text(input_pdf, covered_text_path)
            file1_path = final_output_path
            file2_path = covered_text_path
            output_path = final_output_path
            # Remove common lines between file1 and file2
            remove_common_lines(file1_path, file2_path, output_path)
            # Remove temporary files
            os.remove(output_pdf)
            os.remove(covered_text_path)

if __name__ == "__main__":
    main()