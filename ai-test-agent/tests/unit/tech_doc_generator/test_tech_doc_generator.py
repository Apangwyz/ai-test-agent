import pytest
from unittest.mock import Mock, patch
from src.tech_doc_generator.tech_doc_generator import TechDocGenerator

class TestTechDocGenerator:
    """测试技术文档生成器"""

    def setup_method(self):
        """设置测试环境"""
        self.generator = TechDocGenerator()

    @patch('src.tech_doc_generator.tech_doc_generator.ai_service')
    def test_generate_tech_doc_success(self, mock_ai_service):
        """测试成功生成技术文档"""
        # 模拟AI服务返回
        mock_ai_service.generate.return_value = "## System Architecture\nArchitecture content\n## Technology Stack\nTech stack content\n"
        
        # 测试数据
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        
        # 执行生成
        result = self.generator.generate_tech_doc(structured_data)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert 'architecture' in result
        assert 'tech_stack' in result
        assert 'core_modules' in result
        assert 'interface_design' in result
        assert 'data_flow' in result
        assert 'challenges' in result
        assert 'implementation' in result
        assert 'deployment' in result
        mock_ai_service.generate.assert_called_once()

    @patch('src.tech_doc_generator.tech_doc_generator.ai_service')
    def test_generate_tech_doc_with_clarification(self, mock_ai_service):
        """测试使用澄清文档生成技术文档"""
        # 模拟AI服务返回
        mock_ai_service.generate.return_value = "## System Architecture\nArchitecture content\n"
        
        # 测试数据
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        clarification_doc = {
            'ambiguous_points': ['Test ambiguity'],
            'conflicts': ['Test conflict'],
            'missing_information': ['Test missing'],
            'suggestions': ['Test suggestion']
        }
        
        # 执行生成
        result = self.generator.generate_tech_doc(structured_data, clarification_doc)
        
        # 验证结果
        assert result['version'] == '1.0'
        mock_ai_service.generate.assert_called_once()

    @patch('src.tech_doc_generator.tech_doc_generator.ai_service')
    def test_generate_tech_doc_ai_failure(self, mock_ai_service):
        """测试AI服务失败时的回退机制"""
        # 模拟AI服务抛出异常
        mock_ai_service.generate.side_effect = Exception("AI service failure")
        
        # 测试数据
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        
        # 执行生成
        result = self.generator.generate_tech_doc(structured_data)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert 'architecture' in result
        assert 'tech_stack' in result

    def test_generate_tech_doc_error(self):
        """测试生成技术文档时的错误处理"""
        # 测试数据
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        
        # 模拟异常
        with patch('src.tech_doc_generator.tech_doc_generator.ai_service') as mock_ai_service:
            # 模拟AI服务和规则基础生成都失败
            mock_ai_service.generate.side_effect = Exception("AI service failure")
            with patch.object(self.generator, '_rule_based_generation', side_effect=Exception("Rule-based generation failure")):
                result = self.generator.generate_tech_doc(structured_data)
                assert result['version'] == '1.0'
                assert 'Error generating architecture design' in result['architecture']['content']

    def test_prepare_prompt(self):
        """测试准备提示词"""
        # 测试数据
        structured_data = {
            'sections': ['Section 1', 'Section 2'],
            'requirements': ['Requirement 1', 'Requirement 2'],
            'constraints': ['Constraint 1', 'Constraint 2']
        }
        
        # 执行准备提示词
        prompt = self.generator._prepare_prompt(structured_data, None)
        
        # 验证结果
        assert 'Section 1' in prompt
        assert 'Section 2' in prompt
        assert 'Requirement 1' in prompt
        assert 'Requirement 2' in prompt
        assert 'Constraint 1' in prompt
        assert 'Constraint 2' in prompt

    def test_prepare_prompt_with_clarification(self):
        """测试使用澄清文档准备提示词"""
        # 测试数据
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        clarification_doc = {
            'ambiguous_points': ['Test ambiguity'],
            'conflicts': ['Test conflict'],
            'missing_information': ['Test missing'],
            'suggestions': ['Test suggestion']
        }
        
        # 执行准备提示词
        prompt = self.generator._prepare_prompt(structured_data, clarification_doc)
        
        # 验证结果
        assert 'Clarification notes' in prompt
        assert 'Test ambiguity' in prompt
        assert 'Test conflict' in prompt
        assert 'Test missing' in prompt
        assert 'Test suggestion' in prompt

    def test_rule_based_generation(self):
        """测试规则基础生成"""
        # 测试数据
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        
        # 执行规则基础生成
        result = self.generator._rule_based_generation(structured_data)
        
        # 验证结果
        assert '# Technical Documentation' in result
        assert '## System Architecture' in result
        assert '## Technology Stack' in result
        assert '## Core Modules' in result
        assert '## Interface Design' in result
        assert '## Data Flow' in result
        assert '## Technical Challenges' in result
        assert '## Implementation Plan' in result
        assert '## Deployment Strategy' in result

    def test_structure_tech_doc(self):
        """测试结构化技术文档"""
        # 测试数据
        content = "## System Architecture\nArchitecture content\n## Technology Stack\nTech stack content\n## Core Modules\n- Module 1\n- Module 2\n"
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        
        # 执行结构化
        result = self.generator._structure_tech_doc(content, structured_data)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert 'Architecture content' in result['architecture']['content']
        assert 'Tech stack content' in result['tech_stack']['content']
        assert 'Module 1' in result['core_modules']
        assert 'Module 2' in result['core_modules']

    def test_structure_tech_doc_missing_sections(self):
        """测试缺少部分的结构化技术文档"""
        # 测试数据
        content = ""
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        
        # 执行结构化
        result = self.generator._structure_tech_doc(content, structured_data)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert result['core_modules'] == ['To be defined']
        assert result['challenges'] == ['To be defined']
        assert result['architecture']['content'] == 'To be defined'

    def test_get_default_tech_doc(self):
        """测试获取默认技术文档"""
        # 测试数据
        structured_data = {
            'sections': ['Section 1'],
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        
        # 执行获取默认技术文档
        result = self.generator._get_default_tech_doc(structured_data)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert 'Error generating architecture design' in result['architecture']['content']
        assert 'Error generating tech stack selection' in result['tech_stack']['content']
        assert 'Error generating core modules' in result['core_modules']
        assert 'Error generating interface design' in result['interface_design']['content']
        assert 'Error generating data flow design' in result['data_flow']['content']
        assert 'Error generating technical challenges' in result['challenges']
        assert 'Error generating implementation plan' in result['implementation']['content']
        assert 'Error generating deployment strategy' in result['deployment']['content']

if __name__ == "__main__":
    pytest.main([__file__])
