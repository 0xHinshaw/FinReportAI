import os
import fitz
import pdfplumber
import shutil
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
        header_rect = fitz.Rect(0, 0, page.rect.width, 75)
        footer_rect = fitz.Rect(0, page.rect.height - 75, page.rect.width, page.rect.height)
        page.draw_rect(header_rect, fill=(1, 1, 1))
        page.draw_rect(footer_rect, fill=(1, 1, 1))
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
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text_except_tables)

def remove_covered_text(input_text_path, covered_text_path, output_path, original_pdf_path):
    """
    Remove covered text from the input text and save the result to a file.

    Args:
        input_text_path (str): Path to the input text file.
        covered_text_path (str): Path to the file containing covered text.
        output_path (str): Path to save the cleaned text.
        original_pdf_path (str): Path to the original PDF file.
    """
    with open(input_text_path, 'r', encoding='utf-8') as input_file:
        input_text = input_file.readlines()
    with open(covered_text_path, 'r', encoding='utf-8') as covered_file:
        covered_text = covered_file.readlines()
    # Check if the text in the header and footer sections is blank.
    if not any(line.strip() for line in covered_text):
        # If the TXT file corresponding to the header and footer sections is blank, save a copy of the PDF file to the specified directory.
        shutil.copy(original_pdf_path, '/data/chengsiyu/result/txt/公司公告/noheader/pdf/')
        extract_text_except_tables(original_pdf_path, output_path)
    else:
        # Iterate through the content of 'covered_text' line by line and delete the matched lines in the input text.
        cleaned_text = []
        for line in input_text:
            if line not in covered_text:
                cleaned_text.append(line)
        # Save the result to the specified file.
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.writelines(cleaned_text)

def is_scanned_page(page):
    """
    Check if a page in the PDF document is scanned (contains only images).

    Args:
        page: Page object from PyMuPDF (fitz).

    Returns:
        bool: True if the page is scanned, False otherwise.
    """
    text = page.get_text()
    return len(text.strip()) < 50

def analyze_pdf(file_path, destination_folder):
    """
    Analyze a PDF file to determine if it contains scanned pages.

    Args:
        file_path (str): Path to the PDF file.
        destination_folder (str): Path to the folder where scanned PDFs will be moved.

    Returns:
        bool: True if the PDF contains scanned pages, False otherwise.
    """
    try:
        doc = fitz.open(file_path)
        for page in doc:
            if is_scanned_page(page):
                # Close the document and return the flag indicating the presence of scanned pages.
                doc.close()
                return True
        doc.close()
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return False

def move_scanned_pdfs(source_folder, destination_folder):
    """
    Move scanned PDF files from the source folder to the destination folder.

    Args:
        source_folder (str): Path to the folder containing PDF files.
        destination_folder (str): Path to the folder where scanned PDFs will be moved.
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root, file)
                if analyze_pdf(file_path, destination_folder):
                    shutil.move(file_path, os.path.join(destination_folder, file))

# 主函数
def main():
    """
    Main function to process PDF files and extract text.
    """
    input_dir = "/data/chengsiyu/result/txt/公司公告/blankpdf_re/"  # PDF file path
    output_dir = "/data/chengsiyu/result/txt/公司公告/solution/outpdf"  # the cropped PDF file path
    covered_text_dir = "/data/chengsiyu/result/txt/公司公告/solution/covered_text"  # covered text file path
    mid_output_dir = "/data/chengsiyu/result/txt/公司公告/solution/midtxt"  # Intermediate text output file path
    final_output_dir = "/data/chengsiyu/result/txt/公司公告/noheader/txt/"  # final text output file path
    error_folder = "/data/chengsiyu/result/txt/公司公告/solution/error"  # error folder path
    scanned_pdf_dir = "/data/chengsiyu/result/txt/公司公告/solution/scanned"  # scanned PDF folder path

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(covered_text_dir, exist_ok=True)
    os.makedirs(final_output_dir, exist_ok=True)
    os.makedirs(error_folder, exist_ok=True)
    os.makedirs(mid_output_dir, exist_ok=True)
    os.makedirs(scanned_pdf_dir, exist_ok=True)

    # Move scanned PDF files to the specified folder.
    move_scanned_pdfs(input_dir, scanned_pdf_dir)
    print("Scanned PDF files have been moved.")

    # Iterate through PDF files in the input folder.
    for pdf_file in os.listdir(input_dir):
        if pdf_file.endswith(".pdf"):
            input_pdf = os.path.join(input_dir, pdf_file)
            output_pdf = os.path.join(output_dir, pdf_file)
            covered_text_path = os.path.join(covered_text_dir, os.path.splitext(pdf_file)[0] + ".txt")
            mid_output_path = os.path.join(mid_output_dir, os.path.splitext(pdf_file)[0] + ".txt")
            final_output_path = os.path.join(final_output_dir, os.path.splitext(pdf_file)[0] + ".txt")
            try:
                crop_header_footer(input_pdf, output_pdf)
                extract_text_except_tables(output_pdf, mid_output_path)
                extract_covered_text(input_pdf, covered_text_path)
                remove_covered_text(mid_output_path, covered_text_path, final_output_path, input_pdf)
            except Exception as e:
                error_file_path = os.path.join(error_folder, pdf_file)
                shutil.copyfile(input_pdf, error_file_path)
                print(f"Error processing {input_pdf}: {str(e)}")
            finally:
                if os.path.exists(output_pdf):
                    os.remove(output_pdf)
                if os.path.exists(covered_text_path):
                    os.remove(covered_text_path)

if __name__ == "__main__":
    main()