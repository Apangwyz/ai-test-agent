import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..knowledge_base import (
    knowledge_manager, knowledge_extractor, query_service, 
    KnowledgeEntity, KnowledgeQuery, KnowledgeType
)
from ..common.ai_service import ai_service
from ..prompt_engineering import prompt_generator
from ..feedback import feedback_collector, feedback_manager

class AILoopEngine:
    """AI Loop引擎 - 知识增强的推理流程"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.loop_iterations = 0
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'knowledge_hits': 0,
            'knowledge_misses': 0
        }
    
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理AI Loop请求
        
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
            
            # 2. 知识检索阶段
            self.logger.info("AI Loop: Knowledge retrieval phase")
            knowledge_context = self._retrieve_knowledge(collected_data)
            
            # 3. 提示词生成阶段
            self.logger.info("AI Loop: Prompt generation phase")
            enhanced_prompt = self._generate_prompt(collected_data, knowledge_context)
            
            # 4. 模型推理阶段
            self.logger.info("AI Loop: Model inference phase")
            inference_result = self._perform_inference(enhanced_prompt, collected_data)
            
            # 5. 结果验证阶段
            self.logger.info("AI Loop: Result validation phase")
            validated_result = self._validate_result(inference_result, collected_data)
            
            # 6. 反馈收集阶段
            self.logger.info("AI Loop: Feedback collection phase")
            feedback_data = self._collect_feedback(validated_result, collected_data)
            
            # 7. 知识更新阶段
            self.logger.info("AI Loop: Knowledge update phase")
            self._update_knowledge(collected_data, validated_result, feedback_data)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 更新性能指标
            self.performance_metrics['successful_requests'] += 1
            self._update_performance_metrics(processing_time)
            
            self.loop_iterations += 1
            self.logger.info(f"AI Loop iteration {self.loop_iterations} completed in {processing_time:.2f}s")
            
            return {
                'success': True,
                'result': validated_result,
                'processing_time': processing_time,
                'knowledge_used': len(knowledge_context) > 0,
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
    
    def _collect_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """数据收集阶段"""
        try:
            collected_data = {
                'task_type': request_data.get('task_type', 'general'),
                'context': request_data.get('context', ''),
                'user_id': request_data.get('user_id', 'anonymous'),
                'preferences': request_data.get('preferences', {}),
                'metadata': request_data.get('metadata', {}),
                'collected_at': datetime.now().isoformat()
            }
            
            # 如果有文档数据，提取知识
            if 'document_data' in request_data:
                document_data = request_data['document_data']
                extracted_entities = knowledge_extractor.extract_from_document(document_data)
                collected_data['extracted_knowledge'] = extracted_entities
                
                # 存储提取的知识
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
            
            # 构建查询
            query = KnowledgeQuery(
                query_text=context[:200],
                query_type="hybrid",
                limit=5,
                threshold=0.5
            )
            
            # 执行查询
            results = query_service.query(query)
            
            if results:
                self.performance_metrics['knowledge_hits'] += 1
                
                # 格式化知识内容
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
    
    def _generate_prompt(self, collected_data: Dict[str, Any], knowledge_context: str) -> str:
        """提示词生成阶段"""
        try:
            task_type = collected_data.get('task_type', 'general')
            context = collected_data.get('context', '')
            preferences = collected_data.get('preferences', {})
            
            # 生成自适应提示词
            enhanced_prompt = prompt_generator.generate_adaptive_prompt(
                task_type=task_type,
                context=context,
                user_preferences=preferences
            )
            
            # 如果有知识上下文，添加到提示词中
            if knowledge_context:
                enhanced_prompt = f"""
相关知识：
{knowledge_context}

