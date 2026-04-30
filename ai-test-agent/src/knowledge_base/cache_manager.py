import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict

class CacheManager:
    """
    知识库缓存管理器
    提供查询结果缓存和热门实体预加载功能
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.logger = logging.getLogger(__name__)
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.query_cache = OrderedDict()  # LRU缓存
        self.entity_cache = {}  # 实体缓存
        self.hot_entities = {}  # 热门实体追踪
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'queries_served': 0,
            'avg_cache_time': 0.0
        }
    
    def get_query_result(self, query_key: str) -> Optional[Any]:
        """
        获取缓存的查询结果
        
        Args:
            query_key: 查询的唯一标识
            
        Returns:
            缓存的查询结果，如果不存在或已过期则返回None
        """
        if query_key not in self.query_cache:
            self.cache_stats['misses'] += 1
            return None
        
        entry = self.query_cache[query_key]
        
        # 检查是否过期
        if time.time() - entry['timestamp'] > self.ttl_seconds:
            self._remove_query(query_key)
            self.cache_stats['misses'] += 1
            return None
        
        # 更新访问时间（LRU）
        self.query_cache.move_to_end(query_key)
        self.cache_stats['hits'] += 1
        
        return entry['result']
    
    def set_query_result(self, query_key: str, result: Any):
        """
        设置查询结果缓存
        
        Args:
            query_key: 查询的唯一标识
            result: 查询结果
        """
        # 如果缓存已满，移除最旧的
        if len(self.query_cache) >= self.max_size:
            self.query_cache.popitem(last=False)
            self.cache_stats['evictions'] += 1
        
        self.query_cache[query_key] = {
            'result': result,
            'timestamp': time.time(),
            'access_count': 1
        }
    
    def _remove_query(self, query_key: str):
        """移除查询缓存"""
        if query_key in self.query_cache:
            del self.query_cache[query_key]
    
    def get_entity(self, entity_id: str) -> Optional[Any]:
        """
        获取缓存的实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            缓存的实体，如果不存在或已过期则返回None
        """
        if entity_id not in self.entity_cache:
            self.cache_stats['misses'] += 1
            return None
        
        entry = self.entity_cache[entity_id]
        
        if time.time() - entry['timestamp'] > self.ttl_seconds:
            self._remove_entity(entity_id)
            self.cache_stats['misses'] += 1
            return None
        
        # 更新访问时间
        entry['timestamp'] = time.time()
        entry['access_count'] += 1
        
        # 更新热门实体统计
        self._update_hot_entities(entity_id)
        
        # 更新缓存命中统计
        self.cache_stats['hits'] += 1
        
        return entry['entity']
    
    def set_entity(self, entity_id: str, entity: Any):
        """
        设置实体缓存
        
        Args:
            entity_id: 实体ID
            entity: 实体对象
        """
        self.entity_cache[entity_id] = {
            'entity': entity,
            'timestamp': time.time(),
            'access_count': 1
        }
    
    def _remove_entity(self, entity_id: str):
        """移除实体缓存"""
        if entity_id in self.entity_cache:
            del self.entity_cache[entity_id]
    
    def _update_hot_entities(self, entity_id: str):
        """更新热门实体统计"""
        if entity_id in self.hot_entities:
            self.hot_entities[entity_id] += 1
        else:
            self.hot_entities[entity_id] = 1
    
    def get_hot_entity_ids(self, limit: int = 10) -> List[str]:
        """
        获取热门实体ID列表
        
        Args:
            limit: 返回数量限制
            
        Returns:
            热门实体ID列表（按访问次数排序）
        """
        sorted_entities = sorted(self.hot_entities.items(), key=lambda x: x[1], reverse=True)
        return [entity_id for entity_id, count in sorted_entities[:limit]]
    
    def invalidate_entity(self, entity_id: str):
        """
        使指定实体的缓存失效
        
        Args:
            entity_id: 实体ID
        """
        self._remove_entity(entity_id)
        
        # 同时清除引用此实体的查询缓存
        keys_to_remove = []
        for key, entry in self.query_cache.items():
            try:
                # 检查查询结果中是否包含此实体
                if isinstance(entry['result'], list):
                    for item in entry['result']:
                        if hasattr(item, 'entity') and item.entity.id == entity_id:
                            keys_to_remove.append(key)
                            break
            except Exception:
                pass
        
        for key in keys_to_remove:
            self._remove_query(key)
        
        self.logger.info(f"Invalidated cache for entity: {entity_id}")
    
    def invalidate_all(self):
        """清除所有缓存"""
        self.query_cache.clear()
        self.entity_cache.clear()
        self.hot_entities.clear()
        self.logger.info("All cache invalidated")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计字典
        """
        total_queries = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.cache_stats['hits'] / total_queries if total_queries > 0 else 0.0
        
        return {
            **self.cache_stats,
            'hit_rate': hit_rate,
            'query_cache_size': len(self.query_cache),
            'entity_cache_size': len(self.entity_cache),
            'hot_entity_count': len(self.hot_entities),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds,
            'last_updated': datetime.now().isoformat()
        }
    
    def clear_expired(self):
        """清除过期的缓存项"""
        now = time.time()
        
        # 清除过期的查询缓存
        expired_keys = []
        for key, entry in self.query_cache.items():
            if now - entry['timestamp'] > self.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_query(key)
        
        # 清除过期的实体缓存
        expired_entity_ids = []
        for entity_id, entry in self.entity_cache.items():
            if now - entry['timestamp'] > self.ttl_seconds:
                expired_entity_ids.append(entity_id)
        
        for entity_id in expired_entity_ids:
            self._remove_entity(entity_id)
        
        if expired_keys or expired_entity_ids:
            self.logger.info(f"Cleared {len(expired_keys)} expired queries and {len(expired_entity_ids)} expired entities")

# 创建全局缓存管理器实例
cache_manager = CacheManager(max_size=500, ttl_seconds=1800)
