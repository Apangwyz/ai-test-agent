from .docx_processor import DocxProcessor
from .pdf_processor import PdfProcessor
from .md_processor import MdProcessor

class DocumentProcessorFactory:
    @staticmethod
    def get_processor(file_path):
        """
        Get the appropriate document processor based on file extension
        """
        if file_path.lower().endswith('.docx'):
            return DocxProcessor()
        elif file_path.lower().endswith('.pdf'):
            return PdfProcessor()
        elif file_path.lower().endswith('.md'):
            return MdProcessor()
        else:
            raise ValueError(f"Unsupported file type: {file_path}")