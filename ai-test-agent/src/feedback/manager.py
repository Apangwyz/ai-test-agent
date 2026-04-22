import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
from .models import Feedback, FeedbackAnalysis, FeedbackType, FeedbackCategory, FeedbackPriority, FeedbackStatus

class FeedbackManager:
    """反馈管理器"""
    
    def __init__(self, base_dir: str = "data/feedback"):
        self.logger = logging.getLogger(__name__)
        self.base_dir = Path(base_dir)
        self.feedback_dir = self.base_dir / "feedbacks"
        self.analysis_dir = self.base_dir / "analysis"
        
        self._ensure_directories()
        self._load_feedbacks()
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_feedbacks(self):
        """加载反馈数据"""
        self.feedback_index = {}
        
        for feedback_file in self.feedback_dir.glob("*.json"):
            try:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    feedback_data = json.load(f)
                    feedback = Feedback.from_dict(feedback_data)
                    self.feedback_index[feedback.id] = feedback
            except Exception as e:
                self.logger.error(f"Error loading feedback from {feedback_file}: {e}")
        
        self.logger.info(f"Loaded {len(self.feedback_index)} feedbacks")
    
    def add_feedback(self, feedback: Feedback) -> str:
        """添加反馈"""
        feedback_id = feedback.id
        self.feedback_index[feedback_id] = feedback
        
        feedback_file = self.feedback_dir / f"{feedback_id}.json"
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback.to_dict(), f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Added feedback: {feedback_id}")
        return feedback_id
    
    def get_feedback(self, feedback_id: str) -> Optional[Feedback]:
        """获取反馈"""
        return self.feedback_index.get(feedback_id)
    
    def update_feedback(self, feedback_id: str, updates: Dict[str, Any]) -> bool:
        """更新反馈"""
        feedback = self.feedback_index.get(feedback_id)
        if not feedback:
            return False
        
        for key, value in updates.items():
            if hasattr(feedback, key):
                setattr(feedback, key, value)
        
        feedback.updated_at = datetime.now()
        
        feedback_file = self.feedback_dir / f"{feedback_id}.json"
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback.to_dict(), f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Updated feedback: {feedback_id}")
        return True
    
    def delete_feedback(self, feedback_id: str) -> bool:
        """删除反馈"""
        if feedback_id not in self.feedback_index:
            return False
        
        del self.feedback_index[feedback_id]
        
        feedback_file = self.feedback_dir / f"{feedback_id}.json"
        if feedback_file.exists():
            feedback_file.unlink()
        
        self.logger.info(f"Deleted feedback: {feedback_id}")
        return True
    
    def get_feedbacks_by_user(self, user_id: str) -> List[Feedback]:
        """获取用户的所有反馈"""
        return [feedback for feedback in self.feedback_index.values() if feedback.user_id == user_id]
    
    def get_feedbacks_by_type(self, feedback_type: FeedbackType) -> List[Feedback]:
        """按类型获取反馈"""
        return [feedback for feedback in self.feedback_index.values() if feedback.feedback_type == feedback_type]
    
    def get_feedbacks_by_category(self, category: FeedbackCategory) -> List[Feedback]:
        """按分类获取反馈"""
        return [feedback for feedback in self.feedback_index.values() if feedback.category == category]
    
    def get_feedbacks_by_status(self, status: FeedbackStatus) -> List[Feedback]:
        """按状态获取反馈"""
        return [feedback for feedback in self.feedback_index.values() if feedback.status == status]
    
    def get_feedbacks_by_priority(self, priority: FeedbackPriority) -> List[Feedback]:
        """按优先级获取反馈"""
        return [feedback for feedback in self.feedback_index.values() if feedback.priority == priority]
    
    def get_pending_feedbacks(self) -> List[Feedback]:
        """获取待处理的反馈"""
        return self.get_feedbacks_by_status(FeedbackStatus.PENDING)
    
    def get_high_priority_feedbacks(self) -> List[Feedback]:
        """获取高优先级反馈"""
        return [feedback for feedback in self.feedback_index.values() 
                if feedback.priority in [FeedbackPriority.HIGH, FeedbackPriority.URGENT]]
    
    def respond_to_feedback(self, feedback_id: str, response: str, responder_id: str) -> bool:
        """回复反馈"""
        updates = {
            'response': response,
            'responded_by': responder_id,
            'responded_at': datetime.now(),
            'status': FeedbackStatus.IN_PROGRESS
        }
        return self.update_feedback(feedback_id, updates)
    
    def resolve_feedback(self, feedback_id: str, resolver_id: str) -> bool:
        """解决反馈"""
        updates = {
            'status': FeedbackStatus.RESOLVED,
            'resolved_at': datetime.now()
        }
        return self.update_feedback(feedback_id, updates)
    
    def close_feedback(self, feedback_id: str) -> bool:
        """关闭反馈"""
        updates = {
            'status': FeedbackStatus.CLOSED
        }
        return self.update_feedback(feedback_id, updates)
    
    def analyze_feedbacks(self, days: int = 30) -> FeedbackAnalysis:
        """分析反馈数据"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_feedbacks = [
                feedback for feedback in self.feedback_index.values()
                if feedback.created_at >= cutoff_date
            ]
            
            if not recent_feedbacks:
                return FeedbackAnalysis()
            
            analysis = FeedbackAnalysis()
            analysis.total_feedback = len(recent_feedbacks)
            
            # 统计反馈类型
            type_counts = Counter(feedback.feedback_type for feedback in recent_feedbacks)
            analysis.positive_count = type_counts.get(FeedbackType.POSITIVE, 0)
            analysis.negative_count = type_counts.get(FeedbackType.NEGATIVE, 0)
            analysis.neutral_count = type_counts.get(FeedbackType.NEUTRAL, 0)
            
            # 计算平均评分
            ratings = [feedback.rating for feedback in recent_feedbacks if feedback.rating > 0]
            analysis.average_rating = sum(ratings) / len(ratings) if ratings else 0.0
            
            # 分类分布
            category_counts = Counter(feedback.category for feedback in recent_feedbacks)
            analysis.category_distribution = {cat.value: count for cat, count in category_counts.items()}
            
            # 优先级分布
            priority_counts = Counter(feedback.priority for feedback in recent_feedbacks)
            analysis.priority_distribution = {pri.value: count for pri, count in priority_counts.items()}
            
            # 状态分布
            status_counts = Counter(feedback.status for feedback in recent_feedbacks)
            analysis.status_distribution = {stat.value: count for stat, count in status_counts.items()}
            
            # 提取常见问题
            analysis.common_issues = self._extract_common_issues(recent_feedbacks)
            
            # 生成改进建议
            analysis.improvement_suggestions = self._generate_improvement_suggestions(recent_feedbacks)
            
            # 趋势分析
            analysis.trend_analysis = self._analyze_trends(recent_feedbacks)
            
            self.logger.info(f"Analyzed {len(recent_feedbacks)} feedbacks")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing feedbacks: {e}")
            return FeedbackAnalysis()
    
    def _extract_common_issues(self, feedbacks: List[Feedback]) -> List[str]:
        """提取常见问题"""
        issue_keywords = []
        
        for feedback in feedbacks:
            if feedback.feedback_type == FeedbackType.NEGATIVE or feedback.feedback_type == FeedbackType.BUG_REPORT:
                words = feedback.description.lower().split()
                issue_keywords.extend(words)
        
        keyword_counts = Counter(issue_keywords)
        common_keywords = [word for word, count in keyword_counts.most_common(10) if len(word) > 3]
        
        return common_keywords
    
    def _generate_improvement_suggestions(self, feedbacks: List[Feedback]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        negative_feedbacks = [f for f in feedbacks if f.feedback_type == FeedbackType.NEGATIVE]
        if len(negative_feedbacks) > len(feedbacks) * 0.3:
            suggestions.append("负面反馈比例较高，建议重点关注用户体验改进")
        
        low_rating_feedbacks = [f for f in feedbacks if f.rating < 3]
        if len(low_rating_feedbacks) > len(feedbacks) * 0.2:
            suggestions.append("低评分反馈较多，建议分析具体原因并改进")
        
        pending_feedbacks = [f for f in feedbacks if f.status == FeedbackStatus.PENDING]
        if len(pending_feedbacks) > 10:
            suggestions.append("待处理反馈数量较多，建议增加处理人员或优化处理流程")
        
        return suggestions
    
    def _analyze_trends(self, feedbacks: List[Feedback]) -> Dict[str, Any]:
        """分析趋势"""
        trends = {}
        
        daily_counts = defaultdict(int)
        for feedback in feedbacks:
            date_key = feedback.created_at.strftime("%Y-%m-%d")
            daily_counts[date_key] += 1
        
        trends['daily_feedback_counts'] = dict(daily_counts)
        
        if daily_counts:
            dates = sorted(daily_counts.keys())
            counts = [daily_counts[date] for date in dates]
            
            if len(counts) > 1:
                trend_direction = "increasing" if counts[-1] > counts[0] else "decreasing"
                trends['trend_direction'] = trend_direction
                trends['average_daily_feedback'] = sum(counts) / len(counts)
        
        return trends
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """获取反馈统计信息"""
        total_feedbacks = len(self.feedback_index)
        
        type_counts = Counter(feedback.feedback_type for feedback in self.feedback_index.values())
        category_counts = Counter(feedback.category for feedback in self.feedback_index.values())
        status_counts = Counter(feedback.status for feedback in self.feedback_index.values())
        priority_counts = Counter(feedback.priority for feedback in self.feedback_index.values())
        
        return {
            'total_feedbacks': total_feedbacks,
            'type_distribution': {t.value: count for t, count in type_counts.items()},
            'category_distribution': {c.value: count for c, count in category_counts.items()},
            'status_distribution': {s.value: count for s, count in status_counts.items()},
            'priority_distribution': {p.value: count for p, count in priority_counts.items()},
            'last_updated': datetime.now().isoformat()
        }
    
    def export_feedbacks(self, output_file: str) -> bool:
        """导出所有反馈"""
        try:
            feedbacks_data = [feedback.to_dict() for feedback in self.feedback_index.values()]
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(feedbacks_data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Exported {len(feedbacks_data)} feedbacks to {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting feedbacks: {e}")
            return False

# 创建全局反馈管理器实例
feedback_manager = FeedbackManager()