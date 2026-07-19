"""文档加载器测试"""

import os
import tempfile
import pytest
from src.document_loader.loader import DocumentLoader


class TestDocumentLoader:
    """测试文档加载器"""

    def test_load_txt(self):
        """测试加载 TXT 文件"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("Hello World\n这是测试文本")
            tmp_path = f.name

        try:
            docs = DocumentLoader.load(tmp_path)
            assert len(docs) == 1
            assert "Hello World" in docs[0].page_content
            assert docs[0].metadata["source"] == os.path.basename(tmp_path)
            assert docs[0].metadata["file_type"] == ".txt"
        finally:
            os.unlink(tmp_path)

    def test_load_markdown(self):
        """测试加载 Markdown 文件"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("# 标题\n\n这是一段**加粗**文本")
            tmp_path = f.name

        try:
            docs = DocumentLoader.load(tmp_path)
            assert len(docs) == 1
            assert "# 标题" in docs[0].page_content
            assert docs[0].metadata["format"] == "markdown"
        finally:
            os.unlink(tmp_path)

    def test_unsupported_format(self):
        """测试不支持的文件格式"""
        # 先创建真实文件再测试格式检查
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".xyz", delete=False, encoding="utf-8"
        ) as f:
            f.write("test")
            tmp_path = f.name
        try:
            with pytest.raises(ValueError, match="不支持的文件格式"):
                DocumentLoader.load(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_file_not_found(self):
        """测试文件不存在的情况"""
        with pytest.raises(FileNotFoundError):
            DocumentLoader.load("/nonexistent/file.txt")

    def test_load_empty_txt(self):
        """测试加载空文件"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("")
            tmp_path = f.name

        try:
            docs = DocumentLoader.load(tmp_path)
            assert len(docs) == 1
            assert docs[0].page_content == ""
        finally:
            os.unlink(tmp_path)
