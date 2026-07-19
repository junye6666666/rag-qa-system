"""向量存储 — 基于 ChromaDB 的文档向量管理"""

import os
from typing import List, Optional, Tuple

from langchain_core.documents import Document
from langchain_chroma import Chroma

from ..config import settings
from ..embeddings.embedder import EmbeddingGenerator


class VectorStore:
    """
    ChromaDB 向量存储封装。

    功能：
    - 添加文档（自动生成嵌入并存储）
    - 按文档 ID 删除
    - 语义相似度搜索
    - 获取文档数量
    """

    def __init__(self, embedder: Optional[EmbeddingGenerator] = None):
        self._embedder = embedder or EmbeddingGenerator()
        self._persist_dir = settings.chroma_persist_dir

        os.makedirs(self._persist_dir, exist_ok=True)

        self._store = Chroma(
            collection_name="rag_documents",
            embedding_function=self._embedder._embeddings,
            persist_directory=self._persist_dir,
        )

    def add_documents(self, documents: List[Document]) -> int:
        """
        添加文档到向量存储。

        Args:
            documents: 待添加的文档列表

        Returns:
            新增的文档数量
        """
        if not documents:
            return 0

        self._store.add_documents(documents)
        return len(documents)

    def delete_by_source(self, source_filename: str) -> int:
        """
        按源文件名删除文档的所有切片。

        Args:
            source_filename: 原始文件名

        Returns:
            删除的文档数量
        """
        collection = self._store._collection
        results = collection.get(where={"source": source_filename})
        ids_to_delete = results.get("ids", [])

        if ids_to_delete:
            collection.delete(ids=ids_to_delete)

        return len(ids_to_delete)

    def search(
        self, query: str, top_k: Optional[int] = None
    ) -> List[Tuple[Document, float]]:
        """
        语义搜索。

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            (Document, score) 元组列表，按相似度降序排列
        """
        k = top_k or settings.top_k
        results = self._store.similarity_search_with_relevance_scores(query, k=k)
        return results

    def get_document_sources(self) -> List[dict]:
        """
        获取所有已存储的文档源信息（去重）。

        Returns:
            文档源信息列表，包含文件名、类型、切片数量等
        """
        collection = self._store._collection
        all_data = collection.get()

        if not all_data["ids"]:
            return []

        # 按 source 分组统计
        source_map = {}
        for i, meta in enumerate(all_data["metadatas"]):
            source = meta.get("source", "unknown")
            if source not in source_map:
                source_map[source] = {
                    "source": source,
                    "file_type": meta.get("file_type", ""),
                    "file_size": meta.get("file_size", 0),
                    "chunk_count": 0,
                    "loaded_at": meta.get("loaded_at", ""),
                }
            source_map[source]["chunk_count"] += 1

        return list(source_map.values())

    @property
    def count(self) -> int:
        """向量存储中的总文档数（切片级别）"""
        return self._store._collection.count()
