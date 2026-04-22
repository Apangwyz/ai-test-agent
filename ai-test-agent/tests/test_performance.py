import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time
import threading
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceTester:
    """性能测试器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = []
    
    def test_knowledge_base_performance(self):
        """测试知识库性能"""
        logger.info("=== 测试知识库性能 ===")
        
        try:
            from src.knowledge_base import knowledge_manager, KnowledgeEntity, KnowledgeType, KnowledgeQuery, query_service
            
            # 测试1: 批量插入性能
            logger.info("测试1: 批量插入性能")
            start_time = time.time()
            
            entities = []
            for i in range(100):
                entity = KnowledgeEntity(
                    type=KnowledgeType.REQUIREMENT,
                    title=f"性能测试需求 {i}",
                    content=f"这是第 {i} 个性能测试需求描述",
                    source="performance_test",
                    tags=["test", "performance"]
                )
                entities.append(entity)
            
            for entity in entities:
                knowledge_manager.add_entity(entity)
            
            insert_time = time.time() - start_time
            logger.info(f"✓ 批量插入100个实体耗时: {insert_time:.3f}s")
            logger.info(f"  平均每个实体: {insert_time/100*1000:.2f}ms")
            
            # 测试2: 查询性能
            logger.info("测试2: 查询性能")
            start_time = time.time()
            
            query = KnowledgeQuery(
                query_text="性能测试",
                query_type="keyword",
                limit=10
            )
            
            for _ in range(50):
                query_service.query(query)
            
            query_time = time.time() - start_time
            logger.info(f"✓ 执行50次查询耗时: {query_time:.3f}s")
            logger.info(f"  平均每次查询: {query_time/50*1000:.2f}ms")
            
            # 测试3: 获取统计信息性能
            logger.info("测试3: 获取统计信息性能")
            start_time = time.time()
            
            for _ in range(20):
                knowledge_manager.get_statistics()
            
            stats_time = time.time() - start_time
            logger.info(f"✓ 执行20次统计查询耗时: {stats_time:.3f}s")
            logger.info(f"  平均每次统计: {stats_time/20*1000:.2f}ms")
            
            self.test_results.append({
                'module': 'knowledge_base',
                'insert_time': insert_time,
                'query_time': query_time,
                'stats_time': stats_time,
                'status': 'passed'
            })
            
            logger.info("=== 知识库性能测试完成 ===\n")
            return True
            
        except Exception as e:
            logger.error(f"✗ 知识库性能测试失败: {e}")
            self.test_results.append({
                'module': 'knowledge_base',
                'status': 'failed',
                'error': str(e)
            })
            return False
    
    def test_feedback_system_performance(self):
        """测试反馈系统性能"""
        logger.info("=== 测试反馈系统性能 ===")
        
        try:
            from src.feedback import feedback_manager, feedback_collector, FeedbackType, FeedbackCategory
            
            # 测试1: 批量反馈收集性能
            logger.info("测试1: 批量反馈收集性能")
            start_time = time.time()
            
            feedbacks_data = []
            for i in range(50):
                feedback_data = {
                    'user_id': f'performance_test_user_{i}',
                    'feedback_type': 'positive',
                    'category': 'user_experience',
                    'title': f'性能测试反馈 {i}',
                    'description': f'这是第 {i} 个性能测试反馈',
                    'rating': 4,
                    'tags': ['test', 'performance']
                }
                feedbacks_data.append(feedback_data)
            
            for feedback_data in feedbacks_data:
                feedback_collector.collect_feedback(feedback_data)
            
            collect_time = time.time() - start_time
            logger.info(f"✓ 收集50个反馈耗时: {collect_time:.3f}s")
            logger.info(f"  平均每个反馈: {collect_time/50*1000:.2f}ms")
            
            # 测试2: 反馈分析性能
            logger.info("测试2: 反馈分析性能")
            start_time = time.time()
            
            from src.feedback import feedback_analyzer
            for _ in range(10):
                feedback_analyzer.analyze_feedbacks(days=30)
            
            analysis_time = time.time() - start_time
            logger.info(f"✓ 执行10次反馈分析耗时: {analysis_time:.3f}s")
            logger.info(f"  平均每次分析: {analysis_time/10*1000:.2f}ms")
            
            self.test_results.append({
                'module': 'feedback_system',
                'collect_time': collect_time,
                'analysis_time': analysis_time,
                'status': 'passed'
            })
            
            logger.info("=== 反馈系统性能测试完成 ===\n")
            return True
            
        except Exception as e:
            logger.error(f"✗ 反馈系统性能测试失败: {e}")
            self.test_results.append({
                'module': 'feedback_system',
                'status': 'failed',
                'error': str(e)
            })
            return False
    
    def test_prompt_generation_performance(self):
        """测试提示词生成性能"""
        logger.info("=== 测试提示词生成性能 ===")
        
        try:
            from src.prompt_engineering import prompt_generator
            
            # 测试1: 基础提示词生成性能
            logger.info("测试1: 基础提示词生成性能")
            start_time = time.time()
            
            for _ in range(100):
                prompt_generator.generate_prompt(
                    task_type='requirement_analysis',
                    context='系统需要支持用户管理功能',
                    use_knowledge=False
                )
            
            basic_prompt_time = time.time() - start_time
            logger.info(f"✓ 生成100个基础提示词耗时: {basic_prompt_time:.3f}s")
            logger.info(f"  平均每个提示词: {basic_prompt_time/100*1000:.2f}ms")
            
            # 测试2: 知识增强提示词生成性能
            logger.info("测试2: 知识增强提示词生成性能")
            start_time = time.time()
            
            for _ in range(50):
                prompt_generator.generate_prompt(
                    task_type='technical_solution',
                    context='设计一个用户管理系统',
                    use_knowledge=True
                )
            
            enhanced_prompt_time = time.time() - start_time
            logger.info(f"✓ 生成50个知识增强提示词耗时: {enhanced_prompt_time:.3f}s")
            logger.info(f"  平均每个提示词: {enhanced_prompt_time/50*1000:.2f}ms")
            
            # 测试3: 自适应提示词生成性能
            logger.info("测试3: 自适应提示词生成性能")
            start_time = time.time()
            
            for _ in range(50):
                prompt_generator.generate_adaptive_prompt(
                    task_type='clarification',
                    context='需求描述不够清晰',
                    user_preferences={'detailed_output': True}
                )
            
            adaptive_prompt_time = time.time() - start_time
            logger.info(f"✓ 生成50个自适应提示词耗时: {adaptive_prompt_time:.3f}s")
            logger.info(f"  平均每个提示词: {adaptive_prompt_time/50*1000:.2f}ms")
            
            self.test_results.append({
                'module': 'prompt_generation',
                'basic_prompt_time': basic_prompt_time,
                'enhanced_prompt_time': enhanced_prompt_time,
                'adaptive_prompt_time': adaptive_prompt_time,
                'status': 'passed'
            })
            
            logger.info("=== 提示词生成性能测试完成 ===\n")
            return True
            
        except Exception as e:
            logger.error(f"✗ 提示词生成性能测试失败: {e}")
            self.test_results.append({
                'module': 'prompt_generation',
                'status': 'failed',
                'error': str(e)
            })
            return False
    
    def test_concurrent_performance(self):
        """测试并发性能"""
        logger.info("=== 测试并发性能 ===")
        
        try:
            from src.knowledge_base import knowledge_manager, KnowledgeEntity, KnowledgeType
            
            # 测试并发插入性能
            logger.info("测试1: 并发插入性能")
            
            def insert_entities(thread_id: int):
                for i in range(10):
                    entity = KnowledgeEntity(
                        type=KnowledgeType.REQUIREMENT,
                        title=f"并发测试需求 {thread_id}-{i}",
                        content=f"这是线程 {thread_id} 的第 {i} 个并发测试需求",
                        source="concurrent_test",
                        tags=["test", "concurrent"]
                    )
                    knowledge_manager.add_entity(entity)
            
            start_time = time.time()
            threads = []
            
            for i in range(10):
                thread = threading.Thread(target=insert_entities, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            concurrent_time = time.time() - start_time
            logger.info(f"✓ 10个线程并发插入100个实体耗时: {concurrent_time:.3f}s")
            logger.info(f"  平均每个实体: {concurrent_time/100*1000:.2f}ms")
            
            # 测试并发查询性能
            logger.info("测试2: 并发查询性能")
            
            from src.knowledge_base import query_service, KnowledgeQuery
            
            def query_entities(thread_id: int):
                query = KnowledgeQuery(
                    query_text="并发测试",
                    query_type="keyword",
                    limit=10
                )
                for _ in range(10):
                    query_service.query(query)
            
            start_time = time.time()
            threads = []
            
            for i in range(10):
                thread = threading.Thread(target=query_entities, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            concurrent_query_time = time.time() - start_time
            logger.info(f"✓ 10个线程并发执行100次查询耗时: {concurrent_query_time:.3f}s")
            logger.info(f"  平均每次查询: {concurrent_query_time/100*1000:.2f}ms")
            
            self.test_results.append({
                'module': 'concurrent_performance',
                'concurrent_insert_time': concurrent_time,
                'concurrent_query_time': concurrent_query_time,
                'status': 'passed'
            })
            
            logger.info("=== 并发性能测试完成 ===\n")
            return True
            
        except Exception as e:
            logger.error(f"✗ 并发性能测试失败: {e}")
            self.test_results.append({
                'module': 'concurrent_performance',
                'status': 'failed',
                'error': str(e)
            })
            return False
    
    def test_memory_usage(self):
        """测试内存使用"""
        logger.info("=== 测试内存使用 ===")
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            # 测试前内存使用
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            logger.info(f"初始内存使用: {initial_memory:.2f} MB")
            
            # 执行一些操作
            from src.knowledge_base import knowledge_manager, KnowledgeEntity, KnowledgeType, query_service, KnowledgeQuery
            
            # 创建大量实体
            for i in range(1000):
                entity = KnowledgeEntity(
                    type=KnowledgeType.REQUIREMENT,
                    title=f"内存测试需求 {i}",
                    content=f"这是第 {i} 个内存测试需求描述" * 10,
                    source="memory_test",
                    tags=["test", "memory"]
                )
                knowledge_manager.add_entity(entity)
            
            # 执行查询
            query = KnowledgeQuery(
                query_text="内存测试",
                query_type="keyword",
                limit=50
            )
            query_service.query(query)
            
            # 测试后内存使用
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            logger.info(f"最终内存使用: {final_memory:.2f} MB")
            logger.info(f"内存增加: {memory_increase:.2f} MB")
            logger.info(f"平均每个实体内存: {memory_increase/1000*1024:.2f} KB")
            
            self.test_results.append({
                'module': 'memory_usage',
                'initial_memory': initial_memory,
                'final_memory': final_memory,
                'memory_increase': memory_increase,
                'status': 'passed'
            })
            
            logger.info("=== 内存使用测试完成 ===\n")
            return True
            
        except ImportError:
            logger.warning("⚠ psutil未安装，跳过内存使用测试")
            return True
        except Exception as e:
            logger.error(f"✗ 内存使用测试失败: {e}")
            self.test_results.append({
                'module': 'memory_usage',
                'status': 'failed',
                'error': str(e)
            })
            return False
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能测试报告"""
        report = {
            'test_time': datetime.now().isoformat(),
            'total_tests': len(self.test_results),
            'passed_tests': sum(1 for result in self.test_results if result.get('status') == 'passed'),
            'failed_tests': sum(1 for result in self.test_results if result.get('status') == 'failed'),
            'test_results': self.test_results
        }
        
        # 计算性能指标
        performance_metrics = {}
        for result in self.test_results:
            if result.get('status') == 'passed':
                module = result['module']
                performance_metrics[module] = {
                    key: value for key, value in result.items() 
                    if key not in ['module', 'status', 'error']
                }
        
        report['performance_metrics'] = performance_metrics
        
        return report

