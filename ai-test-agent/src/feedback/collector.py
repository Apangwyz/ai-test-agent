import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .models import Feedback, FeedbackType, FeedbackCategory, FeedbackPriority
from .manager import feedback_manager

class FeedbackCollector:
    """反馈收集器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def collect_feedback(self, feedback_data: Dict[str, Any]) -> Optional[str]:
        """收集用户反馈"""
        try:
            feedback = self._create_feedback(feedback_data)
            feedback_id = feedback_manager.add_feedback(feedback)
            
            self.logger.info(f"Collected feedback: {feedback_id}")
            return feedback_id
            
        except Exception as e:
            self.logger.error(f"Error collecting feedback: {e}")
            return None
    
    def _create_feedback(self, data: Dict[str, Any]) -> Feedback:
        """创建反馈对象"""
        return Feedback(
            user_id=data.get('user_id', 'anonymous'),
            feedback_type=FeedbackType(data.get('feedback_type', 'neutral')),
            category=FeedbackCategory(data.get('category', 'other')),
            priority=self._determine_priority(data),
            title=data.get('title', ''),
            description=data.get('description', ''),
            rating=data.get('rating', 3),
            tags=data.get('tags', []),
            related_entity_id=data.get('related_entity_id'),
            related_entity_type=data.get('related_entity_type'),
            metadata=data.get('metadata', {})
        )
    
    def _determine_priority(self, data: Dict[str, Any]) -> FeedbackPriority:
        """确定反馈优先级"""
        feedback_type = data.get('feedback_type', 'neutral')
        rating = data.get('rating', 3)
        
        if feedback_type == 'bug_report':
            return FeedbackPriority.HIGH
        elif feedback_type == 'negative' and rating <= 2:
            return FeedbackPriority.HIGH
        elif feedback_type == 'feature_request':
            return FeedbackPriority.MEDIUM
        elif rating <= 2:
            return FeedbackPriority.MEDIUM
        else:
            return FeedbackPriority.LOW
    
    def collect_batch_feedbacks(self, feedbacks_data: List[Dict[str, Any]]) -> List[str]:
        """批量收集反馈"""
        feedback_ids = []
        
        for feedback_data in feedbacks_data:
            feedback_id = self.collect_feedback(feedback_data)
            if feedback_id:
                feedback_ids.append(feedback_id)
        
        self.logger.info(f"Collected {len(feedback_ids)} feedbacks in batch")
        return feedback_ids
    
    def collect_rating_feedback(self, user_id: str, entity_id: str, entity_type: str, 
                               rating: int, comment: str = "") -> Optional[str]:
        """收集评分反馈"""
        feedback_data = {
            'user_id': user_id,
            'feedback_type': 'positive' if rating >= 4 else 'negative' if rating <= 2 else 'neutral',
            'category': 'user_experience',
            'title': f"Rating for {entity_type}",
            'description': comment or f"User rated {entity_type} with {rating} stars",
            'rating': rating,
            'tags': ['rating', entity_type],
            'related_entity_id': entity_id,
            'related_entity_type': entity_type
        }
        
        return self.collect_feedback(feedback_data)
    
    def collect_bug_report(self, user_id: str, title: str, description: str, 
                          severity: str = "medium") -> Optional[str]:
        """收集错误报告"""
        priority_map = {
            'low': FeedbackPriority.LOW,
            'medium': FeedbackPriority.MEDIUM,
            'high': FeedbackPriority.HIGH,
            'urgent': FeedbackPriority.URGENT
        }
        
        feedback_data = {
            'user_id': user_id,
            'feedback_type': 'bug_report',
            'category': 'system_performance',
            'priority': priority_map.get(severity, FeedbackPriority.MEDIUM),
            'title': title,
            'description': description,
            'tags': ['bug', 'error_report'],
            'metadata': {'severity': severity}
        }
        
        return self.collect_feedback(feedback_data)
    
    def collect_feature_request(self, user_id: str, title: str, description: str) -> Optional[str]:
        """收集功能请求"""
        feedback_data = {
            'user_id': user_id,
            'feedback_type': 'feature_request',
            'category': 'user_experience',
            'title': title,
            'description': description,
            'tags': ['feature', 'request'],
            'priority': FeedbackPriority.MEDIUM
        }
        
        return self.collect_feedback(feedback_data)
    
    def collect_suggestion(self, user_id: str, category: str, suggestion: str) -> Optional[str]:
        """收集建议"""
        feedback_data = {
            'user_id': user_id,
            'feedback_type': 'suggestion',
            'category': FeedbackCategory(category),
            'title': f"Suggestion for {category}",
            'description': suggestion,
            'tags': ['suggestion', category]
        }
        
        return self.collect_feedback(feedback_data)
    
    def get_feedback_collection_stats(self) -> Dict[str, Any]:
        """获取反馈收集统计信息"""
        stats = feedback_manager.get_feedback_statistics()
        
        stats.update({
            'collector_info': {
                'supported_feedback_types': ['positive', 'negative', 'neutral', 'suggestion', 'bug_report', 'feature_request'],
                'supported_categories': ['requirement_analysis', 'technical_solution', 'coding_task', 'test_case', 'system_performance', 'user_experience', 'other'],
                'rating_scale': '1-5',
                'last_collection_time': datetime.now().isoformat()
            }
        })
        
        return stats

# 创建全局反馈收集器实例
feedback_collector = FeedbackCollector()