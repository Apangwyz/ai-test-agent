from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from src.auth.database import Base, db
import logging

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AuditLog {self.action} by user {self.user_id}>"

class AuditService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_action(self, user_id, action, resource, details=None, ip_address=None, user_agent=None):
        """
        Log user action
        """
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource=resource,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
            return audit_log
            
        except Exception as e:
            self.logger.error(f"Error logging action: {e}")
            db.session.rollback()
            # Don't raise exception to avoid blocking main functionality
            return None
    
    def get_logs(self, user_id=None, action=None, start_date=None, end_date=None, limit=100):
        """
        Get audit logs with filters
        """
        try:
            query = db.query(AuditLog)
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            if action:
                query = query.filter(AuditLog.action == action)
            if start_date:
                query = query.filter(AuditLog.created_at >= start_date)
            if end_date:
                query = query.filter(AuditLog.created_at <= end_date)
            
            return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
            
        except Exception as e:
            self.logger.error(f"Error getting audit logs: {e}")
            return []

# Initialize audit service
audit_service = AuditService()