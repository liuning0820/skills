#!/usr/bin/env python3
# process_raw_files.py - 处理 raw 文件夹中的新文件，防止重复处理

import os
import glob
from pathlib import Path
from datetime import datetime

# 使用当前工作目录的绝对路径
CURRENT_DIR = os.getcwd()
RAW_DIR = os.path.join(CURRENT_DIR, "raw")
SUMMARIES_DIR = os.path.join(CURRENT_DIR, "wiki/summaries")
PROCESSED_FILE = os.path.join(CURRENT_DIR, "wiki/.processed_files")

def main():
    # 在当前工作目录执行（由调用者决定项目目录）

    # 确保目录和文件存在
    Path(SUMMARIES_DIR).mkdir(parents=True, exist_ok=True)
    Path(PROCESSED_FILE).parent.mkdir(parents=True, exist_ok=True)
    Path(PROCESSED_FILE).touch(exist_ok=True)

    print("=== 开始处理 raw 文件夹中的文件 ===")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    new_files = []
    skipped_files = []
    new_count = 0
    skipped_count = 0

    # 读取已处理的记录
    processed_files = set()
    if Path(PROCESSED_FILE).exists():
        with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
            processed_files = set(line.strip() for line in f if line.strip())

    for file_path in glob.glob(os.path.join(RAW_DIR, "*.md")):
        if not os.path.isfile(file_path):
            continue

        filename = os.path.basename(file_path)
        # 从文件名提取主名（去掉 .md）
        basename_no_ext = filename[:-3] if filename.endswith('.md') else filename
        # 生成 summary 文件名
        summary_file = os.path.join(SUMMARIES_DIR, f"{basename_no_ext}_summary.md")

        print(f"检查文件：{filename}")

        # 方案 1：检查已处理记录
        if filename in processed_files:
            print("  [跳过] 方案 1: 已在处理记录中")
            skipped_files.append(filename)
            skipped_count += 1
            continue

        # 方案 2：检查对应的 summary 文件是否存在
        if os.path.isfile(summary_file):
            print("  [跳过] 方案 2: summary 文件已存在")
            # 同时添加到处理记录，保持一致性
            processed_files.add(filename)
            with open(PROCESSED_FILE, 'a', encoding='utf-8') as f:
                f.write(filename + '\n')
            skipped_files.append(filename)
            skipped_count += 1
            continue

        # 方案 3：可选 - 检查 git 状态（仅当文件在 git 跟踪中时使用）
        # 如果文件已被提交且上次 commit 时间超过 1 小时，可能已经处理过
        # 这个检查是可选的，主要用于调试
        # 这里省略 git 检查，因为 bash 版本中已注释

        print("  [新文件] 需要处理")
        new_files.append(filename)
        new_count += 1

    print("")
    print("=== 检查结果 ===")
    print(f"新文件数量：{new_count}")
    print(f"已跳过的文件数量：{skipped_count}")
    print("")

    if new_count > 0:
        print("发现新文件，请执行以下步骤：")
        print("1. 阅读 wiki/LLM_COMPILETION_PROMPT.md")
        print("2. 按照其中的指南处理上述新文件（生成 summary）")
        print("3. 运行 ./scripts/update_index.sh 更新索引文件")
        print("")
        print("新文件列表:")
        for file in new_files:
            print(file)
    else:
        print("所有文件都已被处理过，无需操作。")

    # 检查是否有新的 summary 文件（由人工生成后）
    summary_count = 0
    for summary_path in glob.glob(os.path.join(SUMMARIES_DIR, "*_summary.md")):
        if not os.path.isfile(summary_path):
            continue
        filename = os.path.basename(summary_path)
        # 检查是否已添加到处理记录
        original_filename = filename[:-12] + '.md'  # 去掉 _summary.md
        if original_filename not in processed_files:
            # 如果是新创建的 summary，检查原始文件是否存在
            basename_no_ext = filename[:-12]  # 去掉 _summary.md
            if os.path.isfile(os.path.join(RAW_DIR, f"{basename_no_ext}.md")):
                # 原始文件已存在，summary 是新创建的
                processed_files.add(original_filename)
                with open(PROCESSED_FILE, 'a', encoding='utf-8') as f:
                    f.write(original_filename + '\n')
                summary_count += 1

if __name__ == "__main__":
    main()