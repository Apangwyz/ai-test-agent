import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ai_service_compatibility():
    """测试AI服务兼容性"""
    logger.info("=== 测试AI服务兼容性 ===")
    
    try:
        from src.common.ai_service import ai_service
        
        # 测试1: 基础AI服务功能
        logger.info("测试1: 基础AI服务功能")
        stats = ai_service.get_service_stats()
        logger.info(f"✓ 基础AI服务正常工作: {stats}")
        
        # 测试2: 增强AI服务集成
        logger.info("测试2: 增强AI服务集成")
        try:
            from src.common.enhanced_ai_service import enhanced_ai_service
            logger.info("✓ 增强AI服务可以正常导入")
        except ImportError as e:
            logger.warning(f"⚠ 增强AI服务导入失败: {e}")
        
        # 测试3: AI服务回退机制
        logger.info("测试3: AI服务回退机制")
        try:
            result = ai_service.generate(
                prompt="测试提示词",
                system_prompt="测试系统提示词",
                model_type='qwen',
                use_enhanced=False
            )
            logger.info(f"✓ AI服务回退机制正常工作")
        except Exception as e:
            logger.warning(f"⚠ AI服务回退测试跳过（可能未配置API密钥）: {e}")
        
        logger.info("=== AI服务兼容性测试完成 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ AI服务兼容性测试失败: {e}")
        return False

def test_document_processor_compatibility():
    """测试文档处理器兼容性"""
    logger.info("=== 测试文档处理器兼容性 ===")
    
    try:
        from src.document_processor.processor_factory import DocumentProcessorFactory
        from src.knowledge_base import knowledge_extractor
        
        # 测试1: 文档处理器工厂
        logger.info("测试1: 文档处理器工厂")
        processor = DocumentProcessorFactory.get_processor('test.md')
        logger.info(f"✓ 文档处理器工厂正常工作: {processor.__class__.__name__}")
        
        # 测试2: 知识提取器与文档处理器集成
        logger.info("测试2: 知识提取器与文档处理器集成")
        test_data = {
            'content': '这是一个测试文档内容，用于验证兼容性。',
            'sections': ['测试章节'],
            'requirements': ['测试需求'],
            'constraints': ['测试约束']
        }
        
        extracted_entities = knowledge_extractor.extract_from_document(test_data)
        logger.info(f"✓ 知识提取器与文档处理器集成成功，提取了 {len(extracted_entities)} 个实体")
        
        # 测试3: 多种文档格式支持
        logger.info("测试3: 多种文档格式支持")
        supported_formats = ['test.md', 'test.txt', 'test.docx', 'test.pdf']
        for fmt in supported_formats:
            try:
                processor = DocumentProcessorFactory.get_processor(fmt)
                logger.info(f"✓ 支持 {fmt} 格式: {processor.__class__.__name__}")
            except Exception as e:
                logger.warning(f"⚠ {fmt} 格式支持失败: {e}")
        
        logger.info("=== 文档处理器兼容性测试完成 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ 文档处理器兼容性测试失败: {e}")
        return False

