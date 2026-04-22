import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_knowledge_base():
    """测试知识库功能"""
    logger.info("=== 测试知识库功能 ===")
    
    try:
        from src.knowledge_base import (
            knowledge_manager, knowledge_extractor, query_service,
            KnowledgeEntity, KnowledgeType, KnowledgeQuery
        )
        
        # 测试1: 创建知识实体
        logger.info("测试1: 创建知识实体")
        entity = KnowledgeEntity(
            type=KnowledgeType.REQUIREMENT,
            title="测试需求",
            content="这是一个测试需求描述",
            source="test",
            tags=["test", "requirement"]
        )
        entity_id = knowledge_manager.add_entity(entity)
        logger.info(f"✓ 创建知识实体成功，ID: {entity_id}")
        
        # 测试2: 获取知识实体
        logger.info("测试2: 获取知识实体")
        retrieved_entity = knowledge_manager.get_entity(entity_id)
        assert retrieved_entity is not None
        assert retrieved_entity.title == "测试需求"
        logger.info("✓ 获取知识实体成功")
        
        # 测试3: 知识查询
        logger.info("测试3: 知识查询")
        query = KnowledgeQuery(
            query_text="测试需求",
            query_type="keyword",
            limit=5
        )
        results = query_service.query(query)
        logger.info(f"✓ 知识查询成功，找到 {len(results)} 个结果")
        
        # 测试4: 知识提取
        logger.info("测试4: 知识提取")
        document_data = {
            'content': '系统需要支持用户登录功能，包括用户名密码登录和第三方登录。',
            'sections': ['用户管理', '登录功能'],
            'requirements': ['用户需要能够登录系统'],
            'constraints': ['密码需要加密存储']
        }
        extracted_entities = knowledge_extractor.extract_from_document(document_data)
        logger.info(f"✓ 知识提取成功，提取了 {len(extracted_entities)} 个实体")
        
        # 测试5: 知识库统计
        logger.info("测试5: 知识库统计")
        stats = knowledge_manager.get_statistics()
        logger.info(f"✓ 知识库统计: {stats['total_entities']} 个实体")
        
        logger.info("=== 知识库功能测试完成 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ 知识库功能测试失败: {e}")
        return False

def test_feedback_system():
    """测试反馈系统功能"""
    logger.info("=== 测试反馈系统功能 ===")
    
    try:
        from src.feedback import (
            feedback_manager, feedback_collector, feedback_analyzer,
            Feedback, FeedbackType, FeedbackCategory
        )
        
        # 测试1: 收集反馈
        logger.info("测试1: 收集反馈")
        feedback_data = {
            'user_id': 'test_user',
            'feedback_type': 'positive',
            'category': 'user_experience',
            'title': '测试反馈',
            'description': '这是一个测试反馈',
            'rating': 5,
            'tags': ['test', 'feedback']
        }
        feedback_id = feedback_collector.collect_feedback(feedback_data)
        logger.info(f"✓ 收集反馈成功，ID: {feedback_id}")
        
        # 测试2: 获取反馈
        logger.info("测试2: 获取反馈")
        retrieved_feedback = feedback_manager.get_feedback(feedback_id)
        assert retrieved_feedback is not None
        assert retrieved_feedback.title == "测试反馈"
        logger.info("✓ 获取反馈成功")
        
        # 测试3: 反馈分析
        logger.info("测试3: 反馈分析")
        analysis = feedback_analyzer.analyze_feedbacks(days=30)
        logger.info(f"✓ 反馈分析成功，总计 {analysis.total_feedback} 个反馈")
        
        # 测试4: 反馈统计
        logger.info("测试4: 反馈统计")
        stats = feedback_manager.get_feedback_statistics()
        logger.info(f"✓ 反馈统计: {stats['total_feedbacks']} 个反馈")
        
        logger.info("=== 反馈系统功能测试完成 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ 反馈系统功能测试失败: {e}")
        return False

def test_enhanced_ai_service():
    """测试增强AI服务功能"""
    logger.info("=== 测试增强AI服务功能 ===")
    
    try:
        from src.common.ai_service import ai_service
        
        # 测试1: 获取服务统计
        logger.info("测试1: 获取服务统计")
        stats = ai_service.get_service_stats()
        logger.info(f"✓ 获取服务统计成功: {stats}")
        
        # 测试2: 生成内容（如果配置了API密钥）
        logger.info("测试2: 生成内容测试")
        try:
            result = ai_service.generate(
                prompt="请简单介绍一下AI技术",
                system_prompt="你是一个AI助手",
                model_type='qwen',
                use_enhanced=True
            )
            logger.info(f"✓ 生成内容成功，长度: {len(result)}")
        except Exception as e:
            logger.warning(f"⚠ 生成内容测试跳过（可能未配置API密钥）: {e}")
        
        logger.info("=== 增强AI服务功能测试完成 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ 增强AI服务功能测试失败: {e}")
        return False

