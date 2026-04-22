from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid

class KnowledgeType(Enum):
    """知识类型枚举"""
    REQUIREMENT = "requirement"
    TECHNICAL = "technical"
    BUSINESS_RULE = "business_rule"
    CONSTRAINT = "constraint"
    BEST_PRACTICE = "best_practice"
    SOLUTION = "solution"
    TEST_CASE = "test_case"
    CODING_TASK = "coding_task"
    USER_FEEDBACK = "user_feedback"
    DOMAIN_KNOWLEDGE = "domain_knowledge"

class KnowledgeStatus(Enum):
    """知识状态枚举"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"

@dataclass
class KnowledgeEntity:
    """知识实体数据模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: KnowledgeType = KnowledgeType.DOMAIN_KNOWLEDGE
    title: str = ""
    content: str = ""
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    status: KnowledgeStatus = KnowledgeStatus.ACTIVE
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    embedding: Optional[List[float]] = None
    confidence_score: float = 1.0
    related_entities: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'type': self.type.value,
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'metadata': self.metadata,
            'tags': self.tags,
            'status': self.status.value,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'embedding': self.embedding,
            'confidence_score': self.confidence_score,
            'related_entities': self.related_entities
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeEntity':
        """从字典创建实体"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            type=KnowledgeType(data.get('type', 'domain_knowledge')),
            title=data.get('title', ''),
            content=data.get('content', ''),
            source=data.get('source', ''),
            metadata=data.get('metadata', {}),
            tags=data.get('tags', []),
            status=KnowledgeStatus(data.get('status', 'active')),
            version=data.get('version', '1.0'),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
            created_by=data.get('created_by', 'system'),
            embedding=data.get('embedding'),
            confidence_score=data.get('confidence_score', 1.0),
            related_entities=data.get('related_entities', [])
        )

@dataclass
class KnowledgeRelation:
    """知识关系数据模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_entity_id: str = ""
    target_entity_id: str = ""
    relation_type: str = "related_to"
    strength: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'source_entity_id': self.source_entity_id,
            'target_entity_id': self.target_entity_id,
            'relation_type': self.relation_type,
            'strength': self.strength,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeRelation':
        """从字典创建关系"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            source_entity_id=data.get('source_entity_id', ''),
            target_entity_id=data.get('target_entity_id', ''),
            relation_type=data.get('relation_type', 'related_to'),
            strength=data.get('strength', 1.0),
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            created_by=data.get('created_by', 'system')
        )

@dataclass
class KnowledgeQuery:
    """知识查询数据模型"""
    query_text: str = ""
    query_type: str = "semantic"
    filters: Dict[str, Any] = field(default_factory=dict)
    limit: int = 10
    threshold: float = 0.7
    include_metadata: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'query_text': self.query_text,
            'query_type': self.query_type,
            'filters': self.filters,
            'limit': self.limit,
            'threshold': self.threshold,
            'include_metadata': self.include_metadata
        }

@dataclass
class KnowledgeResult:
    """知识查询结果数据模型"""
    entity: KnowledgeEntity
    score: float
    relevance: str = "high"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'entity': self.entity.to_dict(),
            'score': self.score,
            'relevance': self.relevance,
            'metadata': self.metadata
        }