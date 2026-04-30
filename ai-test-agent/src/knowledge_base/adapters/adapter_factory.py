import logging
from typing import Dict, Any
from .base_adapter import BaseAdapter
from .internal_adapter import InternalAdapter
from .milvus_adapter import MilvusAdapter
from .pinecone_adapter import PineconeAdapter
from .weaviate_adapter import WeaviateAdapter
from .chromadb_adapter import ChromaDBAdapter

class AdapterFactory:
    """
    知识库适配器工厂
    根据配置创建相应的适配器实例
    """
    
    _adapter_types = {
        'internal': InternalAdapter,
        'milvus': MilvusAdapter,
        'pinecone': PineconeAdapter,
        'weaviate': WeaviateAdapter,
        'chromadb': ChromaDBAdapter
    }
    
    @staticmethod
    def create_adapter(provider_type: str, config: Dict[str, Any]) -> BaseAdapter:
        """
        创建适配器实例
        
        Args:
            provider_type: 适配器类型 (internal, milvus, pinecone, weaviate, chromadb)
            config: 适配器配置
        
        Returns:
            BaseAdapter: 适配器实例
        """
        logger = logging.getLogger(__name__)
        
        # 默认使用internal适配器
        if provider_type not in AdapterFactory._adapter_types:
            logger.warning(f"Unknown adapter type: {provider_type}, falling back to internal")
            provider_type = 'internal'
        
        adapter_class = AdapterFactory._adapter_types[provider_type]
        
        try:
            adapter = adapter_class(config)
            logger.info(f"Created {provider_type} adapter")
            return adapter
        except Exception as e:
            logger.error(f"Failed to create {provider_type} adapter: {e}")
            # 失败时回退到internal适配器
            logger.info("Falling back to internal adapter")
            return InternalAdapter({})
    
    @staticmethod
    def get_supported_adapters() -> list:
        """
        获取支持的适配器类型列表
        
        Returns:
            list: 支持的适配器类型名称列表
        """
        return list(AdapterFactory._adapter_types.keys())
    
    @staticmethod
    def validate_config(provider_type: str, config: Dict[str, Any]) -> bool:
        """
        验证配置是否完整
        
        Args:
            provider_type: 适配器类型
            config: 配置字典
        
        Returns:
            bool: 配置是否有效
        """
        required_configs = {
            'internal': [],
            'milvus': ['host', 'port', 'collection_name'],
            'pinecone': ['api_key', 'environment', 'index_name'],
            'weaviate': ['host', 'port', 'schema_name'],
            'chromadb': ['collection_name']
        }
        
        if provider_type not in required_configs:
            return False
        
        required = required_configs[provider_type]
        missing = [key for key in required if key not in config or not config[key]]
        
        if missing:
            logging.getLogger(__name__).warning(f"Missing required config for {provider_type}: {missing}")
            return False
        
        return True
    
    @staticmethod
    def create_and_connect(provider_type: str, config: Dict[str, Any]) -> BaseAdapter:
        """
        创建适配器并连接
        
        Args:
            provider_type: 适配器类型
            config: 适配器配置
        
        Returns:
            BaseAdapter: 已连接的适配器实例
        """
        adapter = AdapterFactory.create_adapter(provider_type, config)
        
        if adapter:
            try:
                if adapter.connect():
                    return adapter
                else:
                    # 连接失败，尝试回退到internal
                    logging.getLogger(__name__).warning(f"Failed to connect to {provider_type}, falling back to internal")
                    return InternalAdapter({})
            except Exception as e:
                logging.getLogger(__name__).error(f"Error connecting to {provider_type}: {e}")
                return InternalAdapter({})
        
        return InternalAdapter({})
