import os
import sys
import json
import time
import re
import pdfplumber
import requests
from typing import List, Tuple, Dict, Optional

# ---------- CONFIG ----------
MODEL = "xiaomi/mimo-v2-flash:free"
OPENROUTER_API_KEY = "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"
CHUNK_PAGES_DEFAULT = 10 # Số trang mỗi lần gửi cho AI
URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS_BASE = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "http://localhost:5000", # Required by OpenRouter for some models
    "X-Title": "Data Engineering Book Splitter"
}

# Regex nhận diện Chương và Phần cho sách tiếng Anh
HEADING_PATTERNS = [
    r"^\s*Chapter\s+\d+",           # Chapter 1
    r"^\s*Part\s+[IVXLCDM]+",      # Part I
    r"^\s*Appendix\s+[A-Z]",        # Appendix A
]

def clean_filename(title: str) -> str:
    """Làm sạch tên file để không chứa ký tự đặc biệt."""
    return re.sub(r'[\\/*?:\"<>|]', "", title).strip().replace(" ", "_")

def extract_text_from_pdf(path: str) -> List[str]:
    pages = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            pages.append(p.extract_text() or "")
    return pages

def detect_sections(pages: List[str]) -> List[Dict]:
    """Phát hiện các chương dựa trên heading."""
    starts = []
    pattern_compiled = [re.compile(p, re.IGNORECASE) for p in HEADING_PATTERNS]

    for i, page in enumerate(pages):
        lines = page.strip().splitlines()
        if not lines: continue
        
        # Thường tiêu đề chương nằm ở 10 dòng đầu trang
        for ln in lines[:10]:
            for pat in pattern_compiled:
                if pat.search(ln):
                    starts.append({"title": ln.strip(), "start_page": i + 1})
                    break
            else: continue
            break

    sections = []
    if not starts:
        return [{"title": "Full_Book", "start": 1, "end": len(pages)}]

    for idx, item in enumerate(starts):
        start = item["start_page"]
        end = starts[idx + 1]["start_page"] - 1 if idx + 1 < len(starts) else len(pages)
        # Bổ sung logic lấy tên chương đầy đủ hơn nếu dòng tiêu đề quá ngắn
        sections.append({"title": item["title"], "start": start, "end": end})
    
    return sections

def call_openrouter(prompt: str) -> Optional[str]:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    try:
        resp = requests.post(URL, headers=HEADERS_BASE, json=payload, timeout=120)
        if resp.status_code == 200:
            result = resp.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                print(f"Empty response from AI: {result}")
        else:
            print(f"Error calling AI (Status {resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"Exception during AI call: {e}")
    return None

def build_chunk_prompt(chunk_text: str, section_title: str) -> str:
    return f"""
Bạn là một chuyên gia Data Engineering. Hãy dịch và tổng hợp nội dung sau đây từ chương "{section_title}" của sách sang tiếng Việt dưới dạng Markdown.

YÊU CẦU:
1. Giữ nguyên các thuật ngữ chuyên ngành bằng tiếng Anh (ví dụ: Data Pipeline, Ingestion, Storage, Orchestration) nhưng có giải thích tiếng Việt bên cạnh.
2. Viết theo phong cách "Decision Guide" (Hướng dẫn ra quyết định): tập trung vào Tại sao dùng? Khi nào dùng? Ưu nhược điểm.
3. Cấu trúc Markdown rõ ràng (##, ###).
4. Nếu có bảng so sánh hoặc kiến trúc, hãy mô tả bằng Markdown table.

NỘI DUNG GỐC:
{chunk_text}
"""

def process_book(pdf_path: str):
    filename = os.path.basename(pdf_path)
    book_folder = clean_filename(filename.replace(".pdf", ""))
    
    if not os.path.exists(book_folder):
        os.makedirs(book_folder)
        print(f"Created folder: {book_folder}")

    pages = extract_text_from_pdf(pdf_path)
    sections = detect_sections(pages)
    print(f"Detected {len(sections)} sections.")

    for i, sec in enumerate(sections):
        sec_title = sec["title"]
        # Tạo tên file: 01_Chapter_1_Data_Engineering_Described.md
        file_name = f"{i:02d}_{clean_filename(sec_title)}.md"
        file_path = os.path.join(book_folder, file_name)
        
        print(f"\n--- Processing: {sec_title} (Pages {sec['start']}-{sec['end']}) ---")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {sec_title}\n\n")
            
            # Chia nhỏ nội dung chương thành các chunk để AI xử lý không bị quá giới hạn
            for start_p in range(sec["start"], sec["end"] + 1, CHUNK_PAGES_DEFAULT):
                end_p = min(start_p + CHUNK_PAGES_DEFAULT - 1, sec["end"])
                print(f"  > Processing pages {start_p} to {end_p}...")
                
                chunk_text = "\n\n".join(pages[start_p-1 : end_p])
                prompt = build_chunk_prompt(chunk_text, sec_title)
                
                response = call_openrouter(prompt)
                if response:
                    f.write(response + "\n\n---\n\n")
                    f.flush() # Lưu ngay lập tức
                time.sleep(1) # Tránh bị rate limit

    print("\nDONE! All chapters have been saved in the folder.")

if __name__ == "__main__":
    pdf_input = "Fundamentals-of-Data-Engineering.pdf" # Đổi tên file của bạn ở đây
    process_book(pdf_input)
