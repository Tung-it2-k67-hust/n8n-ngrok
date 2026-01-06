
import os

new_code = r'''#!/usr/bin/env python3
"""
openrouter_pdf_analyzer.py

Module xử lý PDF và tương tác với OpenRouter API.
Hỗ trợ:
1. CLI: Quét thư mục, xử lý danh sách file.
2. Web: Generator để streaming kết quả về frontend.
"""
import os
import sys
import json
import glob
import time
import pdfplumber
import requests

# ---------- CONFIG DEFAULTS ----------
# Các thư mục mặc định khi chạy scan toàn bộ
DEFAULT_FOLDERS_TO_SCAN = [
    r"E:\n8n-ngrok\n8n_test",
    r"E:\n8n-ngrok\web_slide"
]

OPENROUTER_API_KEY = "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"
MODEL = "xiaomi/mimo-v2-flash:free"
CHUNK_SIZE = 10
URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:5000",
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
        yield pages[i:i + size], i + 1

def build_prompt(chunk_text, start_page, previous_concepts=None):
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
        "messages": [{"role": "user", "content": prompt}]
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.post(URL, headers=HEADERS, data=json.dumps(payload), timeout=120)
            if resp.status_code == 200:
                result = resp.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                return ""
            elif resp.status_code == 429:
                time.sleep(10)
            else:
                print(f"DEBUG: {resp.status_code} - {resp.text}")
                time.sleep(2)
        except Exception as e:
            print(f"DEBUG: Exception {e}")
            time.sleep(2)
    return None

def analyze_pdf_stream(pdf_path):
    """
    Generator chính xử lý file PDF.
    Yields: Dictionary events {'type': 'log'|'chunk'|'error', 'message'|'content': '...'}
    """
    if not os.path.exists(pdf_path):
        yield {'type': 'error', 'message': f"File not found: {pdf_path}"}
        return

    filename = os.path.basename(pdf_path)
    yield {'type': 'log', 'message': f"Reading PDF: {filename}..."}
    
    all_pages = extract_text_from_pdf(pdf_path)
    if not all_pages:
        yield {'type': 'error', 'message': "File is empty or unreadable."}
        return

    total_pages = len(all_pages)
    yield {'type': 'log', 'message': f"Total pages: {total_pages}. Chunk size: {CHUNK_SIZE}."}

    # Header cho file Markdown
    header_md = f"# DEVELOPER DECISION GUIDE: {filename}\n\n> Generated by OpenRouter ({MODEL}) on {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    yield {'type': 'chunk', 'content': header_md}

    previous_concepts_accumulator = []

    for chunk, start_page in chunk_pages(all_pages, CHUNK_SIZE):
        chunk_range = f"{start_page}-{min(start_page+CHUNK_SIZE-1, total_pages)}"
        yield {'type': 'log', 'message': f"Processing chunk {chunk_range}..."}

        chunk_text = "\n\n".join(chunk)
        prev_concepts_str = ", ".join(previous_concepts_accumulator[-5:]) if previous_concepts_accumulator else "None"
        
        prompt = build_prompt(chunk_text, start_page, prev_concepts_str)
        content = call_openrouter(prompt)

        if content:
            content = content.strip()
            # Simple concept extraction for context
            lines = content.split('\n')
            for line in lines:
                if line.startswith('## '):
                    header = line.replace('## ', '').strip()
                    if header not in previous_concepts_accumulator:
                        previous_concepts_accumulator.append(header)
            
            chunk_md = f"\n\n<!-- CHUNK {chunk_range} -->\n\n{content}"
            yield {'type': 'chunk', 'content': chunk_md}
        else:
            yield {'type': 'log', 'message': f"Warning: No response for chunk {chunk_range}"}
        
        time.sleep(1)

    yield {'type': 'log', 'message': "Analysis complete."}

# --- CLI HELPERS ---

def process_single_file_cli(pdf_path):
    """Helper để chạy CLI (lưu file vào đĩa)."""
    directory = os.path.dirname(pdf_path)
    filename = os.path.basename(pdf_path)
    output_filename = filename.replace(".pdf", "_GUIDE.md")
    output_path = os.path.join(directory, output_filename)

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"Skip (Done): {filename}")
        return

    print(f"\n>> Start: {filename} -> {output_filename}")
    
    with open(output_path, "w", encoding="utf-8") as f:
        pass # Create/Trace file

    for event in analyze_pdf_stream(pdf_path):
        if event['type'] == 'log':
            print(f"   {event['message']}")
        elif event['type'] == 'chunk':
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(event['content'])
        elif event['type'] == 'error':
            print(f"   ERROR: {event['message']}")

    print(f"   Query finished: {output_path}")

def main():
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.isfile(target):
            process_single_file_cli(target)
        else:
            print(f"File not found: {target}")
        return

    print(">>> Scanning configured folders...")
    for folder in DEFAULT_FOLDERS_TO_SCAN:
        if not os.path.exists(folder):
            print(f"Folder not found, creating: {folder}")
            os.makedirs(folder, exist_ok=True)
            continue
        
        print(f"\n--- Checking: {folder} ---")
        pdf_files = glob.glob(os.path.join(folder, "*.pdf"))
        
        if not pdf_files:
            print("   (No PDF files)")
            continue

        for pdf in pdf_files:
            process_single_file_cli(pdf)

    print("\n>>> All tasks finished.")

if __name__ == "__main__":
    main()
'''

with open(r"e:\n8n-ngrok\openrouter_pdf_analyzer.py", "w", encoding="utf-8") as f:
    f.write(new_code)
print("Updated openrouter_pdf_analyzer.py v2")
