import pytest
from unittest.mock import Mock, patch
from src.clarification_generator.clarification_generator import ClarificationGenerator

class TestClarificationGenerator:
    """测试澄清文档生成器"""

    def setup_method(self):
        """设置测试环境"""
        self.generator = ClarificationGenerator()

    @patch('src.clarification_generator.clarification_generator.ai_service')
    def test_generate_clarification_success(self, mock_ai_service):
        """测试成功生成澄清文档"""
        # 模拟AI服务返回
        mock_ai_service.generate.return_value = "Ambiguous points:\n- Test ambiguity\nConflicts:\n- Test conflict\n"
        
        # 测试数据
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        
        # 执行生成
        result = self.generator.generate_clarification(structured_data)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert 'ambiguous_points' in result
        assert 'conflicts' in result
        assert 'missing_information' in result
        assert 'suggestions' in result
        mock_ai_service.generate.assert_called_once()

    @patch('src.clarification_generator.clarification_generator.ai_service')
    def test_generate_clarification_ai_failure(self, mock_ai_service):
        """测试AI服务失败时的回退机制"""
        # 模拟AI服务抛出异常
        mock_ai_service.generate.side_effect = Exception("AI service failure")
        
        # 测试数据
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1 should be done'],
            'constraints': []
        }
        
        # 执行生成
        result = self.generator.generate_clarification(structured_data)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert 'suggestions' in result

    def test_generate_clarification_error(self):
        """测试生成澄清文档时的错误处理"""
        # 测试数据
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        
        # 模拟异常
        with patch('src.clarification_generator.clarification_generator.ai_service') as mock_ai_service:
            # 模拟AI服务和规则基础分析都失败
            mock_ai_service.generate.side_effect = Exception("AI service failure")
            with patch.object(self.generator, '_rule_based_analysis', side_effect=Exception("Rule-based analysis failure")):
                result = self.generator.generate_clarification(structured_data)
                assert 'Error generating clarification' in result['suggestions'][0]

    def test_prepare_prompt(self):
        """测试准备提示词"""
        # 测试数据
        structured_data = {
            'sections': ['Section 1', 'Section 2'],
            'requirements': ['Requirement 1', 'Requirement 2'],
            'constraints': ['Constraint 1', 'Constraint 2']
        }
        
        # 执行准备提示词
        prompt = self.generator._prepare_prompt(structured_data)
        
        # 验证结果
        assert 'Section 1' in prompt
        assert 'Section 2' in prompt
        assert 'Requirement 1' in prompt
        assert 'Requirement 2' in prompt
        assert 'Constraint 1' in prompt
        assert 'Constraint 2' in prompt

    def test_rule_based_analysis(self):
        """测试规则基础分析"""
        # 测试数据1：完整数据
        structured_data1 = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        result1 = self.generator._rule_based_analysis(structured_data1)
        assert result1 == ''
        
        # 测试数据2：缺少需求
        structured_data2 = {
            'sections': ['Section 1'],
            'requirements': [],
            'constraints': ['Constraint 1']
        }
        result2 = self.generator._rule_based_analysis(structured_data2)
        assert 'No functional requirements identified' in result2
        
        # 测试数据3：缺少约束
        structured_data3 = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': []
        }
        result3 = self.generator._rule_based_analysis(structured_data3)
        assert 'No constraints or non-functional requirements identified' in result3
        
        # 测试数据4：包含模糊需求
        structured_data4 = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1 should be done', 'Requirement 2 may be added'],
            'constraints': ['Constraint 1']
        }
        result4 = self.generator._rule_based_analysis(structured_data4)
        assert 'Ambiguous requirement' in result4
        
        # 测试数据5：包含不完整需求
        structured_data5 = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1 includes etc.'],
            'constraints': ['Constraint 1']
        }
        result5 = self.generator._rule_based_analysis(structured_data5)
        assert 'Incomplete requirement' in result5

    def test_structure_clarification(self):
        """测试结构化澄清文档"""
        # 测试数据
        content = "Ambiguous points:\n- Test ambiguity\nConflicts:\n- Test conflict\nMissing information:\n- Test missing\nSuggestions:\n- Test suggestion\n"
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        
        # 执行结构化
        result = self.generator._structure_clarification(content, structured_data)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert 'Test ambiguity' in result['ambiguous_points']
        assert 'Test conflict' in result['conflicts']
        assert 'Test missing' in result['missing_information']
        assert 'Test suggestion' in result['suggestions']

    def test_structure_clarification_no_issues(self):
        """测试无问题时的结构化澄清文档"""
        # 测试数据
        content = "No issues found"
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        
        # 执行结构化
        result = self.generator._structure_clarification(content, structured_data)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert len(result['ambiguous_points']) == 0
        assert len(result['conflicts']) == 0
        assert len(result['missing_information']) == 0
        assert 'No major issues identified' in result['suggestions'][0]

    def test_get_default_clarification(self):
        """测试获取默认澄清文档"""
        # 测试数据
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        
        # 执行获取默认澄清文档
        result = self.generator._get_default_clarification(structured_data)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert len(result['ambiguous_points']) == 0
        assert len(result['conflicts']) == 0
        assert len(result['missing_information']) == 0
        assert 'Error generating clarification' in result['suggestions'][0]

if __name__ == "__main__":
    pytest.main([__file__])
