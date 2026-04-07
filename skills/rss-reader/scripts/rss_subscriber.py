#!/usr/bin/env python3
"""
RSS 订阅器 - 从 RSS 源获取文章并保存到本地文件夹

使用方法:
    python rss_subscriber.py [rss_url] [--output output_dir]
    python rss_subscriber.py --opml "path/to/feeds.opml" [--output output_dir]
    python rss_subscriber.py  (不传参数时使用默认的 feeds.opml)

示例:
    python rss_subscriber.py "https://example.com/feed.rss"
    python rss_subscriber.py "https://example.com/feed.rss" --output "./raw"
    python rss_subscriber.py --opml "./subscriptions.opml"
    python rss_subscriber.py  (使用脚本目录下的默认 feeds.opml)
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import ssl
import urllib.request

# 获取脚本所在目录路径，用于查找默认的 feeds.opml 文件
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OPML_FILE = os.path.join(SCRIPT_DIR, 'feeds.opml')

# 日期过滤：默认只获取最近 1 年的文章
ONE_YEAR_AGO = datetime.now() - timedelta(days=365)


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '').strip()
    name = name.replace(' ', '_')
    name = ''.join(c if c.isalnum() or c in '._-' else '' for c in name)
    if not name:
        return 'untitled'
    if len(name) > 100:
        name = name[:100]
    return name


def parse_date(date_str: str) -> str:
    """解析 RSS 日期格式为 YYYY-MM-DD"""
    if not date_str:
        return datetime.now().strftime('%Y-%m-%d')

    # 清理日期字符串：去掉时区信息
    date_str = date_str.split('+')[0].strip()
    # 去掉 GMT、UTC 等时区后缀
    date_str = re.sub(r'\s*(GMT|UTC|UTC\d|[A-Z]{3,4})\s*$', '', date_str).strip()

    try:
        dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass

    try:
        dt = datetime.strptime(date_str, '%a, %d %b %Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass

    try:
        dt = datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass

    # 尝试解析 ISO 8601 格式 (2026-02-04T12:34:56)
    try:
        if 'T' in date_str:
            dt = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass

    # 如果所有解析都失败，返回当前日期
    return datetime.now().strftime('%Y-%m-%d')


def fetch_rss(url: str) -> list:
    """从 RSS URL 获取条目列表"""
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)

        response = urllib.request.urlopen(req, context=ssl_context, timeout=30)
        content = response.read().decode('utf-8')
    except Exception as e:
        print(f"  获取 RSS 失败：{e}")
        return []

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        print(f"  XML 解析失败：{e}")
        return []

    articles = []

    # RSS 2.0 / RSS 1.0 格式
    for item in root.findall('.//item'):
        title = item.find('title')
        link = item.find('link')
        pub_date = item.find('pubDate')
        description = item.find('description')
        content_item = item.find('content:encoded', namespaces={'content': 'http://purl.org/rss/1.0/modules/content/'})

        articles.append({
            'title': title.text if title is not None else 'Untitled',
            'link': link.text if link is not None else '',
            'date': parse_date(pub_date.text) if pub_date is not None else datetime.now().strftime('%Y-%m-%d'),
            'description': description.text if description is not None else '',
            'content': content_item.text if content_item is not None else (description.text or '')
        })

    # Atom 格式
    for item in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
        title = item.find('{http://www.w3.org/2005/Atom}title')
        link = item.find('{http://www.w3.org/2005/Atom}link')
        pub_date = item.find('{http://www.w3.org/2005/Atom}updated')
        if pub_date is None:
            pub_date = item.find('{http://www.w3.org/2005/Atom}published')
        summary = item.find('{http://www.w3.org/2005/Atom}summary')
        content_item = item.find('{http://www.w3.org/2005/Atom}content')

        if title is not None:
            articles.append({
                'title': title.text,
                'link': link.get('href', '') if link is not None else '',
                'date': parse_date(pub_date.text) if pub_date is not None else datetime.now().strftime('%Y-%m-%d'),
                'description': summary.text if summary is not None else '',
                'content': content_item.text if content_item is not None else (summary.text or '')
            })

    return articles


def parse_opml(opml_path: str) -> list:
    """
    解析 OPML 文件，提取所有 RSS 订阅源 URL

    支持本地文件路径和 URL 地址
    """
    feeds = []

    try:
        # 检查是否为 URL
        if opml_path.startswith(('http://', 'https://')):
            # 从 URL 获取 OPML 内容
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req = urllib.request.Request(opml_path, headers=headers)
            response = urllib.request.urlopen(req, context=ssl_context, timeout=30)
            content = response.read().decode('utf-8')
            root = ET.fromstring(content)
        else:
            # 从本地文件读取
            if not os.path.exists(opml_path):
                print(f"  OPML 文件不存在：{opml_path}")
                return []

            tree = ET.parse(opml_path)
            root = tree.getroot()

        # 提取所有 rssUrl 属性 (OPML 标准格式)
        for outline in root.iter('outline'):
            xml_url = outline.get('xmlUrl')
            if xml_url:
                title = outline.get('text') or outline.get('title') or 'Unnamed'
                feeds.append({
                    'url': xml_url,
                    'title': title
                })

        # 如果没有找到 xmlUrl，尝试查找 htmlUrl 作为备用
        if not feeds:
            for outline in root.iter('outline'):
                html_url = outline.get('htmlUrl')
                if html_url: 
                    title = outline.get('text') or outline.get('title') or 'Unnamed'
                    feeds.append({
                        'url': html_url,
                        'title': title
                    })

        print(f"  从 OPML 文件解析到 {len(feeds)} 个订阅源")

    except ET.ParseError as e:
        print(f"  OPML 解析失败：{e}")
    except Exception as e:
        print(f"  读取 OPML 失败：{e}")

    return feeds




def article_to_markdown(article: dict, rss_source: str) -> str:
    """将文章条目转换为 Markdown 格式"""
    content = f"""# {article['title']}

