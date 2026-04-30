"""
知识库适配器测试用例
"""
import pytest
import logging
from src.knowledge_base.adapters import (
    AdapterFactory, InternalAdapter,
    MilvusAdapter, PineconeAdapter,
    WeaviateAdapter, ChromaDBAdapter
)
from src.knowledge_base.models import KnowledgeEntity, KnowledgeQuery, KnowledgeType, KnowledgeStatus

logging.basicConfig(level=logging.INFO)

class TestAdapters:
    """适配器测试类"""
    
    def test_get_supported_adapters(self):
        """测试获取支持的适配器列表"""
        adapters = AdapterFactory.get_supported_adapters()
        
        assert isinstance(adapters, list)
        assert 'internal' in adapters
        assert 'milvus' in adapters
        assert 'pinecone' in adapters
        assert 'weaviate' in adapters
        assert 'chromadb' in adapters
    
    def test_create_internal_adapter(self):
        """测试创建内部适配器"""
        adapter = AdapterFactory.create_adapter('internal', {})
        
        assert adapter is not None
        assert isinstance(adapter, InternalAdapter)
        
        # 测试连接
        assert adapter.connect() is True
        
        # 测试基本操作
        entity = KnowledgeEntity(
            type=KnowledgeType.DOMAIN_KNOWLEDGE,
            title="适配器测试",
            content="测试内容",
            source="test"
        )
        
        entity_id = adapter.add_entity(entity)
        assert entity_id == entity.id
        
        retrieved = adapter.get_entity(entity_id)
        assert retrieved is not None
        assert retrieved.title == "适配器测试"
        
        adapter.disconnect()
    
    def test_create_milvus_adapter(self):
        """测试创建Milvus适配器（不实际连接）"""
        config = {
            'host': 'localhost',
            'port': 19530,
            'collection_name': 'test_collection'
        }
        
        adapter = AdapterFactory.create_adapter('milvus', config)
        assert adapter is not None
        assert isinstance(adapter, MilvusAdapter)
        
        # 连接可能失败（如果Milvus未运行），这是预期的
        result = adapter.connect()
        # 不断言结果，因为Milvus可能未运行
    
    def test_create_pinecone_adapter(self):
        """测试创建Pinecone适配器（不实际连接）"""
        config = {
            'api_key': 'test_key',
            'environment': 'us-west1-gcp',
            'index_name': 'test_index'
        }
        
        adapter = AdapterFactory.create_adapter('pinecone', config)
        assert adapter is not None
        assert isinstance(adapter, PineconeAdapter)
    
    def test_create_weaviate_adapter(self):
        """测试创建Weaviate适配器（不实际连接）"""
        config = {
            'host': 'localhost',
            'port': 8080,
            'schema_name': 'TestEntity'
        }
        
        adapter = AdapterFactory.create_adapter('weaviate', config)
        assert adapter is not None
        assert isinstance(adapter, WeaviateAdapter)
    
    def test_create_chromadb_adapter(self):
        """测试创建ChromaDB适配器"""
        config = {
            'collection_name': 'test_chroma_collection'
        }
        
        adapter = AdapterFactory.create_adapter('chromadb', config)
        assert adapter is not None
        assert isinstance(adapter, ChromaDBAdapter)
        
        # 测试连接
        result = adapter.connect()
        assert result is True
        
        # 测试基本操作
        entity = KnowledgeEntity(
            type=KnowledgeType.DOMAIN_KNOWLEDGE,
            title="ChromaDB测试",
            content="测试内容",
            source="test"
        )
        
        entity_id = adapter.add_entity(entity)
        assert entity_id == entity.id
        
        retrieved = adapter.get_entity(entity_id)
        assert retrieved is not None
        
        adapter.disconnect()
    
    def test_adapter_factory_fallback(self):
        """测试适配器工厂的回退机制"""
        # 测试未知适配器类型
        adapter = AdapterFactory.create_adapter('unknown_type', {})
        
        # 应该回退到internal适配器
        assert isinstance(adapter, InternalAdapter)
    
    def test_validate_config(self):
        """测试配置验证"""
        # 测试有效的Milvus配置
        milvus_config = {
            'host': 'localhost',
            'port': 19530,
            'collection_name': 'test'
        }
        assert AdapterFactory.validate_config('milvus', milvus_config) is True
        
        # 测试无效的Milvus配置（缺少必要字段）
        invalid_config = {
            'host': 'localhost'
        }
        assert AdapterFactory.validate_config('milvus', invalid_config) is False

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
