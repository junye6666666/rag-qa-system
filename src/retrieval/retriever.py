"""检索器 — 语义搜索并返回相关文档片段"""

from typing import List, Optional

from langchain_core.documents import Document

from ..config import settings
from ..vector_store.store import VectorStore
from ..embeddings.embedder import EmbeddingGenerator


class DocumentRetriever:
    """
    文档检索器。

    功能：
    - 基于语义相似度检索最相关的文档片段
    - 返回带相关性分数的结果
    """

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedder: Optional[EmbeddingGenerator] = None,
    ):
        self._vector_store = vector_store or VectorStore(embedder=embedder)
        self._embedder = embedder or EmbeddingGenerator()

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[dict]:
        """
        检索与查询最相关的文档片段。

        Args:
            query: 用户查询文本
            top_k: 返回的最大结果数量

        Returns:
            [{"content": str, "source": str, "score": float}, ...]
        """
        k = top_k or settings.top_k
        results = self._vector_store.search(query, top_k=k)

        return [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "score": round(score, 4),
            }
            for doc, score in results
        ]

    def format_context(self, retrieved_docs: List[dict]) -> str:
        """
        将检索结果格式化为 LLM 可用的上下文字符串。

        Args:
            retrieved_docs: retrieve() 的返回结果

        Returns:
            格式化的上下文字符串
        """
        if not retrieved_docs:
            return "暂无相关文档。请基于你的知识回答问题，并告知用户当前知识库中没有相关信息。"

        parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            parts.append(
                f"[文档片段 {i}] 来源: {doc['source']} (相关度: {doc['score']})\n"
                f"{doc['content']}\n"
            )

        return "\n".join(parts)
