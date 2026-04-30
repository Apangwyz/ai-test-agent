import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from .models import KnowledgeEntity, KnowledgeRelation, KnowledgeQuery, KnowledgeResult, KnowledgeType, KnowledgeStatus
from .adapters import AdapterFactory
from .cache_manager import cache_manager
from .permission_manager import permission_manager

class KnowledgeBaseManager:
    """知识库管理器（支持多后端适配器）"""
    
    def __init__(self, provider_type: str = "internal", config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.provider_type = provider_type
        self.config = config or {}
        
        # 创建适配器
        self.adapter = AdapterFactory.create_and_connect(provider_type, self.config)
        
        # 关系存储（始终使用内部存储）
        self.base_dir = Path(self.config.get('data_dir', "data/knowledge_base"))
        self.relations_dir = self.base_dir / "relations"
        self.relations_dir.mkdir(parents=True, exist_ok=True)
        self.relation_index = {}
        self._load_relations()
        
        self.logger.info(f"KnowledgeBaseManager initialized with {provider_type} adapter")
    
    def _load_relations(self):
        """加载关系数据"""
        for relation_file in self.relations_dir.glob("*.json"):
            try:
                with open(relation_file, 'r', encoding='utf-8') as f:
                    relation_data = json.load(f)
                    relation = KnowledgeRelation.from_dict(relation_data)
                    self.relation_index[relation.id] = relation
            except Exception as e:
                self.logger.error(f"Error loading relation from {relation_file}: {e}")
        
        self.logger.info(f"Loaded {len(self.relation_index)} relations")
    
    def add_entity(self, entity: KnowledgeEntity, user_id: str = "system") -> str:
        """添加知识实体（带权限检查）"""
        if not permission_manager.can_write(user_id):
            self.logger.warning(f"Permission denied: user {user_id} cannot add entity")
            return ""
        
        entity_id = self.adapter.add_entity(entity)
        
        if entity_id:
            # 更新缓存
            cache_manager.set_entity(entity_id, entity)
            # 设置默认权限
            permission_manager.set_entity_permission(entity_id, user_id, permission_manager.role_permissions['admin'])
        
        return entity_id
    
    def get_entity(self, entity_id: str, user_id: str = "system") -> Optional[KnowledgeEntity]:
        """获取知识实体（带权限检查和缓存）"""
        # 先检查缓存
        cached_entity = cache_manager.get_entity(entity_id)
        if cached_entity:
            return cached_entity
        
        # 权限检查
        if not permission_manager.can_read(user_id, entity_id):
            self.logger.warning(f"Permission denied: user {user_id} cannot read entity {entity_id}")
            return None
        
        entity = self.adapter.get_entity(entity_id)
        
        if entity:
            cache_manager.set_entity(entity_id, entity)
        
        return entity
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any], user_id: str = "system") -> bool:
        """更新知识实体（带权限检查）"""
        if not permission_manager.can_write(user_id, entity_id):
            self.logger.warning(f"Permission denied: user {user_id} cannot update entity {entity_id}")
            return False
        
        success = self.adapter.update_entity(entity_id, updates)
        
        if success:
            # 使缓存失效
            cache_manager.invalidate_entity(entity_id)
        
        return success
    
    def delete_entity(self, entity_id: str, user_id: str = "system") -> bool:
        """删除知识实体（带权限检查）"""
        if not permission_manager.can_delete(user_id, entity_id):
            self.logger.warning(f"Permission denied: user {user_id} cannot delete entity {entity_id}")
            return False
        
        success = self.adapter.delete_entity(entity_id)
        
        if success:
            # 使缓存失效
            cache_manager.invalidate_entity(entity_id)
            # 删除权限记录（如果存在）
            if entity_id in self.relation_index:
                del self.relation_index[entity_id]
        
        return success
    
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
    
    def query_entities(self, query: KnowledgeQuery, user_id: str = "system") -> List[KnowledgeResult]:
        """查询知识实体（带缓存）"""
        # 生成查询缓存键
        query_key = f"{query.query_text}_{query.query_type}_{query.limit}_{query.threshold}"
        
        # 检查缓存
        cached_results = cache_manager.get_query_result(query_key)
        if cached_results is not None:
            return cached_results
        
        # 执行查询
        results = self.adapter.query(query)
        
        # 过滤无权限的实体
        filtered_results = []
        for result in results:
            if permission_manager.can_read(user_id, result.entity.id):
                filtered_results.append(result)
        
        # 更新缓存
        cache_manager.set_query_result(query_key, filtered_results)
        
        return filtered_results
    
    def search_vectors(self, query_vector: List[float], k: int = 10) -> List:
        """向量搜索"""
        return self.adapter.search_vectors(query_vector, k)
    
    def batch_add_entities(self, entities: List[KnowledgeEntity], user_id: str = "system") -> List[str]:
        """批量添加实体"""
        if not permission_manager.can_write(user_id):
            self.logger.warning(f"Permission denied: user {user_id} cannot batch add entities")
            return []
        
        entity_ids = self.adapter.batch_add_entities(entities)
        
        # 更新缓存
        for entity, entity_id in zip(entities, entity_ids):
            cache_manager.set_entity(entity_id, entity)
        
        return entity_ids
    
    def batch_delete_entities(self, entity_ids: List[str], user_id: str = "system") -> int:
        """批量删除实体"""
        if not permission_manager.can_delete(user_id):
            self.logger.warning(f"Permission denied: user {user_id} cannot batch delete entities")
            return 0
        
        count = self.adapter.batch_delete_entities(entity_ids)
        
        # 使缓存失效
        for entity_id in entity_ids:
            cache_manager.invalidate_entity(entity_id)
        
        return count
    
    def get_entities_by_type(self, knowledge_type: KnowledgeType) -> List[KnowledgeEntity]:
        """按类型获取知识实体"""
        # 构建查询
        query = KnowledgeQuery(
            query_text="",
            query_type="keyword",
            limit=1000,
            threshold=0.0
        )
        
        all_results = self.adapter.query(query)
        return [result.entity for result in all_results if result.entity.type == knowledge_type]
    
    def get_entities_by_tags(self, tags: List[str]) -> List[KnowledgeEntity]:
        """按标签获取知识实体"""
        query = KnowledgeQuery(
            query_text="",
            query_type="keyword",
            limit=1000,
            threshold=0.0
        )
        
        all_results = self.adapter.query(query)
        results = []
        for result in all_results:
            if any(tag in result.entity.tags for tag in tags):
                results.append(result.entity)
        return results
    
    def search_by_content(self, content: str, limit: int = 10, user_id: str = "system") -> List[KnowledgeResult]:
        """按内容搜索知识实体"""
        query = KnowledgeQuery(
            query_text=content,
            query_type="content",
            limit=limit,
            threshold=0.3
        )
        return self.query_entities(query, user_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        adapter_stats = self.adapter.get_stats()
        
        type_counts = {}
        try:
            query = KnowledgeQuery(
                query_text="",
                query_type="keyword",
                limit=10000,
                threshold=0.0
            )
            all_results = self.adapter.query(query)
            for result in all_results:
                type_name = result.entity.type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
        except Exception as e:
            self.logger.warning(f"Failed to get type distribution: {e}")
        
        status_counts = {}
        try:
            query = KnowledgeQuery(
                query_text="",
                query_type="keyword",
                limit=10000,
                threshold=0.0
            )
            all_results = self.adapter.query(query)
            for result in all_results:
                status_name = result.entity.status.value
                status_counts[status_name] = status_counts.get(status_name, 0) + 1
        except Exception as e:
            self.logger.warning(f"Failed to get status distribution: {e}")
        
        return {
            **adapter_stats,
            'total_relations': len(self.relation_index),
            'type_distribution': type_counts,
            'status_distribution': status_counts,
            'cache_stats': cache_manager.get_stats(),
            'last_updated': datetime.now().isoformat()
        }
    
    def export_entities(self, output_file: str) -> bool:
        """导出所有知识实体"""
        try:
            query = KnowledgeQuery(
                query_text="",
                query_type="keyword",
                limit=10000,
                threshold=0.0
            )
            results = self.adapter.query(query)
            entities_data = [result.entity.to_dict() for result in results]
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(entities_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Exported {len(entities_data)} entities to {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting entities: {e}")
            return False
    
    def import_entities(self, input_file: str, user_id: str = "system") -> bool:
        """导入知识实体"""
        if not permission_manager.can_write(user_id):
            self.logger.warning(f"Permission denied: user {user_id} cannot import entities")
            return False
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                entities_data = json.load(f)
            
            entities = [KnowledgeEntity.from_dict(data) for data in entities_data]
            self.batch_add_entities(entities, user_id)
            
            self.logger.info(f"Imported {len(entities)} entities from {input_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error importing entities: {e}")
            return False
    
    def get_supported_adapters(self) -> List[str]:
        """获取支持的适配器类型"""
        return AdapterFactory.get_supported_adapters()
    
    def switch_adapter(self, provider_type: str, config: Dict[str, Any]) -> bool:
        """切换适配器"""
        try:
            new_adapter = AdapterFactory.create_and_connect(provider_type, config)
            
            if new_adapter.is_connected():
                # 关闭旧适配器
                self.adapter.disconnect()
                
                # 切换到新适配器
                self.adapter = new_adapter
                self.provider_type = provider_type
                self.config = config
                
                # 清空缓存
                cache_manager.invalidate_all()
                
                self.logger.info(f"Switched to {provider_type} adapter")
                return True
            else:
                self.logger.error(f"Failed to connect to {provider_type} adapter")
                return False
        except Exception as e:
            self.logger.error(f"Error switching adapter: {e}")
            return False

# 创建全局知识库管理器实例（使用配置文件中的设置）
try:
    # 尝试从配置文件读取设置
    config_path = Path(__file__).parent.parent / "config" / "knowledge_base.yaml"
    if config_path.exists():
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            kb_config = yaml.safe_load(f)
        knowledge_manager = KnowledgeBaseManager(
            provider_type=kb_config.get('provider', 'internal'),
            config=kb_config.get('config', {})
        )
    else:
        knowledge_manager = KnowledgeBaseManager()
except Exception as e:
    logging.getLogger(__name__).warning(f"Failed to load config, using default: {e}")
    knowledge_manager = KnowledgeBaseManager()
