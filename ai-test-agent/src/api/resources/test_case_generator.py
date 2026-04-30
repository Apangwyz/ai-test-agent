from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.test_case_generator.test_case_generator import TestCaseGenerator
from src.knowledge_base.manager import KnowledgeBaseManager
from datetime import datetime

class TestCaseGeneratorResource(Resource):
    @jwt_required()
    def post(self):
        """
        Generate test cases based on requirements and technical documentation
        """
        parser = reqparse.RequestParser()
        parser.add_argument('structured_data', type=dict, required=True, help='Structured requirements data')
        parser.add_argument('tech_doc', type=dict, required=False, help='Technical documentation')
        parser.add_argument('save_to_kb', type=bool, default=False, help='Save to knowledge base')
        args = parser.parse_args()
        
        try:
            generator = TestCaseGenerator()
            test_cases = generator.generate_test_cases(args['structured_data'], args.get('tech_doc'))
            
            kb_id = None
            if args.get('save_to_kb'):
                kb_manager = KnowledgeBaseManager()
                kb_id = kb_manager.save_record(
                    title='Test Cases',
                    content=test_cases,
                    record_type='test_cases',
                    project_id=None
                )
            
            return {
                'status': 'success',
                'test_cases': test_cases,
                'knowledge_base_id': kb_id
            }, 200
            
        except Exception as e:
            return self._error_response('PROCESSING_ERROR', str(e)), 500
    
    def _error_response(self, code, message):
        return {
            'status': 'error',
            'code': code,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
