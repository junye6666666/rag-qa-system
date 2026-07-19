"""文本切片器 — 将文档拆分为适合检索的小片段"""

from typing import List, Optional

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import settings


class TextChunker:
    """
    文本切片器，使用递归字符分割策略。

    分割优先级：段落(\\n\\n) > 换行(\\n) > 句号(。) > 空格( ) > 字符
    这种策略对中英文混合文本都有较好的效果。
    """

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", ".", " ", ""],
            keep_separator=True,
        )

    def split(self, documents: List[Document]) -> List[Document]:
        """
        将文档列表切分为小片段。

        Args:
            documents: LangChain Document 列表

        Returns:
            切分后的 Document 列表，每个包含原始文档的元数据
        """
        if not documents:
            return []

        chunks = self._splitter.split_documents(documents)

        # 为每个 chunk 添加序号信息
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["chunk_count"] = len(chunks)

        return chunks

    def split_text(self, text: str) -> List[str]:
        """切分纯文本（不包含元数据）"""
        return self._splitter.split_text(text)


def chunk_documents(
    documents: List[Document],
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> List[Document]:
    """便捷函数：切分文档"""
    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.split(documents)
