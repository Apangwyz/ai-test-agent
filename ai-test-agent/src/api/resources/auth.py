from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from src.auth.auth_service import AuthService

class RegisterResource(Resource):
    def post(self):
        """
        Register a new user
        """
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Username')
        parser.add_argument('email', type=str, required=True, help='Email')
        parser.add_argument('password', type=str, required=True, help='Password')
        args = parser.parse_args()
        
        try:
            auth_service = AuthService()
            user = auth_service.register(args['username'], args['email'], args['password'])
            
            return {
                'status': 'success',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, 201
            
        except Exception as e:
            return {'error': f'Error registering user: {str(e)}'}, 500

class LoginResource(Resource):
    def post(self):
        """
        Login and get access token
        """
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='Email')
        parser.add_argument('password', type=str, required=True, help='Password')
        args = parser.parse_args()
        
        try:
            auth_service = AuthService()
            user = auth_service.login(args['email'], args['password'])
            
            # Create access token
            access_token = create_access_token(identity=user.id)
            
            return {
                'status': 'success',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, 200
            
        except Exception as e:
            return {'error': f'Error logging in: {str(e)}'}, 401