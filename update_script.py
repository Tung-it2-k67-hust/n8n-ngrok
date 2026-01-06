
import os

new_content = r'''#!/usr/bin/env python3
"""
openrouter_pdf_analyzer.py

Chức năng:
    1. Quét các file .pdf trong các thư mục cấu hình hoặc file cụ thể qua tham số.
    2. Đọc nội dung và CHIA NHỎ (Chunking) theo số trang quy định.
    3. Gửi từng chunk lên OpenRouter API để tạo "Developer Decision Guide" (Markdown).
    4. Ghi trực tiếp kết quả vào file .md (cùng thư mục với file gốc).

Cấu hình:
    - FOLDERS_TO_SCAN: Danh sách thư mục cần quét.
    - OPENROUTER_API_KEY: Key OpenAI/OpenRouter.
    - CHUNK_SIZE: Số trang mỗi lần gửi.
"""
import os
import sys
import json
import glob
import time
import pdfplumber
import requests

# ---------- USER CONFIG ----------
FOLDERS_TO_SCAN = [
    r"E:\n8n-ngrok\n8n_test",
    r"E:\n8n-ngrok\web_slide"
]

OPENROUTER_API_KEY = "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"

# Model trên OpenRouter.
MODEL = "xiaomi/mimo-v2-flash:free" 

CHUNK_SIZE = 10  # Số trang mỗi lần gửi đi phân tích
# ----------------------------------

URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    # "HTTP-Referer": "http://localhost:3000", # Optional
}

def extract_text_from_pdf(path):
    """Đọc toàn bộ trang PDF."""
    pages = []
    try:
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                text = p.extract_text() or ""
                pages.append(text)
    except Exception as e:
        print(f"Lỗi đọc PDF {path}: {e}")
    return pages

def chunk_pages(pages, size):
    """Chia danh sách trang thành các chunk nhỏ."""
    for i in range(0, len(pages), size):
        yield pages[i:i + size], i + 1  # Trả về (chunk, start_page_num)

def build_prompt(chunk_text, start_page, previous_concepts=None):
    """Tạo prompt cho từng chunk."""
    
    prev_concepts_str = previous_concepts if previous_concepts else "None"

    return f"""
You are a SENIOR SOFTWARE ENGINEER and TECHNICAL INSTRUCTOR.

Your task is to produce a **DEVELOPER DECISION GUIDE**
for Kotlin Coroutines (or the specific topic in the text) that can be:
- Printed as slides
- Brought into an exam room
- Used as a quick reference while coding

========================
IMPORTANT RULES
========================
- DO NOT summarize like a textbook.
- DO NOT repeat the same concept multiple times.
- TRULY MERGE or OMIT duplicated concepts if they were listed in "Previously covered concepts".
- KEEP ALL technical terms, APIs, and keywords in ENGLISH.
- ALL explanations MUST be in VIETNAMESE.
- PRIORITIZE: "WHEN TO USE WHAT" over theory.
- NO IMAGES.
- TEXT, TABLES, CODE ONLY.
- Be concise but information-dense.

Previously covered concepts (DO NOT repeat):
{prev_concepts_str}

========================
WHAT TO BUILD (for the provided text chunk)
========================

Build a **STRUCTURED MARKDOWN DOCUMENT** with the following sections (fill ONLY if the text chunk contains relevant info):

--------------------------------
SECTION 1: CORE MENTAL MODEL
--------------------------------
Explain (if present in text):
- What concepts are (vs others)
- Key mental models

--------------------------------
SECTION 2: DECISION TABLES (VERY IMPORTANT)
--------------------------------

Provide tables answering "When to use X vs Y" (if present in text).
Each table MUST include: Use case, Should use, Why, Common mistake.

--------------------------------
SECTION 3: BUILDERS & SCOPE – HOW THEY RELATE
--------------------------------
Relationships, hierarchies, structure (if present).

--------------------------------
SECTION 4: CODE PATTERNS (EXAM-READY)
--------------------------------
For EACH pattern found:
- When to use (Vietnamese)
- Why this pattern is correct
- Minimal but COMPLETE code example

--------------------------------
SECTION 5: ANTI-PATTERNS & WARNINGS
--------------------------------
List dangerous practices found in the text.

--------------------------------
SECTION 6: ONE-PAGE CHEAT SHEET ITEMS
--------------------------------
Add rules found here to the cheat sheet.

========================
INPUT TEXT (Chunk starting page {start_page})
========================
{chunk_text}

========================
OUTPUT FORMAT
========================
- Output ONLY Markdown
- Use headings, tables, and code blocks
- NO JSON
- NO explanations outside the document
- If a section has no information in this chunk, OMIT IT.
"""

def call_openrouter(prompt):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.post(URL, headers=HEADERS, data=json.dumps(payload), timeout=120)
            if resp.status_code == 200:
                result = resp.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    return ""
            elif resp.status_code == 429:
                print(f"  -> Rate limit (429). Đợi 10s... (Lần {attempt+1})")
                time.sleep(10)
            else:
                print(f"  -> API Error {resp.status_code}: {resp.text}")
                time.sleep(2)
        except Exception as e:
            print(f"  -> Request Exception: {e}")
            time.sleep(2)
    return None

def process_single_file(pdf_path):
    """Xử lý một file PDF duy nhất."""
    if not os.path.exists(pdf_path):
        print(f"File không tồn tại: {pdf_path}")
        return

    filename = os.path.basename(pdf_path)
    directory = os.path.dirname(pdf_path)
    
    # Output file nằm cùng thư mục với file gốc
    output_filename = filename.replace(".pdf", "_GUIDE.md")
    output_path = os.path.join(directory, output_filename)
    
    if os.path.exists(output_path):
        print(f"File đã được phân tích trước đó (bỏ qua): {output_path}")
        return

    print(f"\n>> Đang xử lý: {filename}")
    
    all_pages = extract_text_from_pdf(pdf_path)
    if not all_pages:
        print("   File trống hoặc không đọc được text.")
        return
    
    total_pages = len(all_pages)
    print(f"   Tổng số trang: {total_pages}. Chia thành các chunk {CHUNK_SIZE} trang.")

    # Init Output File
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# DEVELOPER DECISION GUIDE: {filename}\\n\\n")
        f.write(f"> Generated by OpenRouter ({MODEL}) on {time.strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")

    previous_concepts_accumulator = []

    # Loop qua từng chunk
    for chunk, start_page in chunk_pages(all_pages, CHUNK_SIZE):
        chunk_range = f"{start_page}-{min(start_page+CHUNK_SIZE-1, total_pages)}"
        print(f"   Running chunk trang {chunk_range}...")
        
        chunk_text = "\\n\\n".join(chunk)
        
        prev_concepts_str = ", ".join(previous_concepts_accumulator[-5:]) if previous_concepts_accumulator else "None"
        
        prompt = build_prompt(chunk_text, start_page, prev_concepts_str)
        
        content = call_openrouter(prompt)
        
        if content:
            # Basic extraction of headers to track "concepts" roughly
            lines = content.split('\\n')
            for line in lines:
                if line.startswith('## '):
                    header = line.replace('## ', '').strip()
                    if header not in previous_concepts_accumulator:
                        previous_concepts_accumulator.append(header)

            # Write directly to file
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(f"\\n\\n<!-- CHUNK {chunk_range} -->\\n\\n")
                f.write(content)
            
            print(f"     -> Xong chunk {chunk_range}.")
        else:
            print(f"     -> Lỗi: Không nhận được phản hồi cho chunk {chunk_range}")

        # Avoid hitting rate limits too hard
        time.sleep(2)
    
    print(f"   ✅ Đã lưu kết quả tại: {output_path}")

def main():
    # Case 1: Chạy với tham số dòng lệnh (cho n8n hoặc manual run specific file)
    # Usage: python script.py "path/to/file.pdf"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        print(f"Chế độ Single File: {target_file}")
        process_single_file(target_file)
        return

    # Case 2: Scan directories (chạy mặc định)
    print("Chế độ Scan Folder...")
    for folder in FOLDERS_TO_SCAN:
        if not os.path.exists(folder):
            print(f"Không tìm thấy thư mục: {folder} (Sẽ tạo mới)")
            try:
                os.makedirs(folder)
            except OSError:
                pass
            continue
        
        print(f"\n--- Quét folder: {folder} ---")
        pdf_files = glob.glob(os.path.join(folder, "*.pdf"))
        
        if not pdf_files:
            print("   (Không có file PDF nào)")
            continue
            
        for pdf_path in pdf_files:
            process_single_file(pdf_path)

    print("\\nHoàn tất xử lý tất cả file.")

if __name__ == "__main__":
    main()
'''

with open(r"e:\n8n-ngrok\openrouter_pdf_analyzer.py", "w", encoding="utf-8") as f:
    f.write(new_content)
print("File rewritten successfully")
