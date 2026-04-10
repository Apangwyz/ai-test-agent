from flask_restful import Api
from .resources.document_processor import DocumentProcessorResource
from .resources.clarification_generator import ClarificationGeneratorResource
from .resources.tech_doc_generator import TechDocGeneratorResource
from .resources.coding_task_generator import CodingTaskGeneratorResource
from .resources.test_case_generator import TestCaseGeneratorResource
from .resources.auth import LoginResource, RegisterResource

def register_routes(api):
    """
    Register all API routes
    """
    # Authentication routes
    api.add_resource(RegisterResource, '/api/auth/register')
    api.add_resource(LoginResource, '/api/auth/login')
    
    # Document processing routes
    api.add_resource(DocumentProcessorResource, '/api/documents/process')
    
    # Clarification generation routes
    api.add_resource(ClarificationGeneratorResource, '/api/clarification/generate')
    
    # Technical document generation routes
    api.add_resource(TechDocGeneratorResource, '/api/tech-doc/generate')
    
    # Coding task generation routes
    api.add_resource(CodingTaskGeneratorResource, '/api/tasks/generate')
    
    # Test case generation routes
    api.add_resource(TestCaseGeneratorResource, '/api/test-cases/generate')