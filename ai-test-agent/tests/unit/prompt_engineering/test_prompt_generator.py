import pytest
from unittest.mock import Mock, patch
from src.prompt_engineering.generator import PromptGenerator
from src.knowledge_base import KnowledgeEntity, KnowledgeType

class TestPromptGenerator:
    """测试提示词生成器"""

    def setup_method(self):
        """设置测试环境"""
        self.generator = PromptGenerator()

    def test_initialization(self):
        """测试初始化"""
        assert hasattr(self.generator, 'prompt_templates')
        assert 'requirement_analysis' in self.generator.prompt_templates
        assert 'technical_solution' in self.generator.prompt_templates
        assert 'clarification' in self.generator.prompt_templates
        assert 'coding_task' in self.generator.prompt_templates
        assert 'test_case' in self.generator.prompt_templates
        assert 'knowledge_enhanced' in self.generator.prompt_templates

    def test_generate_prompt_basic(self):
        """测试基本提示词生成"""
        prompt = self.generator.generate_prompt('requirement_analysis', '测试需求', use_knowledge=False)
        assert '作为专业的需求分析师' in prompt
        assert '测试需求' in prompt

    @patch('src.prompt_engineering.generator.query_service')
    def test_generate_prompt_with_knowledge(self, mock_query_service):
        """测试带知识增强的提示词生成"""
        # 模拟知识查询结果
        mock_entity = Mock(spec=KnowledgeEntity)
        mock_entity.type = KnowledgeType.REQUIREMENT
        mock_entity.type.value = 'requirement'
        mock_entity.title = '测试知识'
        mock_entity.content = '测试知识内容'
        
        mock_result = Mock()
        mock_result.entity = mock_entity
        mock_result.score = 0.9
        
        mock_query_service.query.return_value = [mock_result]
        
        # 生成提示词
        prompt = self.generator.generate_prompt('requirement_analysis', '测试需求', use_knowledge=True)
        assert '作为专业的需求分析师' in prompt
        assert '测试需求' in prompt
        assert '测试知识' in prompt
        assert '测试知识内容' in prompt

    @patch('src.prompt_engineering.generator.query_service')
    def test_generate_prompt_no_knowledge(self, mock_query_service):
        """测试无知识时的提示词生成"""
        # 模拟空知识查询结果
        mock_query_service.query.return_value = []
        
        # 生成提示词
        prompt = self.generator.generate_prompt('requirement_analysis', '测试需求', use_knowledge=True)
        assert '作为专业的需求分析师' in prompt
        assert '测试需求' in prompt

    def test_generate_prompt_error(self):
        """测试提示词生成错误处理"""
        # 模拟异常
        with patch('src.prompt_engineering.generator.query_service') as mock_query_service:
            mock_query_service.query.side_effect = Exception("测试异常")
            prompt = self.generator.generate_prompt('requirement_analysis', '测试需求', use_knowledge=True)
            assert prompt == '测试需求'

    def test_generate_adaptive_prompt(self):
        """测试自适应提示词生成"""
        # 无用户偏好
        prompt1 = self.generator.generate_adaptive_prompt('requirement_analysis', '测试需求')
        assert '测试需求' in prompt1
        
        # 有用户偏好
        preferences = {
            'detailed_output': True,
            'include_examples': True
        }
        prompt2 = self.generator.generate_adaptive_prompt('requirement_analysis', '测试需求', user_preferences=preferences)
        assert '测试需求' in prompt2
        assert '请提供详细的分析和解释' in prompt2
        assert '请在输出中包含具体的示例' in prompt2

    def test_generate_adaptive_prompt_error(self):
        """测试自适应提示词生成错误处理"""
        # 模拟异常
        with patch('src.prompt_engineering.generator.query_service') as mock_query_service:
            mock_query_service.query.side_effect = Exception("测试异常")
            prompt = self.generator.generate_adaptive_prompt('requirement_analysis', '测试需求')
            assert '测试需求' in prompt

    def test_generate_prompt_with_feedback(self):
        """测试基于反馈的提示词生成"""
        # 无反馈
        prompt1 = self.generator.generate_prompt_with_feedback('requirement_analysis', '测试需求')
        assert '测试需求' in prompt1
        
        # 有反馈
        feedback = {
            'type': 'insufficient_detail',
            'content': '需要更多细节'
        }
        prompt2 = self.generator.generate_prompt_with_feedback('requirement_analysis', '测试需求', feedback=feedback)
        assert '测试需求' in prompt2
        assert '基于用户反馈，请提供更详细的分析' in prompt2
        assert '需要更多细节' in prompt2

    def test_generate_prompt_with_feedback_error(self):
        """测试基于反馈的提示词生成错误处理"""
        # 模拟异常
        with patch('src.prompt_engineering.generator.query_service') as mock_query_service:
            mock_query_service.query.side_effect = Exception("测试异常")
            prompt = self.generator.generate_prompt_with_feedback('requirement_analysis', '测试需求')
            assert '测试需求' in prompt

    def test_optimize_prompt_quality(self):
        """测试为质量优化提示词"""
        prompt = self.generator.optimize_prompt('requirement_analysis', '测试需求', optimization_goal='quality')
        assert '测试需求' in prompt
        assert '质量要求' in prompt
        assert '确保分析的准确性和专业性' in prompt

    def test_optimize_prompt_efficiency(self):
        """测试为效率优化提示词"""
        prompt = self.generator.optimize_prompt('requirement_analysis', '测试需求', optimization_goal='efficiency')
        assert '测试需求' in prompt
        assert '效率要求' in prompt
        assert '直接回答核心问题' in prompt

    def test_optimize_prompt_balance(self):
        """测试为平衡优化提示词"""
        prompt = self.generator.optimize_prompt('requirement_analysis', '测试需求', optimization_goal='balance')
        assert '测试需求' in prompt
        assert '平衡要求' in prompt
        assert '在质量和效率之间保持平衡' in prompt

    def test_optimize_prompt_error(self):
        """测试优化提示词错误处理"""
        # 模拟异常
        with patch('src.prompt_engineering.generator.query_service') as mock_query_service:
            mock_query_service.query.side_effect = Exception("测试异常")
            prompt = self.generator.optimize_prompt('requirement_analysis', '测试需求')
            assert '测试需求' in prompt

    def test_get_prompt_statistics(self):
        """测试获取提示词统计信息"""
        stats = self.generator.get_prompt_statistics()
        assert 'available_templates' in stats
        assert 'knowledge_integration' in stats
        assert 'adaptive_generation' in stats
        assert 'feedback_improvement' in stats
        assert 'optimization_modes' in stats
        assert 'last_updated' in stats
        assert 'quality' in stats['optimization_modes']
        assert 'efficiency' in stats['optimization_modes']
        assert 'balance' in stats['optimization_modes']

    def test_apply_user_preferences(self):
        """测试应用用户偏好"""
        prompt = "基础提示词"
        preferences = {
            'detailed_output': True,
            'concise_output': False,
            'include_examples': True
        }
        enhanced_prompt = self.generator._apply_user_preferences(prompt, preferences)
        assert '基础提示词' in enhanced_prompt
        assert '请提供详细的分析和解释' in enhanced_prompt
        assert '请在输出中包含具体的示例' in enhanced_prompt

    def test_apply_user_preferences_error(self):
        """测试应用用户偏好错误处理"""
        prompt = "基础提示词"
        # 模拟异常
        result = self.generator._apply_user_preferences(prompt, None)
        assert result == prompt

    def test_improve_prompt_with_feedback(self):
        """测试根据反馈改进提示词"""
        prompt = "基础提示词"
        
        # 测试不同类型的反馈
        feedback1 = {'type': 'insufficient_detail', 'content': '需要更多细节'}
        result1 = self.generator._improve_prompt_with_feedback(prompt, feedback1)
        assert '基于用户反馈，请提供更详细的分析' in result1
        
        feedback2 = {'type': 'too_verbose'}
        result2 = self.generator._improve_prompt_with_feedback(prompt, feedback2)
        assert '请简化输出，重点关注核心要点' in result2
        
        feedback3 = {'type': 'missing_aspects', 'content': '缺少某些方面'}
        result3 = self.generator._improve_prompt_with_feedback(prompt, feedback3)
        assert '请补充以下方面的分析' in result3
        
        feedback4 = {'type': 'quality_issue'}
        result4 = self.generator._improve_prompt_with_feedback(prompt, feedback4)
        assert '请特别注意输出的准确性和专业性' in result4
        
        feedback5 = {'type': 'format_issue'}
        result5 = self.generator._improve_prompt_with_feedback(prompt, feedback5)
        assert '请按照标准格式输出结果' in result5

    def test_improve_prompt_with_feedback_error(self):
        """测试根据反馈改进提示词错误处理"""
        prompt = "基础提示词"
        # 模拟异常
        result = self.generator._improve_prompt_with_feedback(prompt, None)
        assert result == prompt

    def test_combine_context(self):
        """测试组合上下文"""
        original_context = "原始需求"
        knowledge_context = "相关知识"
        combined = self.generator._combine_context(original_context, knowledge_context)
        assert '原始需求' in combined
        assert '相关知识' in combined

if __name__ == "__main__":
    pytest.main([__file__])
