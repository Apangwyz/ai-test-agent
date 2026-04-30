from flask_restful import Api
from .resources.document_processor import DocumentProcessorResource, DocumentProcessFullResource
from .resources.clarification_generator import ClarificationGeneratorResource
from .resources.tech_doc_generator import TechDocGeneratorResource
from .resources.coding_task_generator import CodingTaskGeneratorResource
from .resources.test_case_generator import TestCaseGeneratorResource
from .resources.auth import LoginResource, RegisterResource, RefreshResource
from .resources.projects import ProjectListResource, ProjectResource
from .resources.knowledge_base import KnowledgeBaseSearchResource, KnowledgeBaseResource
from .resources.health import HealthResource

def register_routes(api):
    """
    Register all API routes
    """
    # Authentication routes
    api.add_resource(RegisterResource, '/api/auth/register')
    api.add_resource(LoginResource, '/api/auth/login')
    api.add_resource(RefreshResource, '/api/auth/refresh')
    
    # Document processing routes
    api.add_resource(DocumentProcessorResource, '/api/document/parse')
    api.add_resource(DocumentProcessFullResource, '/api/document/process-full')
    
    # Clarification generation routes
    api.add_resource(ClarificationGeneratorResource, '/api/generate/clarification')
    
    # Technical document generation routes
    api.add_resource(TechDocGeneratorResource, '/api/generate/tech-doc')
    
    # Coding task generation routes
    api.add_resource(CodingTaskGeneratorResource, '/api/generate/tasks')
    
    # Test case generation routes
    api.add_resource(TestCaseGeneratorResource, '/api/generate/test-cases')
    
    # Project management routes
    api.add_resource(ProjectListResource, '/api/projects')
    api.add_resource(ProjectResource, '/api/projects/<string:project_id>')
    
    # Knowledge base routes
    api.add_resource(KnowledgeBaseSearchResource, '/api/knowledge-base/search')
    api.add_resource(KnowledgeBaseResource, '/api/knowledge-base/<string:kb_id>')
    
    # Health check route
    api.add_resource(HealthResource, '/api/health')
