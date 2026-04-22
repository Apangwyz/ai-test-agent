import os
import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path
from .models import KnowledgeEntity, KnowledgeRelation, KnowledgeQuery, KnowledgeResult, KnowledgeType, KnowledgeStatus

class KnowledgeBaseManager:
    """知识库管理器"""
    
    def __init__(self, base_dir: str = "data/knowledge_base"):
        self.logger = logging.getLogger(__name__)
        self.base_dir = Path(base_dir)
        self.entities_dir = self.base_dir / "entities"
        self.relations_dir = self.base_dir / "relations"
        self.index_dir = self.base_dir / "index"
        
        self._ensure_directories()
        self._load_index()
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        self.entities_dir.mkdir(parents=True, exist_ok=True)
        self.relations_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_index(self):
        """加载索引"""
        self.entity_index = {}
        self.relation_index = {}
        
        for entity_file in self.entities_dir.glob("*.json"):
            try:
                with open(entity_file, 'r', encoding='utf-8') as f:
                    entity_data = json.load(f)
                    entity = KnowledgeEntity.from_dict(entity_data)
                    self.entity_index[entity.id] = entity
            except Exception as e:
                self.logger.error(f"Error loading entity from {entity_file}: {e}")
        
        for relation_file in self.relations_dir.glob("*.json"):
            try:
                with open(relation_file, 'r', encoding='utf-8') as f:
                    relation_data = json.load(f)
                    relation = KnowledgeRelation.from_dict(relation_data)
                    self.relation_index[relation.id] = relation
            except Exception as e:
                self.logger.error(f"Error loading relation from {relation_file}: {e}")
        
        self.logger.info(f"Loaded {len(self.entity_index)} entities and {len(self.relation_index)} relations")
    
    def add_entity(self, entity: KnowledgeEntity) -> str:
        """添加知识实体"""
        entity_id = entity.id
        self.entity_index[entity_id] = entity
        
        entity_file = self.entities_dir / f"{entity_id}.json"
        with open(entity_file, 'w', encoding='utf-8') as f:
            json.dump(entity.to_dict(), f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Added entity: {entity_id}")
        return entity_id
    
    def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """获取知识实体"""
        return self.entity_index.get(entity_id)
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """更新知识实体"""
        entity = self.entity_index.get(entity_id)
        if not entity:
            return False
        
        for key, value in updates.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        entity.updated_at = datetime.now()
        
        entity_file = self.entities_dir / f"{entity_id}.json"
        with open(entity_file, 'w', encoding='utf-8') as f:
            json.dump(entity.to_dict(), f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Updated entity: {entity_id}")
        return True
    
    def delete_entity(self, entity_id: str) -> bool:
        """删除知识实体"""
        if entity_id not in self.entity_index:
            return False
        
        del self.entity_index[entity_id]
        
        entity_file = self.entities_dir / f"{entity_id}.json"
        if entity_file.exists():
            entity_file.unlink()
        
        self.logger.info(f"Deleted entity: {entity_id}")
        return True
    
    def add_relation(self, relation: KnowledgeRelation) -> str:
        """添加知识关系"""
        relation_id = relation.id
        self.relation_index[relation_id] = relation
        
        relation_file = self.relations_dir / f"{relation_id}.json"
        with open(relation_file, 'w', encoding='utf-8') as f:
            json.dump(relation.to_dict(), f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Added relation: {relation_id}")
        return relation_id
    
    def get_relations(self, entity_id: str) -> List[KnowledgeRelation]:
        """获取实体的所有关系"""
        relations = []
        for relation in self.relation_index.values():
            if relation.source_entity_id == entity_id or relation.target_entity_id == entity_id:
                relations.append(relation)
        return relations
    
    def query_entities(self, query: KnowledgeQuery) -> List[KnowledgeResult]:
        """查询知识实体"""
        results = []
        
        for entity in self.entity_index.values():
            if entity.status != KnowledgeStatus.ACTIVE:
                continue
            
            score = self._calculate_relevance(entity, query)
            
            if score >= query.threshold:
                relevance = "high" if score > 0.8 else "medium" if score > 0.6 else "low"
                results.append(KnowledgeResult(
                    entity=entity,
                    score=score,
                    relevance=relevance
                ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:query.limit]
    
    def _calculate_relevance(self, entity: KnowledgeEntity, query: KnowledgeQuery) -> float:
        """计算相关性分数"""
        score = 0.0
        
        query_text = query.query_text.lower()
        title = entity.title.lower()
        content = entity.content.lower()
        
        if query_text in title:
            score += 0.5
        
        if query_text in content:
            score += 0.3
        
        for tag in entity.tags:
            if query_text in tag.lower():
                score += 0.1
        
        for filter_key, filter_value in query.filters.items():
            if hasattr(entity, filter_key):
                entity_value = getattr(entity, filter_key)
                if isinstance(entity_value, str) and filter_value.lower() in entity_value.lower():
                    score += 0.1
                elif entity_value == filter_value:
                    score += 0.1
        
        return min(score, 1.0)
    
    def get_entities_by_type(self, knowledge_type: KnowledgeType) -> List[KnowledgeEntity]:
        """按类型获取知识实体"""
        return [entity for entity in self.entity_index.values() if entity.type == knowledge_type]
    
    def get_entities_by_tags(self, tags: List[str]) -> List[KnowledgeEntity]:
        """按标签获取知识实体"""
        results = []
        for entity in self.entity_index.values():
            if any(tag in entity.tags for tag in tags):
                results.append(entity)
        return results
    
    def search_by_content(self, content: str, limit: int = 10) -> List[KnowledgeResult]:
        """按内容搜索知识实体"""
        query = KnowledgeQuery(
            query_text=content,
            query_type="content",
            limit=limit
        )
        return self.query_entities(query)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        type_counts = {}
        for entity in self.entity_index.values():
            type_name = entity.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        status_counts = {}
        for entity in self.entity_index.values():
            status_name = entity.status.value
            status_counts[status_name] = status_counts.get(status_name, 0) + 1
        
        return {
            'total_entities': len(self.entity_index),
            'total_relations': len(self.relation_index),
            'type_distribution': type_counts,
            'status_distribution': status_counts,
            'last_updated': datetime.now().isoformat()
        }
    
    def export_entities(self, output_file: str) -> bool:
        """导出所有知识实体"""
        try:
            entities_data = [entity.to_dict() for entity in self.entity_index.values()]
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(entities_data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Exported {len(entities_data)} entities to {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting entities: {e}")
            return False
    
    def import_entities(self, input_file: str) -> bool:
        """导入知识实体"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                entities_data = json.load(f)
            
            imported_count = 0
            for entity_data in entities_data:
                entity = KnowledgeEntity.from_dict(entity_data)
                self.add_entity(entity)
                imported_count += 1
            
            self.logger.info(f"Imported {imported_count} entities from {input_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error importing entities: {e}")
            return False

# 创建全局知识库管理器实例
knowledge_manager = KnowledgeBaseManager()