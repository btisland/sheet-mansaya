#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 _shared/ 內的共用區塊同步到各專案 index.html 對應的 marker 之間。

單一來源：_shared/line-setup.html
注入位置：每個 {專案}/index.html 中
    <!-- LINE-SETUP:START ... -->
    ...（此區內容會被覆蓋）...
    <!-- LINE-SETUP:END -->

用法：
    python3 sync_shared.py
改完共用內容後務必執行，再接著跑 python3 update_cache_bust.py 更新圖片 hash。
"""
import re
from pathlib import Path

BASE = Path(__file__).parent

# 共用片段對應的 marker 名稱（未來要加別的共用區塊，在這裡擴充即可）
SHARED_BLOCKS = {
    "LINE-SETUP": "_shared/line-setup.html",
}


def load_body(rel_path: str) -> str:
    """讀取共用片段內容，去掉檔首的來源註解行。"""
    text = (BASE / rel_path).read_text(encoding="utf-8")
    text = re.sub(r"^<!--.*?-->\n", "", text, count=1)
    return text.rstrip()


def sync_block(content: str, name: str, body: str) -> str:
    """把 content 中 name 對應 marker 之間的內容換成 body。"""
    pattern = re.compile(
        rf"([ \t]*<!-- {name}:START[^\n]*-->\n).*?([ \t]*<!-- {name}:END -->)",
        re.DOTALL,
    )
    # 用函式回傳避免 body 內的反斜線被當成群組參照
    return pattern.sub(lambda m: m.group(1) + body + "\n" + m.group(2), content)


bodies = {name: load_body(path) for name, path in SHARED_BLOCKS.items()}

total = 0
for html_path in sorted(BASE.glob("*/index.html")):
    content = html_path.read_text(encoding="utf-8")
    new_content = content
    touched = []
    for name, body in bodies.items():
        if f"<!-- {name}:START" in new_content:
            new_content = sync_block(new_content, name, body)
            touched.append(name)
    if new_content != content:
        html_path.write_text(new_content, encoding="utf-8")
        total += 1
        print(f"  同步 {html_path.relative_to(BASE)}：{', '.join(touched)}")

print(f"\n✅ 完成，更新 {total} 個專案")
