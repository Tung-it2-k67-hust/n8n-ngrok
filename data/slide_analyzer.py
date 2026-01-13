import os
import time
import re
from dotenv import load_dotenv
import requests
from typing import List, Optional, Tuple

import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Tải các biến môi trường từ tệp .env
load_dotenv()

# ================= CONFIG =================
# Get API Key from .env file
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "xiaomi/mimo-v2-flash:free"
URL = "https://openrouter.ai/api/v1/chat/completions"

# --- USER-REQUESTED PATHS ---
# Point to the directory containing the medical PDF
PDF_DIR = r"E:\n8n-ngrok\data\y_hoc"
# Create a dedicated output directory for the analysis
OUTPUT_DIR = r"E:\n8n-ngrok\data\y_hoc_analysis"

# Process 5 pages per API call
CHUNK_PAGES_DEFAULT = 5

# ================= OCR CONFIG =================
DPI = 300
OCR_LANG = "vie+eng"  # Vietnamese + English for medical terms

# IMPORTANT: If Tesseract is not in your system's PATH, uncomment and set the path here
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ================= NETWORK HEADERS =================
HEADERS_BASE = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "http://localhost:5000", # Can be any dummy URL
    "X-Title": "Medical PDF Analyzer"
}

# ================= UTILS =================
def clean_filename(title: str) -> str:
    """Removes invalid characters from a string to make it a valid filename."""
    return re.sub(r'[\\/*?:\"<>|]', "", title).strip().replace(" ", "_")

# ================= OCR ENGINE =================
def extract_text_from_pdf_ocr(
    pdf_path: str,
    start_page: int,
    end_page: int
) -> List[str]:
    """
    Converts specified pages of a PDF to images and uses Tesseract to extract text.
    This is necessary for scanned or image-based PDFs.
    """
    print(f"  OCR'ing pages {start_page} -> {end_page}...")
    try:
        images = convert_from_path(
            pdf_path,
            dpi=DPI,
            first_page=start_page,
            last_page=end_page,
            # poppler_path=r"C:\path\to\poppler\bin" # Add if poppler is not in PATH
        )

        pages_text = []
        for idx, img in enumerate(images, start=start_page):
            # Use Tesseract to get text from the image
            text = pytesseract.image_to_string(img, lang=OCR_LANG)
            text = text.strip()
            pages_text.append(text if text else f"[Trang {idx}: Không nhận dạng được chữ]")
        
        print(f"    -> Extracted text from {len(pages_text)} pages.")
        return pages_text
    except Exception as e:
        print(f"    !! ERROR during OCR on pages {start_page}-{end_page}: {e}")
        print("    !! This might be a Poppler or Tesseract issue. Make sure they are installed and in PATH.")
        return []


# ================= AI CALLER =================
def call_openrouter(prompt: str) -> Tuple[Optional[str], Optional[str]]:
    """Sends the prompt to the OpenRouter API and returns the response."""
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2, # Lower temperature for more factual, less creative output
    }
    try:
        resp = requests.post(URL, headers=HEADERS_BASE, json=payload, timeout=240) # Increased timeout
        resp.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx) 
        
        data = resp.json()
        return data["choices"][0]["message"]["content"], None
    except requests.exceptions.HTTPError as e:
        error_message = f"AI API HTTP Error {e.response.status_code}: {e.response.text}"
        print(f"  !! {error_message}")
        return None, error_message
    except requests.exceptions.RequestException as e:
        error_message = f"AI API Request Exception: {e}"
        print(f"  !! {error_message}")
        return None, error_message
    except Exception as e:
        error_message = f"An unexpected error occurred in call_openrouter: {e}"
        print(f"  !! {error_message}")
        return None, error_message