def main():
    """主测试函数"""
    logger.info("开始AI Loop性能测试\n")
    logger.info(f"测试时间: {datetime.now().isoformat()}\n")
    
    tester = PerformanceTester()
    
    # 执行各项性能测试
    tester.test_knowledge_base_performance()
    tester.test_feedback_system_performance()
    tester.test_prompt_generation_performance()
    tester.test_concurrent_performance()
    tester.test_memory_usage()
    
    # 生成性能报告
    report = tester.generate_performance_report()
    
    # 输出测试结果
    logger.info("\n=== 性能测试结果汇总 ===")
    logger.info(f"总测试数: {report['total_tests']}")
    logger.info(f"通过测试: {report['passed_tests']}")
    logger.info(f"失败测试: {report['failed_tests']}")
    logger.info(f"成功率: {report['passed_tests']/report['total_tests']*100:.1f}%")
    
    logger.info("\n=== 性能指标详情 ===")
    for module, metrics in report['performance_metrics'].items():
        logger.info(f"\n{module}:")
        for key, value in metrics.items():
            if 'time' in key:
                logger.info(f"  {key}: {value:.3f}s")
            elif 'memory' in key:
                logger.info(f"  {key}: {value:.2f} MB")
            else:
                logger.info(f"  {key}: {value}")
    
    if report['passed_tests'] == report['total_tests']:
        logger.info("\n🎉 所有性能测试通过！")
        return 0
    else:
        logger.info(f"\n⚠ 有 {report['failed_tests']} 个测试失败")
        return 1

if __name__ == "__main__":
    exit(main())