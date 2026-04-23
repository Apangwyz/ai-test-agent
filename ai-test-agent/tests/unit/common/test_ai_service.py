import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.common.ai_service import AIService
from src.common.enhanced_ai_service import EnhancedAIService, ModelPerformance, CacheEntry

class TestAIService:
    """测试基本AI服务"""

    def setup_method(self):
        """设置测试环境"""
        # 保存原始环境变量
        import os
        self.original_env = os.environ.copy()
        # 清除可能的API密钥
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        if 'QWEN_API_KEY' in os.environ:
            del os.environ['QWEN_API_KEY']
        # 创建服务实例
        self.service = AIService()

    def teardown_method(self):
        """清理测试环境"""
        import os
        # 恢复原始环境变量
        os.environ.update(self.original_env)

    def test_initialization_no_keys(self):
        """测试无API密钥的初始化"""
        assert self.service.openai_api_key is None
        assert self.service.qwen_api_key is None
        assert self.service.use_enhanced is True  # 增强服务应该可用

    def test_initialization_with_keys(self):
        """测试有API密钥的初始化"""
        import os
        os.environ['OPENAI_API_KEY'] = 'test_openai_key'
        os.environ['QWEN_API_KEY'] = 'test_qwen_key'
        # 重新创建服务实例
        service = AIService()
        assert service.openai_api_key == 'test_openai_key'
        assert service.qwen_api_key == 'test_qwen_key'

    def test_generate_no_api_key(self):
        """测试无API密钥时的生成"""
        result = self.service.generate("test prompt", "test system prompt", model_type='qwen')
        assert result == "Error: No API key configured"

    @patch('src.common.ai_service.dashscope')
    def test_generate_with_qwen(self, mock_dashscope):
        """测试使用Qwen模型生成"""
        import os
        os.environ['QWEN_API_KEY'] = 'test_qwen_key'
        # 重新创建服务实例
        service = AIService()
        
        # 模拟Qwen API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_output = Mock()
        mock_output.text = "Qwen response"
        mock_response.output = mock_output
        mock_dashscope.Generation.call.return_value = mock_response
        
        # 执行测试
        result = service.generate("test prompt", "test system prompt", model_type='qwen')
        assert result == "Qwen response"
        mock_dashscope.Generation.call.assert_called_once()

    @patch('src.common.ai_service.openai')
    def test_generate_with_openai(self, mock_openai):
        """测试使用OpenAI模型生成"""
        import os
        os.environ['OPENAI_API_KEY'] = 'test_openai_key'
        # 重新创建服务实例
        service = AIService()
        
        # 模拟OpenAI API响应
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "OpenAI response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        # 执行测试
        result = service.generate("test prompt", "test system prompt", model_type='openai')
        assert result == "OpenAI response"
        mock_openai.ChatCompletion.create.assert_called_once()

    def test_get_service_stats_basic(self):
        """测试获取基本服务统计信息"""
        # 模拟增强服务不可用
        self.service.use_enhanced = False
        stats = self.service.get_service_stats()
        assert stats['enhanced_service'] is False
        assert stats['basic_service'] is True

    @patch('src.common.ai_service.enhanced_ai_service')
    def test_get_service_stats_enhanced(self, mock_enhanced):
        """测试获取增强服务统计信息"""
        mock_stats = {'enhanced': True}
        mock_enhanced.get_service_stats.return_value = mock_stats
        stats = self.service.get_service_stats()
        assert stats == mock_stats
        mock_enhanced.get_service_stats.assert_called_once()

