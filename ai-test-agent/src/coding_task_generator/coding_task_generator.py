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
            system_prompt = "You are an expert project manager specializing in software development. Your task is to break down technical documentation into actionable coding tasks."
            
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
        Break down the following technical documentation into actionable coding tasks:
        
        System Architecture:
        {architecture}
        
        Technology Stack:
        {tech_stack}
        
        Core Modules:
        {core_modules}
        
        Interface Design:
        {interface_design}
        
        For each task, provide:
        1. Task ID
        2. Task name
        3. Description
        4. Technical requirements
        5. Inputs/outputs
        6. Estimated time (hours) - should not exceed 8 hours per task
        7. Dependencies (if any)
        8. Priority
        
        The tasks should be granular enough to be completed in 8 hours or less, and should cover all aspects of the system implementation.
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
                # Parse task details
                if 'description' in line.lower() and 'technical' not in line.lower():
                    current_task['description'] = line.split(':', 1)[1].strip() if ':' in line else line
                elif 'technical' in line.lower() and 'requirements' in line.lower():
                    current_task['technical_requirements'] = line.split(':', 1)[1].strip() if ':' in line else line
                elif 'input' in line.lower() or 'output' in line.lower():
                    current_task['inputs_outputs'] = line.split(':', 1)[1].strip() if ':' in line else line
                elif 'time' in line.lower() or 'estimate' in line.lower():
                    try:
                        current_task['estimated_time'] = float(''.join(c for c in line if c.isdigit() or c == '.'))
                    except:
                        pass
                elif 'dependency' in line.lower():
                    dependencies = line.split(':', 1)[1].strip() if ':' in line else line
                    current_task['dependencies'] = [dep.strip() for dep in dependencies.split(',')]
                elif 'priority' in line.lower():
                    current_task['priority'] = line.split(':', 1)[1].strip().lower() if ':' in line else line.lower()
        
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
    
    def _get_default_task_list(self):
        """
        Get default task list
        """
        return [
            {
                'id': 1,
                'name': 'Set up project structure',
                'description': 'Create the basic project structure and install dependencies',
                'technical_requirements': 'Python, Flask, required libraries',
                'inputs_outputs': 'Input: project requirements, Output: project structure',
                'estimated_time': 2,
                'dependencies': [],
                'priority': 'high'
            },
            {
                'id': 2,
                'name': 'Implement core modules',
                'description': 'Develop the core functionality modules',
                'technical_requirements': 'Python, relevant libraries',
                'inputs_outputs': 'Input: module specifications, Output: implemented modules',
                'estimated_time': 8,
                'dependencies': [1],
                'priority': 'high'
            },
            {
                'id': 3,
                'name': 'Build API endpoints',
                'description': 'Create RESTful API endpoints',
                'technical_requirements': 'Flask-RESTful',
                'inputs_outputs': 'Input: API specifications, Output: API endpoints',
                'estimated_time': 6,
                'dependencies': [2],
                'priority': 'high'
            },
            {
                'id': 4,
                'name': 'Implement authentication',
                'description': 'Add user authentication and authorization',
                'technical_requirements': 'Flask-JWT-Extended',
                'inputs_outputs': 'Input: authentication requirements, Output: auth system',
                'estimated_time': 4,
                'dependencies': [3],
                'priority': 'medium'
            },
            {
                'id': 5,
                'name': 'Write tests',
                'description': 'Create unit and integration tests',
                'technical_requirements': 'pytest',
                'inputs_outputs': 'Input: codebase, Output: test suite',
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