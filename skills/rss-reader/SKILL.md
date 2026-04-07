---
name: rss-reader
description: "Use when the user wants to fetch content from RSS feeds, save RSS articles to local folders, subscribe to blogs, organize articles by date and title, or process OPML files containing multiple RSS sources. Triggers: 'RSS feed', 'subscribe to blog', 'save RSS articles', 'OPML file', 'fetch latest articles'."
---

# RSS Reader 技能

从 RSS 源订阅并获取最新内容，自动保存到本地知识库。

## 何时使用此技能

**务必使用此技能当：**
- 用户要求从 RSS 订阅源获取最新内容
- 用户想要保存 RSS 文章到本地文件夹
- 用户提到 RSS 订阅、博客订阅、内容获取
- 用户想要按日期和标题整理 RSS 文章
- 用户提供一个 OPML 文件包含多个订阅源

**不要使用此技能当：**
- 用户只需要查看单个 URL 的内容（直接用 WebFetch）
- 用户想要获取非 RSS 格式的内容

## 使用方法

### 基本用法 - 单个 RSS URL

文章将保存到当前工作目录的 `raw` 文件夹：

```bash
python scripts/rss_subscriber.py "https://example.com/feed.rss"
```

### 指定输出目录

```bash
python scripts/rss_subscriber.py "https://example.com/feed.rss" --output "./my_folder"
```

### 使用 OPML 文件批量订阅

OPML (Outline Processor Markup Language) 是一种用于交换大纲列表的 XML 格式，常用于 RSS 订阅源的导入导出。

```bash
python scripts/rss_subscriber.py --opml "path/to/subscriptions.opml"
```

支持以下两种文件路径格式：
- 本地文件路径：`./my-feeds.opml` 或 `C:/Users/.../feeds.opml`
- URL 地址：`https://example.com/feeds.opml`

### 使用默认订阅源

如果不提供任何参数，将自动使用技能目录下的默认 `feeds.opml` 文件：

```bash
python scripts/rss_subscriber.py
```

### 日期过滤选项

**默认行为（只获取最近 1 年的文章）：**

```bash
python scripts/rss_subscriber.py --opml "feeds.opml"
```

这会过滤掉 1 年前的旧文章，专注于最新内容。

**获取所有历史文章：**

使用 `--get-all` 选项获取 RSS 源中的所有文章，包括 1 年前的：

```bash
python scripts/rss_subscriber.py --opml "feeds.opml" --get-all
```

## 输出格式

文章将保存为以下格式的 Markdown 文件：

```
raw/2025-01-06_Article-Title.md
```

每个文件包含：
- 文章标题
- 来源（RSS 域名）
- 发布日期
- 原文链接
- 摘要
- 正文内容

## 文件命名规则

- 格式：`YYYY-MM-DD_文章标题.md`
- 自动清理文件名中的非法字符
- 如果文件已存在，跳过保存

## 支持的格式

### RSS 格式
- RSS 2.0
- RSS 1.0
- Atom 1.0

### OPML 格式

支持标准的 OPML 1.0/2.0 格式，示例：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <body>
    <outline text="Tech Blogs" title="Tech Blogs">
      <outline type="rss" text="Martin Fowler" xmlUrl="https://martinfowler.com/feed.atom"/>
      <outline type="rss" text="Dev Blog" xmlUrl="https://devblog.com/feed.rss"/>
    </outline>
  </body>
</opml>
```

## 依赖

- Python 3.6+
- 无外部依赖（使用标准库）

## 默认的 feeds.opml 文件

技能目录下包含一个默认的 `feeds.opml` 文件，不传任何参数时会自动使用。你可以在该文件中添加你的默认订阅源。
