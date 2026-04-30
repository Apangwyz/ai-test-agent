import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from ..models import KnowledgeEntity, KnowledgeQuery, KnowledgeResult, KnowledgeStatus
from .base_adapter import BaseAdapter

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    Settings = None

class ChromaDBAdapter(BaseAdapter):
    """
    ChromaDB向量数据库适配器
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.persist_directory = config.get('persist_directory', 'data/chromadb')
        self.collection_name = config.get('collection_name', 'knowledge_base')
        self.client = None
        self.collection = None
    
    def connect(self) -> bool:
        """连接到ChromaDB"""
        if not CHROMADB_AVAILABLE:
            self.logger.error("ChromaDB not available - chromadb package not installed")
            return False
        
        try:
            # 创建客户端
            self.client = chromadb.Client(Settings(
                persist_directory=self.persist_directory,
                anonymized_telemetry=False
            ))
            
            # 创建或获取集合
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            
            self.connected = True
            self.logger.info(f"Connected to ChromaDB collection: {self.collection_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to ChromaDB: {e}")
            return False
    
    def disconnect(self) -> bool:
        """断开连接"""
        try:
            if self.client:
                self.client.persist()
            self.connected = False
            self.logger.info("Disconnected from ChromaDB")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from ChromaDB: {e}")
            return False
    
    def add_entity(self, entity: KnowledgeEntity) -> str:
        """添加知识实体"""
        if not self.connected or not CHROMADB_AVAILABLE:
            return ""
        
        try:
            # 准备元数据
            metadata = {
                "title": entity.title,
                "content": entity.content,
                "type": entity.type.value,
                "source": entity.source,
                "status": entity.status.value,
                "confidence_score": entity.confidence_score,
                "created_at": entity.created_at.isoformat(),
                "updated_at": entity.updated_at.isoformat()
            }
            
            # 插入数据
            self.collection.add(
                ids=[entity.id],
                embeddings=[entity.embedding] if entity.embedding else None,
                metadatas=[metadata],
                documents=[entity.content]
            )
            
            self.logger.info(f"Added entity to ChromaDB: {entity.id}")
            return entity.id
        except Exception as e:
            self.logger.error(f"Error adding entity to ChromaDB: {e}")
            return ""
    
    def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """获取知识实体"""
        if not self.connected or not CHROMADB_AVAILABLE:
            return None
        
        try:
            result = self.collection.get(ids=[entity_id])
            
            if result and result['ids']:
                idx = result['ids'].index(entity_id)
                return self._convert_to_entity(entity_id, result, idx)
            return None
        except Exception as e:
            self.logger.error(f"Error getting entity from ChromaDB: {e}")
            return None
    
    def _convert_to_entity(self, entity_id: str, result: Dict[str, Any], idx: int) -> KnowledgeEntity:
        """将ChromaDB记录转换为实体对象"""
        from ..models import KnowledgeType
        
        metadata = result['metadatas'][idx] if result.get('metadatas') else {}
        
        return KnowledgeEntity(
            id=entity_id,
            type=KnowledgeType(metadata.get("type", "GENERAL")),
            title=metadata.get("title", ""),
            content=metadata.get("content", "") if metadata else (result['documents'][idx] if result.get('documents') else ""),
            source=metadata.get("source", ""),
            status=KnowledgeStatus(metadata.get("status", "ACTIVE")),
            embedding=result['embeddings'][idx] if result.get('embeddings') else [],
            confidence_score=metadata.get("confidence_score", 0.0),
            created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.now().isoformat()))
        )
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """更新知识实体"""
        if not self.connected or not CHROMADB_AVAILABLE:
            return False
        
        try:
            # 获取当前实体
            result = self.collection.get(ids=[entity_id])
            if not result['ids']:
                return False
            
            idx = result['ids'].index(entity_id)
            metadata = result['metadatas'][idx].copy() if result.get('metadatas') else {}
            
            # 更新元数据
            for key, value in updates.items():
                if key == 'updated_at':
                    metadata['updated_at'] = datetime.now().isoformat()
                else:
                    metadata[key] = value
            
            # 更新文档
            document = result['documents'][idx] if result.get('documents') else ""
            if 'content' in updates:
                document = updates['content']
            
            # 更新向量（如果提供）
            embedding = None
            if 'embedding' in updates:
                embedding = [updates['embedding']]
            
            # 先删除再添加（ChromaDB的update限制）
            self.collection.delete(ids=[entity_id])
            
            self.collection.add(
                ids=[entity_id],
                embeddings=embedding,
                metadatas=[metadata],
                documents=[document]
            )
            
            self.logger.info(f"Updated entity in ChromaDB: {entity_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating entity in ChromaDB: {e}")
            return False
    
    def delete_entity(self, entity_id: str) -> bool:
        """删除知识实体"""
        if not self.connected or not CHROMADB_AVAILABLE:
            return False
        
        try:
            self.collection.delete(ids=[entity_id])
            self.logger.info(f"Deleted entity from ChromaDB: {entity_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting entity from ChromaDB: {e}")
            return False
    
    def query(self, query: KnowledgeQuery) -> List[KnowledgeResult]:
        """查询知识实体"""
        if not self.connected or not CHROMADB_AVAILABLE:
            return []
        
        if not self._validate_query(query):
            return []
        
        try:
            # 构建where子句
            where_clause = {"status": KnowledgeStatus.ACTIVE.value}
            
            # 向量搜索
            if query.query_type in ["semantic", "hybrid"] and query.embedding:
                results = self.collection.query(
                    query_embeddings=[query.embedding],
                    n_results=query.limit,
                    where=where_clause,
                    include=["metadatas", "documents", "distances"]
                )
                
                knowledge_results = []
                for i, entity_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i] if results.get('distances') else 1.0
                    score = 1.0 / (1.0 + distance)
                    entity = self._convert_to_entity(entity_id, results, i)
                    relevance = self._calculate_relevance(score)
                    knowledge_results.append(KnowledgeResult(
                        entity=entity,
                        score=score,
                        relevance=relevance
                    ))
                return knowledge_results
            
            # 关键词搜索
            if query.query_type in ["keyword", "hybrid"]:
                results = self.collection.query(
                    query_texts=[query.query_text],
                    n_results=query.limit,
                    where=where_clause,
                    include=["metadatas", "documents", "distances"]
                )
                
                knowledge_results = []
                for i, entity_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i] if results.get('distances') else 1.0
                    score = max(0.5, 1.0 / (1.0 + distance))
                    entity = self._convert_to_entity(entity_id, results, i)
                    relevance = self._calculate_relevance(score)
                    knowledge_results.append(KnowledgeResult(
                        entity=entity,
                        score=score,
                        relevance=relevance
                    ))
                return knowledge_results
            
            return []
        except Exception as e:
            self.logger.error(f"Error querying ChromaDB: {e}")
            return []
    
    def search_vectors(self, query_vector: List[float], k: int = 10) -> List[Tuple[str, float]]:
        """向量搜索"""
        if not self.connected or not CHROMADB_AVAILABLE:
            return []
        
        try:
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=k,
                include=["distances"]
            )
            
            entity_results = []
            for i, entity_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i] if results.get('distances') else 1.0
                score = 1.0 / (1.0 + distance)
                entity_results.append((entity_id, score))
            
            return entity_results
        except Exception as e:
            self.logger.error(f"Error searching vectors in ChromaDB: {e}")
            return []
    
    def batch_add_entities(self, entities: List[KnowledgeEntity]) -> List[str]:
        """批量添加实体"""
        if not self.connected or not CHROMADB_AVAILABLE:
            return []
        
        try:
            ids = []
            embeddings = []
            metadatas = []
            documents = []
            
            for entity in entities:
                ids.append(entity.id)
                embeddings.append(entity.embedding)
                metadatas.append({
                    "title": entity.title,
                    "content": entity.content,
                    "type": entity.type.value,
                    "source": entity.source,
                    "status": entity.status.value,
                    "confidence_score": entity.confidence_score,
                    "created_at": entity.created_at.isoformat(),
                    "updated_at": entity.updated_at.isoformat()
                })
                documents.append(entity.content)
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            
            self.logger.info(f"Batch added {len(entities)} entities to ChromaDB")
            return ids
        except Exception as e:
            self.logger.error(f"Error batch adding entities to ChromaDB: {e}")
            return []
    
    def batch_delete_entities(self, entity_ids: List[str]) -> int:
        """批量删除实体"""
        if not self.connected or not CHROMADB_AVAILABLE:
            return 0
        
        try:
            self.collection.delete(ids=entity_ids)
            self.logger.info(f"Batch deleted {len(entity_ids)} entities from ChromaDB")
            return len(entity_ids)
        except Exception as e:
            self.logger.error(f"Error batch deleting entities from ChromaDB: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.connected or not CHROMADB_AVAILABLE:
            return {}
        
        try:
            count = self.collection.count()
            return {
                'total_entities': count,
                'storage_type': 'chromadb',
                'collection_name': self.collection_name,
                'persist_directory': self.persist_directory,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting ChromaDB stats: {e}")
            return {}
    
    def create_index(self, field_name: str) -> bool:
        """创建索引（ChromaDB自动管理）"""
        self.logger.info("Index management handled automatically by ChromaDB")
        return True
    
    def drop_index(self, field_name: str) -> bool:
        """删除索引（ChromaDB自动管理）"""
        self.logger.info("Index management handled automatically by ChromaDB")
        return True
