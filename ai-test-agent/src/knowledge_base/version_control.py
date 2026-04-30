import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from .models import KnowledgeEntity

class EntityVersion:
    """
    实体版本记录
    """
    
    def __init__(self, entity_id: str, version: int, timestamp: datetime, 
                 action: str, user_id: str, snapshot: Dict[str, Any]):
        self.entity_id = entity_id
        self.version = version
        self.timestamp = timestamp
        self.action = action  # create, update, delete
        self.user_id = user_id
        self.snapshot = snapshot
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'entity_id': self.entity_id,
            'version': self.version,
            'timestamp': self.timestamp.isoformat(),
            'action': self.action,
            'user_id': self.user_id,
            'snapshot': self.snapshot
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EntityVersion':
        return cls(
            entity_id=data['entity_id'],
            version=data['version'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            action=data['action'],
            user_id=data['user_id'],
            snapshot=data['snapshot']
        )

class VersionManager:
    """
    版本控制管理器
    提供实体版本历史记录和回滚功能
    """
    
    def __init__(self, base_dir: str = "data/knowledge_base/versions"):
        self.logger = logging.getLogger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 内存缓存版本信息
        self.version_cache = {}  # {entity_id: List[EntityVersion]}
        
        # 加载已有的版本记录
        self._load_versions()
    
    def _load_versions(self):
        """加载已有的版本记录"""
        for version_file in self.base_dir.glob("*.json"):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for version_data in data:
                        version = EntityVersion.from_dict(version_data)
                        if version.entity_id not in self.version_cache:
                            self.version_cache[version.entity_id] = []
                        self.version_cache[version.entity_id].append(version)
                    
                    # 按版本号排序
                    self.version_cache[version.entity_id].sort(key=lambda v: v.version)
            except Exception as e:
                self.logger.error(f"Error loading versions from {version_file}: {e}")
        
        self.logger.info(f"Loaded version history for {len(self.version_cache)} entities")
    
    def _save_versions(self, entity_id: str):
        """保存实体的版本记录"""
        if entity_id not in self.version_cache:
            return
        
        versions = self.version_cache[entity_id]
        version_file = self.base_dir / f"{entity_id}.json"
        
        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                versions_data = [v.to_dict() for v in versions]
                json.dump(versions_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving versions for {entity_id}: {e}")
    
    def create_version(self, entity: KnowledgeEntity, action: str, user_id: str):
        """
        创建实体版本记录
        
        Args:
            entity: 知识实体
            action: 操作类型 (create, update, delete)
            user_id: 操作用户ID
        """
        if entity.id not in self.version_cache:
            self.version_cache[entity.id] = []
        
        # 获取下一个版本号
        versions = self.version_cache[entity.id]
        next_version = len(versions) + 1
        
        # 创建版本快照
        snapshot = entity.to_dict()
        
        # 创建版本记录
        version = EntityVersion(
            entity_id=entity.id,
            version=next_version,
            timestamp=datetime.now(),
            action=action,
            user_id=user_id,
            snapshot=snapshot
        )
        
        self.version_cache[entity.id].append(version)
        
        # 保存到文件
        self._save_versions(entity.id)
        
        self.logger.info(f"Created version {next_version} for entity {entity.id} (action: {action})")
    
    def get_versions(self, entity_id: str) -> List[EntityVersion]:
        """
        获取实体的所有版本记录
        
        Args:
            entity_id: 实体ID
            
        Returns:
            版本记录列表
        """
        return self.version_cache.get(entity_id, [])
    
    def get_version(self, entity_id: str, version: int) -> Optional[EntityVersion]:
        """
        获取特定版本的记录
        
        Args:
            entity_id: 实体ID
            version: 版本号
            
        Returns:
            版本记录，如果不存在则返回None
        """
        versions = self.version_cache.get(entity_id, [])
        for v in versions:
            if v.version == version:
                return v
        return None
    
    def rollback_to_version(self, entity_id: str, version: int) -> Optional[KnowledgeEntity]:
        """
        回滚到指定版本
        
        Args:
            entity_id: 实体ID
            version: 目标版本号
            
        Returns:
            回滚后的实体，如果失败则返回None
        """
        version_record = self.get_version(entity_id, version)
        
        if not version_record:
            self.logger.error(f"Version {version} not found for entity {entity_id}")
            return None
        
        # 创建回滚的实体
        try:
            entity = KnowledgeEntity.from_dict(version_record.snapshot)
            self.logger.info(f"Rolled back entity {entity_id} to version {version}")
            return entity
        except Exception as e:
            self.logger.error(f"Error rolling back entity {entity_id}: {e}")
            return None
    
    def get_latest_version(self, entity_id: str) -> Optional[EntityVersion]:
        """
        获取实体的最新版本
        
        Args:
            entity_id: 实体ID
            
        Returns:
            最新版本记录，如果不存在则返回None
        """
        versions = self.version_cache.get(entity_id, [])
        if versions:
            return versions[-1]
        return None
    
    def get_version_count(self, entity_id: str) -> int:
        """
        获取实体的版本数量
        
        Args:
            entity_id: 实体ID
            
        Returns:
            版本数量
        """
        return len(self.version_cache.get(entity_id, []))
    
    def get_version_diff(self, entity_id: str, version1: int, version2: int) -> Dict[str, Any]:
        """
        获取两个版本之间的差异
        
        Args:
            entity_id: 实体ID
            version1: 版本1
            version2: 版本2
            
        Returns:
            差异字典
        """
        v1 = self.get_version(entity_id, version1)
        v2 = self.get_version(entity_id, version2)
        
        if not v1 or not v2:
            return {}
        
        diff = {
            'entity_id': entity_id,
            'version_from': version1,
            'version_to': version2,
            'changes': []
        }
        
        snapshot1 = v1.snapshot
        snapshot2 = v2.snapshot
        
        # 比较字段差异
        all_keys = set(snapshot1.keys()) | set(snapshot2.keys())
        
        for key in all_keys:
            val1 = snapshot1.get(key)
            val2 = snapshot2.get(key)
            
            if val1 != val2:
                diff['changes'].append({
                    'field': key,
                    'from': val1,
                    'to': val2
                })
        
        return diff
    
    def delete_version_history(self, entity_id: str):
        """
        删除实体的版本历史
        
        Args:
            entity_id: 实体ID
        """
        if entity_id in self.version_cache:
            del self.version_cache[entity_id]
            
            version_file = self.base_dir / f"{entity_id}.json"
            if version_file.exists():
                version_file.unlink()
            
            self.logger.info(f"Deleted version history for entity {entity_id}")
    
    def get_version_statistics(self) -> Dict[str, Any]:
        """
        获取版本控制统计信息
        
        Returns:
            统计信息字典
        """
        total_versions = sum(len(versions) for versions in self.version_cache.values())
        entities_with_history = len(self.version_cache)
        
        action_counts = {}
        for versions in self.version_cache.values():
            for v in versions:
                action_counts[v.action] = action_counts.get(v.action, 0) + 1
        
        return {
            'total_entities_with_history': entities_with_history,
            'total_versions': total_versions,
            'action_distribution': action_counts,
            'last_updated': datetime.now().isoformat()
        }

# 创建全局版本管理器实例
version_manager = VersionManager()
