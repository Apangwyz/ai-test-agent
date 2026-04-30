import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from ..models import KnowledgeEntity, KnowledgeQuery, KnowledgeResult, KnowledgeStatus
from .base_adapter import BaseAdapter

try:
    import weaviate
    from weaviate.util import generate_uuid5
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    weaviate = None
    generate_uuid5 = None

class WeaviateAdapter(BaseAdapter):
    """
    Weaviate向量数据库适配器
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 8080)
        self.schema_name = config.get('schema_name', 'KnowledgeEntity')
        self.client = None
    
    def connect(self) -> bool:
        """连接到Weaviate"""
        if not WEAVIATE_AVAILABLE:
            self.logger.error("Weaviate not available - weaviate package not installed")
            return False
        
        try:
            self.client = weaviate.Client(
                url=f"http://{self.host}:{self.port}"
            )
            
            # 创建schema（如果不存在）
            self._create_schema_if_not_exists()
            
            self.connected = True
            self.logger.info(f"Connected to Weaviate at {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Weaviate: {e}")
            return False
    
    def _create_schema_if_not_exists(self):
        """创建schema（如果不存在）"""
        if not self.client.schema.exists(self.schema_name):
            schema = {
                "class": self.schema_name,
                "vectorizer": "none",  # 我们自己提供向量
                "properties": [
                    {
                        "name": "title",
                        "dataType": ["string"]
                    },
                    {
                        "name": "content",
                        "dataType": ["text"]
                    },
                    {
                        "name": "type",
                        "dataType": ["string"]
                    },
                    {
                        "name": "source",
                        "dataType": ["string"]
                    },
                    {
                        "name": "status",
                        "dataType": ["string"]
                    },
                    {
                        "name": "confidence_score",
                        "dataType": ["number"]
                    },
                    {
                        "name": "created_at",
                        "dataType": ["string"]
                    },
                    {
                        "name": "updated_at",
                        "dataType": ["string"]
                    }
                ]
            }
            self.client.schema.create_class(schema)
            self.logger.info(f"Created schema: {self.schema_name}")
    
    def disconnect(self) -> bool:
        """断开连接"""
        try:
            if self.client:
                self.client.close()
            self.connected = False
            self.logger.info("Disconnected from Weaviate")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from Weaviate: {e}")
            return False
    
    def add_entity(self, entity: KnowledgeEntity) -> str:
        """添加知识实体"""
        if not self.connected or not WEAVIATE_AVAILABLE:
            return ""
        
        try:
            data_obj = {
                "title": entity.title,
                "content": entity.content,
                "type": entity.type.value,
                "source": entity.source,
                "status": entity.status.value,
                "confidence_score": entity.confidence_score,
                "created_at": entity.created_at.isoformat(),
                "updated_at": entity.updated_at.isoformat()
            }
            
            # 使用entity.id作为UUID
            self.client.data_object.create(
                data_obj=data_obj,
                class_name=self.schema_name,
                uuid=entity.id,
                vector=entity.embedding
            )
            
            self.logger.info(f"Added entity to Weaviate: {entity.id}")
            return entity.id
        except Exception as e:
            self.logger.error(f"Error adding entity to Weaviate: {e}")
            return ""
    
    def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """获取知识实体"""
        if not self.connected or not WEAVIATE_AVAILABLE:
            return None
        
        try:
            result = self.client.data_object.get_by_id(
                uuid=entity_id,
                class_name=self.schema_name
            )
            
            if result:
                return self._convert_to_entity(result)
            return None
        except Exception as e:
            self.logger.error(f"Error getting entity from Weaviate: {e}")
            return None
    
    def _convert_to_entity(self, data_obj: Dict[str, Any]) -> KnowledgeEntity:
        """将Weaviate记录转换为实体对象"""
        from ..models import KnowledgeType
        
        properties = data_obj.get('properties', {})
        
        return KnowledgeEntity(
            id=data_obj.get('id', ""),
            type=KnowledgeType(properties.get("type", "GENERAL")),
            title=properties.get("title", ""),
            content=properties.get("content", ""),
            source=properties.get("source", ""),
            status=KnowledgeStatus(properties.get("status", "ACTIVE")),
            embedding=data_obj.get('vector', []),
            confidence_score=properties.get("confidence_score", 0.0),
            created_at=datetime.fromisoformat(properties.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(properties.get("updated_at", datetime.now().isoformat()))
        )
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """更新知识实体"""
        if not self.connected or not WEAVIATE_AVAILABLE:
            return False
        
        try:
            # 准备更新数据
            data_obj = {}
            for key, value in updates.items():
                if key == 'updated_at':
                    data_obj['updated_at'] = datetime.now().isoformat()
                else:
                    data_obj[key] = value
            
            self.client.data_object.update(
                data_obj=data_obj,
                class_name=self.schema_name,
                uuid=entity_id
            )
            
            self.logger.info(f"Updated entity in Weaviate: {entity_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating entity in Weaviate: {e}")
            return False
    
    def delete_entity(self, entity_id: str) -> bool:
        """删除知识实体"""
        if not self.connected or not WEAVIATE_AVAILABLE:
            return False
        
        try:
            self.client.data_object.delete(
                uuid=entity_id,
                class_name=self.schema_name
            )
            self.logger.info(f"Deleted entity from Weaviate: {entity_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting entity from Weaviate: {e}")
            return False
    
    def query(self, query: KnowledgeQuery) -> List[KnowledgeResult]:
        """查询知识实体"""
        if not self.connected or not WEAVIATE_AVAILABLE:
            return []
        
        if not self._validate_query(query):
            return []
        
        try:
            # 向量搜索
            if query.query_type in ["semantic", "hybrid"] and query.embedding:
                near_vector = {"vector": query.embedding}
                
                results = self.client.query.get(
                    self.schema_name,
                    ["title", "content", "type", "source", "status", "confidence_score", "created_at", "updated_at"]
                ) \
                .with_near_vector(near_vector) \
                .with_limit(query.limit) \
                .with_additional(["distance", "id", "vector"]) \
                .do()
                
                knowledge_results = []
                for item in results.get('data', {}).get('Get', {}).get(self.schema_name, []):
                    entity = self._convert_to_entity({
                        'id': item.get('_additional', {}).get('id', ''),
                        'vector': item.get('_additional', {}).get('vector', []),
                        'properties': item
                    })
                    distance = item.get('_additional', {}).get('distance', 1.0)
                    score = 1.0 / (1.0 + distance)
                    relevance = self._calculate_relevance(score)
                    knowledge_results.append(KnowledgeResult(
                        entity=entity,
                        score=score,
                        relevance=relevance
                    ))
                return knowledge_results
            
            # 关键词搜索（使用Weaviate的BM25搜索）
            if query.query_type in ["keyword", "hybrid"]:
                results = self.client.query.get(
                    self.schema_name,
                    ["title", "content", "type", "source", "status", "confidence_score", "created_at", "updated_at"]
                ) \
                .with_bm25(query=query.query_text) \
                .with_limit(query.limit) \
                .with_additional(["score", "id", "vector"]) \
                .do()
                
                knowledge_results = []
                for item in results.get('data', {}).get('Get', {}).get(self.schema_name, []):
                    entity = self._convert_to_entity({
                        'id': item.get('_additional', {}).get('id', ''),
                        'vector': item.get('_additional', {}).get('vector', []),
                        'properties': item
                    })
                    score = item.get('_additional', {}).get('score', 0.5)
                    relevance = self._calculate_relevance(score)
                    knowledge_results.append(KnowledgeResult(
                        entity=entity,
                        score=score,
                        relevance=relevance
                    ))
                return knowledge_results
            
            return []
        except Exception as e:
            self.logger.error(f"Error querying Weaviate: {e}")
            return []
    
    def search_vectors(self, query_vector: List[float], k: int = 10) -> List[Tuple[str, float]]:
        """向量搜索"""
        if not self.connected or not WEAVIATE_AVAILABLE:
            return []
        
        try:
            near_vector = {"vector": query_vector}
            
            results = self.client.query.get(
                self.schema_name,
                []
            ) \
            .with_near_vector(near_vector) \
            .with_limit(k) \
            .with_additional(["distance", "id"]) \
            .do()
            
            entity_results = []
            for item in results.get('data', {}).get('Get', {}).get(self.schema_name, []):
                entity_id = item.get('_additional', {}).get('id', '')
                distance = item.get('_additional', {}).get('distance', 1.0)
                score = 1.0 / (1.0 + distance)
                entity_results.append((entity_id, score))
            
            return entity_results
        except Exception as e:
            self.logger.error(f"Error searching vectors in Weaviate: {e}")
            return []
    
    def batch_add_entities(self, entities: List[KnowledgeEntity]) -> List[str]:
        """批量添加实体"""
        if not self.connected or not WEAVIATE_AVAILABLE:
            return []
        
        try:
            objects = []
            entity_ids = []
            
            for entity in entities:
                data_obj = {
                    "title": entity.title,
                    "content": entity.content,
                    "type": entity.type.value,
                    "source": entity.source,
                    "status": entity.status.value,
                    "confidence_score": entity.confidence_score,
                    "created_at": entity.created_at.isoformat(),
                    "updated_at": entity.updated_at.isoformat()
                }
                
                objects.append({
                    "class": self.schema_name,
                    "id": entity.id,
                    "properties": data_obj,
                    "vector": entity.embedding
                })
                entity_ids.append(entity.id)
            
            self.client.batch.add_objects(objects)
            self.client.batch.create_objects()
            
            self.logger.info(f"Batch added {len(entities)} entities to Weaviate")
            return entity_ids
        except Exception as e:
            self.logger.error(f"Error batch adding entities to Weaviate: {e}")
            return []
    
    def batch_delete_entities(self, entity_ids: List[str]) -> int:
        """批量删除实体"""
        if not self.connected or not WEAVIATE_AVAILABLE:
            return 0
        
        try:
            count = 0
            for entity_id in entity_ids:
                if self.delete_entity(entity_id):
                    count += 1
            return count
        except Exception as e:
            self.logger.error(f"Error batch deleting entities from Weaviate: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.connected or not WEAVIATE_AVAILABLE:
            return {}
        
        try:
            # Weaviate没有直接的统计API，这里使用count查询
            result = self.client.query.aggregate(self.schema_name).with_meta_count().do()
            count = result.get('data', {}).get('Aggregate', {}).get(self.schema_name, [{}])[0].get('meta', {}).get('count', 0)
            
            return {
                'total_entities': count,
                'storage_type': 'weaviate',
                'host': self.host,
                'port': self.port,
                'schema_name': self.schema_name,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting Weaviate stats: {e}")
            return {}
    
    def create_index(self, field_name: str) -> bool:
        """创建索引（Weaviate自动管理）"""
        self.logger.info("Index management handled automatically by Weaviate")
        return True
    
    def drop_index(self, field_name: str) -> bool:
        """删除索引（Weaviate自动管理）"""
        self.logger.info("Index management handled automatically by Weaviate")
        return True
