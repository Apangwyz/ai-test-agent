import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from .models import Feedback, FeedbackAnalysis, FeedbackType, FeedbackCategory, FeedbackPriority, FeedbackStatus
from .manager import feedback_manager

class FeedbackAnalyzer:
    """反馈分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_feedbacks(self, days: int = 30) -> FeedbackAnalysis:
        """分析反馈数据"""
        return feedback_manager.analyze_feedbacks(days)
    
    def analyze_by_category(self, category: FeedbackCategory, days: int = 30) -> Dict[str, Any]:
        """按分类分析反馈"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            category_feedbacks = [
                feedback for feedback in feedback_manager.get_feedbacks_by_category(category)
                if feedback.created_at >= cutoff_date
            ]
            
            if not category_feedbacks:
                return {'category': category.value, 'total': 0}
            
            analysis = {
                'category': category.value,
                'total': len(category_feedbacks),
                'average_rating': sum(f.rating for f in category_feedbacks if f.rating > 0) / len([f for f in category_feedbacks if f.rating > 0]),
                'type_distribution': self._get_type_distribution(category_feedbacks),
                'priority_distribution': self._get_priority_distribution(category_feedbacks),
                'status_distribution': self._get_status_distribution(category_feedbacks),
                'common_tags': self._get_common_tags(category_feedbacks),
                'trend': self._analyze_category_trend(category, days)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing by category: {e}")
            return {'category': category.value, 'total': 0}
    
    def analyze_by_user(self, user_id: str) -> Dict[str, Any]:
        """按用户分析反馈"""
        try:
            user_feedbacks = feedback_manager.get_feedbacks_by_user(user_id)
            
            if not user_feedbacks:
                return {'user_id': user_id, 'total': 0}
            
            analysis = {
                'user_id': user_id,
                'total': len(user_feedbacks),
                'average_rating': sum(f.rating for f in user_feedbacks if f.rating > 0) / len([f for f in user_feedbacks if f.rating > 0]),
                'category_distribution': self._get_category_distribution(user_feedbacks),
                'type_distribution': self._get_type_distribution(user_feedbacks),
                'feedback_frequency': self._calculate_feedback_frequency(user_feedbacks),
                'most_active_period': self._get_most_active_period(user_feedbacks),
                'satisfaction_trend': self._analyze_satisfaction_trend(user_feedbacks)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing by user: {e}")
            return {'user_id': user_id, 'total': 0}
    
    def analyze_sentiment(self, feedbacks: List[Feedback]) -> Dict[str, Any]:
        """分析情感倾向"""
        try:
            if not feedbacks:
                return {'total': 0}
            
            sentiment_counts = Counter(feedback.feedback_type for feedback in feedbacks)
            
            positive_ratio = sentiment_counts.get(FeedbackType.POSITIVE, 0) / len(feedbacks)
            negative_ratio = sentiment_counts.get(FeedbackType.NEGATIVE, 0) / len(feedbacks)
            neutral_ratio = sentiment_counts.get(FeedbackType.NEUTRAL, 0) / len(feedbacks)
            
            overall_sentiment = "positive" if positive_ratio > 0.5 else "negative" if negative_ratio > 0.3 else "neutral"
            
            return {
                'total': len(feedbacks),
                'positive_count': sentiment_counts.get(FeedbackType.POSITIVE, 0),
                'negative_count': sentiment_counts.get(FeedbackType.NEGATIVE, 0),
                'neutral_count': sentiment_counts.get(FeedbackType.NEUTRAL, 0),
                'positive_ratio': positive_ratio,
                'negative_ratio': negative_ratio,
                'neutral_ratio': neutral_ratio,
                'overall_sentiment': overall_sentiment
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
            return {'total': 0}
    
    def identify_issues(self, days: int = 30) -> List[Dict[str, Any]]:
        """识别关键问题"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_feedbacks = [
                feedback for feedback in feedback_manager.feedback_index.values()
                if feedback.created_at >= cutoff_date
            ]
            
            issues = []
            
            # 识别高频问题
            negative_feedbacks = [f for f in recent_feedbacks if f.feedback_type == FeedbackType.NEGATIVE]
            if negative_feedbacks:
                common_issues = self._extract_common_issues_from_text(negative_feedbacks)
                for issue, count in common_issues.items():
                    if count >= 2:
                        issues.append({
                            'type': 'common_issue',
                            'description': issue,
                            'frequency': count,
                            'severity': 'high' if count >= 5 else 'medium'
                        })
            
            # 识别高优先级未解决问题
            high_priority_pending = [
                f for f in recent_feedbacks 
                if f.priority in [FeedbackPriority.HIGH, FeedbackPriority.URGENT] 
                and f.status == FeedbackStatus.PENDING
            ]
            if high_priority_pending:
                issues.append({
                    'type': 'high_priority_pending',
                    'count': len(high_priority_pending),
                    'severity': 'urgent'
                })
            
            # 识别低评分问题
            low_rating_feedbacks = [f for f in recent_feedbacks if f.rating <= 2]
            if len(low_rating_feedbacks) > len(recent_feedbacks) * 0.2:
                issues.append({
                    'type': 'low_rating',
                    'count': len(low_rating_feedbacks),
                    'ratio': len(low_rating_feedbacks) / len(recent_feedbacks),
                    'severity': 'medium'
                })
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Error identifying issues: {e}")
            return []
    
    def generate_improvement_recommendations(self, days: int = 30) -> List[str]:
        """生成改进建议"""
        try:
            analysis = self.analyze_feedbacks(days)
            issues = self.identify_issues(days)
            recommendations = []
            
            # 基于分析结果生成建议
            if analysis.average_rating < 3.5:
                recommendations.append("整体评分较低，建议全面审查用户体验并制定改进计划")
            
            if analysis.negative_count > analysis.positive_count:
                recommendations.append("负面反馈多于正面反馈，建议重点关注用户痛点和问题解决")
            
            if analysis.status_distribution.get('pending', 0) > 10:
                recommendations.append("待处理反馈数量较多，建议优化反馈处理流程或增加处理资源")
            
            # 基于识别的问题生成建议
            for issue in issues:
                if issue['type'] == 'common_issue':
                    recommendations.append(f"常见问题：{issue['description']}，建议优先解决")
                elif issue['type'] == 'high_priority_pending':
                    recommendations.append(f"存在{issue['count']}个高优先级待处理反馈，建议立即处理")
                elif issue['type'] == 'low_rating':
                    recommendations.append(f"低评分反馈占比{issue['ratio']:.1%}，建议分析原因并改进")
            
            # 基于分类分布生成建议
            if analysis.category_distribution:
                top_category = max(analysis.category_distribution.items(), key=lambda x: x[1])
                recommendations.append(f"最多反馈分类为{top_category[0]}，建议重点关注该领域的改进")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _get_type_distribution(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        """获取类型分布"""
        type_counts = Counter(feedback.feedback_type for feedback in feedbacks)
        return {t.value: count for t, count in type_counts.items()}
    
    def _get_priority_distribution(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        """获取优先级分布"""
        priority_counts = Counter(feedback.priority for feedback in feedbacks)
        return {p.value: count for p, count in priority_counts.items()}
    
    def _get_status_distribution(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        """获取状态分布"""
        status_counts = Counter(feedback.status for feedback in feedbacks)
        return {s.value: count for s, count in status_counts.items()}
    
    def _get_category_distribution(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        """获取分类分布"""
        category_counts = Counter(feedback.category for feedback in feedbacks)
        return {c.value: count for c, count in category_counts.items()}
    
    def _get_common_tags(self, feedbacks: List[Feedback]) -> List[str]:
        """获取常见标签"""
        all_tags = []
        for feedback in feedbacks:
            all_tags.extend(feedback.tags)
        
        tag_counts = Counter(all_tags)
        return [tag for tag, count in tag_counts.most_common(10)]
    
    def _analyze_category_trend(self, category: FeedbackCategory, days: int) -> Dict[str, Any]:
        """分析分类趋势"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            category_feedbacks = [
                feedback for feedback in feedback_manager.get_feedbacks_by_category(category)
                if feedback.created_at >= cutoff_date
            ]
            
            daily_counts = defaultdict(int)
            for feedback in category_feedbacks:
                date_key = feedback.created_at.strftime("%Y-%m-%d")
                daily_counts[date_key] += 1
            
            if not daily_counts:
                return {'trend': 'no_data'}
            
            dates = sorted(daily_counts.keys())
            counts = [daily_counts[date] for date in dates]
            
            if len(counts) > 1:
                trend = "increasing" if counts[-1] > counts[0] else "decreasing"
                return {
                    'trend': trend,
                    'average_daily': sum(counts) / len(counts),
                    'peak_day': max(daily_counts.items(), key=lambda x: x[1])
                }
            else:
                return {'trend': 'insufficient_data'}
                
        except Exception as e:
            self.logger.error(f"Error analyzing category trend: {e}")
            return {'trend': 'error'}
    
    def _calculate_feedback_frequency(self, feedbacks: List[Feedback]) -> Dict[str, Any]:
        """计算反馈频率"""
        if not feedbacks:
            return {}
        
        sorted_feedbacks = sorted(feedbacks, key=lambda f: f.created_at)
        if len(sorted_feedbacks) < 2:
            return {'frequency': 'low'}
        
        time_span = (sorted_feedbacks[-1].created_at - sorted_feedbacks[0].created_at).days
        if time_span == 0:
            time_span = 1
        
        frequency = len(feedbacks) / time_span
        
        if frequency > 1:
            return {'frequency': 'high', 'feedbacks_per_day': frequency}
        elif frequency > 0.5:
            return {'frequency': 'medium', 'feedbacks_per_day': frequency}
        else:
            return {'frequency': 'low', 'feedbacks_per_day': frequency}
    
    def _get_most_active_period(self, feedbacks: List[Feedback]) -> Dict[str, Any]:
        """获取最活跃时间段"""
        if not feedbacks:
            return {}
        
        hour_counts = Counter(feedback.created_at.hour for feedback in feedbacks)
        most_active_hour = hour_counts.most_common(1)[0][0]
        
        if 6 <= most_active_hour < 12:
            period = "morning"
        elif 12 <= most_active_hour < 18:
            period = "afternoon"
        elif 18 <= most_active_hour < 24:
            period = "evening"
        else:
            period = "night"
        
        return {
            'most_active_hour': most_active_hour,
            'period': period,
            'count': hour_counts[most_active_hour]
        }
    
    def _analyze_satisfaction_trend(self, feedbacks: List[Feedback]) -> Dict[str, Any]:
        """分析满意度趋势"""
        if not feedbacks:
            return {}
        
        sorted_feedbacks = sorted(feedbacks, key=lambda f: f.created_at)
        ratings = [f.rating for f in sorted_feedbacks if f.rating > 0]
        
        if len(ratings) < 2:
            return {'trend': 'insufficient_data'}
        
        first_half = ratings[:len(ratings)//2]
        second_half = ratings[len(ratings)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg + 0.5:
            trend = "improving"
        elif second_avg < first_avg - 0.5:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            'trend': trend,
            'first_half_avg': first_avg,
            'second_half_avg': second_avg,
            'overall_avg': sum(ratings) / len(ratings)
        }
    
    def _extract_common_issues_from_text(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        """从文本中提取常见问题"""
        issue_keywords = []
        
        for feedback in feedbacks:
            words = feedback.description.lower().split()
            issue_keywords.extend(words)
        
        keyword_counts = Counter(issue_keywords)
        common_issues = {word: count for word, count in keyword_counts.items() if len(word) > 4 and count >= 2}
        
        return common_issues
    
    def get_analytics_dashboard_data(self, days: int = 30) -> Dict[str, Any]:
        """获取分析仪表板数据"""
        try:
            analysis = self.analyze_feedbacks(days)
            issues = self.identify_issues(days)
            recommendations = self.generate_improvement_recommendations(days)
            
            return {
                'overview': analysis.to_dict(),
                'issues': issues,
                'recommendations': recommendations,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {}

# 创建全局反馈分析器实例
feedback_analyzer = FeedbackAnalyzer()