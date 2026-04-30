"""
性能测试用例
"""
import pytest
import time
import logging
import concurrent.futures
from src.ai_loop.engine import AILoopEngine
from src.knowledge_base import knowledge_manager, cache_manager, KnowledgeEntity, KnowledgeQuery, KnowledgeType

logging.basicConfig(level=logging.INFO)

class TestPerformance:
    """性能测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.engine = AILoopEngine()
        self.engine.reset_performance_metrics()
        
        # 添加测试数据
        self.test_entities = []
        for i in range(100):
            entity = KnowledgeEntity(
                type=KnowledgeType.DOMAIN_KNOWLEDGE,
                title=f"性能测试实体{i}",
                content=f"这是性能测试实体{i}的内容，用于测试知识库查询性能。" * 10,
                source="performance_test",
                tags=["performance", "test"]
            )
            knowledge_manager.add_entity(entity, "admin_user")
            self.test_entities.append(entity)
    
    def teardown_method(self):
        """清理测试环境"""
        for entity in self.test_entities:
            knowledge_manager.delete_entity(entity.id, "admin_user")
    
    def test_ai_loop_throughput(self):
        """测试AI Loop引擎吞吐量"""
        start_time = time.time()
        request_count = 5
        
        for i in range(request_count):
            request_data = {
                'task_type': 'general',
                'context': f'性能测试请求{i}',
                'user_id': 'test_user'
            }
            self.engine.process_request(request_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n=== AI Loop吞吐量测试 ===")
        print(f"请求数量: {request_count}")
        print(f"总耗时: {duration:.2f}秒")
        print(f"吞吐量: {request_count/duration:.2f} 请求/秒")
        print(f"平均响应时间: {duration/request_count*1000:.2f} 毫秒")
        
        # AI调用需要时间，设置较宽松的阈值
        assert duration < 180, f"吞吐量测试超时，耗时{duration:.2f}秒"
    
    def test_knowledge_base_query_performance(self):
        """测试知识库查询性能"""
        query = KnowledgeQuery(
            query_text="性能测试",
            query_type="keyword",
            limit=10,
            threshold=0.5
        )
        
        # 预热
        knowledge_manager.query_entities(query, "admin_user")
        
        # 实际测试
        start_time = time.time()
        query_count = 50
        
        for i in range(query_count):
            knowledge_manager.query_entities(query, "admin_user")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n=== 知识库查询性能测试 ===")
        print(f"查询次数: {query_count}")
        print(f"总耗时: {duration:.2f}秒")
        print(f"吞吐量: {query_count/duration:.2f} 查询/秒")
        print(f"平均响应时间: {duration/query_count*1000:.2f} 毫秒")
        
        assert duration < 10, f"知识库查询性能测试超时，耗时{duration:.2f}秒"
    
    def test_cache_performance(self):
        """测试缓存性能"""
        # 设置缓存
        for i in range(50):
            cache_manager.set_entity(f"cache_test_{i}", {"data": f"value_{i}"})
        
        # 测试缓存命中性能
        start_time = time.time()
        access_count = 100
        
        for i in range(access_count):
            cache_manager.get_entity(f"cache_test_{i % 50}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        stats = cache_manager.get_stats()
        
        print(f"\n=== 缓存性能测试 ===")
        print(f"访问次数: {access_count}")
        print(f"总耗时: {duration:.2f}秒")
        print(f"吞吐量: {access_count/duration:.2f} 访问/秒")
        print(f"平均响应时间: {duration/access_count*1000:.2f} 毫秒")
        print(f"缓存命中率: {stats['hits']/(stats['hits']+stats['misses'])*100:.2f}%")
        
        assert duration < 1, f"缓存性能测试超时，耗时{duration:.2f}秒"
    
    def test_concurrent_requests(self):
        """测试并发请求处理"""
        def process_request(i):
            request_data = {
                'task_type': 'general',
                'context': f'并发测试请求{i}',
                'user_id': 'test_user'
            }
            return self.engine.process_request(request_data)
        
        start_time = time.time()
        concurrent_count = 5
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_count) as executor:
            futures = [executor.submit(process_request, i) for i in range(concurrent_count)]
            results = [f.result() for f in futures]
        
        end_time = time.time()
        duration = end_time - start_time
        
        success_count = sum(1 for r in results if r.get('success', False))
        
        print(f"\n=== 并发请求测试 ===")
        print(f"并发数: {concurrent_count}")
        print(f"总耗时: {duration:.2f}秒")
        print(f"成功率: {success_count/concurrent_count*100:.2f}%")
        
        assert success_count == concurrent_count, f"并发请求测试失败，成功{success_count}/{concurrent_count}"
    
    def test_entity_crud_performance(self):
        """测试实体CRUD性能"""
        # 测试创建性能
        start_time = time.time()
        create_count = 20
        created_ids = []
        
        for i in range(create_count):
            entity = KnowledgeEntity(
                type=KnowledgeType.DOMAIN_KNOWLEDGE,
                title=f"CRUD测试实体{i}",
                content=f"CRUD测试内容{i}",
                source="crud_test"
            )
            entity_id = knowledge_manager.add_entity(entity, "admin_user")
            created_ids.append(entity_id)
        
        create_duration = time.time() - start_time
        
        # 测试读取性能
        start_time = time.time()
        for entity_id in created_ids:
            knowledge_manager.get_entity(entity_id, "admin_user")
        read_duration = time.time() - start_time
        
        # 测试更新性能
        start_time = time.time()
        for entity_id in created_ids:
            knowledge_manager.update_entity(entity_id, {"title": "更新后"}, "admin_user")
        update_duration = time.time() - start_time
        
        # 测试删除性能
        start_time = time.time()
        for entity_id in created_ids:
            knowledge_manager.delete_entity(entity_id, "admin_user")
        delete_duration = time.time() - start_time
        
        print(f"\n=== 实体CRUD性能测试 ===")
        print(f"操作数量: {create_count}")
        print(f"创建耗时: {create_duration:.2f}秒 ({create_count/create_duration:.2f}/秒)")
        print(f"读取耗时: {read_duration:.2f}秒 ({create_count/read_duration:.2f}/秒)")
        print(f"更新耗时: {update_duration:.2f}秒 ({create_count/update_duration:.2f}/秒)")
        print(f"删除耗时: {delete_duration:.2f}秒 ({create_count/delete_duration:.2f}/秒)")
        
        assert create_duration < 5, f"创建性能测试超时"
        assert read_duration < 2, f"读取性能测试超时"
        assert update_duration < 3, f"更新性能测试超时"
        assert delete_duration < 2, f"删除性能测试超时"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
