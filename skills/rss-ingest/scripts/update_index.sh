#!/bin/bash
# update_index.sh - 更新 wiki/index.md 文件，添加新的 summary 链接

SUMMARIES_DIR="wiki/summaries"
INDEX_FILE="wiki/index.md"

# 在当前工作目录执行（由调用者决定项目目录）

if [ ! -d "$SUMMARIES_DIR" ]; then
    echo "错误：summaries 目录不存在"
    exit 1
fi

if [ ! -f "$INDEX_FILE" ]; then
    echo "错误：index.md 文件不存在"
    exit 1
fi

echo "== 更新索引文件 =="
echo "时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 获取所有 summary 文件，按日期排序（文件名前缀是 YYYY-MM-DD）
mapfile -t summary_files < <(ls -1 "$SUMMARIES_DIR"/*_summary.md 2>/dev/null | sort)

if [ ${#summary_files[@]} -eq 0 ]; then
    echo "未找到任何 summary 文件"
    exit 0
fi

# 提取最新的 10 个 summary 并构建链接
latest_entries=""
for file in "${summary_files[@]: -10}"; do
    [ -f "$file" ] || continue
    filename=$(basename "$file")
    # 提取日期（文件名前缀）
    date_prefix=$(echo "$filename" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}')
    if [ -n "$date_prefix" ]; then
        # 按日期正序添加（最新的在前）
        latest_entries="[[${filename}]] (${date_prefix})"$'\n'"$latest_entries"
    fi
done

# 反转顺序（让最新的在最前面）
reversed_entries=$(echo "$latest_entries" | tac)

# 将条目转换为带 - 的列表格式
list_entries=$(echo "$reversed_entries" | sed 's/^/- /')

# 检查是否已经有这些条目（检查是否有 llm-wiki_summary）
if grep -q "llm-wiki_summary" "$INDEX_FILE"; then
    echo "索引已包含 llm-wiki_summary，无需更新"
    exit 0
fi

# 在 "## 最新汇总" 后面插入新条目（替换原来的占位内容）
{
    head -n 4 "$INDEX_FILE"
    echo ""
    echo "$list_entries"
    tail -n +5 "$INDEX_FILE"
} > "${INDEX_FILE}.tmp"

mv "${INDEX_FILE}.tmp" "$INDEX_FILE"

echo "已更新 $INDEX_FILE"
echo ""
echo "最新的 10 个 summary:"
echo "$list_entries"
