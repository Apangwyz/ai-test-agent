from flask_restful import Resource, reqparse
from src.tech_doc_generator.tech_doc_generator import TechDocGenerator

class TechDocGeneratorResource(Resource):
    def post(self):
        """
        Generate technical documentation based on structured requirements
        """
        parser = reqparse.RequestParser()
        parser.add_argument('structured_data', type=dict, required=True, help='Structured requirements data')
        parser.add_argument('clarification_doc', type=dict, required=False, help='Clarification document')
        args = parser.parse_args()
        
        try:
            generator = TechDocGenerator()
            tech_doc = generator.generate_tech_doc(args['structured_data'], args.get('clarification_doc'))
            
            return {
                'status': 'success',
                'tech_doc': tech_doc
            }, 200
            
        except Exception as e:
            return {'error': f'Error generating technical document: {str(e)}'}, 500