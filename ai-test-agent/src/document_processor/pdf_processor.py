from .base_processor import BaseDocumentProcessor
import PyPDF2

class PdfProcessor(BaseDocumentProcessor):
    def validate_file(self, file_path):
        return file_path.lower().endswith('.pdf')
    
    def process(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                content = []
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        content.append(text)
                return '\n'.join(content)
        except Exception as e:
            self.logger.error(f"Error processing PDF file: {e}")
            raise
    
    def extract_structure(self, content):
        # Extract structured information from PDF content
        lines = content.split('\n')
        structured_data = {
            'sections': [],
            'requirements': [],
            'constraints': []
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Simple section detection based on formatting
            if line.endswith(':') or line.isupper():
                structured_data['sections'].append(line)
            elif 'requirement' in line.lower() or 'need' in line.lower():
                structured_data['requirements'].append(line)
            elif 'constraint' in line.lower() or 'limit' in line.lower():
                structured_data['constraints'].append(line)
        
        return structured_data