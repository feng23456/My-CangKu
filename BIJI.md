# Python 实战学习笔记

> 三个小项目：网页爬虫、FastAPI 流式接口、大模型自动打标签
> 环境：Windows + Python 3

---

## 第一章：环境搭建（地基）

### 1.1 Python 安装
- 官网下载：https://www.python.org/downloads/
- ⚠️ 安装时**必须勾选 "Add python.exe to PATH"**，否则命令行找不到 python
- 验证（新开 cmd 窗口）：
  ```
  python --version
  pip --version
  ```

### 1.2 pip 使用要点
| 命令 | 说明 |
|---|---|
| `pip install 包名` | 安装第三方库 |
| `python -m pip install 包名` | 同上，但通过 Python 调用，PATH 有问题时用这句保底 |
| `python -m playwright install chromium` | 同理，`xxx 不是内部或外部命令` 时的通用解法 |

**核心经验**：`xxx 不是内部或外部命令` = 系统 PATH 里找不到这个程序，改用 `python -m xxx` 形式几乎总能解决。

### 1.3 运行脚本
```
cd 文件所在目录        # 如 cd Desktop
python 文件名.py       # 输入前几个字母后按 Tab 可自动补全
```

---

## 第二章：项目一 —— 网页爬虫（Playwright + DrissionPage）

### 2.1 任务
抓取 https://mitadmissions.org/blogs/ 的文章标题、作者、评论数、时间、正文、图片，存为 CSV。

### 2.2 为什么用两个库？
- **Playwright**：负责列表页。页面是 JS 动态渲染的，普通 requests 拿不到内容，必须开真实浏览器。
- **DrissionPage**：负责详情页。它的 `ele()` 元素查找 API 写解析逻辑非常顺手。
- 两个库各自独立：**Playwright 用自己下载的 Chromium**（`playwright install chromium`），**DrissionPage 用本机安装的 Chrome**（不需要 chromedriver）。

### 2.3 核心知识点

**① 选择器（最重要的基本功）**
```python
page.query_selector_all('a[href*="/blogs/entry/"]')   # CSS：href 包含某字符串
page.ele('tag:h1')                                     # DrissionPage：按标签
page.ele('css:.entry-title')                           # 按 class
page.ele('xpath://a[contains(text(),"Comment")]')      # XPath：按文本内容
```
技巧：选**稳定特征**（如 URL 规律）比猜 class 名更可靠；写多个备选选择器逐个尝试，提高容错。

**② 等待**
- `page.wait_for_timeout(3000)`（Playwright）、`time.sleep(2)`：等 JS 渲染完成再提取，否则抓到空。

**③ 数据清洗细节**
- `urljoin(base, href)`：补全相对路径
- `.split("#")[0]`：去掉 `#comments` 锚点，给链接去重
- `img.attr("src") or img.attr("data-src")`：兼容懒加载图片

**④ 写 CSV**
```python
with open("out.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=[...])
    writer.writeheader()
    writer.writerows(rows)
```
- `encoding="utf-8-sig"`：让 **Excel 打开不乱码**（关键！）
- `newline=""`：防止 Windows 下出现空行

**⑤ 爬虫礼仪**：加 `time.sleep()` 延时、控制抓取数量，不给目标网站施压。

---

## 第三章：项目二 —— FastAPI 流式输出

### 3.1 核心概念

**普通返回 vs 流式返回**
```
普通：服务器攒齐全部内容 → 一次性发给浏览器
流式：每产生一小块 → 立刻发一块（打字机效果）
```

**三大件：**
1. **生成器 + `yield`**：每次 yield 立刻把这一块数据推送出去，这是流式的灵魂
2. **`async/await`**：`await asyncio.sleep(0.1)` 异步等待，不阻塞其他请求
3. **`StreamingResponse`**：FastAPI 提供的流式响应包装器

```python
async def text_generator():
    for char in TEXT:
        yield char                 # 立刻发送这一个字
        await asyncio.sleep(0.1)   # 停顿，制造打字效果

@app.get("/stream")
async def stream():
    return StreamingResponse(text_generator(), media_type="text/plain")
```