class TestEnhancedAIService:
    """测试增强AI服务"""

    def setup_method(self):
        """设置测试环境"""
        # 保存原始环境变量
        import os
        self.original_env = os.environ.copy()
        # 清除可能的API密钥
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        if 'QWEN_API_KEY' in os.environ:
            del os.environ['QWEN_API_KEY']
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        # 设置缓存目录
        os.environ['CACHE_ENABLED'] = 'true'
        os.environ['CACHE_TTL'] = '3600'
        # 模拟缓存目录
        self.cache_dir = Path(self.temp_dir) / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        # 模拟Path
        with patch('src.common.enhanced_ai_service.Path') as mock_path:
            mock_path.return_value = self.cache_dir
            mock_path.mkdir = Mock()
            mock_path.glob = self.cache_dir.glob
            mock_path.exists = self.cache_dir.exists
            # 创建服务实例
            self.service = EnhancedAIService()

    def teardown_method(self):
        """清理测试环境"""
        import os
        # 恢复原始环境变量
        os.environ.update(self.original_env)
        # 清理临时目录
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """测试增强AI服务初始化"""
        assert hasattr(self.service, 'model_performance')
        assert 'qwen' in self.service.model_performance
        assert 'openai' in self.service.model_performance
        assert hasattr(self.service, 'memory_cache')
        assert hasattr(self.service, 'cache_stats')

    def test_model_performance_update(self):
        """测试模型性能更新"""
        performance = ModelPerformance(model_name='test')
        performance.update_performance(True, 1.5)
        assert performance.total_calls == 1
        assert performance.successful_calls == 1
        assert performance.average_time == 1.5
        assert performance.success_rate == 1.0

    def test_cache_entry(self):
        """测试缓存条目"""
        entry = CacheEntry(key='test', content='test content')
        assert entry.key == 'test'
        assert entry.content == 'test content'
        assert not entry.is_expired()
        entry.access()
        assert entry.access_count == 1

    def test_select_model_performance(self):
        """测试基于性能选择模型"""
        # 设置性能数据
        self.service.model_performance['qwen'].update_performance(True, 0.5)
        self.service.model_performance['openai'].update_performance(True, 1.0)
        # 设置路由策略
        self.service.routing_strategy = 'performance'
        # 测试选择
        model = self.service._select_model('test', 'test')
        assert model in ['qwen', 'openai']

    def test_select_model_cost(self):
        """测试基于成本选择模型"""
        # 设置路由策略
        self.service.routing_strategy = 'cost'
        # 测试选择
        model = self.service._select_model('test', 'test')
        assert model in ['qwen', 'openai']

    def test_select_model_availability(self):
        """测试基于可用性选择模型"""
        # 设置路由策略
        self.service.routing_strategy = 'availability'
        # 测试选择
        model = self.service._select_model('test', 'test')
        assert model in ['qwen', 'openai']

    def test_get_cache_key(self):
        """测试生成缓存键"""
        key1 = self.service._get_cache_key('prompt', 'system', 'qwen', 0.3)
        key2 = self.service._get_cache_key('prompt', 'system', 'qwen', 0.3)
        key3 = self.service._get_cache_key('different', 'system', 'qwen', 0.3)
        assert key1 == key2
        assert key1 != key3

    def test_cache_operations(self):
        """测试缓存操作"""
        # 保存到缓存
        self.service._save_to_cache('prompt', 'system', 'qwen', 0.3, 'content')
        # 从缓存获取
        result = self.service._get_from_cache('prompt', 'system', 'qwen', 0.3)
        assert result == 'content'
        # 测试缓存命中
        assert self.service.cache_stats['hits'] == 1

    def test_clear_cache(self):
        """测试清空缓存"""
        # 保存到缓存
        self.service._save_to_cache('prompt', 'system', 'qwen', 0.3, 'content')
        assert len(self.service.memory_cache) > 0
        # 清空缓存
        self.service.clear_cache()
        assert len(self.service.memory_cache) == 0
        assert self.service.cache_stats['hits'] == 0
        assert self.service.cache_stats['misses'] == 0
        assert self.service.cache_stats['size'] == 0

    def test_get_cache_stats(self):
        """测试获取缓存统计信息"""
        stats = self.service.get_cache_stats()
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'hit_rate' in stats
        assert 'enabled' in stats
        assert 'ttl' in stats

    def test_get_model_performance(self):
        """测试获取模型性能"""
        # 更新性能数据
        self.service.model_performance['qwen'].update_performance(True, 0.5)
        stats = self.service.get_model_performance()
        assert 'qwen' in stats
        assert 'openai' in stats
        assert 'total_calls' in stats['qwen']
        assert 'success_rate' in stats['qwen']

    def test_get_service_stats(self):
        """测试获取服务统计信息"""
        stats = self.service.get_service_stats()
        assert 'cache_stats' in stats
        assert 'model_performance' in stats
        assert 'routing_strategy' in stats
        assert 'load_balancing' in stats

    @patch('src.common.enhanced_ai_service.dashscope')
    def test_generate_with_qwen(self, mock_dashscope):
        """测试使用Qwen模型生成"""
        import os
        os.environ['QWEN_API_KEY'] = 'test_qwen_key'
        # 重新创建服务实例
        with patch('src.common.enhanced_ai_service.Path') as mock_path:
            mock_path.return_value = self.cache_dir
            mock_path.mkdir = Mock()
            mock_path.glob = self.cache_dir.glob
            mock_path.exists = self.cache_dir.exists
            service = EnhancedAIService()
        
        # 模拟Qwen API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_output = Mock()
        mock_output.text = "Qwen response"
        mock_response.output = mock_output
        mock_dashscope.Generation.call.return_value = mock_response
        
        # 执行测试
        result = service.generate("test prompt", "test system prompt", model_type='qwen')
        assert result == "Qwen response"
        mock_dashscope.Generation.call.assert_called_once()

    @patch('src.common.enhanced_ai_service.openai')
    def test_generate_with_openai(self, mock_openai):
        """测试使用OpenAI模型生成"""
        import os
        os.environ['OPENAI_API_KEY'] = 'test_openai_key'
        # 重新创建服务实例
        with patch('src.common.enhanced_ai_service.Path') as mock_path:
            mock_path.return_value = self.cache_dir
            mock_path.mkdir = Mock()
            mock_path.glob = self.cache_dir.glob
            mock_path.exists = self.cache_dir.exists
            service = EnhancedAIService()
        
        # 模拟OpenAI API响应
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "OpenAI response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        # 执行测试
        result = service.generate("test prompt", "test system prompt", model_type='openai')
        assert result == "OpenAI response"
        mock_openai.ChatCompletion.create.assert_called_once()

    @patch('src.common.enhanced_ai_service.dashscope')
    @patch('src.common.enhanced_ai_service.openai')
    def test_failover(self, mock_openai, mock_dashscope):
        """测试故障转移"""
        import os
        os.environ['QWEN_API_KEY'] = 'test_qwen_key'
        os.environ['OPENAI_API_KEY'] = 'test_openai_key'
        # 重新创建服务实例
        with patch('src.common.enhanced_ai_service.Path') as mock_path:
            mock_path.return_value = self.cache_dir
            mock_path.mkdir = Mock()
            mock_path.glob = self.cache_dir.glob
            mock_path.exists = self.cache_dir.exists
            service = EnhancedAIService()
        
        # 模拟Qwen API失败
        mock_qwen_response = Mock()
        mock_qwen_response.status_code = 500
        mock_dashscope.Generation.call.return_value = mock_qwen_response
        
        # 模拟OpenAI API成功
        mock_openai_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "OpenAI response"
        mock_choice.message = mock_message
        mock_openai_response.choices = [mock_choice]
        mock_openai.ChatCompletion.create.return_value = mock_openai_response
        
        # 执行测试
        result = service.generate("test prompt", "test system prompt", model_type='qwen')
        assert result == "OpenAI response"
        mock_dashscope.Generation.call.assert_called_once()
        mock_openai.ChatCompletion.create.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])
