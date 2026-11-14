## 📖 项目简介
本项目为求职笔试作品。基于 Python 的 `FastAPI` 框架实现了一个流式输出（Streaming API）演示服务，模拟大模型（如 ChatGPT）对话时“文字逐个蹦出”的打字机效果。

## 🛠️ 核心技术
- **FastAPI**：构建高性能异步 Web 接口。
- **StreamingResponse**：利用 FastAPI 的流式响应机制，实现数据的分块传输。
- **AsyncIO**：使用 Python 异步生成器（Async Generator）控制数据推送节奏，模拟真实网络延迟。

## 🚀 快速启动

### 1. 安装依赖
在命令行中运行以下命令安装所需库：
```bash
pip install fastapi uvicorn
