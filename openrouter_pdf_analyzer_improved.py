#!/usr/bin/env python3
"""
openrouter_pdf_analyzer_improved.py

Cải tiến pipeline phân tích PDF tiếng Việt dài.
- Phát hiện chương/tiểu mạch (heuristic heading detection).
- Tóm tắt từng chương (global summary) trước khi phân tích chi tiết.
- Chia chunk bên trong từng tiểu mạch (không cắt ngang mạch logic).
- Lưu ý: KHÔNG để API key cứng trong code; đọc từ biến môi trường OPENROUTER_API_KEY.

Yêu cầu: pip install pdfplumber requests

Cách dùng:
    python openrouter_pdf_analyzer_improved.py "E:\\\\n8n-ngrok\\\\iot\\\\it4735_iot_va_ung_dung_v2025_16.1m.pdf"

"""

import os
import sys
import json
import time
import re
import pdfplumber
import requests
from typing import List, Tuple, Dict, Optional

# ---------- CONFIG ----------
MODEL = os.getenv("OPENROUTER_MODEL", "xiaomi/mimo-v2-flash:free")
OPENROUTER_API_KEY = "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"
CHUNK_PAGES_DEFAULT = int(os.getenv("CHUNK_PAGES", "12"))  # pages per chunk inside a sub-section
URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")

HEADERS_BASE = {
    "Content-Type": "application/json",
    "User-Agent": "Local-PDF-Analyzer/1.0",
    "HTTP-Referer": "http://localhost:5000",
    "X-Title": "Local PDF Analyzer"
}

# Heuristic heading patterns (Vietnamese common headings)
HEADING_PATTERNS = [
    r"^\s*(CHƯƠNG|Chương)\b",        # Chương X
    r"^\s*(Phần|Mục)\s+\d+\b",     # Phần 1, Mục 2
    r"^\s*\d+\.\s+[A-ZÀ-Ỹ]",       # 1. Tiêu đề (viết hoa)
    r"^\s*[A-Z]{3,}\s*$",            # Dòng toàn in hoa (ngắn)
]

# ------------------ PDF utilities ------------------

def extract_text_from_pdf(path: str) -> List[str]:
    """Trả về danh sách text theo trang. Nếu trang rỗng, trả về chuỗi rỗng."""
    pages = []
    try:
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                try:
                    text = p.extract_text() or ""
                except Exception:
                    text = ""
                pages.append(text)
    except Exception as e:
        raise RuntimeError(f"Lỗi đọc PDF {path}: {e}")
    return pages


def detect_sections(pages: List[str]) -> List[Dict]:
    """Phát hiện các section/tiểu mạch theo heuristic.
    Trả về list các dict: {"title": str, "start": int, "end": int}
    Trang được số hóa bắt đầu từ 1.
    Nếu không phát hiện được headings rõ rệt, trả về single section toàn bộ tài liệu.
    """
    starts: List[Tuple[int, str]] = []
    pattern_compiled = [re.compile(p, re.IGNORECASE) for p in HEADING_PATTERNS]

    for i, page in enumerate(pages):
        sample = (page or "").strip().splitlines()
        # Look at first 20 lines of the page
        for ln in sample[:20]:
            ln_clean = ln.strip()
            if not ln_clean:
                continue
            for pat in pattern_compiled:
                if pat.search(ln_clean):
                    title = ln_clean
                    starts.append((i + 1, title))
                    # Found a heading on this page, move to next page
                    break
            else:
                continue
            break

    sections: List[Dict] = []
    if starts:
        for idx, (pg, title) in enumerate(starts):
            start = pg
            end = (starts[idx + 1][0] - 1) if idx + 1 < len(starts) else len(pages)
            sections.append({"title": title, "start": start, "end": end})
        # Merge tiny sections with neighbors: if section has <=2 pages, merge to previous if possible
        merged = []
        for sec in sections:
            if merged and (sec['end'] - sec['start'] + 1) <= 2:
                # merge into previous
                merged[-1]['end'] = sec['end']
                merged[-1]['title'] += " | " + sec['title']
            else:
                merged.append(sec)
        return merged
    else:
        # fallback: one section = entire document
        return [{"title": "Full Document", "start": 1, "end": len(pages)}]


# ------------------ OpenRouter calls ------------------

