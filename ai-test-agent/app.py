from flask import Flask, send_from_directory
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))

# Set static folder
app.static_folder = 'src/frontend'
app.static_url_path = '/static'

# Initialize extensions
api = Api(app)
jwt = JWTManager(app)
CORS(app)

# Root route to serve frontend
@app.route('/')
def serve_root():
    return send_from_directory('src/frontend', 'index.html')

# Import and register routes
from src.api.routes import register_routes
register_routes(api)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5002')), debug=True)