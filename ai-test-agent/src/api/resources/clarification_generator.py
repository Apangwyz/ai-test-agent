from flask_restful import Resource, reqparse
from src.clarification_generator.clarification_generator import ClarificationGenerator

class ClarificationGeneratorResource(Resource):
    def post(self):
        """
        Generate clarification document based on structured requirements
        """
        parser = reqparse.RequestParser()
        parser.add_argument('structured_data', type=dict, required=True, help='Structured requirements data')
        args = parser.parse_args()
        
        try:
            generator = ClarificationGenerator()
            clarification_doc = generator.generate_clarification(args['structured_data'])
            
            return {
                'status': 'success',
                'clarification_doc': clarification_doc
            }, 200
            
        except Exception as e:
            return {'error': f'Error generating clarification: {str(e)}'}, 500