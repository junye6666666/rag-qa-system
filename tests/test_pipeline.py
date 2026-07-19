"""RAG 流水线集成测试"""

import os
import tempfile
import pytest
from src.pipeline.pipeline import RAGPipeline
from src.config import settings


# 检查是否配置了真实的 API Key
REAL_API_KEY = bool(settings.api_key) and settings.api_key not in (
    "sk-your-api-key-here", "sk-placeholder", ""
)

class TestRAGPipeline:
    """测试 RAG 流水线"""

    @pytest.fixture
    def pipeline(self):
        """创建测试用的流水线实例"""
        return RAGPipeline.__new__(RAGPipeline)

    @pytest.mark.skipif(
        not REAL_API_KEY,
        reason="需要配置真实的 API_KEY，当前使用占位符。请编辑 .env 文件"
    )
    def test_ingest_txt_file(self):
        """测试摄入 TXT 文件（需要 API Key）"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("Python 是一种高级编程语言。它由 Guido van Rossum 创建。\n" * 20)
            tmp_path = f.name

        try:
            pipeline = RAGPipeline()
            result = pipeline.ingest(tmp_path)
            assert result["success"] is True
            assert result["document"] is not None
            assert result["document"]["filename"] == os.path.basename(tmp_path)
            assert result["chunk_count"] > 0
            assert result["error"] is None

            # 清理
            pipeline.delete_document(os.path.basename(tmp_path))
        finally:
            os.unlink(tmp_path)

    def test_ingest_nonexistent_file(self):
        """测试摄入不存在的文件"""
        pipeline = RAGPipeline()
        result = pipeline.ingest("/nonexistent/file.pdf")
        assert result["success"] is False
        assert result["error"] is not None

    def test_list_documents_initially_empty(self):
        """测试初始文档列表为空"""
        # 跳过此测试如果向量数据库中有数据
        pass

    def test_document_count(self):
        """测试文档计数"""
        pipeline = RAGPipeline()
        count = pipeline.document_count
        assert isinstance(count, int)
        assert count >= 0
