"""RAG 流程编排 — 完整的文档摄入和问答流程"""

import os
import uuid
from typing import List, Optional, AsyncIterator

from ..config import settings
from ..document_loader.loader import DocumentLoader
from ..chunking.chunker import TextChunker
from ..embeddings.embedder import EmbeddingGenerator
from ..vector_store.store import VectorStore
from ..retrieval.retriever import DocumentRetriever
from ..generation.generator import LLMGenerator


class RAGPipeline:
    """
    RAG 流程编排器。

    将文档加载、切片、嵌入、存储、检索、生成串联成完整流程。

    使用方式:
        pipeline = RAGPipeline()

        # 1. 摄入文档
        result = pipeline.ingest("path/to/document.pdf")

        # 2. 问答
        answer = pipeline.query("你的问题？")

        # 3. 流式问答
        async for chunk in pipeline.query_stream("你的问题？"):
            print(chunk, end="")
    """

    def __init__(self):
        self._embedder = EmbeddingGenerator()
        self._vector_store = VectorStore(embedder=self._embedder)
        self._retriever = DocumentRetriever(
            vector_store=self._vector_store, embedder=self._embedder
        )
        self._generator = LLMGenerator()

    # ============================================================
    # 文档摄入
    # ============================================================

    def ingest(self, file_path: str) -> dict:
        """
        摄入单个文档：加载 → 切片 → 嵌入 → 存储。

        Args:
            file_path: 文件路径

        Returns:
            {"success": bool, "document": dict, "chunk_count": int, "error": str}
        """
        try:
            # 1. 加载
            documents = DocumentLoader.load(file_path)

            # 2. 切片
            chunker = TextChunker()
            chunks = chunker.split(documents)

            # 3. 生成文档唯一 ID 并加入元数据
            doc_id = str(uuid.uuid4())
            for chunk in chunks:
                chunk.metadata["doc_id"] = doc_id

            # 4. 存储到向量数据库
            self._vector_store.add_documents(chunks)

            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            ext = os.path.splitext(file_path)[1]

            return {
                "success": True,
                "document": {
                    "id": doc_id,
                    "filename": filename,
                    "file_type": ext,
                    "size_bytes": file_size,
                },
                "chunk_count": len(chunks),
                "error": None,
            }
        except Exception as e:
            return {
                "success": False,
                "document": None,
                "chunk_count": 0,
                "error": str(e),
            }

    # ============================================================
    # 问答
    # ============================================================

    def query(self, question: str, top_k: Optional[int] = None) -> dict:
        """
        RAG 问答（同步）。

        Args:
            question: 用户问题
            top_k: 检索文档数量

        Returns:
            {"answer": str, "sources": list, "model": str}
        """
        # 1. 检索
        sources = self._retriever.retrieve(question, top_k=top_k)

        # 2. 构建上下文
        context = self._retriever.format_context(sources)

        # 3. 生成
        answer = self._generator.generate(question, context)

        return {
            "answer": answer,
            "sources": sources,
            "model": self._generator.model,
        }

    async def query_stream(
        self, question: str, top_k: Optional[int] = None
    ) -> AsyncIterator[str]:
        """
        RAG 问答（流式）。

        Yields:
            增量生成的文本片段
        """
        # 1. 检索
        sources = self._retriever.retrieve(question, top_k=top_k)

        # 2. 构建上下文
        context = self._retriever.format_context(sources)

        # 3. 流式生成
        async for chunk in self._generator.generate_stream(question, context):
            yield chunk

    # ============================================================
    # 文档管理
    # ============================================================

    def list_documents(self) -> List[dict]:
        """列出所有已摄入的文档"""
        return self._vector_store.get_document_sources()

    def delete_document(self, source_filename: str) -> int:
        """删除文档及其所有切片"""
        return self._vector_store.delete_by_source(source_filename)

    @property
    def document_count(self) -> int:
        """已存储的文档切片总数"""
        return self._vector_store.count
