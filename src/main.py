"""FastAPI 应用入口 — RAG 系统 API 服务"""

import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import ValidationError

from .config import settings
from .pipeline.pipeline import RAGPipeline
from .models.schemas import (
    DocumentInfo,
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentDeleteResponse,
    ChatRequest,
    ChatResponse,
    SourceDocument,
    HealthResponse,
)

# 全局 RAG 流水线（单例）
pipeline: RAGPipeline = None


def get_pipeline() -> RAGPipeline:
    """获取全局 RAG 流水线实例"""
    global pipeline
    if pipeline is None:
        pipeline = RAGPipeline()
    return pipeline


# ============================================================
# 生命周期事件（替代弃用的 on_event）
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭时的生命周期管理"""
    # 启动时执行
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    get_pipeline()  # 预初始化
    print(f"[OK] RAG system started, model: {settings.model_name}")
    yield  # 此处暂停，应用运行中...
    # 关闭时执行
    print("[OK] RAG system shutdown")


# ============================================================
# 应用初始化
# ============================================================

app = FastAPI(
    title="RAG 知识库问答系统",
    description="基于检索增强生成（RAG）的智能知识库问答系统。上传文档，提问即可获得基于文档内容的精准回答。",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 健康检查
# ============================================================

@app.get("/api/v1/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    """健康检查"""
    p = get_pipeline()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        documents_count=p.document_count,
        model=settings.model_name,
    )


# ============================================================
# 文档管理 API
# ============================================================

@app.post("/api/v1/documents/upload", response_model=DocumentUploadResponse, tags=["文档管理"])
async def upload_document(file: UploadFile = File(...)):
    """
    上传文档并摄入到知识库。

    支持格式: PDF, TXT, Markdown (.md), Word (.docx)
    最大大小: 20MB
    """
    p = get_pipeline()

    # 验证文件格式
    ext = os.path.splitext(file.filename or "")[1].lower()
    allowed = {".txt", ".md", ".pdf", ".docx"}
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}，支持: {', '.join(allowed)}",
        )

    # 验证大小
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小 ({size_mb:.1f}MB) 超过限制 ({settings.max_upload_size_mb}MB)",
        )

    # 保存到本地
    safe_filename = f"{uuid.uuid4().hex[:12]}_{file.filename}"
    file_path = os.path.join(settings.upload_dir, safe_filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # 摄入
    result = p.ingest(file_path)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    doc = result["document"]
    return DocumentUploadResponse(
        success=True,
        document=DocumentInfo(
            id=doc["id"],
            filename=doc["filename"],
            file_type=doc["file_type"],
            size_bytes=doc["size_bytes"],
            chunk_count=result["chunk_count"],
            uploaded_at=datetime.now().isoformat(),
        ),
        message=f"文档 '{doc['filename']}' 导入成功，共 {result['chunk_count']} 个片段",
    )


@app.get("/api/v1/documents", response_model=DocumentListResponse, tags=["文档管理"])
async def list_documents():
    """获取已导入的文档列表"""
    p = get_pipeline()
    docs = p.list_documents()

    documents = [
        DocumentInfo(
            id=doc.get("doc_id", doc.get("source", "")),
            filename=doc["source"],
            file_type=doc.get("file_type", ""),
            size_bytes=doc.get("file_size", 0),
            chunk_count=doc["chunk_count"],
            uploaded_at=doc.get("loaded_at", ""),
        )
        for doc in docs
    ]

    return DocumentListResponse(total=len(documents), documents=documents)


@app.delete(
    "/api/v1/documents/{filename}",
    response_model=DocumentDeleteResponse,
    tags=["文档管理"],
)
async def delete_document(filename: str):
    """删除指定文档及其所有知识库片段"""
    p = get_pipeline()
    deleted = p.delete_document(filename)

    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"未找到文档: {filename}")

    # 同时删除上传的文件
    for f in os.listdir(settings.upload_dir):
        if f.endswith(f"_{filename}"):
            os.remove(os.path.join(settings.upload_dir, f))

    return DocumentDeleteResponse(
        success=True, message=f"文档 '{filename}' 已删除（{deleted} 个片段）"
    )


# ============================================================
# 问答 API
# ============================================================

@app.post("/api/v1/chat", response_model=ChatResponse, tags=["问答"])
async def chat(request: ChatRequest):
    """
    RAG 问答（同步模式）。

    提交问题，获取基于知识库文档生成的回答及引用来源。
    """
    p = get_pipeline()
    result = p.query(request.question, top_k=request.top_k)

    sources = [
        SourceDocument(
            content=s["content"],
            source=s["source"],
            relevance_score=s["score"],
        )
        for s in result["sources"]
    ]

    return ChatResponse(answer=result["answer"], sources=sources, model=result["model"])


@app.post("/api/v1/chat/stream", tags=["问答"])
async def chat_stream(request: ChatRequest):
    """
    RAG 问答（流式 SSE 模式）。

    提交问题，通过 Server-Sent Events 流式返回生成的回答。
    """

    async def event_stream():
        p = get_pipeline()
        try:
            # 先发送检索到的来源信息
            sources = p._retriever.retrieve(request.question, top_k=request.top_k)
            import json

            sources_json = json.dumps(
                [
                    {"content": s["content"], "source": s["source"], "score": s["score"]}
                    for s in sources
                ],
                ensure_ascii=False,
            )
            yield f"event: sources\ndata: {sources_json}\n\n"

            # 流式生成回答
            async for chunk in p.query_stream(request.question, top_k=request.top_k):
                yield f"data: {chunk}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================
# 静态文件（前端）
# ============================================================

@app.get("/")
async def serve_frontend():
    """提供前端页面"""
    return FileResponse("static/index.html")


# 挂载静态资源目录
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================================
# 启动入口
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
