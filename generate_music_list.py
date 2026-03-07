#!/usr/bin/env python3
"""
generate_music_list.py
扫描 ./music/ 目录，生成 music/index.json 供前端读取。
每次新增/删除歌曲后运行一次即可。

用法:
    python generate_music_list.py
"""

import os
import json

MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")
OUTPUT    = os.path.join(MUSIC_DIR, "index.json")

def main():
    if not os.path.isdir(MUSIC_DIR):
        os.makedirs(MUSIC_DIR)
        print(f"[+] 创建目录: {MUSIC_DIR}")

    files = sorted(
        f for f in os.listdir(MUSIC_DIR)
        if f.lower().endswith(".mp3")
    )

    data = {"files": files}
    with open(OUTPUT, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)

    print(f"[+] 已写入 {OUTPUT}")
    print(f"[+] 共 {len(files)} 首歌曲:")
    for f in files:
        print(f"    {f}")

if __name__ == "__main__":
    main()
