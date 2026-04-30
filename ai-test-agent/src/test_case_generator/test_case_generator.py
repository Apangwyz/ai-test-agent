import os
from dotenv import load_dotenv
import logging
import json
from src.common.ai_service import ai_service

# Load environment variables
load_dotenv()

class TestCaseGenerator:
    def __init__(self):
        self.model_type = os.getenv('AI_MODEL_TYPE', 'qwen')  # Default to Qwen
        self.logger = logging.getLogger(__name__)
    
    def generate_test_cases(self, structured_data, tech_doc):
        """
        Generate test cases based on requirements and technical documentation
        """
        try:
            # Prepare prompt for AI model
            prompt = self._prepare_prompt(structured_data, tech_doc)
            system_prompt = "你是一位专业的QA工程师，专注于软件测试。你的任务是根据需求和技术文档创建全面的测试案例。请用中文回答。"
            
            try:
                # Use AI service for advanced test case generation
                test_cases_content = ai_service.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model_type=self.model_type,
                    temperature=0.3
                )
            except Exception as e:
                self.logger.warning(f"AI service failed, falling back to rule-based test case generation: {e}")
                # Fallback to rule-based test case generation
                test_cases_content = self._rule_based_test_generation(structured_data, tech_doc)
            
            # Structure the test cases
            test_cases = self._structure_test_cases(test_cases_content, structured_data, tech_doc)
            return test_cases
            
        except Exception as e:
            self.logger.error(f"Error generating test cases: {e}")
            # Return basic test cases structure in case of error
            return self._get_default_test_cases()
    
    def _prepare_prompt(self, structured_data, tech_doc):
        """
        Prepare prompt for AI model
        """
        # Extract relevant information
        requirements = '\n'.join(structured_data.get('requirements', []))
        constraints = '\n'.join(structured_data.get('constraints', []))
        core_modules = '\n'.join(tech_doc.get('core_modules', []))
        interface_design = tech_doc.get('interface_design', {}).get('content', '')
        
        prompt = f"""
        为以下软件系统创建全面的测试案例：
        
        功能需求：
        {requirements}
        
        约束条件：
        {constraints}
        
        核心模块：
        {core_modules}
        
        接口设计：
        {interface_design}
        
        生成涵盖以下类型的测试案例：
        1. 功能测试
        2. 性能测试
        3. 兼容性测试
        4. 安全测试
        
        每个测试案例请提供：
        1. 测试案例ID
        2. 测试案例名称
        3. 测试类型（功能/性能/兼容性/安全）
        4. 测试步骤
        5. 预期结果
        6. 优先级（高/中/低）
        7. 测试环境要求
        
        确保测试案例全面，覆盖所有关键功能。
        """
        return prompt
    
    def _rule_based_test_generation(self, structured_data, tech_doc):
        """
        Rule-based test case generation (fallback)
        """
        test_cases = [
            "1. Functional Test: User authentication",
            "2. Functional Test: Data validation",
            "3. Performance Test: Response time",
            "4. Compatibility Test: Cross-browser support",
            "5. Security Test: Access control",
            "6. Functional Test: Core feature functionality",
            "7. Performance Test: Load testing",
            "8. Compatibility Test: Cross-device support",
            "9. Security Test: Input validation",
            "10. Functional Test: Error handling"
        ]
        
        return '\n'.join(test_cases)
    
    def _structure_test_cases(self, content, structured_data, tech_doc):
        """
        Structure the test cases into a standardized format
        """
        test_cases = {
            'version': '1.0',
            'timestamp': os.path.getmtime(__file__),
            'test_cases': []
        }
        
        # Parse content into structured test cases
        lines = content.split('\n')
        current_test = None
        valid_tests_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for test case ID - more flexible pattern
            is_test_case_start = (
                line.startswith('Test Case') or 
                line.startswith('1.') or 
                line.startswith('2.') or 
                line.startswith('3.') or 
                line.startswith('4.') or 
                line.startswith('5.') or
                line.startswith('### 1.') or
                line.startswith('### 2.') or
                line.startswith('### 3.') or
                line.startswith('### 4.') or
                line.startswith('### 5.')
            )
            
            if is_test_case_start:
                if current_test and current_test.get('name'):
                    # Only add test if it has a valid name
                    test_cases['test_cases'].append(current_test)
                    valid_tests_count += 1
                
                # Extract test case name
                test_name = line
                # Clean up the name
                if '###' in test_name:
                    test_name = test_name.replace('###', '').strip()
                if '.' in test_name and len(test_name.split('.')[0].strip()) <= 3:
                    test_name = '.'.join(test_name.split('.')[1:]).strip()
                
                # Skip invalid test names that don't look like real test cases
                skip_keywords = ['诊断', '说明', '模板', '框架', '填充', '计划', '填充需求', '计划']
                if any(kw in test_name for kw in skip_keywords):
                    current_test = None
                    continue
                
                current_test = {
                    'id': len(test_cases['test_cases']) + 1,
                    'name': test_name,
                    'type': 'functional',
                    'steps': [],
                    'expected_results': [],
                    'priority': 'medium',
                    'environment': '标准测试环境'
                }
            elif current_test:
                # Parse test case details - support both English and Chinese keywords
                if 'type' in line.lower() or '类型' in line:
                    type_value = line.split(':', 1)[1].strip() if ':' in line else line
                    current_test['type'] = self._normalize_test_type(type_value)
                elif ('step' in line.lower() and 's' in line.lower()) or '步骤' in line:
                    # Extract test steps - handle steps that don't have colon
                    step_text = line
                    if ':' in line:
                        step_text = line.split(':', 1)[1].strip()
                    if step_text and not any(kw in step_text.lower() for kw in ['step', '步骤']):
                        current_test['steps'].append(step_text)
                elif ('expected' in line.lower() and 'result' in line.lower()) or '预期结果' in line:
                    # Extract expected results
                    result_text = line
                    if ':' in line:
                        result_text = line.split(':', 1)[1].strip()
                    if result_text and not any(kw in result_text.lower() for kw in ['expected', '预期']):
                        current_test['expected_results'].append(result_text)
                elif 'priority' in line.lower() or '优先级' in line:
                    priority_value = line.split(':', 1)[1].strip() if ':' in line else line
                    current_test['priority'] = self._normalize_priority(priority_value)
                elif 'environment' in line.lower() or '环境' in line:
                    env_text = line.split(':', 1)[1].strip() if ':' in line else line
                    # Translate common English environments to Chinese
                    env_translations = {
                        'Any browser': '任何浏览器',
                        'Multiple browsers': '多种浏览器',
                        'Performance testing environment': '性能测试环境',
                        'Standard test environment': '标准测试环境'
                    }
                    current_test['environment'] = env_translations.get(env_text, env_text)
                else:
                    # If it's a line without a keyword, add to steps if we're in a test
                    if current_test.get('name') and len(current_test.get('steps', [])) == 0:
                        # First content after test case is likely a step
                        if not any(kw in line.lower() for kw in ['type', '优先级', '环境', 'step', 'expected']):
                            current_test['steps'].append(line)
        
        # Add the last valid test case
        if current_test and current_test.get('name'):
            test_cases['test_cases'].append(current_test)
            valid_tests_count += 1
        
        # Add default test cases if no valid tests found
        if valid_tests_count == 0:
            test_cases['test_cases'] = self._get_default_test_cases_list()
        
        return test_cases
    
    def _normalize_test_type(self, type_value):
        """
        Normalize test type to standard format
        Supports both English and Chinese test types
        """
        type_map = {
            'functional': 'functional',
            'performance': 'performance',
            'compatibility': 'compatibility',
            'security': 'security',
            '功能': 'functional',
            '性能': 'performance',
            '兼容': 'compatibility',
            '安全': 'security',
            '功能测试': 'functional',
            '性能测试': 'performance',
            '兼容性测试': 'compatibility',
            '安全测试': 'security'
        }
        return type_map.get(type_value.lower(), 'functional')
    
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
    
    def _get_default_test_cases_list(self):
        """
        Get default test cases list
        """
        return [
            {
                'id': 1,
                'name': '用户认证测试',
                'type': 'functional',
                'steps': [
                    '导航到登录页面',
                    '输入有效凭证',
                    '点击登录按钮'
                ],
                'expected_results': [
                    '用户应成功登录',
                    '用户应被重定向到仪表盘'
                ],
                'priority': 'high',
                'environment': '任何浏览器'
            },
            {
                'id': 2,
                'name': '数据验证测试',
                'type': 'functional',
                'steps': [
                    '导航到表单页面',
                    '输入无效数据',
                    '提交表单'
                ],
                'expected_results': [
                    '表单应显示验证错误',
                    '表单不应提交'
                ],
                'priority': 'medium',
                'environment': '任何浏览器'
            },
            {
                'id': 3,
                'name': '性能负载测试',
                'type': 'performance',
                'steps': [
                    '模拟100个并发用户',
                    '测量响应时间',
                    '监控系统资源'
                ],
                'expected_results': [
                    '响应时间应小于2秒',
                    '系统应保持稳定'
                ],
                'priority': 'medium',
                'environment': '性能测试环境'
            },
            {
                'id': 4,
                'name': '跨浏览器兼容性测试',
                'type': 'compatibility',
                'steps': [
                    '在Chrome中测试',
                    '在Firefox中测试',
                    '在Safari中测试'
                ],
                'expected_results': [
                    '应用应在所有浏览器中正常工作',
                    '不应存在视觉问题'
                ],
                'priority': 'medium',
                'environment': '多种浏览器'
            },
            {
                'id': 5,
                'name': '安全访问控制测试',
                'type': 'security',
                'steps': [
                    '尝试访问受限资源',
                    '验证访问被拒绝',
                    '使用有效凭证测试'
                ],
                'expected_results': [
                    '未授权访问应被阻止',
                    '授权用户应具有访问权限'
                ],
                'priority': 'high',
                'environment': '任何浏览器'
            }
        ]
    
    def _get_default_test_cases(self):
        """
        Get default test cases structure in case of error
        """
        return {
            'version': '1.0',
            'timestamp': os.path.getmtime(__file__),
            'test_cases': self._get_default_test_cases_list()
        }
    
    def export_to_json(self, test_cases, output_path):
        """
        Export test cases to JSON format
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(test_cases, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error exporting test cases to JSON: {e}")
            return False
    
    def export_to_xmind(self, test_cases, output_path):
        """
        Export test cases to XMind format (simplified)
        """
        try:
            # Create a simple XMind-compatible structure
            xmind_content = {
                'title': 'Test Cases',
                'children': []
            }
            
            # Group test cases by type
            test_cases_by_type = {}
            for test in test_cases['test_cases']:
                test_type = test['type']
                if test_type not in test_cases_by_type:
                    test_cases_by_type[test_type] = []
                test_cases_by_type[test_type].append(test)
            
            # Build the XMind structure
            for test_type, tests in test_cases_by_type.items():
                type_node = {
                    'title': test_type.capitalize(),
                    'children': []
                }
                
                for test in tests:
                    test_node = {
                        'title': f"{test['id']}. {test['name']}",
                        'children': [
                            {'title': 'Steps', 'children': [{'title': step} for step in test['steps']]},
                            {'title': 'Expected Results', 'children': [{'title': result} for result in test['expected_results']]},
                            {'title': f"Priority: {test['priority']}"},
                            {'title': f"Environment: {test['environment']}"}
                        ]
                    }
                    type_node['children'].append(test_node)
                
                xmind_content['children'].append(type_node)
            
            # Save as JSON (simplified XMind format)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(xmind_content, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self.logger.error(f"Error exporting test cases to XMind: {e}")
            return False
