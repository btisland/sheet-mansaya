#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 a01/index.html：
1. 加入 Google Fonts preconnect
2. step-img 圖片加上 loading="lazy" decoding="async"
3. 將 step-img 圖片包在 <picture> 元素內，提供 WebP 來源
"""
import re
from pathlib import Path

html_path = Path(__file__).parent / 'a01/index.html'
images_dir = Path(__file__).parent / 'a01/images'

content = html_path.read_text(encoding='utf-8')

# ── 1. 加入 preconnect ───────────────────────────────────────────────────────
preconnect = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
)
fonts_link = '<link href="https://fonts.googleapis.com/'
if preconnect.strip() not in content:
    content = content.replace(fonts_link, preconnect + fonts_link)
    print('✓ 加入 Google Fonts preconnect')
else:
    print('  preconnect 已存在，略過')

# ── 2. 處理 step-img 圖片 ───────────────────────────────────────────────────

def get_webp_srcset(src: str) -> str:
    """images/1779267192000.jpg.jpeg?v=xxx  →  images/1779267192000.webp"""
    src_clean = src.split('?')[0]
    parts = src_clean.split('/')
    base = parts[-1].split('.')[0]          # 取第一個 . 之前的部分
    dir_part = '/'.join(parts[:-1])
    return f'{dir_part}/{base}.webp'


def replace_img(m: re.Match) -> str:
    full_tag = m.group(0)
    src_match = re.search(r'src="([^"]+)"', full_tag)
    if not src_match:
        return full_tag

    src = src_match.group(1)
    if not src.startswith('images/'):
        return full_tag

    # 加上 lazy loading（如果還沒有）
    new_tag = full_tag
    if 'loading=' not in new_tag:
        new_tag = new_tag[:-1] + ' loading="lazy" decoding="async">'

    # 確認 WebP 檔案存在
    webp_srcset = get_webp_srcset(src)
    webp_path = (html_path.parent / webp_srcset).resolve()
    if webp_path.exists():
        return f'<picture><source srcset="{webp_srcset}" type="image/webp">{new_tag}</picture>'

    return new_tag


pattern = r'<img class="step-img[^"]*"[^>]+>'
new_content, count = re.subn(pattern, replace_img, content)

print(f'✓ 處理 {count} 張 step-img 圖片（picture + lazy loading）')

html_path.write_text(new_content, encoding='utf-8')
print(f'✓ 已寫入 {html_path}')
