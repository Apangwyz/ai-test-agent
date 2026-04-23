import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from src.feedback.models import Feedback, FeedbackAnalysis, FeedbackType, FeedbackCategory, FeedbackPriority, FeedbackStatus
from src.feedback.manager import FeedbackManager
from src.feedback.collector import FeedbackCollector
from src.feedback.analyzer import FeedbackAnalyzer

class TestFeedbackModels:
    """测试反馈数据模型"""

    def test_feedback_creation(self):
        """测试反馈创建"""
        feedback = Feedback(
            user_id="test_user",
            feedback_type=FeedbackType.POSITIVE,
            category=FeedbackCategory.USER_EXPERIENCE,
            priority=FeedbackPriority.HIGH,
            title="测试反馈",
            description="测试描述",
            rating=5,
            tags=["test", "feedback"]
        )
        
        assert feedback.user_id == "test_user"
        assert feedback.feedback_type == FeedbackType.POSITIVE
        assert feedback.category == FeedbackCategory.USER_EXPERIENCE
        assert feedback.priority == FeedbackPriority.HIGH
        assert feedback.title == "测试反馈"
        assert feedback.description == "测试描述"
        assert feedback.rating == 5
        assert "test" in feedback.tags
        assert feedback.status == FeedbackStatus.PENDING

    def test_feedback_to_dict(self):
        """测试反馈转换为字典"""
        feedback = Feedback(
            user_id="test_user",
            feedback_type=FeedbackType.NEGATIVE,
            title="测试反馈"
        )
        feedback_dict = feedback.to_dict()
        
        assert feedback_dict['user_id'] == 'test_user'
        assert feedback_dict['feedback_type'] == 'negative'
        assert feedback_dict['title'] == '测试反馈'
        assert 'created_at' in feedback_dict

    def test_feedback_from_dict(self):
        """测试从字典创建反馈"""
        feedback_dict = {
            'user_id': 'test_user',
            'feedback_type': 'positive',
            'category': 'user_experience',
            'title': '测试反馈',
            'description': '测试描述'
        }
        feedback = Feedback.from_dict(feedback_dict)
        
        assert feedback.user_id == 'test_user'
        assert feedback.feedback_type == FeedbackType.POSITIVE
        assert feedback.category == FeedbackCategory.USER_EXPERIENCE
        assert feedback.title == '测试反馈'

    def test_feedback_analysis_creation(self):
        """测试反馈分析结果创建"""
        analysis = FeedbackAnalysis(
            total_feedback=10,
            positive_count=5,
            negative_count=2,
            neutral_count=3,
            average_rating=4.5
        )
        
        assert analysis.total_feedback == 10
        assert analysis.positive_count == 5
        assert analysis.negative_count == 2
        assert analysis.neutral_count == 3
        assert analysis.average_rating == 4.5

    def test_feedback_analysis_to_dict(self):
        """测试反馈分析结果转换为字典"""
        analysis = FeedbackAnalysis(
            total_feedback=5,
            positive_count=3,
            negative_count=1,
            neutral_count=1
        )
        analysis_dict = analysis.to_dict()
        
        assert analysis_dict['total_feedback'] == 5
        assert analysis_dict['positive_count'] == 3
        assert analysis_dict['negative_count'] == 1
        assert analysis_dict['neutral_count'] == 1

