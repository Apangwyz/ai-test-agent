from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.coding_task_generator.coding_task_generator import CodingTaskGenerator
from src.knowledge_base.manager import KnowledgeBaseManager
from datetime import datetime

class CodingTaskGeneratorResource(Resource):
    @jwt_required()
    def post(self):
        """
        Generate coding tasks based on technical documentation
        """
        parser = reqparse.RequestParser()
        parser.add_argument('structured_data', type=dict, required=False, help='Structured requirements data')
        parser.add_argument('tech_doc', type=dict, required=True, help='Technical documentation')
        parser.add_argument('save_to_kb', type=bool, default=False, help='Save to knowledge base')
        args = parser.parse_args()
        
        try:
            generator = CodingTaskGenerator()
            tasks = generator.generate_tasks(args['tech_doc'], args.get('structured_data'))
            
            kb_id = None
            if args.get('save_to_kb'):
                kb_manager = KnowledgeBaseManager()
                kb_id = kb_manager.save_record(
                    title='Coding Tasks',
                    content=tasks,
                    record_type='tasks',
                    project_id=None
                )
            
            return {
                'status': 'success',
                'tasks': tasks,
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
