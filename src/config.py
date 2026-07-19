"""配置管理模块 — 从环境变量读取所有配置项"""

import os
import warnings

from pydantic_settings import BaseSettings
from typing import Optional

# 使用本地 embedding 模型时，不需要 HF Hub 认证（模型在本地缓存）
os.environ.setdefault("HF_HUB_DISABLE_IMPLICIT_TOKEN", "1")


class Settings(BaseSettings):
    """应用配置，自动从 .env 文件和环境变量读取"""

    # --- LLM API 配置 ---
    api_base_url: Optional[str] = None  # None 表示使用 OpenAI 默认地址
    api_key: str = "sk-placeholder"
    model_name: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # --- 本地 Embedding（无需 API，默认启用） ---
    use_local_embeddings: bool = True
    local_embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"

    # --- 向量数据库 ---
    chroma_persist_dir: str = "./chroma_db"

    # --- 文本切片 ---
    chunk_size: int = 500
    chunk_overlap: int = 50

    # --- 检索 ---
    top_k: int = 4

    # --- 服务 ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- 上传 ---
    upload_dir: str = "./data/uploads"
    max_upload_size_mb: int = 20

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


# 全局单例
settings = Settings()
