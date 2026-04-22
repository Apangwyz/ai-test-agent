import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..knowledge_base import query_service, knowledge_manager, KnowledgeQuery, KnowledgeType
from ..common.ai_service import ai_service

class PromptGenerator:
    """基于知识库的提示词生成器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.prompt_templates = self._load_prompt_templates()
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载提示词模板"""
        return {
            'requirement_analysis': """
作为专业的需求分析师，请分析以下需求文档：

{context}

基于以上需求，请完成以下任务：
1. 识别功能需求和非功能需求
2. 分析需求之间的依赖关系
3. 识别潜在的冲突和矛盾
4. 提出需要澄清的问题

请以结构化的方式输出分析结果。
            """,
            
            'technical_solution': """
作为技术架构师，请为以下需求设计技术方案：

{context}

请提供：
1. 系统架构设计
2. 技术栈选型及理由
3. 核心模块划分
4. 接口设计规范
5. 数据流程设计
6. 关键技术难点解决方案

请确保方案符合行业最佳实践。
            """,
            
            'clarification': """
作为需求澄清专家，请分析以下需求并识别需要澄清的问题：

{context}

请识别：
1. 模糊不清的需求描述
2. 缺失的信息
3. 潜在的冲突
4. 需要进一步确认的业务规则

请提供具体的问题列表和建议。
            """,
            
            'coding_task': """
作为项目经理，请将以下技术方案转化为具体的编码任务：

{context}

请为每个任务提供：
1. 任务目标
2. 输入输出
3. 技术要求
4. 时间预估
5. 依赖关系

确保任务拆分合理，单个任务工作量不超过8小时。
            """,
            
            'test_case': """
作为测试工程师，请为以下需求设计测试案例：

{context}

请设计：
1. 功能测试用例
2. 性能测试用例
3. 兼容性测试用例
4. 安全测试用例

每个测试用例应包含：
1. 测试目标
2. 测试步骤
3. 预期结果
4. 测试环境要求
5. 优先级
            """,
            
            'knowledge_enhanced': """
基于以下相关知识，请完成指定的任务：

{knowledge_context}

当前任务：
{task_context}

请利用提供的知识来增强任务完成的质量和准确性。
            """
        }
    
    def generate_prompt(self, task_type: str, context: str, 
                      use_knowledge: bool = True, 
                      knowledge_limit: int = 5) -> str:
        """
        生成增强的提示词
        
        Args:
            task_type: 任务类型
            context: 任务上下文
            use_knowledge: 是否使用知识库增强
            knowledge_limit: 知识检索数量限制
            
        Returns:
            生成的提示词
        """
        try:
            # 获取基础模板
            template = self.prompt_templates.get(task_type, self.prompt_templates['knowledge_enhanced'])
            
            # 如果使用知识库增强
            if use_knowledge:
                knowledge_context = self._retrieve_knowledge(context, task_type, knowledge_limit)
                if knowledge_context:
                    enhanced_context = self._combine_context(context, knowledge_context)
                    prompt = template.format(context=enhanced_context, task_context=context, knowledge_context=knowledge_context)
                else:
                    prompt = template.format(context=context, task_context=context, knowledge_context="")
            else:
                prompt = template.format(context=context, task_context=context, knowledge_context="")
            
            self.logger.info(f"Generated prompt for task type: {task_type}")
            return prompt
            
        except Exception as e:
            self.logger.error(f"Error generating prompt: {e}")
            return context
    
    def _retrieve_knowledge(self, context: str, task_type: str, limit: int) -> str:
        """从知识库检索相关知识"""
        try:
            # 构建查询
            query = KnowledgeQuery(
                query_text=context[:200],  # 使用前200字符作为查询
                query_type="hybrid",
                limit=limit,
                threshold=0.5
            )
            
            # 执行查询
            results = query_service.query(query)
            
            if not results:
                return ""
            
            # 格式化知识内容
            knowledge_items = []
            for result in results:
                entity = result.entity
                knowledge_item = f"""
【{entity.type.value}】{entity.title}
内容：{entity.content}
置信度：{result.score:.2f}
"""
                knowledge_items.append(knowledge_item)
            
            knowledge_context = "\n".join(knowledge_items)
            self.logger.info(f"Retrieved {len(results)} knowledge items")
            return knowledge_context
            
        except Exception as e:
            self.logger.error(f"Error retrieving knowledge: {e}")
            return ""
    
    def _combine_context(self, original_context: str, knowledge_context: str) -> str:
        """组合原始上下文和知识上下文"""
        return f"""
原始需求：
{original_context}

相关知识：
{knowledge_context}
"""
    
    def generate_adaptive_prompt(self, task_type: str, context: str, 
                                user_preferences: Optional[Dict[str, Any]] = None) -> str:
        """
        生成自适应提示词
        
        Args:
            task_type: 任务类型
            context: 任务上下文
            user_preferences: 用户偏好设置
            
        Returns:
            自适应生成的提示词
        """
        try:
            # 获取基础提示词
            base_prompt = self.generate_prompt(task_type, context, use_knowledge=True)
            
            # 根据用户偏好调整提示词
            if user_preferences:
                enhanced_prompt = self._apply_user_preferences(base_prompt, user_preferences)
            else:
                enhanced_prompt = base_prompt
            
            return enhanced_prompt
            
        except Exception as e:
            self.logger.error(f"Error generating adaptive prompt: {e}")
            return self.generate_prompt(task_type, context, use_knowledge=False)
    
    def _apply_user_preferences(self, prompt: str, preferences: Dict[str, Any]) -> str:
        """应用用户偏好到提示词"""
        try:
            enhanced_prompt = prompt
            
            # 根据偏好添加额外指令
            if preferences.get('detailed_output', False):
                enhanced_prompt += "\n\n请提供详细的分析和解释。"
            
            if preferences.get('concise_output', False):
                enhanced_prompt += "\n\n请提供简洁明了的输出。"
            
            if preferences.get('include_examples', False):
                enhanced_prompt += "\n\n请在输出中包含具体的示例。"
            
            if preferences.get('focus_on_quality', False):
                enhanced_prompt += "\n\n请重点关注输出质量和准确性。"
            
            if preferences.get('creative_approach', False):
                enhanced_prompt += "\n\n请采用创新的方法来完成任务。"
            
            return enhanced_prompt
            
        except Exception as e:
            self.logger.error(f"Error applying user preferences: {e}")
            return prompt
    
    def generate_prompt_with_feedback(self, task_type: str, context: str, 
                                     feedback: Optional[Dict[str, Any]] = None) -> str:
        """
        基于反馈生成改进的提示词
        
        Args:
            task_type: 任务类型
            context: 任务上下文
            feedback: 用户反馈信息
            
        Returns:
            改进的提示词
        """
        try:
            # 获取基础提示词
            base_prompt = self.generate_prompt(task_type, context, use_knowledge=True)
            
            # 如果有反馈，根据反馈改进提示词
            if feedback:
                improved_prompt = self._improve_prompt_with_feedback(base_prompt, feedback)
            else:
                improved_prompt = base_prompt
            
            return improved_prompt
            
        except Exception as e:
            self.logger.error(f"Error generating prompt with feedback: {e}")
            return self.generate_prompt(task_type, context, use_knowledge=False)
    
    def _improve_prompt_with_feedback(self, prompt: str, feedback: Dict[str, Any]) -> str:
        """根据反馈改进提示词"""
        try:
            improved_prompt = prompt
            
            # 分析反馈类型
            feedback_type = feedback.get('type', 'general')
            feedback_content = feedback.get('content', '')
            
            if feedback_type == 'insufficient_detail':
                improved_prompt += f"\n\n基于用户反馈，请提供更详细的分析：{feedback_content}"
            elif feedback_type == 'too_verbose':
                improved_prompt += "\n\n请简化输出，重点关注核心要点。"
            elif feedback_type == 'missing_aspects':
                improved_prompt += f"\n\n请补充以下方面的分析：{feedback_content}"
            elif feedback_type == 'quality_issue':
                improved_prompt += "\n\n请特别注意输出的准确性和专业性。"
            elif feedback_type == 'format_issue':
                improved_prompt += "\n\n请按照标准格式输出结果。"
            
            return improved_prompt
            
        except Exception as e:
            self.logger.error(f"Error improving prompt with feedback: {e}")
            return prompt
    
    def optimize_prompt(self, task_type: str, context: str, 
                       optimization_goal: str = "quality") -> str:
        """
        优化提示词
        
        Args:
            task_type: 任务类型
            context: 任务上下文
            optimization_goal: 优化目标（quality, efficiency, balance）
            
        Returns:
            优化后的提示词
        """
        try:
            # 获取基础提示词
            base_prompt = self.generate_prompt(task_type, context, use_knowledge=True)
            
            # 根据优化目标调整提示词
            if optimization_goal == "quality":
                optimized_prompt = self._optimize_for_quality(base_prompt)
            elif optimization_goal == "efficiency":
                optimized_prompt = self._optimize_for_efficiency(base_prompt)
            else:  # balance
                optimized_prompt = self._optimize_for_balance(base_prompt)
            
            return optimized_prompt
            
        except Exception as e:
            self.logger.error(f"Error optimizing prompt: {e}")
            return self.generate_prompt(task_type, context, use_knowledge=False)
    
    def _optimize_for_quality(self, prompt: str) -> str:
        """为质量优化提示词"""
        return prompt + """
\n\n质量要求：
1. 确保分析的准确性和专业性
2. 提供详细的解释和理由
3. 考虑各种可能的情况和边界条件
4. 遵循行业最佳实践
5. 提供可操作的建议和解决方案
"""
    
    def _optimize_for_efficiency(self, prompt: str) -> str:
        """为效率优化提示词"""
        return prompt + """
\n\n效率要求：
1. 直接回答核心问题
2. 避免冗余和重复
3. 使用简洁明了的语言
4. 重点关注关键要点
5. 快速提供可执行的结果
"""
    
    def _optimize_for_balance(self, prompt: str) -> str:
        """为平衡优化提示词"""
        return prompt + """
\n\n平衡要求：
1. 在质量和效率之间保持平衡
2. 提供足够的细节但不冗余
3. 确保准确性的同时保持简洁
4. 重点关注关键问题和解决方案
5. 提供实用的建议和指导
"""
    
    def get_prompt_statistics(self) -> Dict[str, Any]:
        """获取提示词生成统计信息"""
        return {
            'available_templates': list(self.prompt_templates.keys()),
            'knowledge_integration': True,
            'adaptive_generation': True,
            'feedback_improvement': True,
            'optimization_modes': ['quality', 'efficiency', 'balance'],
            'last_updated': datetime.now().isoformat()
        }

# 创建全局提示词生成器实例
prompt_generator = PromptGenerator()