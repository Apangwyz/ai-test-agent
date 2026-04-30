"""
知识库模块测试用例
"""
import pytest
import logging
from datetime import datetime
from src.knowledge_base import (
    KnowledgeEntity, KnowledgeQuery, KnowledgeType, KnowledgeStatus,
    knowledge_manager, cache_manager, permission_manager,
    version_manager, audit_logger, AuditAction
)

logging.basicConfig(level=logging.INFO)

class TestKnowledgeBase:
    """知识库模块测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.test_entity = KnowledgeEntity(
            type=KnowledgeType.DOMAIN_KNOWLEDGE,
            title="测试实体",
            content="这是一个测试知识实体的内容",
            source="test",
            tags=["test", "unit_test"]
        )
        
        # 设置测试用户权限
        permission_manager.set_user_role("test_user", "editor")
        permission_manager.set_user_role("admin_user", "admin")
        permission_manager.set_user_role("read_only_user", "user")
    
    def test_add_entity(self):
        """测试添加实体"""
        entity_id = knowledge_manager.add_entity(self.test_entity, "admin_user")
        
        assert entity_id == self.test_entity.id
        assert knowledge_manager.get_entity(entity_id, "admin_user") is not None
    
    def test_get_entity(self):
        """测试获取实体"""
        # 先添加实体
        knowledge_manager.add_entity(self.test_entity, "admin_user")
        
        # 获取实体
        entity = knowledge_manager.get_entity(self.test_entity.id, "admin_user")
        
        assert entity is not None
        assert entity.title == "测试实体"
        assert entity.content == "这是一个测试知识实体的内容"
    
    def test_update_entity(self):
        """测试更新实体"""
        # 先添加实体
        knowledge_manager.add_entity(self.test_entity, "admin_user")
        
        # 更新实体
        updates = {
            'title': '更新后的标题',
            'content': '更新后的内容'
        }
        success = knowledge_manager.update_entity(self.test_entity.id, updates, "admin_user")
        
        assert success is True
        
        # 验证更新
        updated_entity = knowledge_manager.get_entity(self.test_entity.id, "admin_user")
        assert updated_entity.title == '更新后的标题'
        assert updated_entity.content == '更新后的内容'
    
    def test_delete_entity(self):
        """测试删除实体"""
        # 先添加实体
        knowledge_manager.add_entity(self.test_entity, "admin_user")
        
        # 删除实体
        success = knowledge_manager.delete_entity(self.test_entity.id, "admin_user")
        
        assert success is True
        
        # 验证删除
        deleted_entity = knowledge_manager.get_entity(self.test_entity.id, "admin_user")
        assert deleted_entity is None
    
    def test_query_entities(self):
        """测试查询实体"""
        # 添加测试实体
        knowledge_manager.add_entity(self.test_entity, "admin_user")
        
        # 构建查询
        query = KnowledgeQuery(
            query_text="测试",
            query_type="keyword",
            limit=10,
            threshold=0.5
        )
        
        results = knowledge_manager.query_entities(query, "admin_user")
        
        assert isinstance(results, list)
    
    def test_permission_control(self):
        """测试权限控制"""
        # 添加实体
        knowledge_manager.add_entity(self.test_entity, "admin_user")
        
        # 测试只读用户不能写入
        result = knowledge_manager.add_entity(
            KnowledgeEntity(
                type=KnowledgeType.DOMAIN_KNOWLEDGE,
                title="测试2",
                content="内容2",
                source="test"
            ),
            "read_only_user"
        )
        assert result == ""
        
        # 测试只读用户可以读取
        entity = knowledge_manager.get_entity(self.test_entity.id, "read_only_user")
        assert entity is not None
        
        # 测试只读用户不能更新
        success = knowledge_manager.update_entity(self.test_entity.id, {"title": "new"}, "read_only_user")
        assert success is False
        
        # 测试只读用户不能删除
        success = knowledge_manager.delete_entity(self.test_entity.id, "read_only_user")
        assert success is False
    
    def test_cache_manager(self):
        """测试缓存管理器"""
        # 直接使用cache_manager测试缓存功能
        cache_manager.set_entity("test_cache_entity", {"name": "test"})
        
        # 第一次获取（缓存命中，因为已经设置了）
        cached1 = cache_manager.get_entity("test_cache_entity")
        assert cached1 is not None
        
        # 第二次获取（应该命中缓存）
        cached2 = cache_manager.get_entity("test_cache_entity")
        assert cached2 is not None
        
        # 验证缓存命中（第二次获取应该是缓存命中）
        stats = cache_manager.get_stats()
        assert stats['hits'] >= 1
        
        # 验证缓存失效
        cache_manager.invalidate_entity("test_cache_entity")
        cached_after_invalidate = cache_manager.get_entity("test_cache_entity")
        assert cached_after_invalidate is None
    
    def test_version_control(self):
        """测试版本控制"""
        # 添加实体
        knowledge_manager.add_entity(self.test_entity, "admin_user")
        
        # 创建版本记录
        version_manager.create_version(self.test_entity, "create", "admin_user")
        
        # 获取版本
        versions = version_manager.get_versions(self.test_entity.id)
        assert len(versions) >= 1
        
        # 测试回滚
        latest_version = version_manager.get_latest_version(self.test_entity.id)
        if latest_version:
            rolled_back = version_manager.rollback_to_version(self.test_entity.id, latest_version.version)
            assert rolled_back is not None
    
    def test_audit_logging(self):
        """测试审计日志"""
        # 直接记录审计日志
        audit_logger.log(
            action=AuditAction.CREATE,
            user_id='admin_user',
            resource_type='entity',
            resource_id='test_entity_id',
            details={'test': 'value'}
        )
        
        # 获取最近日志
        recent_logs = audit_logger.get_recent_logs(limit=10)
        assert len(recent_logs) >= 1
        
        # 搜索日志
        logs = audit_logger.search_logs({
            'user_id': 'admin_user',
            'resource_type': 'entity'
        })
        
        assert len(logs) >= 1
    
    def test_batch_operations(self):
        """测试批量操作"""
        entities = [
            KnowledgeEntity(
                type=KnowledgeType.DOMAIN_KNOWLEDGE,
                title=f"批量测试实体{i}",
                content=f"内容{i}",
                source="test"
            )
            for i in range(5)
        ]
        
        # 批量添加
        entity_ids = knowledge_manager.batch_add_entities(entities, "admin_user")
        assert len(entity_ids) == 5
        
        # 批量删除
        count = knowledge_manager.batch_delete_entities(entity_ids, "admin_user")
        assert count == 5

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
