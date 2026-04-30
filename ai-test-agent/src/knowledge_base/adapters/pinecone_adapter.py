import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from ..models import KnowledgeEntity, KnowledgeQuery, KnowledgeResult, KnowledgeStatus
from .base_adapter import BaseAdapter

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    pinecone = None

class PineconeAdapter(BaseAdapter):
    """
    Pinecone向量数据库适配器
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.environment = config.get('environment', 'us-west1-gcp')
        self.index_name = config.get('index_name', 'knowledge-base')
        self.dimension = config.get('dimension', 384)
        self.index = None
    
    def connect(self) -> bool:
        """连接到Pinecone"""
        if not PINECONE_AVAILABLE:
            self.logger.error("Pinecone not available - pinecone package not installed")
            return False
        
        if not self.api_key:
            self.logger.error("Pinecone API key not provided")
            return False
        
        try:
            pinecone.init(
                api_key=self.api_key,
                environment=self.environment
            )
            
            # 创建索引（如果不存在）
            if self.index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine"
                )
            
            self.index = pinecone.Index(self.index_name)
            self.connected = True
            self.logger.info(f"Connected to Pinecone index: {self.index_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Pinecone: {e}")
            return False
    
    def disconnect(self) -> bool:
        """断开连接"""
        try:
            self.index = None
            self.connected = False
            self.logger.info("Disconnected from Pinecone")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from Pinecone: {e}")
            return False
    
    def add_entity(self, entity: KnowledgeEntity) -> str:
        """添加知识实体"""
        if not self.connected or not PINECONE_AVAILABLE:
            return ""
        
        try:
            # 准备元数据
            metadata = {
                "title": entity.title,
                "content": entity.content[:8191],  # Pinecone metadata limit
                "type": entity.type.value,
                "source": entity.source,
                "status": entity.status.value,
                "confidence_score": entity.confidence_score,
                "created_at": entity.created_at.isoformat(),
                "updated_at": entity.updated_at.isoformat()
            }
            
            # 插入向量
            self.index.upsert(
                vectors=[(entity.id, entity.embedding or [0.0] * self.dimension, metadata)]
            )
            
            self.logger.info(f"Added entity to Pinecone: {entity.id}")
            return entity.id
        except Exception as e:
            self.logger.error(f"Error adding entity to Pinecone: {e}")
            return ""
    
    def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """获取知识实体"""
        if not self.connected or not PINECONE_AVAILABLE:
            return None
        
        try:
            result = self.index.fetch(ids=[entity_id])
            
            if result and entity_id in result['vectors']:
                vector_data = result['vectors'][entity_id]
                return self._convert_to_entity(entity_id, vector_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting entity from Pinecone: {e}")
            return None
    
    def _convert_to_entity(self, entity_id: str, vector_data: Dict[str, Any]) -> KnowledgeEntity:
        """将Pinecone记录转换为实体对象"""
        from ..models import KnowledgeType
        
        metadata = vector_data.get('metadata', {})
        
        return KnowledgeEntity(
            id=entity_id,
            type=KnowledgeType(metadata.get("type", "GENERAL")),
            title=metadata.get("title", ""),
            content=metadata.get("content", ""),
            source=metadata.get("source", ""),
            status=KnowledgeStatus(metadata.get("status", "ACTIVE")),
            embedding=vector_data.get('values', []),
            confidence_score=metadata.get("confidence_score", 0.0),
            created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.now().isoformat()))
        )
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """更新知识实体"""
        if not self.connected or not PINECONE_AVAILABLE:
            return False
        
        try:
            entity = self.get_entity(entity_id)
            if not entity:
                return False
            
            # 获取当前向量
            result = self.index.fetch(ids=[entity_id])
            if entity_id not in result['vectors']:
                return False
            
            current_vector = result['vectors'][entity_id]
            current_embedding = current_vector.get('values', [])
            
            # 构建新的元数据
            metadata = current_vector.get('metadata', {})
            for key, value in updates.items():
                if key == 'updated_at':
                    metadata['updated_at'] = datetime.now().isoformat()
                else:
                    metadata[key] = value
            
            # 更新向量
            self.index.upsert(
                vectors=[(entity_id, current_embedding, metadata)]
            )
            
            self.logger.info(f"Updated entity in Pinecone: {entity_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating entity in Pinecone: {e}")
            return False
    
    def delete_entity(self, entity_id: str) -> bool:
        """删除知识实体"""
        if not self.connected or not PINECONE_AVAILABLE:
            return False
        
        try:
            self.index.delete(ids=[entity_id])
            self.logger.info(f"Deleted entity from Pinecone: {entity_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting entity from Pinecone: {e}")
            return False
    
    def query(self, query: KnowledgeQuery) -> List[KnowledgeResult]:
        """查询知识实体"""
        if not self.connected or not PINECONE_AVAILABLE:
            return []
        
        if not self._validate_query(query):
            return []
        
        try:
            # 构建过滤条件
            filter_dict = {"status": KnowledgeStatus.ACTIVE.value}
            
            # 向量搜索
            if query.query_type in ["semantic", "hybrid"] and query.embedding:
                results = self.index.query(
                    vector=query.embedding,
                    top_k=query.limit,
                    include_metadata=True,
                    filter=filter_dict
                )
                
                knowledge_results = []
                for match in results['matches']:
                    entity = self._convert_to_entity(match['id'], match)
                    score = match['score']
                    relevance = self._calculate_relevance(score)
                    knowledge_results.append(KnowledgeResult(
                        entity=entity,
                        score=score,
                        relevance=relevance
                    ))
                return knowledge_results
            
            # 关键词搜索（Pinecone不支持原生关键词搜索，需要元数据过滤）
            if query.query_type in ["keyword", "hybrid"]:
                # 由于Pinecone不支持全文搜索，这里使用元数据过滤
                results = self.index.query(
                    vector=[0.0] * self.dimension,  # 空向量
                    top_k=query.limit,
                    include_metadata=True,
                    filter=filter_dict
                )
                
                knowledge_results = []
                for match in results['matches']:
                    metadata = match.get('metadata', {})
                    content = f"{metadata.get('title', '')} {metadata.get('content', '')}"
                    if query.query_text.lower() in content.lower():
                        entity = self._convert_to_entity(match['id'], match)
                        knowledge_results.append(KnowledgeResult(
                            entity=entity,
                            score=0.6,
                            relevance="medium"
                        ))
                return knowledge_results
            
            return []
        except Exception as e:
            self.logger.error(f"Error querying Pinecone: {e}")
            return []
    
    def search_vectors(self, query_vector: List[float], k: int = 10) -> List[Tuple[str, float]]:
        """向量搜索"""
        if not self.connected or not PINECONE_AVAILABLE:
            return []
        
        try:
            results = self.index.query(
                vector=query_vector,
                top_k=k,
                include_metadata=False
            )
            
            entity_results = []
            for match in results['matches']:
                entity_results.append((match['id'], match['score']))
            
            return entity_results
        except Exception as e:
            self.logger.error(f"Error searching vectors in Pinecone: {e}")
            return []
    
    def batch_add_entities(self, entities: List[KnowledgeEntity]) -> List[str]:
        """批量添加实体"""
        if not self.connected or not PINECONE_AVAILABLE:
            return []
        
        try:
            vectors = []
            entity_ids = []
            
            for entity in entities:
                metadata = {
                    "title": entity.title,
                    "content": entity.content[:8191],
                    "type": entity.type.value,
                    "source": entity.source,
                    "status": entity.status.value,
                    "confidence_score": entity.confidence_score,
                    "created_at": entity.created_at.isoformat(),
                    "updated_at": entity.updated_at.isoformat()
                }
                
                vectors.append((
                    entity.id,
                    entity.embedding or [0.0] * self.dimension,
                    metadata
                ))
                entity_ids.append(entity.id)
            
            self.index.upsert(vectors=vectors)
            self.logger.info(f"Batch added {len(entities)} entities to Pinecone")
            return entity_ids
        except Exception as e:
            self.logger.error(f"Error batch adding entities to Pinecone: {e}")
            return []
    
    def batch_delete_entities(self, entity_ids: List[str]) -> int:
        """批量删除实体"""
        if not self.connected or not PINECONE_AVAILABLE:
            return 0
        
        try:
            self.index.delete(ids=entity_ids)
            self.logger.info(f"Batch deleted {len(entity_ids)} entities from Pinecone")
            return len(entity_ids)
        except Exception as e:
            self.logger.error(f"Error batch deleting entities from Pinecone: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.connected or not PINECONE_AVAILABLE:
            return {}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_entities': stats.get('total_vector_count', 0),
                'storage_type': 'pinecone',
                'environment': self.environment,
                'index_name': self.index_name,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting Pinecone stats: {e}")
            return {}
    
    def create_index(self, field_name: str) -> bool:
        """创建索引（Pinecone自动管理索引）"""
        self.logger.info("Index management handled automatically by Pinecone")
        return True
    
    def drop_index(self, field_name: str) -> bool:
        """删除索引（Pinecone自动管理索引）"""
        self.logger.info("Index management handled automatically by Pinecone")
        return True
