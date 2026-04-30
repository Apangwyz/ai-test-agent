import os
from dotenv import load_dotenv
import logging
import json
from src.common.ai_service import ai_service

# Load environment variables
load_dotenv()

class CodingTaskGenerator:
    def __init__(self):
        self.model_type = os.getenv('AI_MODEL_TYPE', 'qwen')  # Default to Qwen
        self.logger = logging.getLogger(__name__)
    
    def generate_tasks(self, tech_doc):
        """
        Generate coding tasks based on technical documentation
        """
        try:
            # Prepare prompt for AI model
            prompt = self._prepare_prompt(tech_doc)
            system_prompt = "你是一位专业的项目经理，专注于软件开发。你的任务是将技术文档分解为可执行的编码任务。请用中文回答。"
            
            try:
                # Use AI service for advanced task generation
                tasks_content = ai_service.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model_type=self.model_type,
                    temperature=0.3
                )
            except Exception as e:
                self.logger.warning(f"AI service failed, falling back to rule-based task generation: {e}")
                # Fallback to rule-based task generation
                tasks_content = self._rule_based_task_generation(tech_doc)
            
            # Structure the tasks
            tasks = self._structure_tasks(tasks_content, tech_doc)
            return tasks
            
        except Exception as e:
            self.logger.error(f"Error generating coding tasks: {e}")
            # Return basic tasks structure in case of error
            return self._get_default_tasks()
    
    def _prepare_prompt(self, tech_doc):
        """
        Prepare prompt for AI model
        """
        # Extract relevant information from tech doc
        architecture = tech_doc.get('architecture', {}).get('content', '')
        tech_stack = tech_doc.get('tech_stack', {}).get('content', '')
        core_modules = '\n'.join(tech_doc.get('core_modules', []))
        interface_design = tech_doc.get('interface_design', {}).get('content', '')
        
        prompt = f"""
        将以下技术文档分解为可执行的编码任务：
        
        系统架构：
        {architecture}
        
        技术栈：
        {tech_stack}
        
        核心模块：
        {core_modules}
        
        接口设计：
        {interface_design}
        
        每个任务请提供：
        1. 任务ID
        2. 任务名称
        3. 描述
        4. 技术要求
        5. 输入/输出
        6. 预估时间（小时）- 每个任务不应超过8小时
        7. 依赖关系（如有的话）
        8. 优先级
        
        任务应足够细化，能够在8小时或更短时间内完成，并涵盖系统实现的所有方面。
        """
        return prompt
    
    def _rule_based_task_generation(self, tech_doc):
        """
        Rule-based task generation (fallback)
        """
        tasks = [
            "1. Set up project structure and dependencies",
            "2. Implement core data models",
            "3. Develop API endpoints",
            "4. Implement authentication system",
            "5. Build frontend components",
            "6. Integrate frontend and backend",
            "7. Implement data validation",
            "8. Add error handling and logging",
            "9. Write unit tests",
            "10. Deploy the application"
        ]
        
        return '\n'.join(tasks)
    
    def _structure_tasks(self, content, tech_doc):
        """
        Structure the tasks into a standardized format
        """
        tasks = {
            'version': '1.0',
            'timestamp': os.path.getmtime(__file__),
            'tasks': []
        }
        
        # Parse content into structured tasks
        lines = content.split('\n')
        current_task = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for task ID
            if line.startswith('Task') or line.startswith('1.') or line.startswith('2.'):
                if current_task:
                    tasks['tasks'].append(current_task)
                current_task = {
                    'id': line.split('.')[0] if '.' in line else len(tasks['tasks']) + 1,
                    'name': line.split('.')[1].strip() if '.' in line else line,
                    'description': '',
                    'technical_requirements': '',
                    'inputs_outputs': '',
                    'estimated_time': 4,  # Default estimate
                    'dependencies': [],
                    'priority': 'medium'
                }
            elif current_task:
                # Parse task details - support both English and Chinese keywords
                if ('description' in line.lower() or '描述' in line) and 'technical' not in line.lower() and '技术' not in line:
                    current_task['description'] = line.split(':', 1)[1].strip() if ':' in line else line
                elif ('technical' in line.lower() or '技术' in line) and ('requirements' in line.lower() or '要求' in line):
                    current_task['technical_requirements'] = line.split(':', 1)[1].strip() if ':' in line else line
                elif 'input' in line.lower() or 'output' in line.lower() or '输入' in line or '输出' in line:
                    current_task['inputs_outputs'] = line.split(':', 1)[1].strip() if ':' in line else line
                elif 'time' in line.lower() or 'estimate' in line.lower() or '时间' in line or '预估' in line:
                    try:
                        current_task['estimated_time'] = float(''.join(c for c in line if c.isdigit() or c == '.'))
                    except:
                        pass
                elif 'dependency' in line.lower() or '依赖' in line:
                    dependencies = line.split(':', 1)[1].strip() if ':' in line else line
                    current_task['dependencies'] = [dep.strip() for dep in dependencies.split(',')]
                elif 'priority' in line.lower() or '优先级' in line:
                    priority_value = line.split(':', 1)[1].strip() if ':' in line else line
                    current_task['priority'] = self._normalize_priority(priority_value)
        
        # Add the last task
        if current_task:
            tasks['tasks'].append(current_task)
        
        # Ensure all tasks have reasonable estimates
        for task in tasks['tasks']:
            if task['estimated_time'] > 8:
                task['estimated_time'] = 8
            elif task['estimated_time'] < 1:
                task['estimated_time'] = 1
        
        # Add default tasks if none found
        if not tasks['tasks']:
            tasks['tasks'] = self._get_default_task_list()
        
        return tasks
    
    def _normalize_priority(self, priority_value):
        """
        Normalize priority value to standard format (high/medium/low)
        Supports both English and Chinese priority values
        """
        priority_map = {
            'high': 'high',
            'medium': 'medium',
            'low': 'low',
            '高': 'high',
            '中': 'medium',
            '低': 'low',
            '高级': 'high',
            '中级': 'medium',
            '低级': 'low',
            '高优先级': 'high',
            '中优先级': 'medium',
            '低优先级': 'low'
        }
        return priority_map.get(priority_value.lower(), 'medium')
    
    def _get_default_task_list(self):
        """
        Get default task list
        """
        return [
            {
                'id': 1,
                'name': '项目结构搭建',
                'description': '创建基础项目结构并安装依赖',
                'technical_requirements': 'Python, Flask, 所需库',
                'inputs_outputs': '输入: 项目需求, 输出: 项目结构',
                'estimated_time': 2,
                'dependencies': [],
                'priority': 'high'
            },
            {
                'id': 2,
                'name': '核心模块实现',
                'description': '开发核心功能模块',
                'technical_requirements': 'Python, 相关库',
                'inputs_outputs': '输入: 模块规格, 输出: 已实现模块',
                'estimated_time': 8,
                'dependencies': [1],
                'priority': 'high'
            },
            {
                'id': 3,
                'name': 'API端点开发',
                'description': '创建RESTful API端点',
                'technical_requirements': 'Flask-RESTful',
                'inputs_outputs': '输入: API规格, 输出: API端点',
                'estimated_time': 6,
                'dependencies': [2],
                'priority': 'high'
            },
            {
                'id': 4,
                'name': '认证系统实现',
                'description': '添加用户认证和授权功能',
                'technical_requirements': 'Flask-JWT-Extended',
                'inputs_outputs': '输入: 认证需求, 输出: 认证系统',
                'estimated_time': 4,
                'dependencies': [3],
                'priority': 'medium'
            },
            {
                'id': 5,
                'name': '测试用例编写',
                'description': '创建单元测试和集成测试',
                'technical_requirements': 'pytest',
                'inputs_outputs': '输入: 代码库, 输出: 测试套件',
                'estimated_time': 6,
                'dependencies': [4],
                'priority': 'medium'
            }
        ]
    
    def _get_default_tasks(self):
        """
        Get default tasks structure in case of error
        """
        return {
            'version': '1.0',
            'timestamp': os.path.getmtime(__file__),
            'tasks': self._get_default_task_list()
        }
    
    def export_to_json(self, tasks, output_path):
        """
        Export tasks to JSON format
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error exporting tasks to JSON: {e}")
            return False