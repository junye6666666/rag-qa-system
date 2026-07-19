"""Pydantic 数据模型 — API 请求/响应结构"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ============================================================
# 文档相关
# ============================================================

class DocumentInfo(BaseModel):
    """文档元信息"""
    id: str = Field(..., description="文档唯一 ID")
    filename: str = Field(..., description="原始文件名")
    file_type: str = Field(..., description="文件类型（pdf/txt/md/docx）")
    size_bytes: int = Field(..., description="文件大小（字节）")
    chunk_count: int = Field(default=0, description="切片数量")
    uploaded_at: str = Field(..., description="上传时间 ISO 格式")


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    success: bool
    document: Optional[DocumentInfo] = None
    message: str = ""


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    total: int
    documents: List[DocumentInfo]


class DocumentDeleteResponse(BaseModel):
    """文档删除响应"""
    success: bool
    message: str = ""


# ============================================================
# 聊天相关
# ============================================================

class SourceDocument(BaseModel):
    """引用来源文档片段"""
    content: str = Field(..., description="片段内容")
    source: str = Field(..., description="来源文件名")
    relevance_score: float = Field(..., description="相关性分数")


class ChatRequest(BaseModel):
    """聊天请求"""
    question: str = Field(..., min_length=1, max_length=5000, description="用户问题")
    top_k: Optional[int] = Field(default=None, ge=1, le=20, description="检索文档数量")


class ChatResponse(BaseModel):
    """聊天响应"""
    answer: str = Field(..., description="生成的回答")
    sources: List[SourceDocument] = Field(default_factory=list, description="引用的来源文档")
    model: str = Field(..., description="使用的模型名称")


# ============================================================
# 健康检查
# ============================================================

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    version: str = "1.0.0"
    documents_count: int = 0
    model: str = ""
