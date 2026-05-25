#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理 a01/images/ 目錄：
1. 建立 originals/ 子目錄
2. 將所有 .jpg / .jpeg / .jpg.jpeg 移入 originals/，並統一命名為 .jpg
3. 更新 HTML 內所有對應的 href 和 src 路徑
"""
import re
import shutil
from pathlib import Path

PROJ = Path(__file__).parent
images_dir  = PROJ / 'a01/images'
originals   = images_dir / 'originals'
html_path   = PROJ / 'a01/index.html'

# ── 1. 建立 originals 目錄 ───────────────────────────────────────────────────
originals.mkdir(exist_ok=True)

# ── 2. 移動並重新命名 ────────────────────────────────────────────────────────
all_files = sorted(list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.jpeg')))
moved = {}  # old filename → new filename (in originals/)

for f in all_files:
    base = f.name.split('.')[0]           # 取第一個 . 前的數字部分
    dest = originals / f'{base}.jpg'
    shutil.move(str(f), str(dest))
    moved[f.name] = dest.name
    print(f'  {f.name:<40} → originals/{dest.name}')

print(f'\n✓ 共移動 {len(moved)} 個檔案')

# ── 3. 更新 HTML ─────────────────────────────────────────────────────────────
content = html_path.read_text(encoding='utf-8')

def to_new(old_filename: str) -> str:
    """1779267192000.jpg.jpeg  →  originals/1779267192000.jpg"""
    base = old_filename.split('.')[0]
    return f'originals/{base}.jpg'

# href="images/XXXX.ext"（無 query string）
def fix_href(m):
    return f'href="images/{to_new(m.group(1))}"'

content = re.sub(
    r'href="images/([^"?]+\.(?:jpg|jpeg))"',
    fix_href,
    content
)

# src="images/XXXX.ext[?v=...]"（去掉舊 hash，讓 cache busting 重新加）
def fix_src(m):
    return f'src="images/{to_new(m.group(1))}"'

content = re.sub(
    r'src="images/([^"?]+\.(?:jpg|jpeg))(?:\?v=[^"]*)?"',
    fix_src,
    content
)

html_path.write_text(content, encoding='utf-8')
print('✓ HTML 路徑已更新')
