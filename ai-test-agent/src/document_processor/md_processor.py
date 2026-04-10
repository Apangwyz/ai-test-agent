from .base_processor import BaseDocumentProcessor
import mistune

class MdProcessor(BaseDocumentProcessor):
    def validate_file(self, file_path):
        return file_path.lower().endswith('.md')
    
    def process(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except Exception as e:
            self.logger.error(f"Error processing MD file: {e}")
            raise
    
    def extract_structure(self, content):
        # Extract structured information from Markdown content
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
            
            # Detect sections (headings)
            if line.startswith('#'):
                structured_data['sections'].append(line)
            elif 'requirement' in line.lower() or 'need' in line.lower():
                structured_data['requirements'].append(line)
            elif 'constraint' in line.lower() or 'limit' in line.lower():
                structured_data['constraints'].append(line)
        
        return structured_data