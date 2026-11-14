# -*- coding: utf-8 -*-
"""
FastAPI 流式输出 Demo
- /       ：普通接口，一次性返回
- /stream ：流式接口，文字一点点蹦出来
- /sse    ：SSE 格式流式接口（大模型聊天同款格式）
"""
import asyncio

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

TEXT = ("你好，这是一段流式输出的演示文字。"
        "你会看到它一个字一个字地蹦出来，就像 ChatGPT 的打字效果一样。"
        "Streaming API 非常适合大模型对话、日志实时推送这类场景。")


@app.get("/")
def index():
    """普通接口：一次性返回全部内容，用于对比"""
    return {"msg": "访问 /stream 查看流式输出效果"}


async def text_generator():
    """异步生成器：每次 yield 一小块文字，立刻发给客户端"""
    for char in TEXT:
        yield char               # 把这一个字立刻推送出去
        await asyncio.sleep(0.1)  # 停顿 0.1 秒，制造"打字机"效果


@app.get("/stream")
async def stream():
    """流式接口：StreamingResponse 包装生成器"""
    return StreamingResponse(
        text_generator(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"},  # 告诉浏览器/代理不要缓存缓冲
    )


@app.get("/sse")
async def sse():
    """SSE 格式流式接口：每段数据以 'data: ' 开头、两个换行结尾"""
    async def event_generator():
        for char in TEXT:
            yield f"data: {char}\n\n"
            await asyncio.sleep(0.1)
        yield "data: [DONE]\n\n"  # 结束标记

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# 支持直接 python main.py 启动
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)