import os
from dotenv import load_dotenv
import logging
from src.common.ai_service import ai_service

# Load environment variables
load_dotenv()

class ClarificationGenerator:
    def __init__(self):
        self.model_type = os.getenv('AI_MODEL_TYPE', 'qwen')  # Default to Qwen
        self.logger = logging.getLogger(__name__)
    
    def generate_clarification(self, structured_data):
        """
        Generate clarification document based on structured requirements data
        """
        try:
            # Prepare prompt for AI model
            prompt = self._prepare_prompt(structured_data)
            system_prompt = "你是一位专业的业务分析师，专注于需求分析。你的任务是识别软件需求中的模糊点、冲突和缺失信息。请用中文回答。"
            
            try:
                # Use AI service for advanced analysis
                clarification_content = ai_service.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model_type=self.model_type,
                    temperature=0.3
                )
            except Exception as e:
                self.logger.warning(f"AI service failed, falling back to rule-based analysis: {e}")
                # Fallback to rule-based analysis
                clarification_content = self._rule_based_analysis(structured_data)
            
            # Structure the clarification document
            clarification_doc = self._structure_clarification(clarification_content, structured_data)
            return clarification_doc
            
        except Exception as e:
            self.logger.error(f"Error generating clarification: {e}")
            # Return basic clarification structure in case of error
            return self._get_default_clarification(structured_data)
    
    def _prepare_prompt(self, structured_data):
        """
        Prepare prompt for AI model
        """
        sections = '\n'.join(structured_data.get('sections', []))
        requirements = '\n'.join(structured_data.get('requirements', []))
        constraints = '\n'.join(structured_data.get('constraints', []))
        
        prompt = f"""
        请分析以下软件需求并识别：
        1. 需要澄清的模糊点
        2. 需求之间的冲突
        3. 需要明确的缺失信息
        4. 需要进一步定义的业务规则
        
        需求章节：
        {sections}
        
        功能需求：
        {requirements}
        
        约束条件：
        {constraints}
        
        请提供全面的分析，针对每个发现的问题提出具体的问题。
        """
        return prompt
    
    def _rule_based_analysis(self, structured_data):
        """
        Rule-based analysis for clarification (fallback)
        """
        issues = []
        
        # 检查常见问题
        if not structured_data.get('requirements'):
            issues.append("未识别到功能需求")
        
        if not structured_data.get('constraints'):
            issues.append("未识别到约束条件或非功能需求")
        
        # 分析需求中的模糊性
        for req in structured_data.get('requirements', []):
            if '应' in req or '可' in req:
                issues.append(f"模糊需求: {req}")
            if '等等' in req or '等' in req:
                issues.append(f"不完整需求: {req}")
        
        return '\n'.join(issues)
    
    def _structure_clarification(self, content, structured_data):
        """
        Structure the clarification document
        """
        clarification_doc = {
            'version': '1.0',
            'timestamp': os.path.getmtime(__file__),
            'ambiguous_points': [],
            'conflicts': [],
            'missing_information': [],
            'suggestions': []
        }
        
        # 解析内容为结构化格式
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if '模糊' in line or 'Ambiguous' in line or 'ambiguous' in line:
                current_section = 'ambiguous_points'
            elif '冲突' in line or 'Conflict' in line or 'conflict' in line:
                current_section = 'conflicts'
            elif '缺失' in line or 'Missing' in line or 'missing' in line:
                current_section = 'missing_information'
            elif '建议' in line or 'Suggestion' in line or 'suggestion' in line:
                current_section = 'suggestions'
            elif current_section:
                clarification_doc[current_section].append(line)
        
        # 如果没有找到问题，添加默认提示
        if not any([clarification_doc['ambiguous_points'], clarification_doc['conflicts'], clarification_doc['missing_information']]):
            clarification_doc['suggestions'].append("未识别到重大问题。请检查需求的完整性。")
        
        return clarification_doc
    
    def _get_default_clarification(self, structured_data):
        """
        Get default clarification structure in case of error
        """
        return {
            'version': '1.0',
            'timestamp': os.path.getmtime(__file__),
            'ambiguous_points': [],
            'conflicts': [],
            'missing_information': [],
            'suggestions': ["生成需求澄清文档时出错。请检查您的API密钥并重试。"]
        }