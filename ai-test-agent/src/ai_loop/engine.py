import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from ..knowledge_base import (
    knowledge_manager, knowledge_extractor, query_service, 
    KnowledgeEntity, KnowledgeQuery, KnowledgeType
)
from ..common.ai_service import ai_service
from ..prompt_engineering import prompt_generator

class AILoopEngine:
    """AI Loop引擎 - 知识增强的推理流程"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.loop_iterations = 0
        self.max_iterations = 3
        self.min_quality_threshold = 0.6
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'knowledge_hits': 0,
            'knowledge_misses': 0,
            'iterations_per_request': [],
            'auto_correction_count': 0
        }
        
        # 提示词调整策略
        self.prompt_adjustment_strategies = {
            'too_short': "请提供更详细的回答，至少需要200字以上。",
            'low_quality': "请提高回答质量，确保内容结构清晰、逻辑严谨。",
            'irrelevant': "请关注问题的核心，提供与主题相关的回答。",
            'incomplete': "请补充完整的回答，确保涵盖所有关键要点。"
        }
        
        # 缓存成功的提示词模式
        self.successful_prompt_patterns = []
        self.failed_prompt_patterns = []

    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理AI Loop请求（支持多轮迭代优化）
        
        Args:
            request_data: 请求数据，包含任务类型、上下文等信息
            
        Returns:
            处理结果
        """
        try:
            start_time = datetime.now()
            self.performance_metrics['total_requests'] += 1
            
            # 1. 数据收集阶段
            self.logger.info("AI Loop: Data collection phase")
            collected_data = self._collect_data(request_data)
            
            # 2. 多轮迭代优化处理
            self.logger.info("AI Loop: Starting iterative optimization")
            final_result = self._perform_iterative_optimization(collected_data)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 更新性能指标
            self.performance_metrics['successful_requests'] += 1
            self._update_performance_metrics(processing_time)
            
            self.logger.info(f"AI Loop completed in {processing_time:.2f}s")
            
            return {
                'success': True,
                'result': final_result,
                'processing_time': processing_time,
                'loop_iteration': self.loop_iterations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing AI Loop request: {e}")
            self.performance_metrics['failed_requests'] += 1
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _perform_iterative_optimization(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行多轮迭代优化
        """
        last_prompt = None
        last_result = None
        iteration_count = 0
        
        for iteration in range(self.max_iterations):
            iteration_count += 1
            self.logger.info(f"AI Loop iteration {iteration + 1}/{self.max_iterations}")
            
            # 1. 知识检索阶段
            knowledge_context = self._retrieve_knowledge(collected_data)
            
            # 2. 提示词生成阶段（支持动态调整）
            enhanced_prompt = self._generate_adaptive_prompt(
                collected_data, 
                knowledge_context, 
                last_result, 
                iteration
            )
            last_prompt = enhanced_prompt
            
            # 3. 模型推理阶段（带重试机制）
            inference_result = self._perform_inference_with_retry(enhanced_prompt, collected_data)
            last_result = inference_result
            
            # 4. 结果验证阶段
            validated_result = self._validate_result(inference_result, collected_data)
            
            # 5. 检查是否满足质量要求
            if validated_result.get('validated', False):
                self.logger.info(f"AI Loop: Validation passed at iteration {iteration + 1}")
                self._record_successful_pattern(enhanced_prompt, validated_result)
                
                # 6. 反馈收集阶段
                self._collect_feedback(validated_result, collected_data, iteration_count)
                
                # 7. 知识更新阶段
                self._update_knowledge(collected_data, validated_result, None)
                
                return validated_result
            
            # 6. 记录失败模式
            self._record_failed_pattern(enhanced_prompt, validated_result)
            
            # 7. 如果还有迭代机会，调整策略
            if iteration < self.max_iterations - 1:
                self.logger.info(f"AI Loop: Adjusting strategy for next iteration")
                collected_data['adjustment_attempts'] = iteration + 1
                collected_data['last_validation_message'] = validated_result.get('validation_message', '')
        
        # 如果所有迭代都失败，返回最后一次结果并记录
        self.logger.warning(f"AI Loop: All {self.max_iterations} iterations failed")
        self.performance_metrics['auto_correction_count'] += 1
        
        # 收集负面反馈
        self._collect_feedback(last_result, collected_data, iteration_count)
        
        return last_result

    def _collect_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """数据收集阶段"""
        try:
            collected_data = {
                'task_type': request_data.get('task_type', 'general'),
                'context': request_data.get('context', ''),
                'user_id': request_data.get('user_id', 'anonymous'),
                'preferences': request_data.get('preferences', {}),
                'metadata': request_data.get('metadata', {}),
                'adjustment_attempts': 0,
                'collected_at': datetime.now().isoformat()
            }
            
            if 'document_data' in request_data:
                document_data = request_data['document_data']
                extracted_entities = knowledge_extractor.extract_from_document(document_data)
                collected_data['extracted_knowledge'] = extracted_entities
                entity_ids = knowledge_extractor.store_extracted_knowledge(extracted_entities)
                collected_data['stored_entity_ids'] = entity_ids
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error in data collection: {e}")
            return request_data

    def _retrieve_knowledge(self, collected_data: Dict[str, Any]) -> str:
        """知识检索阶段"""
        try:
            context = collected_data.get('context', '')
            task_type = collected_data.get('task_type', 'general')
            
            query = KnowledgeQuery(
                query_text=context[:200],
                query_type="hybrid",
                limit=5,
                threshold=0.5
            )
            
            results = query_service.query(query)
            
            if results:
                self.performance_metrics['knowledge_hits'] += 1
                knowledge_items = []
                for result in results:
                    entity = result.entity
                    knowledge_item = f"【{entity.type.value}】{entity.title}\n内容：{entity.content}\n"
                    knowledge_items.append(knowledge_item)
                return "\n".join(knowledge_items)
            else:
                self.performance_metrics['knowledge_misses'] += 1
                return ""
                
        except Exception as e:
            self.logger.error(f"Error in knowledge retrieval: {e}")
            self.performance_metrics['knowledge_misses'] += 1
            return ""

    def _generate_adaptive_prompt(self, collected_data: Dict[str, Any], 
                                  knowledge_context: str, last_result: Optional[Dict],
                                  iteration: int) -> str:
        """
        生成自适应提示词（支持动态调整）
        """
        try:
            task_type = collected_data.get('task_type', 'general')
            context = collected_data.get('context', '')
            preferences = collected_data.get('preferences', {})
            adjustment_attempts = collected_data.get('adjustment_attempts', 0)
            
            # 生成基础提示词
            enhanced_prompt = prompt_generator.generate_adaptive_prompt(
                task_type=task_type,
                context=context,
                user_preferences=preferences
            )
            
            # 添加知识上下文
            if knowledge_context:
                enhanced_prompt = f"""相关知识：\n{knowledge_context}\n\n任务要求：\n{enhanced_prompt}"""
            
            # 根据迭代次数和上次结果调整提示词
            if iteration > 0 and last_result:
                validation_message = collected_data.get('last_validation_message', '')
                adjustment = self._get_prompt_adjustment(validation_message, iteration)
                if adjustment:
                    enhanced_prompt = f"""{enhanced_prompt}\n\n特别要求：\n{adjustment}"""
            
            # 添加迭代次数提示
            if adjustment_attempts > 0:
                enhanced_prompt = f"""{enhanced_prompt}\n\n（第{adjustment_attempts + 1}次尝试，请确保回答质量）"""
            
            return enhanced_prompt
            
        except Exception as e:
            self.logger.error(f"Error in prompt generation: {e}")
            return collected_data.get('context', '')

    def _get_prompt_adjustment(self, validation_message: str, iteration: int) -> str:
        """
        根据验证结果获取提示词调整策略
        """
        validation_message_lower = validation_message.lower()
        
        if '过短' in validation_message_lower or '太短' in validation_message_lower:
            return self.prompt_adjustment_strategies['too_short']
        elif '质量' in validation_message_lower and ('低' in validation_message_lower or '差' in validation_message_lower):
            return self.prompt_adjustment_strategies['low_quality']
        elif '不相关' in validation_message_lower or '无关' in validation_message_lower:
            return self.prompt_adjustment_strategies['irrelevant']
        elif '不完整' in validation_message_lower or '缺失' in validation_message_lower:
            return self.prompt_adjustment_strategies['incomplete']
        elif iteration >= 2:
            # 如果已经多次失败，使用综合调整
            return "请重新审视问题，提供更全面、详细且高质量的回答。"
        
        return ""

    def _perform_inference_with_retry(self, prompt: str, collected_data: Dict[str, Any], 
                                      max_retries: int = 2) -> Dict[str, Any]:
        """
        模型推理阶段（带重试机制）
        """
        retry_delay = 1.0  # 初始重试延迟
        
        for attempt in range(max_retries + 1):
            try:
                task_type = collected_data.get('task_type', 'general')
                
                system_prompts = {
                    'requirement_analysis': "你是一个专业的需求分析师，擅长分析和理解软件需求。",
                    'technical_solution': "你是一个技术架构师，擅长设计技术方案和系统架构。",
                    'clarification': "你是一个需求澄清专家，擅长识别需求中的模糊点和问题。",
                    'coding_task': "你是一个项目经理，擅长将技术方案转化为具体的编码任务。",
                    'test_case': "你是一个测试工程师，擅长设计全面的测试用例。"
                }
                
                system_prompt = system_prompts.get(task_type, "你是一个专业的AI助手，擅长处理各种任务。")
                
                result = ai_service.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    use_enhanced=True
                )
                
                return {
                    'content': result,
                    'model_used': 'enhanced_ai_service',
                    'generated_at': datetime.now().isoformat(),
                    'retry_attempts': attempt
                }
                
            except Exception as e:
                self.logger.warning(f"Model inference attempt {attempt + 1} failed: {e}")
                if attempt < max_retries:
                    time.sleep(retry_delay * (2 ** attempt))  # 指数退避
                    continue
                else:
                    return {
                        'content': '',
                        'error': str(e),
                        'generated_at': datetime.now().isoformat(),
                        'retry_attempts': attempt
                    }

    def _validate_result(self, inference_result: Dict[str, Any], collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """结果验证阶段"""
        try:
            content = inference_result.get('content', '')
            adjustment_attempts = collected_data.get('adjustment_attempts', 0)
            
            # 动态调整阈值，随着迭代次数增加而降低要求
            threshold = max(
                self.min_quality_threshold,
                0.7 - (adjustment_attempts * 0.05)
            )
            
            # 基本验证
            if not content or len(content) < 10:
                return {
                    **inference_result,
                    'validation_status': 'failed',
                    'validation_message': '生成内容为空或过短',
                    'validated': False,
                    'validation_threshold': threshold,
                    'validation_score': 0.0
                }
            
            # 内容质量验证
            validation_score = self._calculate_content_quality(content)
            
            validated_result = {
                **inference_result,
                'validation_status': 'passed' if validation_score >= threshold else 'warning',
                'validation_score': validation_score,
                'validation_threshold': threshold,
                'validation_message': '内容质量验证通过' if validation_score >= threshold else '内容质量需要改进',
                'validated': validation_score >= threshold,
                'validated_at': datetime.now().isoformat()
            }
            
            return validated_result
            
        except Exception as e:
            self.logger.error(f"Error in result validation: {e}")
            return {
                **inference_result,
                'validation_status': 'error',
                'validation_message': str(e),
                'validated': False
            }

    def _calculate_content_quality(self, content: str) -> float:
        """计算内容质量分数"""
        try:
            score = 0.0
            
            # 长度评分（最多0.3分）
            content_length = len(content)
            if content_length > 500:
                score += 0.3
            elif content_length > 200:
                score += 0.2
            elif content_length > 100:
                score += 0.1
            
            # 结构评分（最多0.3分）
            if '。' in content or '\n' in content or '## ' in content:
                score += 0.2
            if len(content.split('\n')) >= 3:
                score += 0.1
            
            # 关键词评分（最多0.4分）
            keywords = ['分析', '设计', '实现', '测试', '方案', '建议', '结论', '需求', '功能', '模块']
            keyword_count = sum(1 for keyword in keywords if keyword in content)
            score += min(keyword_count * 0.08, 0.4)
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating content quality: {e}")
            return 0.0

    def _record_successful_pattern(self, prompt: str, result: Dict[str, Any]):
        """记录成功的提示词模式"""
        try:
            pattern = {
                'prompt_hash': hash(prompt) % 1000000,
                'task_type': result.get('task_type', 'unknown'),
                'validation_score': result.get('validation_score', 0),
                'timestamp': datetime.now().isoformat()
            }
            self.successful_prompt_patterns.append(pattern)
            
            # 保持列表大小限制
            if len(self.successful_prompt_patterns) > 1000:
                self.successful_prompt_patterns = self.successful_prompt_patterns[-500:]
                
        except Exception as e:
            self.logger.error(f"Error recording successful pattern: {e}")

    def _record_failed_pattern(self, prompt: str, result: Dict[str, Any]):
        """记录失败的提示词模式"""
        try:
            pattern = {
                'prompt_hash': hash(prompt) % 1000000,
                'task_type': result.get('task_type', 'unknown'),
                'validation_score': result.get('validation_score', 0),
                'validation_message': result.get('validation_message', ''),
                'timestamp': datetime.now().isoformat()
            }
            self.failed_prompt_patterns.append(pattern)
            
            # 保持列表大小限制
            if len(self.failed_prompt_patterns) > 500:
                self.failed_prompt_patterns = self.failed_prompt_patterns[-250:]
                
        except Exception as e:
            self.logger.error(f"Error recording failed pattern: {e}")

    def _collect_feedback(self, validated_result: Dict[str, Any], collected_data: Dict[str, Any], 
                          iteration_count: int):
        """反馈收集阶段"""
        try:
            # 自动收集反馈
            if not validated_result.get('validated', False):
                from ..feedback import feedback_collector
                
                feedback_data = {
                    'user_id': collected_data.get('user_id', 'system'),
                    'feedback_type': 'negative',
                    'category': 'system_performance',
                    'title': 'AI Loop结果验证失败',
                    'description': f"验证消息：{validated_result.get('validation_message', '')}, 迭代次数：{iteration_count}",
                    'rating': max(1, 3 - iteration_count),
                    'tags': ['auto_feedback', 'validation_failed', f'iterations_{iteration_count}'],
                    'metadata': {
                        'task_type': collected_data.get('task_type'),
                        'validation_score': validated_result.get('validation_score', 0),
                        'iteration_count': iteration_count
                    }
                }
                
                feedback_collector.collect_feedback(feedback_data)
            
        except Exception as e:
            self.logger.error(f"Error in feedback collection: {e}")

    def _update_knowledge(self, collected_data: Dict[str, Any], validated_result: Dict[str, Any], 
                          feedback_id: Optional[str]):
        """知识更新阶段"""
        try:
            if validated_result.get('validated', False):
                content = validated_result.get('content', '')
                task_type = collected_data.get('task_type', 'general')
                
                new_entity = KnowledgeEntity(
                    type=KnowledgeType.DOMAIN_KNOWLEDGE,
                    title=f"AI Loop生成结果 - {task_type}",
                    content=content[:500],
                    source="ai_loop_generation",
                    metadata={
                        'task_type': task_type,
                        'validation_score': validated_result.get('validation_score', 0),
                        'feedback_id': feedback_id,
                        'loop_iteration': self.loop_iterations
                    },
                    tags=['ai_loop', task_type, 'generated'],
                    confidence_score=validated_result.get('validation_score', 0.7)
                )
                
                entity_id = knowledge_manager.add_entity(new_entity)
                self.logger.info(f"Stored new knowledge entity: {entity_id}")
            
        except Exception as e:
            self.logger.error(f"Error in knowledge update: {e}")

    def _update_performance_metrics(self, processing_time: float):
        """更新性能指标"""
        try:
            total_requests = self.performance_metrics['total_requests']
            current_avg = self.performance_metrics['average_response_time']
            
            new_avg = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
            self.performance_metrics['average_response_time'] = new_avg
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        total_requests = self.performance_metrics['total_requests']
        iterations = self.performance_metrics['iterations_per_request']
        
        return {
            **self.performance_metrics,
            'success_rate': self.performance_metrics['successful_requests'] / total_requests if total_requests > 0 else 0.0,
            'failure_rate': self.performance_metrics['failed_requests'] / total_requests if total_requests > 0 else 0.0,
            'knowledge_hit_rate': self.performance_metrics['knowledge_hits'] / total_requests if total_requests > 0 else 0.0,
            'avg_iterations_per_request': sum(iterations) / len(iterations) if iterations else 1.0,
            'auto_correction_rate': self.performance_metrics['auto_correction_count'] / total_requests if total_requests > 0 else 0.0,
            'last_updated': datetime.now().isoformat()
        }

    def reset_performance_metrics(self):
        """重置性能指标"""
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'knowledge_hits': 0,
            'knowledge_misses': 0,
            'iterations_per_request': [],
            'auto_correction_count': 0
        }
        self.loop_iterations = 0
        self.logger.info("Performance metrics reset")

# 创建全局AI Loop引擎实例
ai_loop_engine = AILoopEngine()
