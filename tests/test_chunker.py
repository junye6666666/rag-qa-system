"""文本切片器测试"""

import pytest
from langchain_core.documents import Document
from src.chunking.chunker import TextChunker


class TestTextChunker:
    """测试文本切片器"""

    def test_split_empty_list(self):
        """测试空文档列表"""
        chunker = TextChunker(chunk_size=100, chunk_overlap=10)
        result = chunker.split([])
        assert result == []

    def test_split_short_document(self):
        """测试短文档（长度小于 chunk_size）"""
        chunker = TextChunker(chunk_size=500, chunk_overlap=50)
        docs = [Document(page_content="这是一个短文本", metadata={"source": "test.txt"})]
        result = chunker.split(docs)
        assert len(result) == 1
        assert result[0].page_content == "这是一个短文本"

    def test_split_long_document(self):
        """测试长文档（长度大于 chunk_size）"""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        long_text = "这是第一段。" * 30  # 约 180 字符
        docs = [Document(page_content=long_text, metadata={"source": "test.txt"})]
        result = chunker.split(docs)
        assert len(result) > 1  # 应该被切分为多个片段

    def test_chunk_metadata_preserved(self):
        """测试切分后保留原始元数据"""
        chunker = TextChunker(chunk_size=100, chunk_overlap=10)
        docs = [
            Document(
                page_content="A" * 300,
                metadata={"source": "orig.txt", "author": "test"},
            )
        ]
        result = chunker.split(docs)
        assert len(result) > 1
        for chunk in result:
            assert chunk.metadata["source"] == "orig.txt"
            assert "chunk_index" in chunk.metadata
            assert "chunk_count" in chunk.metadata

    def test_chunk_overlap(self):
        """测试重叠切片"""
        chunker = TextChunker(chunk_size=100, chunk_overlap=30)
        text = "ABCDEFGHIJ" * 50  # 500 字符
        docs = [Document(page_content=text)]
        result = chunker.split(docs)
        assert len(result) >= 4

    def test_split_text(self):
        """测试纯文本切片"""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        text = "第一段内容。\n\n第二段内容。\n\n第三段内容。" * 5
        chunks = chunker.split_text(text)
        assert len(chunks) > 1
