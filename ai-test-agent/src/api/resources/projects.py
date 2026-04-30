from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.knowledge_base.manager import KnowledgeBaseManager
from datetime import datetime
import os
import json

class ProjectListResource(Resource):
    @jwt_required()
    def get(self):
        """
        Get list of projects with pagination
        """
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('limit', type=int, default=20)
        parser.add_argument('keyword', type=str, default='')
        args = parser.parse_args()
        
        try:
            kb_manager = KnowledgeBaseManager()
            records = kb_manager.search(args.get('keyword'), limit=100)
            
            # Filter by type 'document' which represents processed projects
            projects = []
            for record in records:
                if record.get('type') == 'document':
                    projects.append({
                        'project_id': record.get('project_id', record.get('id', '')),
                        'project_name': record.get('title', ''),
                        'processed_at': record.get('created_at', ''),
                        'status': 'completed'
                    })
            
            # Apply pagination
            page = max(1, args['page'])
            limit = max(1, min(args['limit'], 100))
            total = len(projects)
            pages = (total + limit - 1) // limit
            start = (page - 1) * limit
            end = start + limit
            paginated_projects = projects[start:end]
            
            return {
                'status': 'success',
                'data': paginated_projects,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': pages
                }
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

class ProjectResource(Resource):
    @jwt_required()
    def get(self, project_id):
        """
        Get project details by ID
        """
        try:
            kb_manager = KnowledgeBaseManager()
            record = kb_manager.get_record(project_id)
            
            if not record:
                return self._error_response('NOT_FOUND', 'Project not found'), 404
            
            return {
                'status': 'success',
                'project': {
                    'project_id': record.get('project_id', project_id),
                    'project_name': record.get('title', ''),
                    'processed_at': record.get('created_at', ''),
                    'results': record.get('content', {})
                }
            }, 200
            
        except Exception as e:
            return self._error_response('PROCESSING_ERROR', str(e)), 500
    
    @jwt_required()
    def delete(self, project_id):
        """
        Delete project by ID
        """
        try:
            kb_manager = KnowledgeBaseManager()
            success = kb_manager.delete_record(project_id)
            
            if not success:
                return self._error_response('NOT_FOUND', 'Project not found'), 404
            
            # Also delete exported files
            output_dir = os.path.join('docs', 'requirements', 'api_results', project_id)
            if os.path.exists(output_dir):
                import shutil
                shutil.rmtree(output_dir)
            
            return {
                'status': 'success',
                'message': 'Project deleted successfully'
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
