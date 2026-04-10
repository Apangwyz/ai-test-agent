from .base_processor import BaseDocumentProcessor
from docx import Document
import os

class DocxProcessor(BaseDocumentProcessor):
    def validate_file(self, file_path):
        return file_path.lower().endswith('.docx')
    
    def process(self, file_path):
        try:
            doc = Document(file_path)
            content = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    content.append(paragraph.text)
            return '\n'.join(content)
        except Exception as e:
            self.logger.error(f"Error processing DOCX file: {e}")
            raise
    
    def extract_structure(self, content):
        # Extract structured information from DOCX content
        lines = content.split('\n')
        structured_data = {
            'sections': [],
            'requirements': [],
            'constraints': []
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Simple section detection based on formatting
            if line.endswith(':') or line.isupper():
                current_section = line
                structured_data['sections'].append(current_section)
            elif 'requirement' in line.lower() or 'need' in line.lower():
                structured_data['requirements'].append(line)
            elif 'constraint' in line.lower() or 'limit' in line.lower():
                structured_data['constraints'].append(line)
        
        return structured_data