任务要求：
{enhanced_prompt}
"""
            
            return enhanced_prompt
            
        except Exception as e:
            self.logger.error(f"Error in prompt generation: {e}")
            return collected_data.get('context', '')
    
    def _perform_inference(self, prompt: str, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """模型推理阶段"""
        try:
            task_type = collected_data.get('task_type', 'general')
            
            # 根据任务类型选择系统提示词
            system_prompts = {
                'requirement_analysis': "你是一个专业的需求分析师，擅长分析和理解软件需求。",
                'technical_solution': "你是一个技术架构师，擅长设计技术方案和系统架构。",
                'clarification': "你是一个需求澄清专家，擅长识别需求中的模糊点和问题。",
                'coding_task': "你是一个项目经理，擅长将技术方案转化为具体的编码任务。",
                'test_case': "你是一个测试工程师，擅长设计全面的测试用例。"
            }
            
            system_prompt = system_prompts.get(task_type, "你是一个专业的AI助手，擅长处理各种任务。")
            
            # 调用AI服务生成内容
            result = ai_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                use_enhanced=True
            )
            
            return {
                'content': result,
                'model_used': 'enhanced_ai_service',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in model inference: {e}")
            return {
                'content': '',
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    def _validate_result(self, inference_result: Dict[str, Any], collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """结果验证阶段"""
        try:
            content = inference_result.get('content', '')
            
            # 基本验证
            if not content or len(content) < 10:
                return {
                    **inference_result,
                    'validation_status': 'failed',
                    'validation_message': '生成内容为空或过短',
                    'validated': False
                }
            
            # 内容质量验证
            validation_score = self._calculate_content_quality(content)
            
            validated_result = {
                **inference_result,
                'validation_status': 'passed' if validation_score > 0.6 else 'warning',
                'validation_score': validation_score,
                'validation_message': '内容质量验证通过' if validation_score > 0.6 else '内容质量需要改进',
                'validated': validation_score > 0.6,
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
            
            # 长度评分
            if len(content) > 100:
                score += 0.3
            elif len(content) > 50:
                score += 0.2
            
            # 结构评分
            if '。' in content or '\n' in content:
                score += 0.3
            
            # 关键词评分
            keywords = ['分析', '设计', '实现', '测试', '方案', '建议', '结论']
            keyword_count = sum(1 for keyword in keywords if keyword in content)
            score += min(keyword_count * 0.1, 0.4)
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating content quality: {e}")
            return 0.0
    
    def _collect_feedback(self, validated_result: Dict[str, Any], collected_data: Dict[str, Any]) -> Optional[str]:
        """反馈收集阶段"""
        try:
            # 自动收集反馈
            if not validated_result.get('validated', False):
                feedback_data = {
                    'user_id': collected_data.get('user_id', 'system'),
                    'feedback_type': 'negative',
                    'category': 'system_performance',
                    'title': 'AI Loop结果验证失败',
                    'description': f"验证消息：{validated_result.get('validation_message', '')}",
                    'rating': 2,
                    'tags': ['auto_feedback', 'validation_failed'],
                    'metadata': {
                        'task_type': collected_data.get('task_type'),
                        'validation_score': validated_result.get('validation_score', 0)
                    }
                }
                
                feedback_id = feedback_collector.collect_feedback(feedback_data)
                return feedback_id
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in feedback collection: {e}")
            return None
    
    def _update_knowledge(self, collected_data: Dict[str, Any], validated_result: Dict[str, Any], feedback_id: Optional[str]):
        """知识更新阶段"""
        try:
            # 如果验证通过且内容质量较高，将结果作为新知识存储
            if validated_result.get('validated', False):
                content = validated_result.get('content', '')
                task_type = collected_data.get('task_type', 'general')
                
                # 创建新的知识实体
                new_entity = KnowledgeEntity(
                    type=KnowledgeType.DOMAIN_KNOWLEDGE,
                    title=f"AI Loop生成结果 - {task_type}",
                    content=content[:500],  # 限制内容长度
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
                
                # 存储新知识
                entity_id = knowledge_manager.add_entity(new_entity)
                self.logger.info(f"Stored new knowledge entity: {entity_id}")
            
        except Exception as e:
            self.logger.error(f"Error in knowledge update: {e}")
    
    def _update_performance_metrics(self, processing_time: float):
        """更新性能指标"""
        try:
            total_requests = self.performance_metrics['total_requests']
            current_avg = self.performance_metrics['average_response_time']
            
            # 计算新的平均响应时间
            new_avg = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
            self.performance_metrics['average_response_time'] = new_avg
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        total_requests = self.performance_metrics['total_requests']
        
        return {
            **self.performance_metrics,
            'success_rate': self.performance_metrics['successful_requests'] / total_requests if total_requests > 0 else 0.0,
            'failure_rate': self.performance_metrics['failed_requests'] / total_requests if total_requests > 0 else 0.0,
            'knowledge_hit_rate': self.performance_metrics['knowledge_hits'] / total_requests if total_requests > 0 else 0.0,
            'loop_iterations': self.loop_iterations,
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
            'knowledge_misses': 0
        }
        self.loop_iterations = 0
        self.logger.info("Performance metrics reset")

# 创建全局AI Loop引擎实例
ai_loop_engine = AILoopEngine()