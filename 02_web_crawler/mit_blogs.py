# -*- coding: utf-8 -*-
"""
MIT Admissions 博客爬虫（Windows 版）
Playwright 负责：抓列表页，收集文章链接
DrissionPage 负责：逐篇打开文章页，提取字段
输出：blogs_data.csv
"""

import csv
import re
import time
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright
from DrissionPage import ChromiumPage, ChromiumOptions

LIST_URL = "https://mitadmissions.org/blogs/"  # 博客列表页
MAX_ARTICLES = 10      # 抓取文章数量（先少量测试，跑通后可调大）
HEADLESS = True        # 无头模式；调试时改成 False 可以看到浏览器窗口


# ========== 第一部分：用 Playwright 收集文章链接 ==========
def get_article_links():
    """打开博客列表页，收集所有文章详情页的 URL"""
    links = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()
        page.goto(LIST_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)  # 等待页面 JS 渲染完成

        # 该站所有文章链接都包含 /blogs/entry/，用这个特征抓取最稳定
        for a in page.query_selector_all('a[href*="/blogs/entry/"]'):
            href = a.get_attribute("href")
            if not href:
                continue
            # urljoin 补全相对路径；split("#") 去掉 #comments 这类锚点，避免重复
            full_url = urljoin(LIST_URL, href).split("#")[0]
            if full_url not in links:
                links.append(full_url)

        browser.close()
    return links[:MAX_ARTICLES]


# ========== 工具函数 ==========
def first_ele(page, selectors):
    """按顺序尝试多个选择器，返回第一个匹配到的元素（提高兼容性）"""
    for sel in selectors:
        ele = page.ele(sel, timeout=1)
        if ele:  # DrissionPage 找不到时返回假值
            return ele
    return None


def extract_comment_count(page):
    """在页面中查找 “数字 + Comment(s)” 样式的文本，提取评论数"""
    candidates = page.eles('xpath://a[contains(text(),"omment")]'
                           ' | //h2[contains(text(),"omment")]'
                           ' | //h3[contains(text(),"omment")]')
    for ele in candidates:
        m = re.search(r"(\d+)\s*[Cc]omments?", ele.text)
        if m:
            return m.group(1)
    return ""


# ========== 第二部分：用 DrissionPage 抓文章详情 ==========
def scrape_article(page, url):
    """打开一篇文章页，提取所有需要的字段"""
    page.get(url)
    time.sleep(2)  # 等待页面加载

    # 1. 标题
    title_ele = first_ele(page, ["tag:h1", "css:.entry-title"])
    title = title_ele.text.strip() if title_ele else ""

    # 2. 作者（该站作者链接都指向 /blogs/author/xxx）
    author_ele = first_ele(page, ['css:a[href*="/blogs/author/"]', "css:.author"])
    author = author_ele.text.strip() if author_ele else ""

    # 3. 时间（优先取 <time> 标签的 datetime 属性）
    time_ele = first_ele(page, ["tag:time", "css:.entry-date", "css:.date"])
    pub_time = ""
    if time_ele:
        pub_time = (time_ele.attr("datetime") or time_ele.text).strip()

    # 4. 评论数
    comment_count = extract_comment_count(page)

    # 5 & 6. 正文 + 正文内的图片（在正文容器里找所有 img）
    content, images = "", ""
    content_ele = first_ele(page, [
        "css:.entry-content", "css:.entry", "css:article",
        "css:.post", "css:#content",
    ])
    if content_ele:
        content = content_ele.text.strip()
        img_srcs = []
        for img in content_ele.eles("tag:img"):
            src = img.attr("src") or img.attr("data-src")  # 兼容懒加载图片
            if src:
                img_srcs.append(urljoin(url, src))  # 补全相对路径
        images = "; ".join(img_srcs)  # 多张图片用分号隔开

    return {
        "Title": title,
        "Author": author,
        "Comment Count": comment_count,
        "Time": pub_time,
        "Article Content": content,
        "Images": images,
    }


# ========== 主流程 ==========
def main():
    # 第 1 步：Playwright 拿文章链接
    links = get_article_links()
    print(f"共获取到 {len(links)} 篇文章链接")

    # 第 2 步：DrissionPage 逐篇抓详情
    options = ChromiumOptions()
    options.headless(HEADLESS)
    # 如果电脑没装 Chrome，取消下面一行的注释，指向 Playwright 下载的 Chromium
    # （路径里的 chromium-xxxx 版本号按你电脑上的实际目录名改）：
    # options.set_browser_path(r"C:\Users\你的用户名\AppData\Local\ms-playwright\chromium-1140\chrome-win\chrome.exe")
    page = ChromiumPage(options)

    rows = []
    for i, url in enumerate(links, 1):
        print(f"[{i}/{len(links)}] 正在抓取: {url}")
        try:
            data = scrape_article(page, url)
            rows.append(data)
            print(f"    标题: {data['Title'][:40]}")
        except Exception as e:
            print(f"    抓取失败: {e}")
        time.sleep(2)  # 礼貌延时，避免给网站造成压力
    page.quit()

    # 第 3 步：写入 CSV（utf-8-sig 保证用 Excel 打开不乱码）
    with open("blogs_data.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Title", "Author", "Comment Count", "Time", "Article Content", "Images"
        ])
        writer.writeheader()
        writer.writerows(rows)

    print("完成！数据已保存到 blogs_data.csv")


if __name__ == "__main__":
    main()