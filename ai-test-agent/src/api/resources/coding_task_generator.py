from flask_restful import Resource, reqparse
from src.coding_task_generator.coding_task_generator import CodingTaskGenerator

class CodingTaskGeneratorResource(Resource):
    def post(self):
        """
        Generate coding tasks based on technical documentation
        """
        parser = reqparse.RequestParser()
        parser.add_argument('tech_doc', type=dict, required=True, help='Technical documentation')
        args = parser.parse_args()
        
        try:
            generator = CodingTaskGenerator()
            tasks = generator.generate_tasks(args['tech_doc'])
            
            return {
                'status': 'success',
                'tasks': tasks
            }, 200
            
        except Exception as e:
            return {'error': f'Error generating coding tasks: {str(e)}'}, 500