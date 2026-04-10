from flask_restful import Resource, reqparse
from src.test_case_generator.test_case_generator import TestCaseGenerator

class TestCaseGeneratorResource(Resource):
    def post(self):
        """
        Generate test cases based on requirements and technical documentation
        """
        parser = reqparse.RequestParser()
        parser.add_argument('structured_data', type=dict, required=True, help='Structured requirements data')
        parser.add_argument('tech_doc', type=dict, required=True, help='Technical documentation')
        args = parser.parse_args()
        
        try:
            generator = TestCaseGenerator()
            test_cases = generator.generate_test_cases(args['structured_data'], args['tech_doc'])
            
            return {
                'status': 'success',
                'test_cases': test_cases
            }, 200
            
        except Exception as e:
            return {'error': f'Error generating test cases: {str(e)}'}, 500