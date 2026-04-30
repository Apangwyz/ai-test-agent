from flask_restful import Resource, reqparse
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.document_processor.processor_factory import DocumentProcessorFactory
from src.clarification_generator.clarification_generator import ClarificationGenerator
from src.tech_doc_generator.tech_doc_generator import TechDocGenerator
from src.coding_task_generator.coding_task_generator import CodingTaskGenerator
from src.test_case_generator.test_case_generator import TestCaseGenerator
from src.knowledge_base.manager import KnowledgeBaseManager
from src.common.document_exporter import DocumentExporter
import os
import uuid
from datetime import datetime

class DocumentProcessorResource(Resource):
    def post(self):
        """
        Process a document file and return structured content
        """
        try:
            if 'file' not in request.files:
                return {'error': 'No file uploaded'}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {'error': 'No file selected'}, 400
            
            temp_file_path = f'/tmp/{file.filename}'
            file.save(temp_file_path)
            
            try:
                processor = DocumentProcessorFactory.get_processor(temp_file_path)
                content = processor.process(temp_file_path)
                structured_data = processor.extract_structure(content)
                
                return {
                    'status': 'success',
                    'content': content,
                    'structured_data': structured_data
                }, 200
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': f'Error processing document: {str(e)}'}, 500

class DocumentProcessFullResource(Resource):
    @jwt_required()
    def post(self):
        """
        Full process pipeline: parse → clarification → tech doc → tasks → test cases → save to KB
        """
        try:
            # Get user ID from JWT
            user_id = get_jwt_identity()
            
            # Parse request
            parser = reqparse.RequestParser()
            parser.add_argument('project_name', type=str, required=False)
            parser.add_argument('save_to_knowledge_base', type=bool, default=True)
            args = parser.parse_args()
            
            # Check file
            if 'file' not in request.files:
                return self._error_response('VALIDATION_ERROR', 'No file uploaded'), 400
            
            file = request.files['file']
            if file.filename == '':
                return self._error_response('VALIDATION_ERROR', 'No file selected'), 400
            
            # Extract project name
            project_name = args.get('project_name')
            if not project_name:
                project_name = os.path.splitext(file.filename)[0]
            
            # Generate project ID
            project_id = str(uuid.uuid4())
            
            # Save file temporarily
            temp_file_path = f'/tmp/{file.filename}'
            file.save(temp_file_path)
            
            try:
                # 1. Parse document
                processor = DocumentProcessorFactory.get_processor(temp_file_path)
                content = processor.process(temp_file_path)
                structured_data = processor.extract_structure(content)
                
                # 2. Generate clarification document
                clarification_generator = ClarificationGenerator()
                clarification_doc = clarification_generator.generate(structured_data)
                
                # 3. Generate technical document
                tech_doc_generator = TechDocGenerator()
                tech_doc = tech_doc_generator.generate(structured_data, clarification_doc)
                
                # 4. Generate coding tasks
                task_generator = CodingTaskGenerator()
                tasks = task_generator.generate(structured_data, tech_doc)
                
                # 5. Generate test cases
                test_case_generator = TestCaseGenerator()
                test_cases = test_case_generator.generate(structured_data, tech_doc)
                
                # 6. Save to knowledge base if requested
                kb_id = None
                if args.get('save_to_knowledge_base'):
                    kb_manager = KnowledgeBaseManager()
                    kb_id = kb_manager.save_record(
                        title=project_name,
                        content={
                            'structured_data': structured_data,
                            'clarification_doc': clarification_doc,
                            'tech_doc': tech_doc,
                            'tasks': tasks,
                            'test_cases': test_cases
                        },
                        record_type='document',
                        project_id=project_id
                    )
                
                # Export documents
                exporter = DocumentExporter()
                output_dir = os.path.join('docs', 'requirements', 'api_results', project_id)
                os.makedirs(output_dir, exist_ok=True)
                
                exporter.export_to_markdown(structured_data, os.path.join(output_dir, 'structured_data.md'))
                exporter.export_to_markdown(clarification_doc, os.path.join(output_dir, 'clarification_doc.md'))
                exporter.export_to_markdown(tech_doc, os.path.join(output_dir, 'tech_doc.md'))
                exporter.export_to_markdown(tasks, os.path.join(output_dir, 'tasks.md'))
                exporter.export_to_markdown(test_cases, os.path.join(output_dir, 'test_cases.md'))
                
                # Build response
                response = {
                    'status': 'success',
                    'project_id': project_id,
                    'project_name': project_name,
                    'processed_at': datetime.now().isoformat(),
                    'results': {
                        'structured_data': structured_data,
                        'clarification_doc': clarification_doc,
                        'tech_doc': tech_doc,
                        'tasks': tasks,
                        'test_cases': test_cases
                    },
                    'knowledge_base_saved': args.get('save_to_knowledge_base'),
                    'knowledge_base_id': kb_id
                }
                
                return response, 200
            
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    
        except ValueError as e:
            return self._error_response('VALIDATION_ERROR', str(e)), 400
        except Exception as e:
            return self._error_response('PROCESSING_ERROR', f'Error processing document: {str(e)}'), 500
    
    def _error_response(self, code, message):
        return {
            'status': 'error',
            'code': code,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
