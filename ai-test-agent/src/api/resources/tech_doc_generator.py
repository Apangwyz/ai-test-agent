from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.tech_doc_generator.tech_doc_generator import TechDocGenerator
from src.knowledge_base.manager import KnowledgeBaseManager
from datetime import datetime

class TechDocGeneratorResource(Resource):
    @jwt_required()
    def post(self):
        """
        Generate technical documentation based on structured requirements
        """
        parser = reqparse.RequestParser()
        parser.add_argument('structured_data', type=dict, required=True, help='Structured requirements data')
        parser.add_argument('clarification_doc', type=dict, required=False, help='Clarification document')
        parser.add_argument('save_to_kb', type=bool, default=False, help='Save to knowledge base')
        args = parser.parse_args()
        
        try:
            generator = TechDocGenerator()
            tech_doc = generator.generate_tech_doc(args['structured_data'], args.get('clarification_doc'))
            
            kb_id = None
            if args.get('save_to_kb'):
                kb_manager = KnowledgeBaseManager()
                kb_id = kb_manager.save_record(
                    title='Technical Document',
                    content=tech_doc,
                    record_type='tech_doc',
                    project_id=None
                )
            
            return {
                'status': 'success',
                'tech_doc': tech_doc,
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