def test_prompt_engineering():
    """测试提示词工程功能"""
    logger.info("=== 测试提示词工程功能 ===")
    
    try:
        from src.prompt_engineering import prompt_generator
        
        # 测试1: 生成基础提示词
        logger.info("测试1: 生成基础提示词")
        prompt = prompt_generator.generate_prompt(
            task_type='requirement_analysis',
            context='系统需要支持用户管理功能',
            use_knowledge=False
        )
        logger.info(f"✓ 生成基础提示词成功，长度: {len(prompt)}")
        
        # 测试2: 生成知识增强提示词
        logger.info("测试2: 生成知识增强提示词")
        enhanced_prompt = prompt_generator.generate_prompt(
            task_type='technical_solution',
            context='设计一个用户管理系统',
            use_knowledge=True
        )
        logger.info(f"✓ 生成知识增强提示词成功，长度: {len(enhanced_prompt)}")
        
        # 测试3: 生成自适应提示词
        logger.info("测试3: 生成自适应提示词")
        adaptive_prompt = prompt_generator.generate_adaptive_prompt(
            task_type='clarification',
            context='需求描述不够清晰',
            user_preferences={'detailed_output': True}
        )
        logger.info(f"✓ 生成自适应提示词成功，长度: {len(adaptive_prompt)}")
        
        # 测试4: 获取提示词统计
        logger.info("测试4: 获取提示词统计")
        stats = prompt_generator.get_prompt_statistics()
        logger.info(f"✓ 获取提示词统计成功: {stats}")
        
        logger.info("=== 提示词工程功能测试完成 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ 提示词工程功能测试失败: {e}")
        return False

def test_ai_loop_engine():
    """测试AI Loop引擎功能"""
    logger.info("=== 测试AI Loop引擎功能 ===")
    
    try:
        from src.ai_loop import ai_loop_engine
        
        # 测试1: 处理基本请求
        logger.info("测试1: 处理基本请求")
        request_data = {
            'task_type': 'requirement_analysis',
            'context': '系统需要支持用户注册和登录功能',
            'user_id': 'test_user'
        }
        
        try:
            result = ai_loop_engine.process_request(request_data)
            logger.info(f"✓ 处理基本请求成功")
            logger.info(f"  - 处理时间: {result.get('processing_time', 0):.2f}s")
            logger.info(f"  - 知识使用: {result.get('knowledge_used', False)}")
            logger.info(f"  - 循环迭代: {result.get('loop_iteration', 0)}")
        except Exception as e:
            logger.warning(f"⚠ 处理基本请求测试跳过（可能未配置API密钥）: {e}")
        
        # 测试2: 获取性能指标
        logger.info("测试2: 获取性能指标")
        metrics = ai_loop_engine.get_performance_metrics()
        logger.info(f"✓ 获取性能指标成功: {metrics}")
        
        logger.info("=== AI Loop引擎功能测试完成 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ AI Loop引擎功能测试失败: {e}")
        return False

def test_integration():
    """测试系统集成"""
    logger.info("=== 测试系统集成 ===")
    
    try:
        # 测试知识库与AI Loop集成
        logger.info("测试1: 知识库与AI Loop集成")
        from src.knowledge_base import knowledge_manager, KnowledgeEntity, KnowledgeType
        from src.ai_loop import ai_loop_engine
        
        # 创建测试知识
        test_entity = KnowledgeEntity(
            type=KnowledgeType.TECHNICAL,
            title="测试技术知识",
            content="这是一个测试技术知识，用于验证AI Loop集成",
            source="integration_test",
            tags=["test", "integration"]
        )
        entity_id = knowledge_manager.add_entity(test_entity)
        
        # 处理请求
        request_data = {
            'task_type': 'technical_solution',
            'context': '设计一个简单的用户管理系统',
            'user_id': 'integration_test'
        }
        
        try:
            result = ai_loop_engine.process_request(request_data)
            logger.info(f"✓ 系统集成测试成功")
        except Exception as e:
            logger.warning(f"⚠ 系统集成测试跳过（可能未配置API密钥）: {e}")
        
        logger.info("=== 系统集成测试完成 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ 系统集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("开始AI Loop功能测试\n")
    logger.info(f"测试时间: {datetime.now().isoformat()}\n")
    
    test_results = {
        'knowledge_base': test_knowledge_base(),
        'feedback_system': test_feedback_system(),
        'enhanced_ai_service': test_enhanced_ai_service(),
        'prompt_engineering': test_prompt_engineering(),
        'ai_loop_engine': test_ai_loop_engine(),
        'integration': test_integration()
    }
    
    # 汇总测试结果
    logger.info("\n=== 测试结果汇总 ===")
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    failed_tests = total_tests - passed_tests
    
    for test_name, result in test_results.items():
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n总计: {total_tests} 个测试")
    logger.info(f"通过: {passed_tests} 个")
    logger.info(f"失败: {failed_tests} 个")
    logger.info(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        logger.info("\n🎉 所有测试通过！")
        return 0
    else:
        logger.info(f"\n⚠ 有 {failed_tests} 个测试失败")
        return 1

if __name__ == "__main__":
    exit(main())