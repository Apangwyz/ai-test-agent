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
            system_prompt = "You are an expert business analyst specializing in requirement analysis. Your task is to identify ambiguous points, conflicts, and missing information in software requirements."
            
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
        Analyze the following software requirements and identify:
        1. Ambiguous points that need clarification
        2. Conflicts between requirements
        3. Missing information that should be specified
        4. Business rules that need further definition
        
        Requirements sections:
        {sections}
        
        Functional requirements:
        {requirements}
        
        Constraints:
        {constraints}
        
        Please provide a comprehensive analysis with specific questions for each issue identified.
        """
        return prompt
    
    def _rule_based_analysis(self, structured_data):
        """
        Rule-based analysis for clarification (fallback)
        """
        issues = []
        
        # Check for common issues
        if not structured_data.get('requirements'):
            issues.append("No functional requirements identified")
        
        if not structured_data.get('constraints'):
            issues.append("No constraints or non-functional requirements identified")
        
        # Analyze requirements for ambiguity
        for req in structured_data.get('requirements', []):
            if 'should' in req.lower() or 'may' in req.lower():
                issues.append(f"Ambiguous requirement: {req}")
            if 'etc' in req.lower() or 'etc.' in req.lower():
                issues.append(f"Incomplete requirement: {req}")
        
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
        
        # Parse content into structured format
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'Ambiguous' in line or 'ambiguous' in line:
                current_section = 'ambiguous_points'
            elif 'Conflict' in line or 'conflict' in line:
                current_section = 'conflicts'
            elif 'Missing' in line or 'missing' in line:
                current_section = 'missing_information'
            elif 'Suggestion' in line or 'suggestion' in line:
                current_section = 'suggestions'
            elif current_section:
                clarification_doc[current_section].append(line)
        
        # Add default issues if none found
        if not any([clarification_doc['ambiguous_points'], clarification_doc['conflicts'], clarification_doc['missing_information']]):
            clarification_doc['suggestions'].append("No major issues identified. Please review requirements for completeness.")
        
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
            'suggestions': ["Error generating clarification. Please check your OpenAI API key and try again."]
        }