#!/usr/bin/env python3
"""
gemini_pdf_analyzer.py

Usage:
    - Edit FOLDER_PATH and API_KEY below.
    - Install dependencies: pip install pdfplumber requests
    - (Optional) Install poppler and pdftotext if you prefer command-line extraction.
    - Run: python gemini_pdf_analyzer.py

What it does:
    1. Finds all .pdf files in FOLDER_PATH
    2. Extracts text per PDF (page-by-page) using pdfplumber
    3. Builds a careful prompt in Vietnamese asking Gemini to:
        - Split the PDF into "lessons"
        - For each lesson, identify code blocks, detect language, show syntax and explain why code is written that way
        - Return a structured JSON with lessons, code_blocks with explanations, and a detailed analysis
    4. Calls Gemini REST endpoint using your API key (x-goog-api-key header).
    5. Saves a JSON report next to each PDF (same name + .analysis.json)

NOTE: Modify MODEL and ENDPOINT if you prefer a different Gemini model/version.
"""
import os
import json
import glob
import time
import pdfplumber
import requests

# ---------- USER CONFIG ----------
FOLDER_PATH = r"E:\n8n-ngrok\n8n_test"
API_KEY = "AIzaSyAz-eJ2ctwlHN3Cysdc1zACPewlFpxYucQ"
MODEL = "gemini-1.5-flash"  # Changed to stable model for better rate limits
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
# ----------------------------------

HEADERS = {
    "Content-Type": "application/json",
    "x-goog-api-key": API_KEY
}

def extract_text_from_pdf(path):
    """Return list of pages (each page is text). Uses pdfplumber."""
    pages = []
    try:
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                text = p.extract_text() or ""
                pages.append(text)
    except Exception as e:
        print(f"Error reading PDF {path}: {e}")
    return pages

def build_prompt(pdf_name, pages):
    joined = "\n\n".join(f"--- PAGE {i+1} ---\n{p}" for i,p in enumerate(pages))
    prompt = f"""
Bạn là một trợ giảng thông minh, đầu ra CHỈ LÀ JSON hợp lệ UTF-8. Đọc nội dung PDF (tên file: {pdf_name}) được đưa bên dưới, tiếng Việt. Nhiệm vụ:
1) Chia tài liệu thành các "lesson" (bài học). Mỗi lesson cần:
   - title: tiêu đề (nếu có, hoặc suy đoán ngắn)
   - pages: danh sách số trang (1-based)
   - summary: tóm tắt chi tiết (không quá ngắn) giải thích mục tiêu lesson
   - details: phân tích chi tiết các phần quan trọng (giải thích ý tưởng, thuật toán, điểm cần lưu ý)
   - code_blocks: mảng các đối tượng {{"language","code","line_range","why","what_it_does","complexity_notes"}}
2) Khi phát hiện đoạn code:
   - Nhận diện ngôn ngữ (Java, Kotlin, XML layout, Python, C, v.v.) và ghi vào "language"
   - Đưa nguyên văn code (preserve indentation) vào "code"
   - Giải thích từng phần: tại sao code làm như vậy, alternatives (nếu có), lỗi/anti-patterns cần tránh
   - Nếu code gọi API hay framework Android (Activity, Intent, RecyclerView...), giải thích luồng dữ liệu và lifecycle liên quan
3) Nếu có pseudo-code hoặc bullets mô tả thuật toán, chuyển thành mô tả step-by-step và (nếu cần) ví dụ ngắn
4) Output phải là 1 JSON object:
{{
  "file": "<pdf file name>",
  "lessons": [
    {{
      "title": "...",
      "pages": [1,2],
      "summary": "...",
      "details": "...",
      "code_blocks": [
        {{
          "language": "...",
          "code": "...",
          "line_range": [10,18],
          "why": "...",
          "what_it_does": "...",
          "complexity_notes": "..."
        }}
      ]
    }}
  ]
}}
Dưới đây là nội dung PDF:
{joined}
Hãy trả về CHỈ JSON đúng theo schema ở trên, không thêm markdown formatting.
"""
    return prompt

def call_gemini(prompt):
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]} 
        ]
    }
    
    max_retries = 5
    for attempt in range(max_retries):
        resp = requests.post(ENDPOINT, headers=HEADERS, json=payload, timeout=120)
        if resp.status_code == 429:
            print(f"Rate limit hit (429). Waiting 20 seconds before retry {attempt+1}/{max_retries}...")
            time.sleep(20)
            continue
        if resp.status_code != 200:
            raise RuntimeError(f"API error {resp.status_code}: {resp.text}")
        break

    if resp.status_code != 200:
        raise RuntimeError(f"API error {resp.status_code} after retries: {resp.text}")

    data = resp.json()
    
    text = None
    if "candidates" in data and isinstance(data["candidates"], list):
        first = data["candidates"][0]
        if "content" in first and "parts" in first["content"]:
             parts = first["content"]["parts"]
             if parts and "text" in parts[0]:
                 text = parts[0]["text"]
    
    if not text:
        text = json.dumps(data, ensure_ascii=False)
    return text

def main():
    if not os.path.exists(FOLDER_PATH):
        print(f"Creating folder: {FOLDER_PATH}")
        os.makedirs(FOLDER_PATH)
        
    pdf_paths = glob.glob(os.path.join(FOLDER_PATH, "*.pdf"))
    if not pdf_paths:
        print("Không tìm thấy file PDF trong folder:", FOLDER_PATH)
        return
        
    for path in pdf_paths:
        name = os.path.basename(path)
        print("Processing", name)
        pages = extract_text_from_pdf(path)
        if not pages:
            print("Skipping (no text)")
            continue
        prompt = build_prompt(name, pages)
        try:
            ai_text = call_gemini(prompt)
            # Cleanup potential markdown code blocks
            clean_text = ai_text.strip()
            if clean_text.startswith("```json"): clean_text = clean_text[7:]
            if clean_text.startswith("```"): clean_text = clean_text[3:]
            if clean_text.endswith("```"): clean_text = clean_text[:-3]
            
            parsed = json.loads(clean_text)
        except Exception as e:
            print("Error:", e)
            parsed = {"raw": ai_text} if 'ai_text' in locals() else {"error": str(e)}

        out_path = os.path.join(os.path.dirname(path), name + ".analysis.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
        print("Saved to", out_path)
        time.sleep(1)

if __name__ == "__main__":
    main()