import pytest
from unittest.mock import Mock, patch, mock_open
from src.test_case_generator.test_case_generator import TestCaseGenerator

class TestTestCaseGenerator:
    """测试测试用例生成器"""

    def setup_method(self):
        """设置测试环境"""
        self.generator = TestCaseGenerator()

    @patch('src.test_case_generator.test_case_generator.ai_service')
    def test_generate_test_cases_success(self, mock_ai_service):
        """测试成功生成测试用例"""
        # 模拟AI服务返回
        mock_ai_service.generate.return_value = "Test Case 1. User Authentication Test\nType: functional\nSteps: 1. Navigate to login page\nExpected results: User should be logged in\nPriority: high\n"
        
        # 测试数据
        structured_data = {
            'requirements': ['User should be able to login'],
            'constraints': ['Must use HTTPS']
        }
        tech_doc = {
            'core_modules': ['Authentication module'],
            'interface_design': {'content': 'Login form'}
        }
        
        # 执行生成
        result = self.generator.generate_test_cases(structured_data, tech_doc)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert 'test_cases' in result
        assert len(result['test_cases']) > 0
        mock_ai_service.generate.assert_called_once()

    @patch('src.test_case_generator.test_case_generator.ai_service')
    def test_generate_test_cases_ai_failure(self, mock_ai_service):
        """测试AI服务失败时的回退机制"""
        # 模拟AI服务抛出异常
        mock_ai_service.generate.side_effect = Exception("AI service failure")
        
        # 测试数据
        structured_data = {
            'requirements': ['User should be able to login'],
            'constraints': ['Must use HTTPS']
        }
        tech_doc = {
            'core_modules': ['Authentication module'],
            'interface_design': {'content': 'Login form'}
        }
        
        # 执行生成
        result = self.generator.generate_test_cases(structured_data, tech_doc)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert 'test_cases' in result
        assert len(result['test_cases']) > 0

    def test_generate_test_cases_error(self):
        """测试生成测试用例时的错误处理"""
        # 测试数据
        structured_data = {
            'requirements': ['User should be able to login'],
            'constraints': ['Must use HTTPS']
        }
        tech_doc = {
            'core_modules': ['Authentication module'],
            'interface_design': {'content': 'Login form'}
        }
        
        # 模拟异常
        with patch('src.test_case_generator.test_case_generator.ai_service') as mock_ai_service:
            # 模拟AI服务和规则基础测试生成都失败
            mock_ai_service.generate.side_effect = Exception("AI service failure")
            with patch.object(self.generator, '_rule_based_test_generation', side_effect=Exception("Rule-based generation failure")):
                result = self.generator.generate_test_cases(structured_data, tech_doc)
                assert result['version'] == '1.0'
                assert len(result['test_cases']) > 0

    def test_prepare_prompt(self):
        """测试准备提示词"""
        # 测试数据
        structured_data = {
            'requirements': ['Requirement 1', 'Requirement 2'],
            'constraints': ['Constraint 1', 'Constraint 2']
        }
        tech_doc = {
            'core_modules': ['Module 1', 'Module 2'],
            'interface_design': {'content': 'Interface design'}
        }
        
        # 执行准备提示词
        prompt = self.generator._prepare_prompt(structured_data, tech_doc)
        
        # 验证结果
        assert 'Requirement 1' in prompt
        assert 'Requirement 2' in prompt
        assert 'Constraint 1' in prompt
        assert 'Constraint 2' in prompt
        assert 'Module 1' in prompt
        assert 'Module 2' in prompt
        assert 'Interface design' in prompt

    def test_rule_based_test_generation(self):
        """测试规则基础测试用例生成"""
        # 测试数据
        structured_data = {
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        tech_doc = {
            'core_modules': ['Module 1'],
            'interface_design': {'content': 'Interface design'}
        }
        
        # 执行规则基础测试用例生成
        result = self.generator._rule_based_test_generation(structured_data, tech_doc)
        
        # 验证结果
        assert 'User authentication' in result
        assert 'Data validation' in result
        assert 'Response time' in result
        assert 'Cross-browser support' in result
        assert 'Access control' in result

    def test_structure_test_cases(self):
        """测试结构化测试用例"""
        # 测试数据
        content = "Test Case 1. User Authentication Test\nType: functional\nSteps: 1. Navigate to login page\nExpected results: User should be logged in\nPriority: high\nEnvironment: Any browser\n"
        structured_data = {
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        tech_doc = {
            'core_modules': ['Module 1'],
            'interface_design': {'content': 'Interface design'}
        }
        
        # 执行结构化
        result = self.generator._structure_test_cases(content, structured_data, tech_doc)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert len(result['test_cases']) == 1
        test_case = result['test_cases'][0]
        assert test_case['id'] == 'Test Case 1'
        assert test_case['name'] == 'User Authentication Test'
        assert test_case['type'] == 'functional'
        assert test_case['priority'] == 'high'
        assert test_case['environment'] == 'Any browser'

    def test_structure_test_cases_no_cases(self):
        """测试无测试用例时的处理"""
        # 测试数据
        content = ""
        structured_data = {
            'requirements': ['Requirement 1'],
            'constraints': ['Constraint 1']
        }
        tech_doc = {
            'core_modules': ['Module 1'],
            'interface_design': {'content': 'Interface design'}
        }
        
        # 执行结构化
        result = self.generator._structure_test_cases(content, structured_data, tech_doc)
        
        # 验证结果
        assert len(result['test_cases']) > 0  # 应该添加默认测试用例

    def test_get_default_test_cases_list(self):
        """测试获取默认测试用例列表"""
        # 执行获取默认测试用例列表
        test_cases = self.generator._get_default_test_cases_list()
        
        # 验证结果
        assert len(test_cases) == 5
        assert test_cases[0]['name'] == 'User Authentication Test'
        assert test_cases[1]['name'] == 'Data Validation Test'
        assert test_cases[2]['name'] == 'Performance Load Test'
        assert test_cases[3]['name'] == 'Cross-Browser Compatibility Test'
        assert test_cases[4]['name'] == 'Security Access Control Test'

    def test_get_default_test_cases(self):
        """测试获取默认测试用例结构"""
        # 执行获取默认测试用例结构
        result = self.generator._get_default_test_cases()
        
        # 验证结果
        assert result['version'] == '1.0'
        assert len(result['test_cases']) == 5

    @patch('builtins.open', new_callable=mock_open)
    def test_export_to_json_success(self, mock_file):
        """测试成功导出测试用例为JSON"""
        # 测试数据
        test_cases = {
            'version': '1.0',
            'test_cases': [{'id': 1, 'name': 'Test case'}]
        }
        output_path = 'test_cases.json'
        
        # 执行导出
        result = self.generator.export_to_json(test_cases, output_path)
        
        # 验证结果
        assert result is True
        mock_file.assert_called_once_with(output_path, 'w', encoding='utf-8')

    @patch('builtins.open', new_callable=mock_open)
    def test_export_to_json_error(self, mock_file):
        """测试导出测试用例为JSON时的错误处理"""
        # 测试数据
        test_cases = {
            'version': '1.0',
            'test_cases': [{'id': 1, 'name': 'Test case'}]
        }
        output_path = 'test_cases.json'
        
        # 模拟文件写入异常
        mock_file.side_effect = Exception("File write error")
        
        # 执行导出
        result = self.generator.export_to_json(test_cases, output_path)
        
        # 验证结果
        assert result is False

    @patch('builtins.open', new_callable=mock_open)
    def test_export_to_xmind_success(self, mock_file):
        """测试成功导出测试用例为XMind"""
        # 测试数据
        test_cases = {
            'version': '1.0',
            'test_cases': [{
                'id': 1,
                'name': 'Test case',
                'type': 'functional',
                'steps': ['Step 1'],
                'expected_results': ['Result 1'],
                'priority': 'high',
                'environment': 'Test environment'
            }]
        }
        output_path = 'test_cases.xmind.json'
        
        # 执行导出
        result = self.generator.export_to_xmind(test_cases, output_path)
        
        # 验证结果
        assert result is True
        mock_file.assert_called_once_with(output_path, 'w', encoding='utf-8')

    @patch('builtins.open', new_callable=mock_open)
    def test_export_to_xmind_error(self, mock_file):
        """测试导出测试用例为XMind时的错误处理"""
        # 测试数据
        test_cases = {
            'version': '1.0',
            'test_cases': [{'id': 1, 'name': 'Test case'}]
        }
        output_path = 'test_cases.xmind.json'
        
        # 模拟文件写入异常
        mock_file.side_effect = Exception("File write error")
        
        # 执行导出
        result = self.generator.export_to_xmind(test_cases, output_path)
        
        # 验证结果
        assert result is False

if __name__ == "__main__":
    pytest.main([__file__])
