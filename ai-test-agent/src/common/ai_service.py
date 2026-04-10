import os
import openai
import dashscope
from dotenv import load_dotenv
import logging
import time

# Load environment variables
load_dotenv()

class AIService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # OpenAI configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')
        
        # Qwen configuration
        self.qwen_api_key = os.getenv('QWEN_API_KEY')
        self.qwen_model = os.getenv('QWEN_MODEL_NAME', 'qwen-turbo')
        self.qwen_api_base = os.getenv('QWEN_API_BASE', 'https://api.dashscope.aliyuncs.com/api/v1')
        self.qwen_timeout = int(os.getenv('QWEN_TIMEOUT', '60'))
        
        # Initialize clients
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        if self.qwen_api_key:
            dashscope.api_key = self.qwen_api_key
    
    def generate(self, prompt, system_prompt, model_type='qwen', temperature=0.3):
        """
        Generate content using the specified model
        
        Args:
            prompt (str): User prompt
            system_prompt (str): System prompt
            model_type (str): Model type ('qwen' or 'openai')
            temperature (float): Temperature for generation
            
        Returns:
            str: Generated content
        """
        try:
            if model_type == 'qwen' and self.qwen_api_key:
                return self._generate_with_qwen(prompt, system_prompt, temperature)
            elif model_type == 'openai' and self.openai_api_key:
                return self._generate_with_openai(prompt, system_prompt, temperature)
            else:
                self.logger.warning(f"No API key configured for model type: {model_type}")
                return "Error: No API key configured"
        except Exception as e:
            self.logger.error(f"Error generating content: {e}")
            raise
    
    def _generate_with_qwen(self, prompt, system_prompt, temperature):
        """
        Generate content using Qwen model
        """
        try:
            start_time = time.time()
            response = dashscope.Generation.call(
                model=self.qwen_model,
                prompt=prompt,
                system=system_prompt,
                temperature=temperature,
                max_tokens=2000,
                top_p=0.8
            )
            
            if response.status_code == 200 and response.output:
                self.logger.info(f"Qwen API call completed in {time.time() - start_time:.2f} seconds")
                return response.output.text
            else:
                error_msg = response.message if hasattr(response, 'message') else "Unknown error"
                self.logger.error(f"Qwen API error: {error_msg}")
                raise Exception(f"Qwen API error: {error_msg}")
        except Exception as e:
            self.logger.error(f"Error calling Qwen API: {e}")
            raise
    
    def _generate_with_openai(self, prompt, system_prompt, temperature):
        """
        Generate content using OpenAI model
        """
        try:
            start_time = time.time()
            response = openai.ChatCompletion.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=2000
            )
            
            self.logger.info(f"OpenAI API call completed in {time.time() - start_time:.2f} seconds")
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error calling OpenAI API: {e}")
            raise

# Create singleton instance
ai_service = AIService()