def call_openrouter(prompt: str, model: str = MODEL, max_retries: int = 3, timeout: int = 120) -> Optional[str]:
    """Call OpenRouter chat completion. Returns content string or None on failure."""
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set. Export it to environment variable before running.")

    headers = HEADERS_BASE.copy()
    headers["Authorization"] = f"Bearer {OPENROUTER_API_KEY}"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(URL, headers=headers, data=json.dumps(payload), timeout=timeout)
            if resp.status_code == 200:
                result = resp.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                return None
            elif resp.status_code == 429:
                wait = 5 * attempt
                print(f"Rate limited, sleeping {wait}s (attempt {attempt})")
                time.sleep(wait)
            else:
                print(f"OpenRouter error {resp.status_code}: {resp.text}")
                time.sleep(2)
        except Exception as e:
            print(f"Request exception: {e}")
            time.sleep(2)
    return None


# ------------------ Prompt builders ------------------

def build_section_summary_prompt(section_title: str, section_pages_text: str, filename: str) -> str:
    """Prompt để tạo tóm tắt (global context) cho một section/tiểu mạch.
    Kết quả dùng làm anchor context khi phân tích chi tiết các chunk bên trong.
    """
    return f"""
Bạn là một chuyên gia kỹ thuật và người hướng dẫn.
Tài liệu nguồn: "{filename}"
Tiêu đề phần: "{section_title}"

Nhiệm vụ của bạn: TRẢ VỀ MỘT BẢN TÓM TẮT NGẮN (MAX 10-15 DÒNG) bằng TIẾNG VIỆT, gồm:
- Mục tiêu chính của phần
- Các khái niệm cốt lõi xuất hiện (liệt kê dạng bullets)
- Những phụ thuộc quan trọng (ví dụ: cần đọc Chương X trước)
- Từ khoá / thuật ngữ cần nhớ (short glossary)

KHÔNG phân tích chi tiết, chỉ tạo "Global Section Summary" để dùng làm ngữ cảnh cho phân tích chi tiết tiếp theo.

Nguồn (phần):
{section_pages_text}
""".strip()


def build_chunk_prompt(chunk_text: str, section_summary: str, prev_concepts: List[str], section_title: str, start_page: int) -> str:
    """Prompt để AI phân tích từng chunk chi tiết. Kết hợp section_summary làm ngữ cảnh cố định.
    Yêu cầu output là Markdown (Developer Decision Guide) giống yêu cầu cũ nhưng bằng Tiếng Việt.
    """
    prev_str = ", ".join(prev_concepts[-10:]) if prev_concepts else "None"
    return f"""
Bạn là một KỸ SƯ PHẦN MỀM cao cấp và GIẢNG VIÊN KỸ THUẬT.
Mục tiêu: Dựa trên phần tài liệu (bên dưới) và summary của phần, hãy sinh ra 1 tài liệu MARKDOWN dạng "DEVELOPER DECISION GUIDE" bằng TIẾNG VIỆT, súc tích nhưng đầy đủ thực dụng.

========================
NGỮ CẢNH TOÀN CỤC (section-level)
========================
Section title: {section_title}
Section summary (anchor context):
{section_summary}

Previously covered concepts (do not repeat): {prev_str}

========================
INPUT (chunk bắt đầu trang {start_page}):
{chunk_text}

========================
OUTPUT:
- Chỉ output MARKDOWN
- Giữ cấu trúc: Core mental model, Decision tables, Architecture, Code patterns, Anti-patterns, Cheat sheet
- Giữ các thuật ngữ kỹ thuật IN ENGLISH + giải thích tiếng Việt (ví dụ: "Coroutine (Tiến trình rút gọn)")
- Mỗi khái niệm/pattern phải có 1 ví dụ code hoàn chỉnh (ngắn)
- Không chèn hình

HÃY NGẮT KHOẢNG RÕ RÀNG giữa các section markdown (h2/h3).
""".strip()


# ------------------ Analysis pipeline ------------------

def chunk_pages_range(pages: List[str], start: int, end: int, size: int) -> List[Tuple[int, List[str]]]:
    """Chia trang từ start..end (1-indexed) thành các chunk có size trang.
    Trả về list tuple (start_page, [texts]).
    """
    result = []
    total = end - start + 1
    for offset in range(0, total, size):
        s = start + offset
        e = min(start + offset + size - 1, end)
        # pages list index = page-1
        block = pages[s - 1:e]
        result.append((s, block))
    return result


def simple_extract_headers_from_markdown(md: str) -> List[str]:
    """Lấy các header markdown (## , ###) để cấu thành previous concepts list."""
    headers = []
    for line in md.splitlines():
        if line.startswith('## '):
            h = line.replace('## ', '').strip()
            headers.append(h)
        elif line.startswith('# '):
            h = line.replace('# ', '').strip()
            headers.append(h)
    return headers


