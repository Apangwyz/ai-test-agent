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
            system_prompt = "You are an expert QA engineer specializing in software testing. Your task is to create comprehensive test cases based on requirements and technical documentation."
            
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
        Create comprehensive test cases for the following software system:
        
        Functional Requirements:
        {requirements}
        
        Constraints:
        {constraints}
        
        Core Modules:
        {core_modules}
        
        Interface Design:
        {interface_design}
        
        Generate test cases covering:
        1. Functional testing
        2. Performance testing
        3. Compatibility testing
        4. Security testing
        
        For each test case, provide:
        1. Test case ID
        2. Test case name
        3. Test type (functional/performance/compatibility/security)
        4. Test steps
        5. Expected results
        6. Priority (high/medium/low)
        7. Test environment requirements
        
        Ensure test cases are comprehensive and cover all critical functionality.
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
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for test case ID
            if line.startswith('Test Case') or line.startswith('1.') or line.startswith('2.'):
                if current_test:
                    test_cases['test_cases'].append(current_test)
                current_test = {
                    'id': line.split('.')[0] if '.' in line else len(test_cases['test_cases']) + 1,
                    'name': line.split('.')[1].strip() if '.' in line else line,
                    'type': 'functional',  # Default type
                    'steps': [],
                    'expected_results': [],
                    'priority': 'medium',  # Default priority
                    'environment': 'Standard test environment'
                }
            elif current_test:
                # Parse test case details
                if 'type' in line.lower():
                    current_test['type'] = line.split(':', 1)[1].strip().lower() if ':' in line else line.lower()
                elif 'step' in line.lower() and 's' in line.lower():
                    # Extract test steps
                    if 'steps' not in current_test:
                        current_test['steps'] = []
                    step_text = line.split(':', 1)[1].strip() if ':' in line else line
                    current_test['steps'].append(step_text)
                elif 'expected' in line.lower() and 'result' in line.lower():
                    # Extract expected results
                    if 'expected_results' not in current_test:
                        current_test['expected_results'] = []
                    result_text = line.split(':', 1)[1].strip() if ':' in line else line
                    current_test['expected_results'].append(result_text)
                elif 'priority' in line.lower():
                    current_test['priority'] = line.split(':', 1)[1].strip().lower() if ':' in line else line.lower()
                elif 'environment' in line.lower():
                    current_test['environment'] = line.split(':', 1)[1].strip() if ':' in line else line
        
        # Add the last test case
        if current_test:
            test_cases['test_cases'].append(current_test)
        
        # Add default test cases if none found
        if not test_cases['test_cases']:
            test_cases['test_cases'] = self._get_default_test_cases_list()
        
        return test_cases
    
    def _get_default_test_cases_list(self):
        """
        Get default test cases list
        """
        return [
            {
                'id': 1,
                'name': 'User Authentication Test',
                'type': 'functional',
                'steps': [
                    'Navigate to login page',
                    'Enter valid credentials',
                    'Click login button'
                ],
                'expected_results': [
                    'User should be successfully logged in',
                    'User should be redirected to dashboard'
                ],
                'priority': 'high',
                'environment': 'Any browser'
            },
            {
                'id': 2,
                'name': 'Data Validation Test',
                'type': 'functional',
                'steps': [
                    'Navigate to form page',
                    'Enter invalid data',
                    'Submit form'
                ],
                'expected_results': [
                    'Form should display validation errors',
                    'Form should not submit'
                ],
                'priority': 'medium',
                'environment': 'Any browser'
            },
            {
                'id': 3,
                'name': 'Performance Load Test',
                'type': 'performance',
                'steps': [
                    'Simulate 100 concurrent users',
                    'Measure response time',
                    'Monitor system resources'
                ],
                'expected_results': [
                    'Response time should be < 2 seconds',
                    'System should remain stable'
                ],
                'priority': 'medium',
                'environment': 'Performance testing environment'
            },
            {
                'id': 4,
                'name': 'Cross-Browser Compatibility Test',
                'type': 'compatibility',
                'steps': [
                    'Test in Chrome',
                    'Test in Firefox',
                    'Test in Safari'
                ],
                'expected_results': [
                    'Application should work correctly in all browsers',
                    'No visual issues should be present'
                ],
                'priority': 'medium',
                'environment': 'Multiple browsers'
            },
            {
                'id': 5,
                'name': 'Security Access Control Test',
                'type': 'security',
                'steps': [
                    'Attempt to access restricted resource',
                    'Verify access is denied',
                    'Test with valid credentials'
                ],
                'expected_results': [
                    'Unauthorized access should be blocked',
                    'Authorized users should have access'
                ],
                'priority': 'high',
                'environment': 'Any browser'
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