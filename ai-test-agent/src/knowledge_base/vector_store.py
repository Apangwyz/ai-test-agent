import os
import logging
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from .models import KnowledgeEntity, KnowledgeQuery, KnowledgeResult

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available. Vector search will be disabled.")

class VectorStore:
    """向量存储管理器"""
    
    def __init__(self, dimension: int = 1536, index_type: str = "flat"):
        self.logger = logging.getLogger(__name__)
        self.dimension = dimension
        self.index_type = index_type
        self.base_dir = Path("data/vector_store")
        self.index_file = self.base_dir / "index.faiss"
        self.mapping_file = self.base_dir / "mapping.pkl"
        
        self._ensure_directories()
        self._initialize_index()
        self._load_mapping()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _initialize_index(self):
        """初始化FAISS索引"""
        if not FAISS_AVAILABLE:
            self.logger.warning("FAISS not available, using fallback storage")
            self.index = None
            self.vectors = []
            return
        
        try:
            if self.index_file.exists():
                self.index = faiss.read_index(str(self.index_file))
                self.logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
            else:
                if self.index_type == "flat":
                    self.index = faiss.IndexFlatL2(self.dimension)
                elif self.index_type == "ivf":
                    quantizer = faiss.IndexFlatL2(self.dimension)
                    self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
                    self.index.nprobe = 10
                elif self.index_type == "hnsw":
                    self.index = faiss.IndexHNSWFlat(self.dimension, 32)
                else:
                    self.index = faiss.IndexFlatL2(self.dimension)
                
                self.logger.info(f"Initialized new {self.index_type} FAISS index")
        except Exception as e:
            self.logger.error(f"Error initializing FAISS index: {e}")
            self.index = None
            self.vectors = []
    
    def _load_mapping(self):
        """加载向量到实体的映射"""
        self.vector_to_entity = {}
        
        if self.mapping_file.exists():
            try:
                with open(self.mapping_file, 'rb') as f:
                    self.vector_to_entity = pickle.load(f)
                self.logger.info(f"Loaded mapping for {len(self.vector_to_entity)} vectors")
            except Exception as e:
                self.logger.error(f"Error loading mapping: {e}")
                self.vector_to_entity = {}
    
    def _save_mapping(self):
        """保存向量到实体的映射"""
        try:
            with open(self.mapping_file, 'wb') as f:
                pickle.dump(self.vector_to_entity, f)
            self.logger.info(f"Saved mapping for {len(self.vector_to_entity)} vectors")
        except Exception as e:
            self.logger.error(f"Error saving mapping: {e}")
    
    def _save_index(self):
        """保存FAISS索引"""
        if FAISS_AVAILABLE and self.index is not None:
            try:
                faiss.write_index(self.index, str(self.index_file))
                self.logger.info(f"Saved FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                self.logger.error(f"Error saving FAISS index: {e}")
    
    def add_vector(self, vector: List[float], entity_id: str) -> bool:
        """添加向量到存储"""
        try:
            if not FAISS_AVAILABLE or self.index is None:
                self.vectors.append((vector, entity_id))
                self.vector_to_entity[len(self.vectors) - 1] = entity_id
                return True
            
            vector_array = np.array([vector], dtype=np.float32)
            vector_id = self.index.ntotal
            
            if self.index_type == "ivf" and self.index.ntotal == 0:
                self.index.train(vector_array)
            
            self.index.add(vector_array)
            self.vector_to_entity[vector_id] = entity_id
            
            self._save_mapping()
            self._save_index()
            
            self.logger.info(f"Added vector for entity {entity_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding vector: {e}")
            return False
    
    def search_vectors(self, query_vector: List[float], k: int = 10) -> List[Tuple[str, float]]:
        """搜索相似的向量"""
        try:
            if not FAISS_AVAILABLE or self.index is None:
                return self._fallback_search(query_vector, k)
            
            if self.index.ntotal == 0:
                return []
            
            query_array = np.array([query_vector], dtype=np.float32)
            distances, indices = self.index.search(query_array, k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1 and idx in self.vector_to_entity:
                    entity_id = self.vector_to_entity[idx]
                    distance = distances[0][i]
                    score = 1.0 / (1.0 + distance)
                    results.append((entity_id, score))
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching vectors: {e}")
            return []
    
    def _fallback_search(self, query_vector: List[float], k: int) -> List[Tuple[str, float]]:
        """回退搜索方法"""
        results = []
        
        for i, (vector, entity_id) in enumerate(self.vectors):
            distance = np.linalg.norm(np.array(query_vector) - np.array(vector))
            score = 1.0 / (1.0 + distance)
            results.append((entity_id, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]
    
    def delete_vector(self, entity_id: str) -> bool:
        """删除向量"""
        try:
            vector_ids_to_remove = [vid for vid, eid in self.vector_to_entity.items() if eid == entity_id]
            
            for vid in vector_ids_to_remove:
                del self.vector_to_entity[vid]
            
            self._save_mapping()
            self.logger.info(f"Removed vector for entity {entity_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting vector: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取向量存储统计信息"""
        if FAISS_AVAILABLE and self.index is not None:
            total_vectors = self.index.ntotal
        else:
            total_vectors = len(self.vectors)
        
        return {
            'total_vectors': total_vectors,
            'dimension': self.dimension,
            'index_type': self.index_type,
            'faiss_available': FAISS_AVAILABLE,
            'last_updated': datetime.now().isoformat()
        }
    
    def clear_all(self) -> bool:
        """清除所有向量"""
        try:
            if self.index_file.exists():
                self.index_file.unlink()
            
            if self.mapping_file.exists():
                self.mapping_file.unlink()
            
            self.vector_to_entity = {}
            self.vectors = []
            self._initialize_index()
            
            self.logger.info("Cleared all vectors")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing vectors: {e}")
            return False

class VectorEmbedder:
    """向量嵌入生成器"""
    
    def __init__(self, embedding_dim: int = 1536):
        self.logger = logging.getLogger(__name__)
        self.embedding_dim = embedding_dim
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            self.model_available = True
            self.logger.info("Loaded sentence transformer model")
        except ImportError:
            self.logger.warning("Sentence transformers not available, using fallback embedding")
            self.model = None
            self.model_available = False
    
    def generate_embedding(self, text: str) -> List[float]:
        """生成文本的向量嵌入"""
        try:
            if self.model_available and self.model:
                embedding = self.model.encode(text)
                return embedding.tolist()
            else:
                return self._fallback_embedding(text)
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            return self._fallback_embedding(text)
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """回退嵌入方法"""
        import hashlib
        
        text_hash = hashlib.md5(text.encode()).hexdigest()
        hash_int = int(text_hash, 16)
        
        embedding = []
        for i in range(self.embedding_dim):
            byte_val = (hash_int >> (i * 8)) & 0xFF
            normalized_val = byte_val / 255.0
            embedding.append(normalized_val)
        
        return embedding
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量生成向量嵌入"""
        try:
            if self.model_available and self.model:
                embeddings = self.model.encode(texts)
                return [emb.tolist() for emb in embeddings]
            else:
                return [self._fallback_embedding(text) for text in texts]
        except Exception as e:
            self.logger.error(f"Error generating batch embeddings: {e}")
            return [self._fallback_embedding(text) for text in texts]

# 创建全局向量存储和嵌入生成器实例
vector_store = VectorStore()
vector_embedder = VectorEmbedder()