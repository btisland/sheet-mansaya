#!/usr/bin/env python3
"""
每次 commit 前執行，自動更新 HTML 裡所有圖片的 ?v= cache busting hash。
用法：python3 update_cache_bust.py
"""
import re
import hashlib
from pathlib import Path

BASE = Path(__file__).parent
HTML_FILES = list(BASE.rglob('*.html'))

def md5_short(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()[:8]

def update_html(html_path: Path) -> int:
    content = html_path.read_text(encoding='utf-8')
    updated = 0

    def replace_src(m):
        nonlocal updated
        prefix = m.group(1)   # src="
        img_rel = m.group(2)  # 相對路徑（不含 ?v=...）
        suffix = m.group(3)   # "

        img_abs = (html_path.parent / img_rel).resolve()
        if not img_abs.exists():
            return m.group(0)

        h = md5_short(img_abs)
        new_tag = f'{prefix}{img_rel}?v={h}{suffix}'
        if new_tag != m.group(0):
            updated += 1
        return new_tag

    # 匹配 src="/srcset="相對路徑/圖片"，去除舊的 ?v=... 再重新加
    pattern = r'((?:src|srcset)=")([^"?]+\.(?:jpg|jpeg|png|gif|webp|svg))(?:\?v=[^"]*)?(")'
    content = re.sub(pattern, replace_src, content, flags=re.IGNORECASE)
    html_path.write_text(content, encoding='utf-8')
    return updated

total = 0
for f in HTML_FILES:
    n = update_html(f)
    total += n
    if n:
        print(f'  {f.relative_to(BASE)}：更新 {n} 張')

print(f'\n✅ 完成，共更新 {total} 張圖片的 cache busting hash')
