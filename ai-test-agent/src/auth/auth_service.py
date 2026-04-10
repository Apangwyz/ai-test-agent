from src.auth.models import User
from src.auth.database import db
from werkzeug.security import generate_password_hash, check_password_hash
import logging

class AuthService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def register(self, username, email, password):
        """
        Register a new user
        """
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                raise ValueError('Email already registered')
            
            # Create new user
            hashed_password = generate_password_hash(password, method='sha256')
            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                role='user'  # Default role
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            return new_user
            
        except Exception as e:
            self.logger.error(f"Error registering user: {e}")
            db.session.rollback()
            raise
    
    def login(self, email, password):
        """
        Login user and return user object
        """
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                raise ValueError('Invalid email or password')
            
            if not check_password_hash(user.password_hash, password):
                raise ValueError('Invalid email or password')
            
            return user
            
        except Exception as e:
            self.logger.error(f"Error logging in: {e}")
            raise
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            return user
        except Exception as e:
            self.logger.error(f"Error getting user: {e}")
            raise
    
    def update_user_role(self, user_id, role):
        """
        Update user role
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            
            user.role = role
            db.session.commit()
            return user
        except Exception as e:
            self.logger.error(f"Error updating user role: {e}")
            db.session.rollback()
            raise