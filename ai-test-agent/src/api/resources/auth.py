from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from src.auth.auth_service import AuthService
from datetime import datetime
import os

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
            return self._error_response('AUTH_ERROR', str(e)), 500

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
            
            # Create access and refresh tokens
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            expires_in = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
            
            return {
                'status': 'success',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': expires_in,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, 200
            
        except Exception as e:
            return self._error_response('AUTH_ERROR', str(e)), 401

class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """
        Refresh access token using refresh token
        """
        try:
            user_id = get_jwt_identity()
            access_token = create_access_token(identity=user_id)
            expires_in = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
            
            return {
                'status': 'success',
                'access_token': access_token,
                'expires_in': expires_in
            }, 200
            
        except Exception as e:
            return self._error_response('AUTH_ERROR', str(e)), 401
    
    def _error_response(self, code, message):
        return {
            'status': 'error',
            'code': code,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
