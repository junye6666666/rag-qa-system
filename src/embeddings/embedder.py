"""嵌入向量生成器 — 将文本转为向量表示"""

import os
import logging
from typing import List

# 消掉 HF Hub 未认证警告（模型已缓存本地，无需认证）
os.environ.setdefault("HF_HUB_DISABLE_IMPLICIT_TOKEN", "1")
logging.getLogger("huggingface_hub").setLevel(logging.WARNING)

from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

from ..config import settings


class EmbeddingGenerator:
    """
    嵌入向量生成器。

    支持两种模式：
    1. 本地模型（默认）：使用 HuggingFace sentence-transformers，无需 API Key
    2. 远程 API：使用 OpenAI 兼容的 Embedding API

    切换方式：在 .env 中设置 use_local_embeddings=true/false
    """

    def __init__(self, model: str = None, api_key: str = None, base_url: str = None):
        if settings.use_local_embeddings:
            # 本地模型模式（免费、离线、无需 API Key）
            local_model = model or settings.local_embedding_model
            print(f"[Embedding] Using local model: {local_model}")
            self._embeddings = HuggingFaceEmbeddings(
                model_name=f"sentence-transformers/{local_model}",
                model_kwargs={"device": "cpu", "token": False},
                encode_kwargs={"normalize_embeddings": True},
            )
            self._model = local_model
        else:
            # 远程 API 模式
            kwargs = {
                "model": model or settings.embedding_model,
                "api_key": api_key or settings.api_key,
            }
            if base_url or settings.api_base_url:
                kwargs["base_url"] = base_url or settings.api_base_url
            self._embeddings = OpenAIEmbeddings(**kwargs)
            self._model = kwargs["model"]

    @property
    def model(self) -> str:
        return self._model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成文档嵌入向量。

        Args:
            texts: 文本列表

        Returns:
            向量列表，每个向量是 float 列表
        """
        if not texts:
            return []
        return self._embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """
        生成单条查询的嵌入向量。

        Args:
            text: 查询文本

        Returns:
            向量（float 列表）
        """
        return self._embeddings.embed_query(text)
