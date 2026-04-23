import pytest
from unittest.mock import Mock, patch
from src.document_processor.processor_factory import DocumentProcessorFactory
from src.document_processor.base_processor import BaseDocumentProcessor
from src.document_processor.docx_processor import DocxProcessor
from src.document_processor.pdf_processor import PdfProcessor
from src.document_processor.md_processor import MdProcessor

class TestDocumentProcessorFactory:
    """测试文档处理器工厂类"""

    def test_get_docx_processor(self):
        """测试获取docx处理器"""
        processor = DocumentProcessorFactory.get_processor("test.docx")
        assert isinstance(processor, DocxProcessor)

    def test_get_pdf_processor(self):
        """测试获取pdf处理器"""
        processor = DocumentProcessorFactory.get_processor("test.pdf")
        assert isinstance(processor, PdfProcessor)

    def test_get_md_processor(self):
        """测试获取md处理器"""
        processor = DocumentProcessorFactory.get_processor("test.md")
        assert isinstance(processor, MdProcessor)

    def test_get_unsupported_processor(self):
        """测试获取不支持的文件类型"""
        with pytest.raises(ValueError):
            DocumentProcessorFactory.get_processor("test.txt")

    def test_get_processor_case_insensitive(self):
        """测试大小写不敏感"""
        processor1 = DocumentProcessorFactory.get_processor("test.DOCX")
        processor2 = DocumentProcessorFactory.get_processor("test.PDF")
        processor3 = DocumentProcessorFactory.get_processor("test.MD")
        
        assert isinstance(processor1, DocxProcessor)
        assert isinstance(processor2, PdfProcessor)
        assert isinstance(processor3, MdProcessor)

class TestDocxProcessor:
    """测试Docx处理器"""

    def setup_method(self):
        """设置测试环境"""
        self.processor = DocxProcessor()

    def test_validate_file(self):
        """测试文件验证"""
        assert self.processor.validate_file("test.docx") is True

    @patch('docx.Document')
    def test_process(self, mock_document):
        """测试处理docx文件"""
        # 模拟Document对象
        mock_doc = Mock()
        mock_paragraph = Mock()
        mock_paragraph.text = "Test content"
        mock_doc.paragraphs = [mock_paragraph]
        mock_document.return_value = mock_doc

        # 执行测试
        content = self.processor.process("test.docx")

        # 验证结果
        assert "Test content" in content
        mock_document.assert_called_once_with("test.docx")

    def test_extract_structure(self):
        """测试提取结构"""
        content = "# Title\n\n## Subtitle\n\nContent"
        structure = self.processor.extract_structure(content)

        assert isinstance(structure, dict)
        assert "sections" in structure

class TestPdfProcessor:
    """测试Pdf处理器"""

    def setup_method(self):
        """设置测试环境"""
        self.processor = PdfProcessor()

    def test_validate_file(self):
        """测试文件验证"""
        assert self.processor.validate_file("test.pdf") is True

    @patch('PyPDF2.PdfReader')
    def test_process(self, mock_pdf_reader):
        """测试处理pdf文件"""
        # 模拟PdfReader对象
        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "PDF content"
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        # 执行测试
        content = self.processor.process("test.pdf")

        # 验证结果
        assert "PDF content" in content
        mock_pdf_reader.assert_called_once_with("test.pdf")

    def test_extract_structure(self):
        """测试提取结构"""
        content = "PDF document content"
        structure = self.processor.extract_structure(content)

        assert isinstance(structure, dict)
        assert "sections" in structure

class TestMdProcessor:
    """测试Md处理器"""

    def setup_method(self):
        """设置测试环境"""
        self.processor = MdProcessor()

    def test_validate_file(self):
        """测试文件验证"""
        assert self.processor.validate_file("test.md") is True

    @patch('builtins.open', new_callable=Mock)
    def test_process(self, mock_open):
        """测试处理md文件"""
        # 模拟文件打开
        mock_file = Mock()
        mock_file.read.return_value = "# Markdown content"
        mock_open.return_value.__enter__.return_value = mock_file

        # 执行测试
        content = self.processor.process("test.md")

        # 验证结果
        assert "# Markdown content" in content
        mock_open.assert_called_once_with("test.md", 'r', encoding='utf-8')

    def test_extract_structure(self):
        """测试提取结构"""
        content = "# Title\n\n## Subtitle\n\nContent"
        structure = self.processor.extract_structure(content)

        assert isinstance(structure, dict)
        assert "sections" in structure
        assert "Title" in structure["sections"]
        assert "Subtitle" in structure["sections"]

class TestBaseDocumentProcessor:
    """测试基础文档处理器"""

    def test_validate_file(self):
        """测试文件验证默认实现"""
        # 创建一个基础处理器的子类
        class TestProcessor(BaseDocumentProcessor):
            def process(self, file_path):
                pass
            def extract_structure(self, content):
                pass

        processor = TestProcessor()
        assert processor.validate_file("test.txt") is True

if __name__ == "__main__":
    pytest.main([__file__])
