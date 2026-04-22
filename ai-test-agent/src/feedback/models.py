from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid

class FeedbackType(Enum):
    """反馈类型枚举"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    SUGGESTION = "suggestion"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"

class FeedbackCategory(Enum):
    """反馈分类枚举"""
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    TECHNICAL_SOLUTION = "technical_solution"
    CODING_TASK = "coding_task"
    TEST_CASE = "test_case"
    SYSTEM_PERFORMANCE = "system_performance"
    USER_EXPERIENCE = "user_experience"
    OTHER = "other"

class FeedbackPriority(Enum):
    """反馈优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class FeedbackStatus(Enum):
    """反馈状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

@dataclass
class Feedback:
    """用户反馈数据模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    feedback_type: FeedbackType = FeedbackType.NEUTRAL
    category: FeedbackCategory = FeedbackCategory.OTHER
    priority: FeedbackPriority = FeedbackPriority.MEDIUM
    status: FeedbackStatus = FeedbackStatus.PENDING
    
    title: str = ""
    description: str = ""
    rating: int = 3
    tags: List[str] = field(default_factory=list)
    
    related_entity_id: Optional[str] = None
    related_entity_type: Optional[str] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
    response: Optional[str] = None
    responded_by: Optional[str] = None
    responded_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'feedback_type': self.feedback_type.value,
            'category': self.category.value,
            'priority': self.priority.value,
            'status': self.status.value,
            'title': self.title,
            'description': self.description,
            'rating': self.rating,
            'tags': self.tags,
            'related_entity_id': self.related_entity_id,
            'related_entity_type': self.related_entity_type,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'response': self.response,
            'responded_by': self.responded_by,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Feedback':
        """从字典创建反馈"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            feedback_type=FeedbackType(data.get('feedback_type', 'neutral')),
            category=FeedbackCategory(data.get('category', 'other')),
            priority=FeedbackPriority(data.get('priority', 'medium')),
            status=FeedbackStatus(data.get('status', 'pending')),
            title=data.get('title', ''),
            description=data.get('description', ''),
            rating=data.get('rating', 3),
            tags=data.get('tags', []),
            related_entity_id=data.get('related_entity_id'),
            related_entity_type=data.get('related_entity_type'),
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
            resolved_at=datetime.fromisoformat(data['resolved_at']) if data.get('resolved_at') else None,
            response=data.get('response'),
            responded_by=data.get('responded_by'),
            responded_at=datetime.fromisoformat(data['responded_at']) if data.get('responded_at') else None
        )

@dataclass
class FeedbackAnalysis:
    """反馈分析结果"""
    total_feedback: int = 0
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    average_rating: float = 0.0
    
    category_distribution: Dict[str, int] = field(default_factory=dict)
    priority_distribution: Dict[str, int] = field(default_factory=dict)
    status_distribution: Dict[str, int] = field(default_factory=dict)
    
    common_issues: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    trend_analysis: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'total_feedback': self.total_feedback,
            'positive_count': self.positive_count,
            'negative_count': self.negative_count,
            'neutral_count': self.neutral_count,
            'average_rating': self.average_rating,
            'category_distribution': self.category_distribution,
            'priority_distribution': self.priority_distribution,
            'status_distribution': self.status_distribution,
            'common_issues': self.common_issues,
            'improvement_suggestions': self.improvement_suggestions,
            'trend_analysis': self.trend_analysis
        }