# ================= PROMPT BUILDER =================
def build_medical_prompt(chunk_text: str, pdf_name: str) -> str:
    """Creates a specialized prompt for analyzing medical texts."""
    return f"""
Bạn là một trợ lý y khoa AI, chuyên tóm tắt và hệ thống hóa tài liệu y văn.

Nhiệm vụ của bạn là phân tích nội dung đã được OCR từ các trang của tài liệu "{pdf_name}". Dựa vào nội dung đó, hãy trình bày lại các kiến thức y khoa bằng tiếng Việt theo định dạng Markdown chuyên nghiệp.

**YÊU CẦU CỤ THỂ:**

1.  **Xác định và Tóm tắt Bệnh học/Hội chứng:** Với mỗi bệnh lý hoặc hội chứng tìm thấy, hãy cấu trúc thông tin theo các mục sau:
    *   **Định nghĩa/Tổng quan:** Mô tả ngắn gọn về bệnh.
    *   **Nguyên nhân & Sinh lý bệnh:** Giải thích cơ chế gây bệnh.
    *   **Triệu chứng lâm sàng:** Liệt kê các dấu hiệu và triệu chứng quan trọng (cơ năng và thực thể).
    *   **Cận lâm sàng:** Nêu các xét nghiệm, chẩn đoán hình ảnh, hoặc phương pháp cận lâm sàng cần thiết để chẩn đoán.
    *   **Tiêu chuẩn chẩn đoán:** Nếu tài liệu đề cập, hãy ghi rõ các tiêu chuẩn được sử dụng để chẩn đoán xác định.
    *   **Hướng điều trị:** Tóm tắt các nguyên tắc và phác đồ điều trị chính.

2.  **Định dạng Markdown:**
    *   Sử dụng headings (`##`, `###`), bullet points (`*`, `-`), và bold (`**text**`) để làm nổi bật và cấu trúc thông tin.
    *   Tạo bảng (nếu cần) để so sánh các triệu chứng hoặc phác đồ.

3.  **Xử lý nhiễu OCR:**
    *   Thông minh bỏ qua các từ, ký tự, hoặc dòng chữ vô nghĩa do lỗi OCR.
    *   Tuyệt đối không bịa đặt thông tin không có trong văn bản được cung cấp. Nếu một mục (ví dụ: "Hướng điều trị") không có trong đoạn trích, hãy ghi là "Không được đề cập trong đoạn này."

4.  **Ngôn ngữ:**
    *   Sử dụng ngôn ngữ y khoa chính xác, chuyên nghiệp.
    *   Giữ nguyên các thuật ngữ y khoa tiếng Anh hoặc Latinh quan trọng.

**NỘI DUNG OCR ĐỂ PHÂN TÍCH:**
---
{chunk_text}
---
"""


# ================= MAIN PROCESSING LOGIC =================
def process_pdf_directory(
    pdf_dir: str,
    output_dir: str,
    start_page: int,
    end_page: Optional[int] = None
):
    """
    Processes all PDF files in a given directory within a specified page range.
    """
    os.makedirs(output_dir, exist_ok=True)

    if end_page is None:
        print("FATAL: `end_page` cannot be None for processing. Please specify an end page.")
        return

    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"No PDF files found in '{pdf_dir}'.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        
        # Create a clean filename for the output Markdown file
        clean_pdf_name = clean_filename(pdf_file.replace(".pdf", ""))
        output_filename = f"{clean_pdf_name}_ANALYSIS_p{start_page}-p{end_page}.md"
        output_md_path = os.path.join(output_dir, output_filename)

        if os.path.exists(output_md_path):
            print(f"Skipping '{pdf_file}' (pages {start_page}-{end_page}) as output already exists.")
            continue

        print(f"\n>>> PROCESSING: '{pdf_file}' (Pages: {start_page} -> {end_page})")

        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(f"# Phân tích tài liệu: {pdf_file}\n")
            f.write(f"## Phạm vi trang: {start_page} - {end_page}\n\n")

            current_page = start_page
            # Loop until all pages in the specified range are processed
            while end_page is None or current_page <= end_page:
                # Define the end of the current chunk
                chunk_end = min(current_page + CHUNK_PAGES_DEFAULT - 1, end_page)
                
                print(f"  - Chunk: Pages {current_page} -> {chunk_end}")

                # 1. Extract text via OCR
                pages_text_list = extract_text_from_pdf_ocr(
                    pdf_path,
                    current_page,
                    chunk_end
                )

                if not pages_text_list:
                    f.write(f"> **Lưu ý:** Không thể trích xuất nội dung từ trang {current_page}-{chunk_end}.\n\n")
                    current_page = chunk_end + 1
                    continue

                # 2. Combine text from pages in the chunk
                chunk_text_for_prompt = "\n\n".join(
                    f"---" + " Nội dung trang " + str(i + current_page) + " ---" + "\n" + text
                    for i, text in enumerate(pages_text_list) if text.strip()
                )

                if not chunk_text_for_prompt.strip():
                    f.write(f"> **Lưu ý:** Nội dung từ trang {current_page}-{chunk_end} rỗng hoặc không nhận dạng được.\n\n")
                    current_page = chunk_end + 1
                    continue

                # 3. Call AI for analysis
                print("    -> Sending to AI for analysis...")
                response, error = call_openrouter(build_medical_prompt(chunk_text_for_prompt, pdf_file))

                # 4. Write response to file
                if response:
                    f.write(response + "\n\n---" + "\n\n")
                    print("    -> Successfully received and wrote analysis to file.")
                else:
                    f.write(f"> **Lỗi:** Không nhận được phản hồi từ AI cho các trang {current_page}-{chunk_end}.\n")
                    if error:
                        f.write(f"> **Chi tiết lỗi:** `{error}`\n\n")
                    else:
                        f.write("\n")
                    print("    -> Failed to get analysis from AI.")
                
                f.flush() # Save progress immediately

                time.sleep(2)  # Be nice to the API

                # 5. Move to the next chunk
                current_page = chunk_end + 1

        print(f"\nDONE -> Output saved to {output_md_path}")


# ================= RUN =================
if __name__ == "__main__":
    print("Script started...")
    # This block executes when the script is run directly
    process_pdf_directory(
        pdf_dir=PDF_DIR,
        output_dir=OUTPUT_DIR,
        start_page=10,
        end_page=40  # As requested by the user
    )