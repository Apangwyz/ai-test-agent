from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.clarification_generator.clarification_generator import ClarificationGenerator
from src.knowledge_base.manager import KnowledgeBaseManager
from datetime import datetime

class ClarificationGeneratorResource(Resource):
    @jwt_required()
    def post(self):
        """
        Generate clarification document based on structured requirements
        """
        parser = reqparse.RequestParser()
        parser.add_argument('structured_data', type=dict, required=True, help='Structured requirements data')
        parser.add_argument('save_to_kb', type=bool, default=False, help='Save to knowledge base')
        args = parser.parse_args()
        
        try:
            generator = ClarificationGenerator()
            clarification_doc = generator.generate_clarification(args['structured_data'])
            
            kb_id = None
            if args.get('save_to_kb'):
                kb_manager = KnowledgeBaseManager()
                kb_id = kb_manager.save_record(
                    title='Clarification Document',
                    content=clarification_doc,
                    record_type='clarification',
                    project_id=None
                )
            
            return {
                'status': 'success',
                'clarification_doc': clarification_doc,
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
