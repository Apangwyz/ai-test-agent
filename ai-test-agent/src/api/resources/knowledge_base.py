from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.knowledge_base.manager import KnowledgeBaseManager
from datetime import datetime

class KnowledgeBaseSearchResource(Resource):
    @jwt_required()
    def get(self):
        """
        Search knowledge base
        """
        parser = reqparse.RequestParser()
        parser.add_argument('query', type=str, required=True, help='Search query')
        parser.add_argument('limit', type=int, default=10)
        args = parser.parse_args()
        
        try:
            kb_manager = KnowledgeBaseManager()
            results = kb_manager.search(args['query'], limit=args['limit'])
            
            formatted_results = []
            for record in results:
                formatted_results.append({
                    'id': record.get('id', ''),
                    'title': record.get('title', ''),
                    'content': str(record.get('content', ''))[:500] + '...' if len(str(record.get('content', ''))) > 500 else str(record.get('content', '')),
                    'type': record.get('type', ''),
                    'created_at': record.get('created_at', ''),
                    'score': record.get('score', 0.0)
                })
            
            return {
                'status': 'success',
                'results': formatted_results
            }, 200
            
        except Exception as e:
            return self._error_response('KB_ERROR', str(e)), 500
    
    def _error_response(self, code, message):
        return {
            'status': 'error',
            'code': code,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

class KnowledgeBaseResource(Resource):
    @jwt_required()
    def get(self, kb_id):
        """
        Get knowledge base record by ID
        """
        try:
            kb_manager = KnowledgeBaseManager()
            record = kb_manager.get_record(kb_id)
            
            if not record:
                return self._error_response('NOT_FOUND', 'Record not found'), 404
            
            return {
                'status': 'success',
                'record': {
                    'id': record.get('id', kb_id),
                    'title': record.get('title', ''),
                    'content': record.get('content', {}),
                    'type': record.get('type', ''),
                    'created_at': record.get('created_at', ''),
                    'project_id': record.get('project_id', '')
                }
            }, 200
            
        except Exception as e:
            return self._error_response('KB_ERROR', str(e)), 500
    
    @jwt_required()
    def delete(self, kb_id):
        """
        Delete knowledge base record by ID
        """
        try:
            kb_manager = KnowledgeBaseManager()
            success = kb_manager.delete_record(kb_id)
            
            if not success:
                return self._error_response('NOT_FOUND', 'Record not found'), 404
            
            return {
                'status': 'success',
                'message': 'Record deleted successfully'
            }, 200
            
        except Exception as e:
            return self._error_response('KB_ERROR', str(e)), 500
    
    def _error_response(self, code, message):
        return {
            'status': 'error',
            'code': code,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
