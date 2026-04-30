import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from ..models import KnowledgeEntity, KnowledgeQuery, KnowledgeResult, KnowledgeStatus

class BaseAdapter(ABC):
    """
    知识库适配器抽象基类
    定义统一的知识库操作接口
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """连接到知识库"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """断开连接"""
        pass
    
    @abstractmethod
    def add_entity(self, entity: KnowledgeEntity) -> str:
        """添加知识实体"""
        pass
    
    @abstractmethod
    def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """获取知识实体"""
        pass
    
    @abstractmethod
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """更新知识实体"""
        pass
    
    @abstractmethod
    def delete_entity(self, entity_id: str) -> bool:
        """删除知识实体"""
        pass
    
    @abstractmethod
    def query(self, query: KnowledgeQuery) -> List[KnowledgeResult]:
        """查询知识实体"""
        pass
    
    @abstractmethod
    def search_vectors(self, query_vector: List[float], k: int = 10) -> List[Tuple[str, float]]:
        """向量搜索"""
        pass
    
    @abstractmethod
    def batch_add_entities(self, entities: List[KnowledgeEntity]) -> List[str]:
        """批量添加实体"""
        pass
    
    @abstractmethod
    def batch_delete_entities(self, entity_ids: List[str]) -> int:
        """批量删除实体"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        pass
    
    @abstractmethod
    def create_index(self, field_name: str) -> bool:
        """创建索引"""
        pass
    
    @abstractmethod
    def drop_index(self, field_name: str) -> bool:
        """删除索引"""
        pass
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.connected
    
    def _calculate_relevance(self, score: float) -> str:
        """计算相关性等级"""
        if score > 0.8:
            return "high"
        elif score > 0.6:
            return "medium"
        else:
            return "low"
    
    def _validate_query(self, query: KnowledgeQuery) -> bool:
        """验证查询参数"""
        if not query.query_text:
            self.logger.warning("Query text is empty")
            return False
        if query.limit < 1:
            self.logger.warning("Query limit must be at least 1")
            return False
        if query.threshold < 0 or query.threshold > 1:
            self.logger.warning("Query threshold must be between 0 and 1")
            return False
        return True
