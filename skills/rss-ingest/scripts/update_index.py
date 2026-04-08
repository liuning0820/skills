#!/usr/bin/env python3
# update_index.py - 更新 wiki/index.md 文件，添加新的 summary 链接
# 脚本使用当前工作目录（os.getcwd()）作为项目根目录

import os
import glob
from pathlib import Path
from datetime import datetime

# 使用当前工作目录的绝对路径
CURRENT_DIR = os.getcwd()
SUMMARIES_DIR = os.path.join(CURRENT_DIR, "wiki/summaries")
INDEX_FILE = os.path.join(CURRENT_DIR, "wiki/index.md")


def main():
    # 在当前工作目录执行（由调用者决定项目目录）
    print("=== 更新索引文件 ===")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    # 检查目录和文件是否存在
    if not os.path.isdir(SUMMARIES_DIR):
        print(f"错误：summaries 目录不存在：{SUMMARIES_DIR}")
        exit(1)

    if not os.path.isfile(INDEX_FILE):
        print(f"错误：index.md 文件不存在：{INDEX_FILE}")
        exit(1)

    # 获取所有 summary 文件，按文件名排序（文件名前缀是 YYYY-MM-DD）
    summary_files = sorted(glob.glob(os.path.join(SUMMARIES_DIR, "*_summary.md")))

    if len(summary_files) == 0:
        print("未找到任何 summary 文件")
        exit(0)

    # 提取最新的 10 个 summary 并构建链接
    latest_entries = []
    for file_path in summary_files[-10:]:
        if not os.path.isfile(file_path):
            continue
        filename = os.path.basename(file_path)
        # 提取日期（文件名前缀）
        date_prefix = filename[:10]  # YYYY-MM-DD
        if date_prefix:
            # 按日期正序添加（最新的在前）
            latest_entries.append(f"[[{filename}]] ({date_prefix})")

    # 反转顺序（让最新的在最前面）
    latest_entries.reverse()

    # 转换为带 - 的列表格式
    list_entries = "\n".join(f"- {entry}" for entry in latest_entries)

    # 检查是否已经有这些条目（检查是否有 llm-wiki_summary）
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index_content = f.read()

    if "llm-wiki_summary" in index_content:
        print("索引已包含 llm-wiki_summary，无需更新")
        exit(0)

    # 在 "## 最新汇总" 后面插入新条目（替换原来的占位内容）
    lines = index_content.split('\n')

    # 找到 "## 最新汇总" 行
    insert_index = None
    for i, line in enumerate(lines):
        if line.strip() == "## 最新汇总":
            insert_index = i + 1
            break

    if insert_index is None:
        print("错误：无法找到索引文件中的'## 最新汇总'部分")
        exit(1)

    # 构建新的内容
    new_lines = lines[:insert_index] + [""] + list_entries.split('\n') + lines[insert_index:]
    new_content = '\n'.join(new_lines)

    # 写回文件
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"已更新 {INDEX_FILE}")
    print("")
    print("最新的 10 个 summary:")
    print(list_entries)


if __name__ == "__main__":
    main()