class TestFeedbackManager:
    """测试反馈管理器"""

    def setup_method(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = FeedbackManager(base_dir=self.temp_dir)

    def teardown_method(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)

    def test_add_feedback(self):
        """测试添加反馈"""
        feedback = Feedback(
            user_id="test_user",
            title="测试反馈"
        )
        feedback_id = self.manager.add_feedback(feedback)
        
        assert feedback_id is not None
        assert feedback_id in self.manager.feedback_index

    def test_get_feedback(self):
        """测试获取反馈"""
        feedback = Feedback(
            user_id="test_user",
            title="测试反馈"
        )
        feedback_id = self.manager.add_feedback(feedback)
        
        retrieved_feedback = self.manager.get_feedback(feedback_id)
        assert retrieved_feedback is not None
        assert retrieved_feedback.title == "测试反馈"

    def test_update_feedback(self):
        """测试更新反馈"""
        feedback = Feedback(
            user_id="test_user",
            title="测试反馈",
            status=FeedbackStatus.PENDING
        )
        feedback_id = self.manager.add_feedback(feedback)
        
        updates = {"title": "更新后的反馈", "status": FeedbackStatus.IN_PROGRESS}
        success = self.manager.update_feedback(feedback_id, updates)
        
        assert success is True
        updated_feedback = self.manager.get_feedback(feedback_id)
        assert updated_feedback.title == "更新后的反馈"
        assert updated_feedback.status == FeedbackStatus.IN_PROGRESS

    def test_delete_feedback(self):
        """测试删除反馈"""
        feedback = Feedback(
            user_id="test_user",
            title="测试反馈"
        )
        feedback_id = self.manager.add_feedback(feedback)
        
        success = self.manager.delete_feedback(feedback_id)
        assert success is True
        assert self.manager.get_feedback(feedback_id) is None

    def test_get_feedbacks_by_user(self):
        """测试获取用户的反馈"""
        # 添加测试反馈
        feedback1 = Feedback(user_id="user1", title="反馈1")
        feedback2 = Feedback(user_id="user1", title="反馈2")
        feedback3 = Feedback(user_id="user2", title="反馈3")
        self.manager.add_feedback(feedback1)
        self.manager.add_feedback(feedback2)
        self.manager.add_feedback(feedback3)
        
        # 获取用户1的反馈
        user1_feedbacks = self.manager.get_feedbacks_by_user("user1")
        assert len(user1_feedbacks) == 2
        assert all(feedback.user_id == "user1" for feedback in user1_feedbacks)

    def test_get_feedbacks_by_type(self):
        """测试按类型获取反馈"""
        # 添加测试反馈
        feedback1 = Feedback(feedback_type=FeedbackType.POSITIVE, title="正面反馈")
        feedback2 = Feedback(feedback_type=FeedbackType.NEGATIVE, title="负面反馈")
        feedback3 = Feedback(feedback_type=FeedbackType.POSITIVE, title="另一个正面反馈")
        self.manager.add_feedback(feedback1)
        self.manager.add_feedback(feedback2)
        self.manager.add_feedback(feedback3)
        
        # 获取正面反馈
        positive_feedbacks = self.manager.get_feedbacks_by_type(FeedbackType.POSITIVE)
        assert len(positive_feedbacks) == 2
        assert all(feedback.feedback_type == FeedbackType.POSITIVE for feedback in positive_feedbacks)

    def test_get_feedbacks_by_category(self):
        """测试按分类获取反馈"""
        # 添加测试反馈
        feedback1 = Feedback(category=FeedbackCategory.USER_EXPERIENCE, title="用户体验反馈")
        feedback2 = Feedback(category=FeedbackCategory.SYSTEM_PERFORMANCE, title="性能反馈")
        self.manager.add_feedback(feedback1)
        self.manager.add_feedback(feedback2)
        
        # 获取用户体验反馈
        ux_feedbacks = self.manager.get_feedbacks_by_category(FeedbackCategory.USER_EXPERIENCE)
        assert len(ux_feedbacks) == 1
        assert ux_feedbacks[0].category == FeedbackCategory.USER_EXPERIENCE

    def test_get_feedbacks_by_status(self):
        """测试按状态获取反馈"""
        # 添加测试反馈
        feedback1 = Feedback(status=FeedbackStatus.PENDING, title="待处理反馈")
        feedback2 = Feedback(status=FeedbackStatus.RESOLVED, title="已解决反馈")
        self.manager.add_feedback(feedback1)
        self.manager.add_feedback(feedback2)
        
        # 获取待处理反馈
        pending_feedbacks = self.manager.get_feedbacks_by_status(FeedbackStatus.PENDING)
        assert len(pending_feedbacks) == 1
        assert pending_feedbacks[0].status == FeedbackStatus.PENDING

    def test_get_feedbacks_by_priority(self):
        """测试按优先级获取反馈"""
        # 添加测试反馈
        feedback1 = Feedback(priority=FeedbackPriority.HIGH, title="高优先级反馈")
        feedback2 = Feedback(priority=FeedbackPriority.LOW, title="低优先级反馈")
        self.manager.add_feedback(feedback1)
        self.manager.add_feedback(feedback2)
        
        # 获取高优先级反馈
        high_priority_feedbacks = self.manager.get_feedbacks_by_priority(FeedbackPriority.HIGH)
        assert len(high_priority_feedbacks) == 1
        assert high_priority_feedbacks[0].priority == FeedbackPriority.HIGH

    def test_get_pending_feedbacks(self):
        """测试获取待处理反馈"""
        # 添加测试反馈
        feedback1 = Feedback(status=FeedbackStatus.PENDING, title="待处理反馈1")
        feedback2 = Feedback(status=FeedbackStatus.PENDING, title="待处理反馈2")
        feedback3 = Feedback(status=FeedbackStatus.RESOLVED, title="已解决反馈")
        self.manager.add_feedback(feedback1)
        self.manager.add_feedback(feedback2)
        self.manager.add_feedback(feedback3)
        
        # 获取待处理反馈
        pending_feedbacks = self.manager.get_pending_feedbacks()
        assert len(pending_feedbacks) == 2
        assert all(feedback.status == FeedbackStatus.PENDING for feedback in pending_feedbacks)

    def test_get_high_priority_feedbacks(self):
        """测试获取高优先级反馈"""
        # 添加测试反馈
        feedback1 = Feedback(priority=FeedbackPriority.HIGH, title="高优先级反馈")
        feedback2 = Feedback(priority=FeedbackPriority.URGENT, title="紧急反馈")
        feedback3 = Feedback(priority=FeedbackPriority.MEDIUM, title="中优先级反馈")
        self.manager.add_feedback(feedback1)
        self.manager.add_feedback(feedback2)
        self.manager.add_feedback(feedback3)
        
        # 获取高优先级反馈
        high_priority_feedbacks = self.manager.get_high_priority_feedbacks()
        assert len(high_priority_feedbacks) == 2
        assert all(feedback.priority in [FeedbackPriority.HIGH, FeedbackPriority.URGENT] for feedback in high_priority_feedbacks)

    def test_respond_to_feedback(self):
        """测试回复反馈"""
        feedback = Feedback(title="测试反馈")
        feedback_id = self.manager.add_feedback(feedback)
        
        success = self.manager.respond_to_feedback(feedback_id, "这是回复", "admin")
        assert success is True
        
        updated_feedback = self.manager.get_feedback(feedback_id)
        assert updated_feedback.response == "这是回复"
        assert updated_feedback.responded_by == "admin"
        assert updated_feedback.status == FeedbackStatus.IN_PROGRESS

    def test_resolve_feedback(self):
        """测试解决反馈"""
        feedback = Feedback(title="测试反馈")
        feedback_id = self.manager.add_feedback(feedback)
        
        success = self.manager.resolve_feedback(feedback_id, "admin")
        assert success is True
        
        updated_feedback = self.manager.get_feedback(feedback_id)
        assert updated_feedback.status == FeedbackStatus.RESOLVED
        assert updated_feedback.resolved_at is not None

    def test_close_feedback(self):
        """测试关闭反馈"""
        feedback = Feedback(title="测试反馈")
        feedback_id = self.manager.add_feedback(feedback)
        
        success = self.manager.close_feedback(feedback_id)
        assert success is True
        
        updated_feedback = self.manager.get_feedback(feedback_id)
        assert updated_feedback.status == FeedbackStatus.CLOSED

    def test_analyze_feedbacks(self):
        """测试分析反馈"""
        # 添加测试反馈
        feedback1 = Feedback(
            feedback_type=FeedbackType.POSITIVE,
            category=FeedbackCategory.USER_EXPERIENCE,
            rating=5
        )
        feedback2 = Feedback(
            feedback_type=FeedbackType.NEGATIVE,
            category=FeedbackCategory.SYSTEM_PERFORMANCE,
            rating=2,
            description="系统响应慢"
        )
        self.manager.add_feedback(feedback1)
        self.manager.add_feedback(feedback2)
        
        # 分析反馈
        analysis = self.manager.analyze_feedbacks(days=30)
        assert analysis.total_feedback == 2
        assert analysis.positive_count == 1
        assert analysis.negative_count == 1
        assert analysis.average_rating == 3.5
        assert 'user_experience' in analysis.category_distribution
        assert 'system_performance' in analysis.category_distribution

    def test_get_feedback_statistics(self):
        """测试获取反馈统计信息"""
        # 添加测试反馈
        feedback1 = Feedback(feedback_type=FeedbackType.POSITIVE)
        feedback2 = Feedback(feedback_type=FeedbackType.NEGATIVE)
        self.manager.add_feedback(feedback1)
        self.manager.add_feedback(feedback2)
        
        # 获取统计信息
        stats = self.manager.get_feedback_statistics()
        assert stats['total_feedbacks'] == 2
        assert 'positive' in stats['type_distribution']
        assert 'negative' in stats['type_distribution']

    def test_export_feedbacks(self):
        """测试导出反馈"""
        # 添加测试反馈
        feedback = Feedback(title="测试反馈")
        self.manager.add_feedback(feedback)
        
        # 导出
        export_file = Path(self.temp_dir) / "export.json"
        success = self.manager.export_feedbacks(str(export_file))
        assert success is True
        assert export_file.exists()

class TestFeedbackCollector:
    """测试反馈收集器"""

    def setup_method(self):
        """设置测试环境"""
        self.collector = FeedbackCollector()

    def test_collect_feedback(self):
        """测试收集反馈"""
        feedback_data = {
            'user_id': 'test_user',
            'feedback_type': 'positive',
            'category': 'user_experience',
            'title': '测试反馈',
            'description': '测试描述',
            'rating': 5
        }
        
        with patch('src.feedback.collector.feedback_manager') as mock_manager:
            mock_manager.add_feedback.return_value = "feedback_id"
            feedback_id = self.collector.collect_feedback(feedback_data)
            
            assert feedback_id == "feedback_id"
            mock_manager.add_feedback.assert_called_once()

    def test_validate_feedback_data(self):
        """测试验证反馈数据"""
        # 有效数据
        valid_data = {
            'user_id': 'test_user',
            'feedback_type': 'positive',
            'title': '测试反馈',
            'description': '测试描述'
        }
        assert self.collector.validate_feedback_data(valid_data) is True
        
        # 无效数据（缺少必要字段）
        invalid_data = {
            'user_id': 'test_user'
        }
        assert self.collector.validate_feedback_data(invalid_data) is False

class TestFeedbackAnalyzer:
    """测试反馈分析器"""

    def setup_method(self):
        """设置测试环境"""
        self.analyzer = FeedbackAnalyzer()

    def test_analyze_feedback(self):
        """测试分析单个反馈"""
        feedback = Feedback(
            feedback_type=FeedbackType.NEGATIVE,
            description="系统响应太慢，需要改进"
        )
        
        analysis = self.analyzer.analyze_feedback(feedback)
        assert isinstance(analysis, dict)
        assert 'sentiment' in analysis
        assert 'keywords' in analysis

    def test_analyze_feedback_trends(self):
        """测试分析反馈趋势"""
        feedbacks = [
            Feedback(
                feedback_type=FeedbackType.POSITIVE,
                created_at=Mock()
            ),
            Feedback(
                feedback_type=FeedbackType.NEGATIVE,
                created_at=Mock()
            )
        ]
        
        trends = self.analyzer.analyze_feedback_trends(feedbacks)
        assert isinstance(trends, dict)
        assert 'sentiment_trend' in trends
        assert 'category_trend' in trends

    def test_generate_feedback_report(self):
        """测试生成反馈报告"""
        with patch('src.feedback.analyzer.feedback_manager') as mock_manager:
            mock_analysis = Mock()
            mock_analysis.to_dict.return_value = {}
            mock_manager.analyze_feedbacks.return_value = mock_analysis
            
            report = self.analyzer.generate_feedback_report(days=30)
            assert isinstance(report, dict)
            mock_manager.analyze_feedbacks.assert_called_once_with(days=30)

if __name__ == "__main__":
    pytest.main([__file__])