def analyze_pdf_stream(pdf_path: str):
    """Generator xử lý theo section -> chunk.
    Yields events giống trước: {'type': 'log'|'chunk'|'error', ...}
    """
    if not os.path.exists(pdf_path):
        yield {'type': 'error', 'message': f'File not found: {pdf_path}'}
        return

    filename = os.path.basename(pdf_path)
    yield {'type': 'log', 'message': f'Reading PDF: {filename}'}

    pages = extract_text_from_pdf(pdf_path)
    if not pages:
        yield {'type': 'error', 'message': 'File is empty or unreadable.'}
        return

    total_pages = len(pages)
    yield {'type': 'log', 'message': f'Total pages: {total_pages}'}

    # Detect sections (tiểu mạch)
    sections = detect_sections(pages)
    yield {'type': 'log', 'message': f'Detected {len(sections)} sections.'}

    # Write header
    header_md = f"# DEVELOPER DECISION GUIDE: {filename}\n\n> Generated by OpenRouter ({MODEL}) on {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    yield {'type': 'chunk', 'content': header_md}

    global_previous_concepts: List[str] = []

    for sec_idx, sec in enumerate(sections, start=1):
        sec_title = sec['title']
        sec_start = sec['start']
        sec_end = sec['end']
        sec_range = f"{sec_start}-{sec_end}"
        yield {'type': 'log', 'message': f"Section {sec_idx}/{len(sections)}: '{sec_title}' pages {sec_range}"}

        # Build section text (we may trim very long text to a reasonable size for summary)
        sec_text = "\n\n".join(pages[sec_start - 1:sec_end])
        # Create section summary anchor
        summary_prompt = build_section_summary_prompt(sec_title, sec_text[:6000], filename)
        summary = call_openrouter(summary_prompt)
        if not summary:
            yield {'type': 'log', 'message': f"Warning: no section summary for {sec_title}. Using fallback."}
            summary = "(No summary available)"
        summary = summary.strip()

        # Emit section header into markdown
        sec_header_md = f"\n\n<!-- SECTION {sec_range} -->\n\n## {sec_title} (pages {sec_range})\n\n{summary}\n\n"
        yield {'type': 'chunk', 'content': sec_header_md}

        # Now chunk inside this section
        chunks = chunk_pages_range(pages, sec_start, sec_end, CHUNK_PAGES_DEFAULT)
        previous_concepts_local: List[str] = []

        for start_page, block_pages in chunks:
            chunk_range = f"{start_page}-{start_page + len(block_pages) - 1}"
            yield {'type': 'log', 'message': f" Processing chunk {chunk_range} of section {sec_idx}"}

            chunk_text = "\n\n".join(block_pages)
            prompt = build_chunk_prompt(chunk_text[:8000], summary, global_previous_concepts + previous_concepts_local, sec_title, start_page)
            content = call_openrouter(prompt)

            if content:
                content = content.strip()
                # extract headers to accumulate concepts
                headers = simple_extract_headers_from_markdown(content)
                for h in headers:
                    if h not in previous_concepts_local:
                        previous_concepts_local.append(h)
                    if h not in global_previous_concepts:
                        global_previous_concepts.append(h)

                chunk_md = f"\n\n<!-- CHUNK {chunk_range} -->\n\n{content}\n\n"
                yield {'type': 'chunk', 'content': chunk_md}
            else:
                yield {'type': 'log', 'message': f"Warning: No response for chunk {chunk_range}."}
            # small sleep to avoid burst
            time.sleep(1)

    yield {'type': 'log', 'message': 'Analysis complete.'}


# ------------------ CLI / file writer ------------------

def process_single_file_cli(pdf_path: str):
    directory = os.path.dirname(pdf_path) or os.getcwd()
    filename = os.path.basename(pdf_path)
    output_filename = filename.replace('.pdf', '_GUIDE.md')
    output_path = os.path.join(directory, output_filename)

    print(f"\n>> Start: {filename} -> {output_filename}")

    with open(output_path, 'w', encoding='utf-8') as f:
        pass

    for event in analyze_pdf_stream(pdf_path):
        if event['type'] == 'log':
            print(f"   {event['message']}")
        elif event['type'] == 'chunk':
            with open(output_path, 'a', encoding='utf-8') as f:
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

    # Default: use the path you stated earlier (if exists in environment)
    default_path = os.getenv('PDF_TARGET_PATH')
    if default_path and os.path.isfile(default_path):
        process_single_file_cli(default_path)
        return

    print('Usage: python openrouter_pdf_analyzer_improved.py <path-to-pdf>')


if __name__ == '__main__':
    main()
