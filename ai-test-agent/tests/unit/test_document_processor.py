import unittest
import os
import tempfile
from src.document_processor.processor_factory import DocumentProcessorFactory

class TestDocumentProcessor(unittest.TestCase):
    def setUp(self):
        # Create temporary test files
        self.test_files = {}
        
        # Create test MD file
        md_content = "# Test Document\n\n## Requirements\n- User authentication\n- Data validation\n\n## Constraints\n- Performance requirements"
        md_file = tempfile.NamedTemporaryFile(suffix='.md', delete=False)
        md_file.write(md_content.encode('utf-8'))
        md_file.close()
        self.test_files['md'] = md_file.name
    
    def tearDown(self):
        # Clean up temporary files
        for file_path in self.test_files.values():
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def test_md_processor(self):
        """Test Markdown document processing"""
        processor = DocumentProcessorFactory.get_processor(self.test_files['md'])
        content = processor.process(self.test_files['md'])
        structured_data = processor.extract_structure(content)
        
        self.assertIn('Test Document', content)
        self.assertIn('User authentication', content)
        self.assertIsInstance(structured_data, dict)
        self.assertIn('sections', structured_data)
        self.assertIn('requirements', structured_data)
        self.assertIn('constraints', structured_data)
    
    def test_processor_factory(self):
        """Test processor factory creates correct processor"""
        md_processor = DocumentProcessorFactory.get_processor(self.test_files['md'])
        self.assertTrue(hasattr(md_processor, 'process'))
        self.assertTrue(hasattr(md_processor, 'extract_structure'))
    
    def test_unsupported_file_type(self):
        """Test unsupported file type raises ValueError"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'Test content')
            txt_file = f.name
        
        try:
            with self.assertRaises(ValueError):
                DocumentProcessorFactory.get_processor(txt_file)
        finally:
            if os.path.exists(txt_file):
                os.remove(txt_file)

if __name__ == '__main__':
    unittest.main()