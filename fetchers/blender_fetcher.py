import os
import re
import json
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://docs.blender.org/manual/en/latest/"
CACHE_DIR = Path(__file__).resolve().parents[1] / 'data' / 'cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Candidate pages to fetch (kept small intentionally)
PAGES = [
    "modeling/modifiers/introduction.html",
    "modeling/modifiers/generate/subdivision_surface.html",
    "interface/window_system/",
    "sculpt_paint/sculpting/introduction.html",
    "animation/introduction.html",
    "render/cycles/"
]

def clean_text(s: str) -> str:
    s = re.sub(r"\[.*?\]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def fetch_page(path: str) -> dict:
    url = urljoin(BASE_URL, path)
    headers = {"User-Agent": "PromptLab/1.0 (+https://github.com)"}
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        return {"url": url, "content": ""}
    soup = BeautifulSoup(resp.text, 'html.parser')
    title_tag = soup.find(['h1','h2'])
    title = title_tag.get_text(strip=True) if title_tag else path
    main = soup.find('div', class_='document') or soup.find('article') or soup
    for tag in main.find_all(['nav','footer','script','style']):
        tag.decompose()
    paragraphs = []
    for p in main.find_all(['p','li']):
        t = p.get_text(separator=' ', strip=True)
        if t:
            paragraphs.append(clean_text(t))
    content = '\n'.join(paragraphs)
    return {"url": url, "title": title, "content": content}

def chunk_content(text: str, max_chars: int = 1800):
    if not text:
        return []
    chunks = []
    while len(text) > max_chars:
        idx = text.rfind('.', 0, max_chars)
        if idx == -1:
            idx = max_chars
        chunk = text[:idx+1]
        chunks.append(chunk.strip())
        text = text[idx+1:].strip()
    if text:
        chunks.append(text)
    return chunks

def fetch_and_cache(force: bool = False):
    out = []
    cache_file = CACHE_DIR / 'blender_docs_cache.json'
    if cache_file.exists() and not force:
        try:
            return json.loads(cache_file.read_text(encoding='utf-8'))
        except Exception:
            pass

    for path in PAGES:
        try:
            page = fetch_page(path)
            if page.get('content'):
                chunks = chunk_content(page['content'])
                for i, c in enumerate(chunks):
                    out.append({
                        'id': f"{Path(path).stem}_{i}",
                        'title': page.get('title', path),
                        'url': page.get('url'),
                        'text': c
                    })
            time.sleep(0.5)
        except Exception as e:
            print('Fetch error for', path, e)
            continue

    cache_file.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    return out

if __name__ == '__main__':
    docs = fetch_and_cache(force=True)
    print(f"Fetched {len(docs)} chunks. Cached to {CACHE_DIR}")