**SSE 格式**（大模型聊天接口同款）：
```python
yield f"data: {内容}\n\n"    # 格式：data: 开头，两个换行结尾
# 对应 media_type="text/event-stream"
```

### 3.2 运行与测试
```
uvicorn main:app --reload    # 标准启动方式，--reload 改代码自动重启
```
- 浏览器访问 `http://127.0.0.1:8000/stream` 看逐字效果
- curl 测试：`curl -N http://127.0.0.1:8000/stream`
  - ⚠️ **`-N` 必须加**：关闭输出缓冲，否则等全部接收完才显示，看不到"蹦字"
  - PowerShell 里要写 `curl.exe -N ...`

### 3.3 小知识
- `/favicon.ico 404`：浏览器自动请求标签页图标，没有就 404，**正常现象，忽略**
- 面试关键词：`yield`（分段发送）、`-N`（关闭缓冲）、SSE（`data:` 格式）

---

## 第四章：项目三 —— 大模型自动打标签

### 4.1 Pipeline 四步
```
读取 CSV → 调用模型分类 → 清洗输出 → 对比真值算准确率 → 保存 result.csv
```

### 4.2 核心知识点

**① Prompt 设计（零样本分类）**
```
请判断以下影评的情感倾向，只回答'正面'或'负面'，不要输出任何其他内容。
影评：{text}
```
要点：明确任务 + **限制输出格式**（方便程序解析）。

**② temperature=0**：分类任务要稳定输出，不要随机性。

**③ 输出清洗必须有**：真实模型常返回"正面。"带标点或多余句子，要用 `clean_output()` 规整到固定标签集，并留"未知"兜底。

**④ Mock 模式**：没有 API Key 时，用一个本地函数模拟模型行为，**保证 Pipeline 结构不变**——拿到 key 后只需替换一个函数。这是工程上常用的解耦思路。

**⑤ 结果分析（面试高频）**——模型什么时候出错：
- **反讽/阴阳怪气**："Oh fantastic, another..." 表面都是好词，实际在骂
- **先扬后抑**："视觉很棒，**但**剧情是灾难"——but 后面的才是重点
- 还有：否定句、比较句、领域黑话、过短歧义文本

**⑥ 改进方向**：few-shot 给示例、置信度低的人工复核、多次采样投票、扩大测试集、微调小模型。

---

## 第五章：踩坑速查表

| 报错/现象 | 原因 | 解决 |
|---|---|---|
| `Python was not found...` | 没装 Python 或没加 PATH | 官网安装，勾选 Add to PATH；装完**重开 cmd** |
| `pip 不是内部或外部命令` | pip 不在 PATH | 用 `python -m pip` |
| `playwright 不是内部或外部命令` | 库的 Scripts 目录不在 PATH | 用 `python -m playwright install chromium` |
| `Executable doesn't exist` (Playwright) | 没下载浏览器 | `python -m playwright install chromium` |
| DrissionPage 找不到浏览器 | 没装 Chrome | 装 Chrome，或 `set_browser_path` 指定路径 |
| 保存成 `data.csv.txt` | 记事本默认加 .txt | 另存为时选「所有文件」+ 编码 UTF-8 |
| Excel 打开 CSV 中文乱码 | 编码不对 | 代码里用 `utf-8-sig` 写文件 |
| 文件被占用无法保存 | 文件在 Excel 等程序中打开着 | 关掉占用它的程序再保存 |
| `/favicon.ico 404` | 浏览器自动请求图标 | 正常现象，忽略 |
| curl 看不到流式效果 | 输出被缓冲 | 加 `-N` 参数 |

---

## 第六章：通用经验总结

1. **环境类问题占新手报错的 80%**：PATH、编码、文件占用，遇事先想这三样
2. **选择器用稳定特征**：URL 规律 > class 名（class 可能改版变化）
3. **防御式编程**：多个备选选择器、输出清洗、异常捕获（`try/except`）
4. **可替换设计**：Mock 函数和真实实现保持同样接口，随时切换
5. **utf-8-sig**：凡是要给 Excel 看的 CSV，都用它
