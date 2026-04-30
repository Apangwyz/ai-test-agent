"""
AI Loop引擎测试用例
"""
import pytest
import logging
from src.ai_loop.engine import AILoopEngine

logging.basicConfig(level=logging.INFO)

class TestAILoopEngine:
    """AI Loop引擎测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.engine = AILoopEngine()
        self.engine.reset_performance_metrics()
    
    def test_engine_initialization(self):
        """测试引擎初始化"""
        assert self.engine is not None
        assert self.engine.max_iterations == 3
        assert self.engine.min_quality_threshold == 0.6
    
    def test_process_request_basic(self):
        """测试基本请求处理"""
        request_data = {
            'task_type': 'general',
            'context': '测试AI Loop引擎',
            'user_id': 'test_user'
        }
        
        result = self.engine.process_request(request_data)
        
        assert 'success' in result
        assert result['success'] is True
        assert 'result' in result
    
    def test_calculate_content_quality(self):
        """测试内容质量计算"""
        # 测试短内容
        short_content = "短"
        score = self.engine._calculate_content_quality(short_content)
        assert score < 0.3
        
        # 测试中等长度内容
        medium_content = "这是一段中等长度的测试内容，用于测试内容质量评分功能。"
        score = self.engine._calculate_content_quality(medium_content)
        assert 0.3 <= score < 0.7
        
        # 测试高质量内容
        long_content = """这是一段高质量的测试内容，包含多个段落和专业术语。

## 功能分析
本系统包含以下核心功能模块：
1. 数据收集模块 - 负责收集和预处理输入数据
2. 知识检索模块 - 从知识库中检索相关知识
3. 提示词生成模块 - 生成高质量的提示词
4. 模型推理模块 - 调用AI模型进行推理
5. 结果验证模块 - 验证输出结果的质量

通过以上模块的协同工作，系统能够实现自动化的内容生成和优化。"""
        score = self.engine._calculate_content_quality(long_content)
        assert score >= 0.7
    
    def test_validate_result(self):
        """测试结果验证"""
        inference_result = {
            'content': '测试内容',
            'model_used': 'test_model',
            'generated_at': '2024-01-01T00:00:00'
        }
        collected_data = {
            'task_type': 'general',
            'adjustment_attempts': 0
        }
        
        result = self.engine._validate_result(inference_result, collected_data)
        
        assert 'validated' in result
        assert 'validation_score' in result
        assert 'validation_threshold' in result
    
    def test_prompt_adjustment(self):
        """测试提示词调整策略"""
        # 测试过短内容调整
        adjustment = self.engine._get_prompt_adjustment('生成内容过短', 1)
        assert '更详细' in adjustment
        
        # 测试低质量调整
        adjustment = self.engine._get_prompt_adjustment('内容质量低', 1)
        assert '提高回答质量' in adjustment
        
        # 测试不相关调整
        adjustment = self.engine._get_prompt_adjustment('内容不相关', 1)
        assert '关注问题的核心' in adjustment
        
        # 测试不完整调整
        adjustment = self.engine._get_prompt_adjustment('内容不完整', 1)
        assert '补充完整' in adjustment
    
    def test_get_performance_metrics(self):
        """测试性能指标获取"""
        metrics = self.engine.get_performance_metrics()
        
        assert 'total_requests' in metrics
        assert 'successful_requests' in metrics
        assert 'failed_requests' in metrics
        assert 'average_response_time' in metrics
        assert 'success_rate' in metrics
        assert 'knowledge_hit_rate' in metrics
    
    def test_iterative_optimization(self):
        """测试多轮迭代优化"""
        collected_data = {
            'task_type': 'general',
            'context': '测试多轮迭代优化功能',
            'user_id': 'test_user',
            'adjustment_attempts': 0
        }
        
        # 模拟执行迭代优化
        result = self.engine._perform_iterative_optimization(collected_data)
        
        assert result is not None
        assert 'content' in result or 'error' in result
    
    def test_retry_mechanism(self):
        """测试重试机制"""
        # 测试带重试的推理
        result = self.engine._perform_inference_with_retry(
            prompt='测试重试机制',
            collected_data={'task_type': 'general'},
            max_retries=1
        )
        
        assert result is not None
        assert 'retry_attempts' in result

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