**来源**: {rss_source}

**发布日期**: {article['date']}

**链接**: {article['link']}

---

## 摘要

{article['description']}

---

## 正文

{article['content']}

---

*此文档由 RSS 订阅器自动生成*
"""
    return content


def save_article(article: dict, rss_source: str, output_dir: str) -> str:
    """保存文章到文件，返回保存路径"""
    os.makedirs(output_dir, exist_ok=True)

    safe_title = sanitize_filename(article['title'])
    filename = f"{article['date']}_{safe_title}.md"

    filepath = os.path.join(output_dir, filename)

    if os.path.exists(filepath):
        print(f"  跳过 (已存在): {filename}",
              flush=True,
              file=sys.__stdout__)
        return filepath

    markdown_content = article_to_markdown(article, rss_source)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"  已保存：{filename}",
              flush=True,
              file=sys.__stdout__)
    except Exception as e:
        print(f"  保存失败：{e}")
        return ''

    return filepath


def main():
    """主函数"""
    print("=" * 50)
    print("RSS 订阅器")
    print("=" * 50)

    # 默认配置：使用当前工作目录的 raw 文件夹
    output_dir = 'raw'
    opml_file = None
    direct_url = None
    get_all = False  # 是否获取所有文章（包括 1 年前的）

    # 解析命令行参数
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--opml' and i + 1 < len(args):
            opml_file = args[i + 1]
            i += 2
        elif args[i] == '--output' and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        elif args[i] == '--get-all':
            get_all = True
            i += 1
        elif not args[i].startswith('--'):
            # 直接传入 RSS URL
            direct_url = args[i]
            i += 1
        else:
            i += 1

    # 收集所有订阅源
    all_feeds = []

    # 1. 直接从命令行参数的 URL
    if direct_url:
        all_feeds.append({'url': direct_url, 'title': 'Direct URL'})

    # 2. OPML 文件（命令行指定或默认）
    if opml_file:
        opml_feeds = parse_opml(opml_file)
        all_feeds.extend(opml_feeds)
    elif not all_feeds and os.path.exists(DEFAULT_OPML_FILE):
        # 未指定任何订阅源，使用默认的 feeds.opml 文件
        print(f"\n未指定订阅源，使用默认的 feeds.opml 文件...")
        opml_feeds = parse_opml(DEFAULT_OPML_FILE)
        all_feeds.extend(opml_feeds)

    if not all_feeds:
        print("\n用法：python rss_subscriber.py [选项] [RSS_URL]")
        print("\n选项:")
        print("  --opml <文件>    从 OPML 文件读取订阅源")
        print("  --output <目录>  指定输出目录 (默认：./raw)")
        print("  --get-all        获取所有文章，包括 1 年前的 (默认只获取最近 1 年)")
        print("\n示例:")
        print('  python rss_subscriber.py "https://example.com/feed.rss"')
        print('  python rss_subscriber.py --opml "./subscriptions.opml"')
        print('  python rss_subscriber.py --output "./raw" "https://example.com/feed.rss"')
        print('  python rss_subscriber.py --get-all  (获取所有文章)')
        print('  python rss_subscriber.py  (使用默认的 feeds.opml)')
        return

    # 显示过滤模式
    if get_all:
        print(f"\n过滤模式：获取所有文章（包括 1 年前的）")
    else:
        print(f"\n过滤模式：只获取最近 1 年的文章（{ONE_YEAR_AGO.strftime('%Y-%m-%d')} 之后）")
    print(f"总共处理 {len(all_feeds)} 个订阅源")

    # 处理每个订阅源
    total_saved = 0
    for feed in all_feeds:
        feed_url = feed['url']
        source_name = feed.get('title') or feed_url.split('//')[-1].split('/')[0]

        print(f"\n正在获取：{feed_url}")
        articles = fetch_rss(feed_url)

        if not articles:
            print("  未获取到任何文章")
            continue

        print(f"  获取到 {len(articles)} 篇文章")

        # 日期过滤：默认只获取最近 1 年的文章
        if not get_all:
            filtered_articles = []
            for article in articles:
                article_date = datetime.strptime(article['date'], '%Y-%m-%d')
                if article_date >= ONE_YEAR_AGO:
                    filtered_articles.append(article)
                else:
                    print(f"  跳过 (超过 1 年): {article['date']} - {article['title'][:50]}...",
                          flush=True)
            skipped_count = len(articles) - len(filtered_articles)
            if skipped_count > 0:
                print(f"  过滤后剩余 {len(filtered_articles)} 篇文章（跳过 {skipped_count} 篇旧文章）")
            articles = filtered_articles

        if not articles:
            print("  过滤后没有符合条件的文章")
            continue

        # 按日期排序
        articles.sort(key=lambda x: x['date'], reverse=True)

        # 保存每篇文章
        saved_count = 0
        for article in articles:
            filepath = save_article(article, source_name, output_dir)
            if filepath:
                saved_count += 1

        print(f"\n已保存 {saved_count}/{len(articles)} 篇文章到：{output_dir}")
        total_saved += saved_count

    print("\n" + "=" * 50)
    print(f"完成！共保存 {total_saved} 篇文章")
    print("=" * 50)


if __name__ == '__main__':
    main()