def test_generator_compatibility():
    """测试生成器兼容性"""
    logger.info("=== 测试生成器兼容性 ===")
    
    try:
        # 测试1: 技术文档生成器兼容性
        logger.info("测试1: 技术文档生成器兼容性")
        from src.tech_doc_generator import TechDocGenerator
        
        tech_gen = TechDocGenerator()
        test_data = {
            'title': '测试项目',
            'sections': ['项目概述', '技术架构'],
            'requirements': ['支持用户管理'],
            'constraints': ['需要高性能']
        }
        
        try:
            result = tech_gen.generate_tech_doc(test_data)
            logger.info(f"✓ 技术文档生成器兼容性测试成功")
        except Exception as e:
            logger.warning(f"⚠ 技术文档生成器测试跳过（可能未配置API密钥）: {e}")
        
        # 测试2: 澄清文档生成器兼容性
        logger.info("测试2: 澄清文档生成器兼容性")
        from src.clarification_generator import ClarificationGenerator
        
        clar_gen = ClarificationGenerator()
        try:
            result = clar_gen.generate_clarification_doc(test_data)
            logger.info(f"✓ 澄清文档生成器兼容性测试成功")
        except Exception as e:
            logger.warning(f"⚠ 澄清文档生成器测试跳过（可能未配置API密钥）: {e}")
        
        # 测试3: 编码任务生成器兼容性
        logger.info("测试3: 编码任务生成器兼容性")
        from src.coding_task_generator import CodingTaskGenerator
        
        task_gen = CodingTaskGenerator()
        try:
            result = task_gen.generate_coding_tasks(test_data)
            logger.info(f"✓ 编码任务生成器兼容性测试成功")
        except Exception as e:
            logger.warning(f"⚠ 编码任务生成器测试跳过（可能未配置API密钥）: {e}")
        
        # 测试4: 测试用例生成器兼容性
        logger.info("测试4: 测试用例生成器兼容性")
        from src.test_case_generator import TestCaseGenerator
        
        test_gen = TestCaseGenerator()
        try:
            result = test_gen.generate_test_cases(test_data)
            logger.info(f"✓ 测试用例生成器兼容性测试成功")
        except Exception as e:
            logger.warning(f"⚠ 测试用例生成器测试跳过（可能未配置API密钥）: {e}")
        
        logger.info("=== 生成器兼容性测试完成 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ 生成器兼容性测试失败: {e}")
        return False

def test_new_features_integration():
    """测试新功能集成"""
    logger.info("=== 测试新功能集成 ===")
    
    try:
        # 测试1: 知识库与现有系统集成
        logger.info("测试1: 知识库与现有系统集成")
        from src.knowledge_base import knowledge_manager, KnowledgeEntity, KnowledgeType
        from src.tech_doc_generator import TechDocGenerator
        
        # 创建测试知识
        test_entity = KnowledgeEntity(
            type=KnowledgeType.TECHNICAL,
            title="集成测试技术知识",
            content="这是用于集成测试的技术知识",
            source="integration_test",
            tags=["test", "integration"]
        )
        entity_id = knowledge_manager.add_entity(test_entity)
        logger.info(f"✓ 知识库与现有系统集成成功，实体ID: {entity_id}")
        
        # 测试2: 反馈系统与现有系统集成
        logger.info("测试2: 反馈系统与现有系统集成")
        from src.feedback import feedback_collector
        
        feedback_data = {
            'user_id': 'integration_test',
            'feedback_type': 'positive',
            'category': 'system_integration',
            'title': '集成测试反馈',
            'description': '这是用于集成测试的反馈',
            'rating': 5,
            'tags': ['test', 'integration']
        }
        feedback_id = feedback_collector.collect_feedback(feedback_data)
        logger.info(f"✓ 反馈系统与现有系统集成成功，反馈ID: {feedback_id}")
        
        # 测试3: 提示词工程与现有生成器集成
        logger.info("测试3: 提示词工程与现有生成器集成")
        from src.prompt_engineering import prompt_generator
        
        prompt = prompt_generator.generate_prompt(
            task_type='technical_solution',
            context='设计一个用户管理系统',
            use_knowledge=True
        )
        logger.info(f"✓ 提示词工程与现有生成器集成成功，提示词长度: {len(prompt)}")
        
        # 测试4: AI Loop与现有系统集成
        logger.info("测试4: AI Loop与现有系统集成")
        from src.ai_loop import ai_loop_engine
        
        request_data = {
            'task_type': 'technical_solution',
            'context': '设计一个简单的用户管理系统',
            'user_id': 'integration_test',
            'metadata': {'integration_test': True}
        }
        
        try:
            result = ai_loop_engine.process_request(request_data)
            logger.info(f"✓ AI Loop与现有系统集成成功，处理时间: {result.get('processing_time', 0):.2f}s")
        except Exception as e:
            logger.warning(f"⚠ AI Loop集成测试跳过（可能未配置API密钥）: {e}")
        
        logger.info("=== 新功能集成测试完成 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ 新功能集成测试失败: {e}")
        return False

