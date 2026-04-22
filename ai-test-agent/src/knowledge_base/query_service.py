import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import KnowledgeEntity, KnowledgeQuery, KnowledgeResult, KnowledgeType, KnowledgeStatus
from .manager import knowledge_manager
from .vector_store import vector_store, vector_embedder

class KnowledgeQueryService:
    """知识库查询服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def query(self, query: KnowledgeQuery) -> List[KnowledgeResult]:
        """执行知识查询"""
        results = []
        
        try:
            if query.query_type == "semantic":
                results = self._semantic_search(query)
            elif query.query_type == "keyword":
                results = self._keyword_search(query)
            elif query.query_type == "content":
                results = self._content_search(query)
            else:
                results = self._hybrid_search(query)
            
            self.logger.info(f"Query returned {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            return []
    
    def _semantic_search(self, query: KnowledgeQuery) -> List[KnowledgeResult]:
        """语义搜索"""
        results = []
        
        try:
            query_embedding = vector_embedder.generate_embedding(query.query_text)
            vector_results = vector_store.search_vectors(query_embedding, k=query.limit * 2)
            
            for entity_id, vector_score in vector_results:
                entity = knowledge_manager.get_entity(entity_id)
                if entity and entity.status == KnowledgeStatus.ACTIVE:
                    if self._apply_filters(entity, query.filters):
                        combined_score = self._combine_scores(entity, query.query_text, vector_score)
                        if combined_score >= query.threshold:
                            relevance = self._determine_relevance(combined_score)
                            results.append(KnowledgeResult(
                                entity=entity,
                                score=combined_score,
                                relevance=relevance
                            ))
            
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:query.limit]
            
        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            return []
    
    def _keyword_search(self, query: KnowledgeQuery) -> List[KnowledgeResult]:
        """关键词搜索"""
        results = []
        
        try:
            keywords = query.query_text.lower().split()
            
            for entity in knowledge_manager.entity_index.values():
                if entity.status != KnowledgeStatus.ACTIVE:
                    continue
                
                if not self._apply_filters(entity, query.filters):
                    continue
                
                score = self._calculate_keyword_score(entity, keywords)
                if score >= query.threshold:
                    relevance = self._determine_relevance(score)
                    results.append(KnowledgeResult(
                        entity=entity,
                        score=score,
                        relevance=relevance
                    ))
            
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:query.limit]
            
        except Exception as e:
            self.logger.error(f"Error in keyword search: {e}")
            return []
    
    def _content_search(self, query: KnowledgeQuery) -> List[KnowledgeResult]:
        """内容搜索"""
        return knowledge_manager.search_by_content(query.query_text, limit=query.limit)
    
    def _hybrid_search(self, query: KnowledgeQuery) -> List[KnowledgeResult]:
        """混合搜索"""
        semantic_results = self._semantic_search(query)
        keyword_results = self._keyword_search(query)
        
        combined_results = {}
        
        for result in semantic_results:
            entity_id = result.entity.id
            if entity_id not in combined_results:
                combined_results[entity_id] = result
            else:
                combined_results[entity_id].score = max(combined_results[entity_id].score, result.score)
        
        for result in keyword_results:
            entity_id = result.entity.id
            if entity_id not in combined_results:
                combined_results[entity_id] = result
            else:
                combined_results[entity_id].score = (combined_results[entity_id].score + result.score) / 2
        
        results = list(combined_results.values())
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:query.limit]
    
    def _apply_filters(self, entity: KnowledgeEntity, filters: Dict[str, Any]) -> bool:
        """应用过滤条件"""
        for key, value in filters.items():
            if hasattr(entity, key):
                entity_value = getattr(entity, key)
                if isinstance(entity_value, str) and value.lower() not in entity_value.lower():
                    return False
                elif entity_value != value:
                    return False
            elif key in entity.metadata:
                metadata_value = entity.metadata[key]
                if isinstance(metadata_value, str) and value.lower() not in metadata_value.lower():
                    return False
                elif metadata_value != value:
                    return False
            else:
                return False
        return True
    
    def _calculate_keyword_score(self, entity: KnowledgeEntity, keywords: List[str]) -> float:
        """计算关键词匹配分数"""
        score = 0.0
        text = (entity.title + " " + entity.content + " " + " ".join(entity.tags)).lower()
        
        for keyword in keywords:
            if keyword in text:
                occurrences = text.count(keyword)
                score += min(occurrences * 0.2, 1.0)
        
        return min(score, 1.0)
    
    def _combine_scores(self, entity: KnowledgeEntity, query_text: str, vector_score: float) -> float:
        """组合多种分数"""
        keyword_score = self._calculate_keyword_score(entity, query_text.lower().split())
        
        combined_score = 0.7 * vector_score + 0.3 * keyword_score
        return min(combined_score, 1.0)
    
    def _determine_relevance(self, score: float) -> str:
        """确定相关性等级"""
        if score > 0.8:
            return "high"
        elif score > 0.6:
            return "medium"
        else:
            return "low"
    
    def get_related_entities(self, entity_id: str, limit: int = 5) -> List[KnowledgeResult]:
        """获取相关实体"""
        results = []
        
        try:
            entity = knowledge_manager.get_entity(entity_id)
            if not entity:
                return results
            
            related_ids = entity.related_entities
            for related_id in related_ids[:limit]:
                related_entity = knowledge_manager.get_entity(related_id)
                if related_entity and related_entity.status == KnowledgeStatus.ACTIVE:
                    results.append(KnowledgeResult(
                        entity=related_entity,
                        score=0.8,
                        relevance="medium"
                    ))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting related entities: {e}")
            return []
    
    def get_entities_by_type(self, knowledge_type: KnowledgeType, limit: int = 10) -> List[KnowledgeResult]:
        """按类型获取实体"""
        try:
            entities = knowledge_manager.get_entities_by_type(knowledge_type)
            results = []
            
            for entity in entities[:limit]:
                if entity.status == KnowledgeStatus.ACTIVE:
                    results.append(KnowledgeResult(
                        entity=entity,
                        score=entity.confidence_score,
                        relevance=self._determine_relevance(entity.confidence_score)
                    ))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting entities by type: {e}")
            return []
    
    def get_entities_by_tags(self, tags: List[str], limit: int = 10) -> List[KnowledgeResult]:
        """按标签获取实体"""
        try:
            entities = knowledge_manager.get_entities_by_tags(tags)
            results = []
            
            for entity in entities[:limit]:
                if entity.status == KnowledgeStatus.ACTIVE:
                    score = len(set(entity.tags) & set(tags)) / len(tags)
                    results.append(KnowledgeResult(
                        entity=entity,
                        score=score,
                        relevance=self._determine_relevance(score)
                    ))
            
            results.sort(key=lambda x: x.score, reverse=True)
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting entities by tags: {e}")
            return []
    
    def suggest_entities(self, partial_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """实体建议"""
        try:
            suggestions = []
            
            for entity in knowledge_manager.entity_index.values():
                if entity.status != KnowledgeStatus.ACTIVE:
                    continue
                
                if partial_text.lower() in entity.title.lower():
                    suggestions.append({
                        'id': entity.id,
                        'title': entity.title,
                        'type': entity.type.value,
                        'score': len(partial_text) / len(entity.title)
                    })
            
            suggestions.sort(key=lambda x: x['score'], reverse=True)
            return suggestions[:limit]
            
        except Exception as e:
            self.logger.error(f"Error suggesting entities: {e}")
            return []
    
    def get_query_suggestions(self, query_text: str, limit: int = 5) -> List[str]:
        """查询建议"""
        try:
            suggestions = []
            
            for entity in knowledge_manager.entity_index.values():
                if entity.status != KnowledgeStatus.ACTIVE:
                    continue
                
                if query_text.lower() in entity.title.lower():
                    suggestions.append(entity.title)
                elif query_text.lower() in entity.content.lower():
                    suggestions.append(entity.content[:100])
                
                if len(suggestions) >= limit:
                    break
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Error getting query suggestions: {e}")
            return []
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """获取查询统计信息"""
        try:
            stats = knowledge_manager.get_statistics()
            vector_stats = vector_store.get_statistics()
            
            return {
                'knowledge_base': stats,
                'vector_store': vector_stats,
                'query_service': {
                    'last_updated': datetime.now().isoformat(),
                    'available_query_types': ['semantic', 'keyword', 'content', 'hybrid'],
                    'supported_filters': ['type', 'status', 'tags', 'source']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting query statistics: {e}")
            return {}

# 创建全局查询服务实例
query_service = KnowledgeQueryService()