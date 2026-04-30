import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from ..models import KnowledgeEntity, KnowledgeQuery, KnowledgeResult, KnowledgeStatus
from .base_adapter import BaseAdapter

class InternalAdapter(BaseAdapter):
    """
    内部JSON存储适配器
    使用文件系统存储知识实体
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.data_dir = Path(config.get('data_dir', 'data/knowledge'))
        self.entity_file = self.data_dir / "entities.json"
        self._ensure_directory()
        self.entity_index = {}
        self._load_entities()
    
    def _ensure_directory(self):
        """确保数据目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_entities(self):
        """加载实体数据"""
        if self.entity_file.exists():
            try:
                with open(self.entity_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for entity_id, entity_data in data.items():
                        self.entity_index[entity_id] = KnowledgeEntity.from_dict(entity_data)
                self.logger.info(f"Loaded {len(self.entity_index)} entities")
            except Exception as e:
                self.logger.error(f"Error loading entities: {e}")
                self.entity_index = {}
        else:
            self.entity_index = {}
    
    def _save_entities(self):
        """保存实体数据"""
        try:
            data = {entity_id: entity.to_dict() for entity_id, entity in self.entity_index.items()}
            with open(self.entity_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving entities: {e}")
    
    def connect(self) -> bool:
        """连接到知识库"""
        self.connected = True
        self.logger.info("Internal adapter connected")
        return True
    
    def disconnect(self) -> bool:
        """断开连接"""
        self._save_entities()
        self.connected = False
        self.logger.info("Internal adapter disconnected")
        return True
    
    def add_entity(self, entity: KnowledgeEntity) -> str:
        """添加知识实体"""
        entity_id = entity.id
        self.entity_index[entity_id] = entity
        self._save_entities()
        self.logger.info(f"Added entity: {entity_id}")
        return entity_id
    
    def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """获取知识实体"""
        return self.entity_index.get(entity_id)
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """更新知识实体"""
        if entity_id not in self.entity_index:
            return False
        
        entity = self.entity_index[entity_id]
        for key, value in updates.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        entity.updated_at = datetime.now()
        self._save_entities()
        self.logger.info(f"Updated entity: {entity_id}")
        return True
    
    def delete_entity(self, entity_id: str) -> bool:
        """删除知识实体"""
        if entity_id not in self.entity_index:
            return False
        
        del self.entity_index[entity_id]
        self._save_entities()
        self.logger.info(f"Deleted entity: {entity_id}")
        return True
    
    def query(self, query: KnowledgeQuery) -> List[KnowledgeResult]:
        """查询知识实体"""
        if not self._validate_query(query):
            return []
        
        results = []
        query_text = query.query_text.lower()
        
        for entity in self.entity_index.values():
            if entity.status != KnowledgeStatus.ACTIVE:
                continue
            
            score = self._calculate_entity_score(entity, query_text)
            
            if score >= query.threshold:
                relevance = self._calculate_relevance(score)
                results.append(KnowledgeResult(
                    entity=entity,
                    score=score,
                    relevance=relevance
                ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:query.limit]
    
    def _calculate_entity_score(self, entity: KnowledgeEntity, query_text: str) -> float:
        """计算实体匹配分数"""
        score = 0.0
        
        # 标题匹配
        if query_text in entity.title.lower():
            score += 0.3
        
        # 内容匹配
        if query_text in entity.content.lower():
            score += 0.4
        
        # 标签匹配
        for tag in entity.tags:
            if query_text in tag.lower():
                score += 0.1
        
        # 类型匹配
        if query_text in entity.type.value.lower():
            score += 0.1
        
        # 来源匹配
        if query_text in entity.source.lower():
            score += 0.1
        
        return min(score, 1.0)
    
    def search_vectors(self, query_vector: List[float], k: int = 10) -> List[Tuple[str, float]]:
        """向量搜索（简单实现）"""
        results = []
        
        for entity_id, entity in self.entity_index.items():
            if entity.embedding is not None:
                # 计算余弦相似度
                similarity = self._cosine_similarity(query_vector, entity.embedding)
                results.append((entity_id, similarity))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def batch_add_entities(self, entities: List[KnowledgeEntity]) -> List[str]:
        """批量添加实体"""
        entity_ids = []
        for entity in entities:
            entity_id = self.add_entity(entity)
            entity_ids.append(entity_id)
        return entity_ids
    
    def batch_delete_entities(self, entity_ids: List[str]) -> int:
        """批量删除实体"""
        count = 0
        for entity_id in entity_ids:
            if self.delete_entity(entity_id):
                count += 1
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        active_count = sum(1 for e in self.entity_index.values() if e.status == KnowledgeStatus.ACTIVE)
        inactive_count = sum(1 for e in self.entity_index.values() if e.status == KnowledgeStatus.INACTIVE)
        
        type_counts = {}
        for entity in self.entity_index.values():
            type_name = entity.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            'total_entities': len(self.entity_index),
            'active_entities': active_count,
            'inactive_entities': inactive_count,
            'type_distribution': type_counts,
            'storage_type': 'internal_json',
            'last_updated': datetime.now().isoformat()
        }
    
    def create_index(self, field_name: str) -> bool:
        """创建索引（内部存储不需要显式索引）"""
        self.logger.info(f"Index creation not required for internal storage: {field_name}")
        return True
    
    def drop_index(self, field_name: str) -> bool:
        """删除索引（内部存储不需要显式索引）"""
        self.logger.info(f"Index drop not required for internal storage: {field_name}")
        return True
