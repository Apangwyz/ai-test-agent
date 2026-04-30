from flask_restful import Resource
from datetime import datetime
import os

class HealthResource(Resource):
    def get(self):
        """
        Health check endpoint
        """
        try:
            # Check AI service
            ai_service_status = 'online'
            try:
                from src.common.ai_service import AIService
                ai = AIService()
                ai_service_status = 'online'
            except Exception as e:
                ai_service_status = 'offline'
            
            # Check database
            db_status = 'online'
            try:
                from src.auth.database import db
                db_status = 'online'
            except Exception as e:
                db_status = 'offline'
            
            # Check knowledge base
            kb_status = 'online'
            try:
                from src.knowledge_base.manager import KnowledgeBaseManager
                kb = KnowledgeBaseManager()
                kb_status = 'online'
            except Exception as e:
                kb_status = 'offline'
            
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'services': {
                    'ai_service': ai_service_status,
                    'database': db_status,
                    'knowledge_base': kb_status
                }
            }, 200
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'error': str(e)
            }, 500
