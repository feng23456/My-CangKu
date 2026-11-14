# Web Crawler Demo (网页数据自动化爬虫)

## 📖 项目简介
本项目为求职笔试作品。基于 Python 编写，结合 `Playwright` 与 `DrissionPage` 两大自动化工具，针对目标网站（mitadmissions.org）进行多维度数据采集，并将结果结构化导出为 CSV 文件。

## 🛠️ 核心技术
- **Playwright**：处理网页动态渲染与自动化交互。
- **DrissionPage**：结合 requests 和 selenium 的优势，高效抓取 DOM 结构与网络数据。
- **数据清洗**：提取目标字段并规范化保存。

## 📂 文件说明
- `crawler.py`：爬虫主程序代码。
- `blogs_data.csv`：抓取结果文件（包含标题、作者、评论数、时间、文章内容、图片链接）。

## 🚀 快速启动
1. 安装依赖：
   `pip install playwright drissionpage`
2. 安装 Playwright 浏览器驱动：
   `playwright install`
3. 运行代码：
   `python crawler.py`
