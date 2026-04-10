from flask_restful import Resource, reqparse
from flask import request
from src.document_processor.processor_factory import DocumentProcessorFactory
import os

class DocumentProcessorResource(Resource):
    def post(self):
        """
        Process a document file and return structured content
        """
        try:
            # Check if file is uploaded
            if 'file' not in request.files:
                return {'error': 'No file uploaded'}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {'error': 'No file selected'}, 400
            
            # Save file temporarily
            temp_file_path = f'/tmp/{file.filename}'
            file.save(temp_file_path)
            
            try:
                # Get appropriate processor
                processor = DocumentProcessorFactory.get_processor(temp_file_path)
                
                # Process document
                content = processor.process(temp_file_path)
                
                # Extract structure
                structured_data = processor.extract_structure(content)
                
                return {
                    'status': 'success',
                    'content': content,
                    'structured_data': structured_data
                }, 200
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': f'Error processing document: {str(e)}'}, 500