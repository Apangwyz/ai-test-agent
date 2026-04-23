import pytest
from unittest.mock import Mock, patch, mock_open
from src.coding_task_generator.coding_task_generator import CodingTaskGenerator

class TestCodingTaskGenerator:
    """测试编码任务生成器"""

    def setup_method(self):
        """设置测试环境"""
        self.generator = CodingTaskGenerator()

    @patch('src.coding_task_generator.coding_task_generator.ai_service')
    def test_generate_tasks_success(self, mock_ai_service):
        """测试成功生成编码任务"""
        # 模拟AI服务返回
        mock_ai_service.generate.return_value = "Task 1. Set up project structure\nDescription: Create project structure\nTechnical requirements: Python, Flask\nEstimated time: 2 hours\n"
        
        # 测试数据
        tech_doc = {
            'architecture': {'content': 'System architecture'},
            'tech_stack': {'content': 'Python, Flask'},
            'core_modules': ['Module 1', 'Module 2'],
            'interface_design': {'content': 'RESTful API'}
        }
        
        # 执行生成
        result = self.generator.generate_tasks(tech_doc)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert 'tasks' in result
        assert len(result['tasks']) > 0
        mock_ai_service.generate.assert_called_once()

    @patch('src.coding_task_generator.coding_task_generator.ai_service')
    def test_generate_tasks_ai_failure(self, mock_ai_service):
        """测试AI服务失败时的回退机制"""
        # 模拟AI服务抛出异常
        mock_ai_service.generate.side_effect = Exception("AI service failure")
        
        # 测试数据
        tech_doc = {
            'architecture': {'content': 'System architecture'},
            'tech_stack': {'content': 'Python, Flask'},
            'core_modules': ['Module 1', 'Module 2'],
            'interface_design': {'content': 'RESTful API'}
        }
        
        # 执行生成
        result = self.generator.generate_tasks(tech_doc)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert 'tasks' in result
        assert len(result['tasks']) > 0

    def test_generate_tasks_error(self):
        """测试生成编码任务时的错误处理"""
        # 测试数据
        tech_doc = {
            'architecture': {'content': 'System architecture'},
            'tech_stack': {'content': 'Python, Flask'},
            'core_modules': ['Module 1', 'Module 2'],
            'interface_design': {'content': 'RESTful API'}
        }
        
        # 模拟异常
        with patch('src.coding_task_generator.coding_task_generator.ai_service') as mock_ai_service:
            # 模拟AI服务和规则基础任务生成都失败
            mock_ai_service.generate.side_effect = Exception("AI service failure")
            with patch.object(self.generator, '_rule_based_task_generation', side_effect=Exception("Rule-based generation failure")):
                result = self.generator.generate_tasks(tech_doc)
                assert result['version'] == '1.0'
                assert len(result['tasks']) > 0

    def test_prepare_prompt(self):
        """测试准备提示词"""
        # 测试数据
        tech_doc = {
            'architecture': {'content': 'System architecture'},
            'tech_stack': {'content': 'Python, Flask'},
            'core_modules': ['Module 1', 'Module 2'],
            'interface_design': {'content': 'RESTful API'}
        }
        
        # 执行准备提示词
        prompt = self.generator._prepare_prompt(tech_doc)
        
        # 验证结果
        assert 'System architecture' in prompt
        assert 'Python, Flask' in prompt
        assert 'Module 1' in prompt
        assert 'Module 2' in prompt
        assert 'RESTful API' in prompt

    def test_rule_based_task_generation(self):
        """测试规则基础任务生成"""
        # 测试数据
        tech_doc = {
            'architecture': {'content': 'System architecture'},
            'tech_stack': {'content': 'Python, Flask'},
            'core_modules': ['Module 1', 'Module 2'],
            'interface_design': {'content': 'RESTful API'}
        }
        
        # 执行规则基础任务生成
        result = self.generator._rule_based_task_generation(tech_doc)
        
        # 验证结果
        assert 'Set up project structure' in result
        assert 'Implement core data models' in result
        assert 'Develop API endpoints' in result

    def test_structure_tasks(self):
        """测试结构化任务"""
        # 测试数据
        content = "Task 1. Set up project structure\nDescription: Create project structure\nTechnical requirements: Python, Flask\nEstimated time: 2 hours\nDependencies: None\nPriority: high\n"
        tech_doc = {
            'architecture': {'content': 'System architecture'},
            'tech_stack': {'content': 'Python, Flask'},
            'core_modules': ['Module 1', 'Module 2'],
            'interface_design': {'content': 'RESTful API'}
        }
        
        # 执行结构化
        result = self.generator._structure_tasks(content, tech_doc)
        
        # 验证结果
        assert result['version'] == '1.0'
        assert len(result['tasks']) == 1
        task = result['tasks'][0]
        assert task['id'] == 'Task 1'
        assert task['name'] == 'Set up project structure'
        assert task['description'] == 'Create project structure'
        assert task['technical_requirements'] == 'Python, Flask'
        assert task['estimated_time'] == 2
        assert task['priority'] == 'high'

    def test_structure_tasks_time_validation(self):
        """测试任务时间验证"""
        # 测试数据
        content = "Task 1. Test task\nEstimated time: 10 hours\n"
        tech_doc = {
            'architecture': {'content': 'System architecture'},
            'tech_stack': {'content': 'Python, Flask'},
            'core_modules': ['Module 1', 'Module 2'],
            'interface_design': {'content': 'RESTful API'}
        }
        
        # 执行结构化
        result = self.generator._structure_tasks(content, tech_doc)
        
        # 验证结果
        assert result['tasks'][0]['estimated_time'] == 8  # 超过8小时会被限制

    def test_structure_tasks_no_tasks(self):
        """测试无任务时的处理"""
        # 测试数据
        content = ""
        tech_doc = {
            'architecture': {'content': 'System architecture'},
            'tech_stack': {'content': 'Python, Flask'},
            'core_modules': ['Module 1', 'Module 2'],
            'interface_design': {'content': 'RESTful API'}
        }
        
        # 执行结构化
        result = self.generator._structure_tasks(content, tech_doc)
        
        # 验证结果
        assert len(result['tasks']) > 0  # 应该添加默认任务

    def test_get_default_task_list(self):
        """测试获取默认任务列表"""
        # 执行获取默认任务列表
        tasks = self.generator._get_default_task_list()
        
        # 验证结果
        assert len(tasks) == 5
        assert tasks[0]['name'] == 'Set up project structure'
        assert tasks[1]['name'] == 'Implement core modules'
        assert tasks[2]['name'] == 'Build API endpoints'
        assert tasks[3]['name'] == 'Implement authentication'
        assert tasks[4]['name'] == 'Write tests'

    def test_get_default_tasks(self):
        """测试获取默认任务结构"""
        # 执行获取默认任务结构
        result = self.generator._get_default_tasks()
        
        # 验证结果
        assert result['version'] == '1.0'
        assert len(result['tasks']) == 5

    @patch('builtins.open', new_callable=mock_open)
    def test_export_to_json_success(self, mock_file):
        """测试成功导出任务为JSON"""
        # 测试数据
        tasks = {
            'version': '1.0',
            'tasks': [{'id': 1, 'name': 'Test task'}]
        }
        output_path = 'test_tasks.json'
        
        # 执行导出
        result = self.generator.export_to_json(tasks, output_path)
        
        # 验证结果
        assert result is True
        mock_file.assert_called_once_with(output_path, 'w', encoding='utf-8')

    @patch('builtins.open', new_callable=mock_open)
    def test_export_to_json_error(self, mock_file):
        """测试导出任务为JSON时的错误处理"""
        # 测试数据
        tasks = {
            'version': '1.0',
            'tasks': [{'id': 1, 'name': 'Test task'}]
        }
        output_path = 'test_tasks.json'
        
        # 模拟文件写入异常
        mock_file.side_effect = Exception("File write error")
        
        # 执行导出
        result = self.generator.export_to_json(tasks, output_path)
        
        # 验证结果
        assert result is False

if __name__ == "__main__":
    pytest.main([__file__])
