#!/bin/bash
# process_raw_files.sh - 处理 raw 文件夹中的新文件，防止重复处理

RAW_DIR="raw"
SUMMARIES_DIR="wiki/summaries"
PROCESSED_FILE="wiki/.processed_files"

# 在当前工作目录执行（由调用者决定项目目录）

# 确保目录和文件存在
mkdir -p "$SUMMARIES_DIR"
mkdir -p "$(dirname "$PROCESSED_FILE")"
touch "$PROCESSED_FILE"

echo "=== 开始处理 raw 文件夹中的文件 ==="
echo "时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

new_files=""
skipped_files=""
new_count=0
skipped_count=0

for file in "$RAW_DIR"/*.md; do
    [ -f "$file" ] || continue

    filename=$(basename "$file")
    # 从文件名提取主名（去掉 .md）
    basename_no_ext="${filename%.md}"
    # 生成 summary 文件名
    summary_file="${SUMMARIES_DIR}/${basename_no_ext}_summary.md"

    echo "检查文件：$filename"

    # 方案 1：检查已处理记录
    if grep -qF "$filename" "$PROCESSED_FILE" 2>/dev/null; then
        echo "  [跳过] 方案 1: 已在处理记录中"
        skipped_files="$skipped_files $filename"
        skipped_count=$((skipped_count + 1))
        continue
    fi

    # 方案 2：检查对应的 summary 文件是否存在
    if [ -f "$summary_file" ]; then
        echo "  [跳过] 方案 2: summary 文件已存在"
        # 同时添加到处理记录，保持一致性
        echo "$filename" >> "$PROCESSED_FILE"
        skipped_files="$skipped_files $filename"
        skipped_count=$((skipped_count + 1))
        continue
    fi

    # 方案 3：可选 - 检查 git 状态（仅当文件在 git 跟踪中时使用）
    # 如果文件已被提交且上次 commit 时间超过 1 小时，可能已经处理过
    # 这个检查是可选的，主要用于调试
    # if git ls-files --error-unmatch "$file" 2>/dev/null; then
    #     last_commit_time=$(git log -1 --format=%ct "$file" 2>/dev/null || echo "0")
    #     current_time=$(date +%s)
    #     age=$((current_time - last_commit_time))
    #     if [ $age -gt 3600 ]; then
    #         echo "  [可选] 方案 3: 文件已在 git 中且超过 1 小时未修改"
    #     fi
    # fi

    echo "  [新文件] 需要处理"
    new_files="$new_files $filename"
    new_count=$((new_count + 1))
done

echo ""
echo "=== 检查结果 ==="
echo "新文件数量：$new_count"
echo "已跳过的文件数量：$skipped_count"
echo ""

if [ $new_count -gt 0 ]; then
    echo "发现新文件，请执行以下步骤："
    echo "1. 阅读 wiki/LLM_COMPILETION_PROMPT.md"
    echo "2. 按照其中的指南处理上述新文件（生成 summary）"
    echo "3. 运行 ./scripts/update_index.sh 更新索引文件"
    echo ""
    echo "新文件列表:"
    echo "$new_files" | tr ' ' '\n' | sed '/^$/d'
else
    echo "所有文件都已被处理过，无需操作。"
fi

# 检查是否有新的 summary 文件（由人工生成后）
summary_count=0
for summary in "$SUMMARIES_DIR"/*_summary.md; do
    [ -f "$summary" ] || continue
    filename=$(basename "$summary")
    # 检查是否已添加到处理记录
    if ! grep -qF "${filename%_summary.md}.md" "$PROCESSED_FILE" 2>/dev/null; then
        # 如果是新创建的 summary，检查原始文件是否存在
        basename_no_ext="${filename%_summary.md}"
        if [ -f "raw/${basename_no_ext}.md" ]; then
            # 原始文件已存在，summary 是新创建的
            echo "$basename_no_ext.md" >> "$PROCESSED_FILE"
            summary_count=$((summary_count + 1))
        fi
    fi
done

if [ $summary_count -gt 0 ]; then
    echo ""
    echo "发现 $summary_count 个新的 summary 文件，建议运行：./scripts/update_index.sh"
fi
