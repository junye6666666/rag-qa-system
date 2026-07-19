"""检索器测试"""

import pytest
from src.retrieval.retriever import DocumentRetriever


class TestDocumentRetriever:
    """测试检索器"""

    def test_format_context_empty(self):
        """测试空检索结果的上下文格式化"""
        retriever = DocumentRetriever.__new__(DocumentRetriever)  # 不调用 __init__
        result = retriever.format_context([])
        assert "暂无相关文档" in result

    def test_format_context_with_docs(self):
        """测试有结果的上下文格式化"""
        retriever = DocumentRetriever.__new__(DocumentRetriever)
        docs = [
            {
                "content": "Python 是一种编程语言",
                "source": "python_intro.md",
                "score": 0.95,
            },
            {
                "content": "FastAPI 是一个 Web 框架",
                "source": "fastapi_guide.md",
                "score": 0.82,
            },
        ]
        result = retriever.format_context(docs)
        assert "Python 是一种编程语言" in result
        assert "python_intro.md" in result
        assert "FastAPI 是一个 Web 框架" in result
        assert "fastapi_guide.md" in result
        assert "相关度" in result
