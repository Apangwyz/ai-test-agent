import os
from dotenv import load_dotenv
import logging
from src.common.ai_service import ai_service

# Load environment variables
load_dotenv()

class TechDocGenerator:
    def __init__(self):
        self.model_type = os.getenv('AI_MODEL_TYPE', 'qwen')  # Default to Qwen
        self.logger = logging.getLogger(__name__)
    
    def generate_tech_doc(self, structured_data, clarification_doc=None):
        """
        Generate technical documentation based on structured requirements
        """
        try:
            # Prepare prompt for AI model
            prompt = self._prepare_prompt(structured_data, clarification_doc)
            system_prompt = "You are an expert solution architect specializing in software design. Your task is to create comprehensive technical documentation based on software requirements."
            
            try:
                # Use AI service for advanced analysis
                tech_doc_content = ai_service.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model_type=self.model_type,
                    temperature=0.3
                )
            except Exception as e:
                self.logger.warning(f"AI service failed, falling back to rule-based generation: {e}")
                # Fallback to rule-based generation
                tech_doc_content = self._rule_based_generation(structured_data)
            
            # Structure the technical document
            tech_doc = self._structure_tech_doc(tech_doc_content, structured_data)
            return tech_doc
            
        except Exception as e:
            self.logger.error(f"Error generating technical document: {e}")
            # Return basic technical document structure in case of error
            return self._get_default_tech_doc(structured_data)
    
    def _prepare_prompt(self, structured_data, clarification_doc):
        """
        Prepare prompt for AI model
        """
        sections = '\n'.join(structured_data.get('sections', []))
        requirements = '\n'.join(structured_data.get('requirements', []))
        constraints = '\n'.join(structured_data.get('constraints', []))
        
        clarification_notes = ''
        if clarification_doc:
            clarification_items = [item for section in clarification_doc.values() if isinstance(section, list) for item in section]
            joined_items = '\n'.join(clarification_items)
            clarification_notes = f"Clarification notes:\n{joined_items}"
        
        prompt = f"""
        Create a comprehensive technical documentation for a software system based on the following requirements:
        
        Requirements sections:
        {sections}
        
        Functional requirements:
        {requirements}
        
        Constraints:
        {constraints}
        
        {clarification_notes}
        
        The technical documentation should include:
        1. System architecture design with diagrams
        2. Technology stack selection with comparison analysis
        3. Core module breakdown
        4. Interface design specifications
        5. Data flow design
        6. Key technical challenges and solutions
        7. Implementation approach
        8. Deployment strategy
        
        Please provide detailed, professional, and actionable technical documentation that follows industry best practices.
        """
        return prompt
    
    def _rule_based_generation(self, structured_data):
        """
        Rule-based technical document generation (fallback)
        """
        sections = [
            "# Technical Documentation",
            "## System Architecture",
            "### High-level Architecture",
            "### Component Diagram",
            "## Technology Stack",
            "### Backend",
            "### Frontend",
            "### Database",
            "## Core Modules",
            "## Interface Design",
            "## Data Flow",
            "## Technical Challenges",
            "## Implementation Plan",
            "## Deployment Strategy"
        ]
        
        return '\n\n'.join(sections)
    
    def _structure_tech_doc(self, content, structured_data):
        """
        Structure the technical document
        """
        tech_doc = {
            'version': '1.0',
            'timestamp': os.path.getmtime(__file__),
            'architecture': {},
            'tech_stack': {},
            'core_modules': [],
            'interface_design': {},
            'data_flow': {},
            'challenges': [],
            'implementation': {},
            'deployment': {}
        }
        
        # Parse content into structured format
        lines = content.split('\n')
        current_section = None
        
        section_mapping = {
            'architecture': ['architecture', 'system design'],
            'tech_stack': ['technology', 'tech stack', 'tech选型'],
            'core_modules': ['core modules', 'modules', 'components'],
            'interface_design': ['interface', 'api', '接口'],
            'data_flow': ['data flow', '数据流'],
            'challenges': ['challenges', '技术难点'],
            'implementation': ['implementation', '开发计划'],
            'deployment': ['deployment', '部署']
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            for section_key, keywords in section_mapping.items():
                if any(keyword.lower() in line.lower() for keyword in keywords):
                    current_section = section_key
                    break
            
            if current_section:
                if current_section in ['core_modules', 'challenges']:
                    if line and not line.startswith('#'):
                        tech_doc[current_section].append(line)
                else:
                    if 'tech_doc[current_section]' not in locals():
                        tech_doc[current_section] = {}
                    tech_doc[current_section]['content'] = tech_doc[current_section].get('content', '') + line + '\n'
        
        # Add default content if sections are missing
        for section in tech_doc:
            if section not in ['version', 'timestamp'] and not tech_doc[section]:
                if section in ['core_modules', 'challenges']:
                    tech_doc[section] = ['To be defined']
                else:
                    tech_doc[section] = {'content': 'To be defined'}
        
        return tech_doc
    
    def _get_default_tech_doc(self, structured_data):
        """
        Get default technical document structure in case of error
        """
        return {
            'version': '1.0',
            'timestamp': os.path.getmtime(__file__),
            'architecture': {'content': 'Error generating architecture design'}, 
            'tech_stack': {'content': 'Error generating tech stack selection'},
            'core_modules': ['Error generating core modules'],
            'interface_design': {'content': 'Error generating interface design'},
            'data_flow': {'content': 'Error generating data flow design'},
            'challenges': ['Error generating technical challenges'],
            'implementation': {'content': 'Error generating implementation plan'},
            'deployment': {'content': 'Error generating deployment strategy'}
        }