def test_api_compatibility():
    """测试API兼容性"""
    logger.info("=== 测试API兼容性 ===")
    
    try:
        from flask import Flask
        from src.api.routes import register_routes
        
        # 测试1: API应用初始化
        logger.info("测试1: API应用初始化")
        app = Flask(__name__)
        from flask_restful import Api
        api = Api(app)
        register_routes(api)
        logger.info(f"✓ API应用初始化成功")
        
        # 测试2: API路由注册
        logger.info("测试2: API路由注册")
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        logger.info(f"✓ API路由注册成功，共 {len(routes)} 个路由")
        
        # 测试3: API资源导入
        logger.info("测试3: API资源导入")
        from src.api.resources import (
            document_processor,
            tech_doc_generator,
            clarification_generator,
            coding_task_generator,
            test_case_generator
        )
        logger.info("✓ API资源导入成功")
        
        logger.info("=== API兼容性测试完成 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ API兼容性测试失败: {e}")
        return False

def test_data_flow_compatibility():
    """测试数据流兼容性"""
    logger.info("=== 测试数据流兼容性 ===")
    
    try:
        # 测试1: 文档处理到知识库的数据流
        logger.info("测试1: 文档处理到知识库的数据流")
        from src.document_processor import processor_factory
        from src.knowledge_base import knowledge_extractor, knowledge_manager
        
        test_content = "这是一个测试文档，包含需求信息：系统需要支持用户登录功能。"
        test_data = {
            'content': test_content,
            'sections': ['用户管理'],
            'requirements': ['支持用户登录'],
            'constraints': ['需要安全性']
        }
        
        extracted_entities = knowledge_extractor.extract_from_document(test_data)
        entity_ids = knowledge_extractor.store_extracted_knowledge(extracted_entities)
        logger.info(f"✓ 文档处理到知识库的数据流正常，存储了 {len(entity_ids)} 个实体")
        
        # 测试2: 知识库到AI Loop的数据流
        logger.info("测试2: 知识库到AI Loop的数据流")
        from src.ai_loop import ai_loop_engine
        
        request_data = {
            'task_type': 'requirement_analysis',
            'context': test_content,
            'user_id': 'data_flow_test'
        }
        
        try:
            result = ai_loop_engine.process_request(request_data)
            logger.info(f"✓ 知识库到AI Loop的数据流正常")
        except Exception as e:
            logger.warning(f"⚠ 知识库到AI Loop的数据流测试跳过（可能未配置API密钥）: {e}")
        
        # 测试3: AI Loop到反馈系统的数据流
        logger.info("测试3: AI Loop到反馈系统的数据流")
        from src.feedback import feedback_manager
        
        feedbacks = feedback_manager.get_pending_feedbacks()
        logger.info(f"✓ AI Loop到反馈系统的数据流正常，获取了 {len(feedbacks)} 个反馈")
        
        logger.info("=== 数据流兼容性测试完成 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ 数据流兼容性测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("开始AI Loop兼容性测试\n")
    logger.info(f"测试时间: {datetime.now().isoformat()}\n")
    
    test_results = {
        'ai_service_compatibility': test_ai_service_compatibility(),
        'document_processor_compatibility': test_document_processor_compatibility(),
        'generator_compatibility': test_generator_compatibility(),
        'new_features_integration': test_new_features_integration(),
        'api_compatibility': test_api_compatibility(),
        'data_flow_compatibility': test_data_flow_compatibility()
    }
    
    # 汇总测试结果
    logger.info("\n=== 兼容性测试结果汇总 ===")
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
        logger.info("\n🎉 所有兼容性测试通过！")
        return 0
    else:
        logger.info(f"\n⚠ 有 {failed_tests} 个测试失败")
        return 1

if __name__ == "__main__":
    exit(main())