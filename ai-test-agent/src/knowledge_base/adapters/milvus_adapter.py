import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from ..models import KnowledgeEntity, KnowledgeQuery, KnowledgeResult, KnowledgeStatus
from .base_adapter import BaseAdapter

try:
    from pymilvus import (
        connections,
        Collection,
        FieldSchema,
        CollectionSchema,
        DataType,
        utility
    )
    MILVUS_AVAILABLE = True
except ImportError:
    MILVUS_AVAILABLE = False
    connections = None
    Collection = None
    FieldSchema = None
    CollectionSchema = None
    DataType = None
    utility = None

class MilvusAdapter(BaseAdapter):
    """
    Milvus向量数据库适配器
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 19530)
        self.collection_name = config.get('collection_name', 'knowledge_base')
        self.dimension = config.get('dimension', 384)
        self.collection = None
    
    def connect(self) -> bool:
        """连接到Milvus"""
        if not MILVUS_AVAILABLE:
            self.logger.error("Milvus not available - pymilvus not installed")
            return False
        
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            
            # 创建集合（如果不存在）
            self._create_collection_if_not_exists()
            
            self.connected = True
            self.logger.info(f"Connected to Milvus at {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Milvus: {e}")
            return False
    
    def _create_collection_if_not_exists(self):
        """创建集合（如果不存在）"""
        if not utility.has_collection(self.collection_name):
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="type", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=256),
                FieldSchema(name="status", dtype=DataType.VARCHAR, max_length=32),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
                FieldSchema(name="confidence_score", dtype=DataType.FLOAT),
                FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=32),
                FieldSchema(name="updated_at", dtype=DataType.VARCHAR, max_length=32)
            ]
            
            schema = CollectionSchema(fields=fields, description="Knowledge Base Collection")
            self.collection = Collection(name=self.collection_name, schema=schema)
            
            # 创建索引
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            self.collection.create_index(field_name="embedding", index_params=index_params)
            self.logger.info(f"Created collection: {self.collection_name}")
        else:
            self.collection = Collection(self.collection_name)
    
    def disconnect(self) -> bool:
        """断开连接"""
        try:
            if connections is not None:
                connections.disconnect("default")
            self.connected = False
            self.logger.info("Disconnected from Milvus")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from Milvus: {e}")
            return False
    
    def add_entity(self, entity: KnowledgeEntity) -> str:
        """添加知识实体"""
        if not self.connected or not MILVUS_AVAILABLE:
            return ""
        
        try:
            self.collection.load()
            
            # 准备插入数据
            entities = [
                [entity.id],
                [entity.title],
                [entity.content[:65535]],
                [entity.type.value],
                [entity.source],
                [entity.status.value],
                [entity.embedding] if entity.embedding else [[0.0] * self.dimension],
                [entity.confidence_score],
                [entity.created_at.isoformat()],
                [entity.updated_at.isoformat()]
            ]
            
            self.collection.insert(entities)
            self.collection.flush()
            
            self.logger.info(f"Added entity to Milvus: {entity.id}")
            return entity.id
        except Exception as e:
            self.logger.error(f"Error adding entity to Milvus: {e}")
            return ""
    
    def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """获取知识实体"""
        if not self.connected or not MILVUS_AVAILABLE:
            return None
        
        try:
            self.collection.load()
            result = self.collection.query(
                expr=f"id == '{entity_id}'",
                output_fields=["*"]
            )
            
            if result:
                return self._convert_to_entity(result[0])
            return None
        except Exception as e:
            self.logger.error(f"Error getting entity from Milvus: {e}")
            return None
    
    def _convert_to_entity(self, record: Dict[str, Any]) -> KnowledgeEntity:
        """将Milvus记录转换为实体对象"""
        from ..models import KnowledgeType
        
        return KnowledgeEntity(
            id=record.get("id", ""),
            type=KnowledgeType(record.get("type", "GENERAL")),
            title=record.get("title", ""),
            content=record.get("content", ""),
            source=record.get("source", ""),
            status=KnowledgeStatus(record.get("status", "ACTIVE")),
            embedding=record.get("embedding", []),
            confidence_score=record.get("confidence_score", 0.0),
            created_at=datetime.fromisoformat(record.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(record.get("updated_at", datetime.now().isoformat()))
        )
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """更新知识实体"""
        if not self.connected or not MILVUS_AVAILABLE:
            return False
        
        try:
            self.collection.load()
            
            # 构建更新表达式
            set_clauses = []
            for key, value in updates.items():
                if key == 'updated_at':
                    value = datetime.now().isoformat()
                elif isinstance(value, str):
                    value = f"'{value}'"
                set_clauses.append(f"{key} = {value}")
            
            if set_clauses:
                expr = f"id == '{entity_id}'"
                self.collection.update(
                    expr=expr,
                    update_fields=dict(updates)
                )
                self.collection.flush()
                self.logger.info(f"Updated entity in Milvus: {entity_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error updating entity in Milvus: {e}")
            return False
    
    def delete_entity(self, entity_id: str) -> bool:
        """删除知识实体"""
        if not self.connected or not MILVUS_AVAILABLE:
            return False
        
        try:
            self.collection.load()
            expr = f"id == '{entity_id}'"
            self.collection.delete(expr)
            self.collection.flush()
            self.logger.info(f"Deleted entity from Milvus: {entity_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting entity from Milvus: {e}")
            return False
    
    def query(self, query: KnowledgeQuery) -> List[KnowledgeResult]:
        """查询知识实体"""
        if not self.connected or not MILVUS_AVAILABLE:
            return []
        
        if not self._validate_query(query):
            return []
        
        try:
            self.collection.load()
            
            # 向量搜索
            if query.query_type in ["semantic", "hybrid"] and query.embedding:
                search_params = {
                    "metric_type": "L2",
                    "params": {"nprobe": 10}
                }
                
                results = self.collection.search(
                    data=[query.embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=query.limit,
                    expr=f"status == '{KnowledgeStatus.ACTIVE.value}'"
                )
                
                knowledge_results = []
                for hit in results[0]:
                    entity = self.get_entity(hit.id)
                    if entity:
                        score = 1.0 / (1.0 + hit.distance)
                        relevance = self._calculate_relevance(score)
                        knowledge_results.append(KnowledgeResult(
                            entity=entity,
                            score=score,
                            relevance=relevance
                        ))
                return knowledge_results
            
            # 关键词搜索
            if query.query_type in ["keyword", "hybrid"]:
                expr = f"status == '{KnowledgeStatus.ACTIVE.value}'"
                results = self.collection.query(
                    expr=expr,
                    output_fields=["*"],
                    limit=query.limit
                )
                
                knowledge_results = []
                for record in results:
                    entity = self._convert_to_entity(record)
                    content = f"{record.get('title', '')} {record.get('content', '')}"
                    if query.query_text.lower() in content.lower():
                        knowledge_results.append(KnowledgeResult(
                            entity=entity,
                            score=0.7,
                            relevance="medium"
                        ))
                return knowledge_results
            
            return []
        except Exception as e:
            self.logger.error(f"Error querying Milvus: {e}")
            return []
    
    def search_vectors(self, query_vector: List[float], k: int = 10) -> List[Tuple[str, float]]:
        """向量搜索"""
        if not self.connected or not MILVUS_AVAILABLE:
            return []
        
        try:
            self.collection.load()
            
            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 10}
            }
            
            results = self.collection.search(
                data=[query_vector],
                anns_field="embedding",
                param=search_params,
                limit=k
            )
            
            entity_results = []
            for hit in results[0]:
                score = 1.0 / (1.0 + hit.distance)
                entity_results.append((hit.id, score))
            
            return entity_results
        except Exception as e:
            self.logger.error(f"Error searching vectors in Milvus: {e}")
            return []
    
    def batch_add_entities(self, entities: List[KnowledgeEntity]) -> List[str]:
        """批量添加实体"""
        if not self.connected or not MILVUS_AVAILABLE:
            return []
        
        try:
            self.collection.load()
            
            ids = []
            titles = []
            contents = []
            types = []
            sources = []
            statuses = []
            embeddings = []
            confidence_scores = []
            created_ats = []
            updated_ats = []
            
            for entity in entities:
                ids.append(entity.id)
                titles.append(entity.title)
                contents.append(entity.content[:65535])
                types.append(entity.type.value)
                sources.append(entity.source)
                statuses.append(entity.status.value)
                embeddings.append(entity.embedding if entity.embedding else [0.0] * self.dimension)
                confidence_scores.append(entity.confidence_score)
                created_ats.append(entity.created_at.isoformat())
                updated_ats.append(entity.updated_at.isoformat())
            
            all_entities = [ids, titles, contents, types, sources, statuses, 
                           embeddings, confidence_scores, created_ats, updated_ats]
            
            self.collection.insert(all_entities)
            self.collection.flush()
            
            self.logger.info(f"Batch added {len(entities)} entities to Milvus")
            return ids
        except Exception as e:
            self.logger.error(f"Error batch adding entities to Milvus: {e}")
            return []
    
    def batch_delete_entities(self, entity_ids: List[str]) -> int:
        """批量删除实体"""
        if not self.connected or not MILVUS_AVAILABLE:
            return 0
        
        try:
            count = 0
            for entity_id in entity_ids:
                if self.delete_entity(entity_id):
                    count += 1
            return count
        except Exception as e:
            self.logger.error(f"Error batch deleting entities from Milvus: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.connected or not MILVUS_AVAILABLE:
            return {}
        
        try:
            stats = self.collection.get_collection_stats()
            return {
                'total_entities': stats.get('row_count', 0),
                'storage_type': 'milvus',
                'host': self.host,
                'port': self.port,
                'collection_name': self.collection_name,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting Milvus stats: {e}")
            return {}
    
    def create_index(self, field_name: str) -> bool:
        """创建索引"""
        if not self.connected or not MILVUS_AVAILABLE:
            return False
        
        try:
            if field_name == "embedding":
                index_params = {
                    "metric_type": "L2",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 1024}
                }
                self.collection.create_index(field_name="embedding", index_params=index_params)
                self.logger.info(f"Created index on {field_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error creating index: {e}")
            return False
    
    def drop_index(self, field_name: str) -> bool:
        """删除索引"""
        if not self.connected or not MILVUS_AVAILABLE:
            return False
        
        try:
            self.collection.drop_index(field_name=field_name)
            self.logger.info(f"Dropped index on {field_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error dropping index: {e}")
            return False
