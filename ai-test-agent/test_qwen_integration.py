#!/usr/bin/env python3
"""
Qwen模型集成测试脚本
验证Qwen大模型的对接是否成功
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.common.ai_service import ai_service
from src.clarification_generator.clarification_generator import ClarificationGenerator
from src.tech_doc_generator.tech_doc_generator import TechDocGenerator
from src.coding_task_generator.coding_task_generator import CodingTaskGenerator
from src.test_case_generator.test_case_generator import TestCaseGenerator

def test_ai_service():
    """测试AI服务"""
    print("\n=== 测试AI服务 ===")
    try:
        # 测试Qwen模型
        prompt = "你好，Qwen模型"
        system_prompt = "你是一个智能助手"
        
        print("测试Qwen模型...")
        response = ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            model_type='qwen',
            temperature=0.3
        )
        
        print(f"Qwen模型响应: {response[:100]}...")
        print("✓ Qwen模型测试成功")
        
        return True
    except Exception as e:
        print(f"✗ Qwen模型测试失败: {e}")
        return False

def test_clarification_generator():
    """测试需求澄清生成器"""
    print("\n=== 测试需求澄清生成器 ===")
    try:
        generator = ClarificationGenerator()
        test_data = {
            'sections': ['# 智能客服系统需求'],
            'requirements': [
                '支持用户注册和登录',
                '支持文本对话',
                '响应时间不超过1秒'
            ],
            'constraints': [
                '使用Python语言开发',
                '部署在云服务器上'
            ]
        }
        
        clarification_doc = generator.generate_clarification(test_data)
        print(f"生成的澄清文档包含: {len(clarification_doc.get('ambiguous_points', []))}个模糊点, {len(clarification_doc.get('missing_information', []))}个缺失信息")
        print("✓ 需求澄清生成器测试成功")
        
        return True
    except Exception as e:
        print(f"✗ 需求澄清生成器测试失败: {e}")
        return False

def test_tech_doc_generator():
    """测试技术方案生成器"""
    print("\n=== 测试技术方案生成器 ===")
    try:
        generator = TechDocGenerator()
        test_data = {
            'sections': ['# 智能客服系统需求'],
            'requirements': [
                '支持用户注册和登录',
                '支持文本对话'
            ],
            'constraints': [
                '使用Python语言开发'
            ]
        }
        
        tech_doc = generator.generate_tech_doc(test_data)
        print(f"生成的技术方案包含: {len(tech_doc.get('core_modules', []))}个核心模块, {len(tech_doc.get('challenges', []))}个技术难点")
        print("✓ 技术方案生成器测试成功")
        
        return True
    except Exception as e:
        print(f"✗ 技术方案生成器测试失败: {e}")
        return False

def test_coding_task_generator():
    """测试编码任务生成器"""
    print("\n=== 测试编码任务生成器 ===")
    try:
        generator = CodingTaskGenerator()
        test_tech_doc = {
            'architecture': {'content': '系统采用微服务架构'},
            'tech_stack': {'content': 'Python, Flask, PostgreSQL'},
            'core_modules': ['用户管理模块', '对话管理模块'],
            'interface_design': {'content': 'RESTful API'}
        }
        
        tasks = generator.generate_tasks(test_tech_doc)
        print(f"生成的编码任务数: {len(tasks.get('tasks', []))}")
        print("✓ 编码任务生成器测试成功")
        
        return True
    except Exception as e:
        print(f"✗ 编码任务生成器测试失败: {e}")
        return False

def test_test_case_generator():
    """测试测试案例生成器"""
    print("\n=== 测试测试案例生成器 ===")
    try:
        generator = TestCaseGenerator()
        test_structured_data = {
            'sections': ['# 智能客服系统需求'],
            'requirements': [
                '支持用户注册和登录',
                '支持文本对话'
            ],
            'constraints': [
                '响应时间不超过1秒'
            ]
        }
        test_tech_doc = {
            'architecture': {'content': '系统采用微服务架构'},
            'core_modules': ['用户管理模块', '对话管理模块'],
            'interface_design': {'content': 'RESTful API'}
        }
        
        test_cases = generator.generate_test_cases(test_structured_data, test_tech_doc)
        print(f"生成的测试案例数: {len(test_cases.get('test_cases', []))}")
        print("✓ 测试案例生成器测试成功")
        
        return True
    except Exception as e:
        print(f"✗ 测试案例生成器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=== Qwen模型集成测试 ===")
    print("开始验证Qwen大模型对接是否成功...")
    
    # 测试各个模块
    test_results = [
        test_ai_service(),
        test_clarification_generator(),
        test_tech_doc_generator(),
        test_coding_task_generator(),
        test_test_case_generator()
    ]
    
    # 统计测试结果
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n=== 测试结果 ===")
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过，Qwen模型集成成功！")
    else:
        print("✗ 部分测试失败，需要检查配置和代码")

if __name__ == "__main__":
    main()