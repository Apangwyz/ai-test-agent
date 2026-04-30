#!/usr/bin/env python3
"""
通用需求文档全流程测试脚本

此脚本用于：
1. 处理任意目录下的需求文档（支持命令行参数指定）
2. 调用项目中的文档解析功能
3. 自动生成测试案例、需求澄清文档、技术方案等相关材料
4. 验证项目主流程的完整性和正确性

使用方法：
python scripts/process_requirements.py --input <输入目录> --output <输出目录>
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.document_processor.processor_factory import DocumentProcessorFactory
from src.clarification_generator.clarification_generator import ClarificationGenerator
from src.tech_doc_generator.tech_doc_generator import TechDocGenerator
from src.coding_task_generator.coding_task_generator import CodingTaskGenerator
from src.test_case_generator.test_case_generator import TestCaseGenerator
from src.common.document_exporter import DocumentExporter

def process_single_document(file_path, project_name):
    """
    处理单个需求文档
    """
    print(f"\n{'='*70}")
    print(f"处理项目: {project_name}")
    print(f"{'='*70}")

    results = {}

    print("\n[1] 解析需求文档...")
    try:
        processor = DocumentProcessorFactory.get_processor(file_path)
        content = processor.process(file_path)
        structured_data = processor.extract_structure(content)
        if structured_data:
            print(f"    ✓ 文档解析成功")
            results['structured_data'] = structured_data
        else:
            print(f"    ✗ 结构化数据提取失败")
            return None
    except Exception as e:
        print(f"    ✗ 文档解析失败: {str(e)}")
        return None

    print("\n[2] 生成需求澄清文档...")
    try:
        generator = ClarificationGenerator()
        clarification_doc = generator.generate_clarification(structured_data)
        if clarification_doc:
            print(f"    ✓ 需求澄清文档生成成功")
            results['clarification_doc'] = clarification_doc
        else:
            print(f"    ✗ 需求澄清文档生成失败")
    except Exception as e:
        print(f"    ✗ 需求澄清文档生成失败: {str(e)}")

    print("\n[3] 生成技术方案文档...")
    try:
        generator = TechDocGenerator()
        tech_doc = generator.generate_tech_doc(structured_data, clarification_doc)
        if tech_doc:
            print(f"    ✓ 技术方案文档生成成功")
            results['tech_doc'] = tech_doc
        else:
            print(f"    ✗ 技术方案文档生成失败")
    except Exception as e:
        print(f"    ✗ 技术方案文档生成失败: {str(e)}")

    print("\n[4] 生成编码任务清单...")
    try:
        if 'tech_doc' in results:
            generator = CodingTaskGenerator()
            tasks = generator.generate_tasks(results['tech_doc'])
            if tasks:
                print(f"    ✓ 编码任务清单生成成功")
                results['tasks'] = tasks
            else:
                print(f"    ✗ 编码任务清单生成失败")
        else:
            print(f"    ⊗ 跳过（依赖技术方案文档）")
    except Exception as e:
        print(f"    ✗ 编码任务清单生成失败: {str(e)}")

    print("\n[5] 生成测试案例...")
    try:
        if 'structured_data' in results and 'tech_doc' in results:
            generator = TestCaseGenerator()
            test_cases = generator.generate_test_cases(results['structured_data'], results['tech_doc'])
            if test_cases:
                print(f"    ✓ 测试案例生成成功")
                results['test_cases'] = test_cases
            else:
                print(f"    ✗ 测试案例生成失败")
        else:
            print(f"    ⊗ 跳过（依赖结构化数据和技术方案文档）")
    except Exception as e:
        print(f"    ✗ 测试案例生成失败: {str(e)}")

    return results

def save_results(project_name, results, output_dir):
    """
    保存生成的结果文件
    """
    print(f"\n[6] 保存生成结果...")
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    json_dir = os.path.join(output_dir, 'json')
    md_dir = os.path.join(output_dir, 'markdown')
    html_dir = os.path.join(output_dir, 'html')
    
    for dir_path in [json_dir, md_dir, html_dir]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    safe_name = re.sub(r'[\\/*?:"<>|]', '_', project_name)
    exporter = DocumentExporter()
    
    doc_types = [
        ('structured_data', '结构化数据'),
        ('clarification_doc', '需求澄清文档'),
        ('tech_doc', '技术方案文档'),
        ('tasks', '编码任务清单'),
        ('test_cases', '测试案例')
    ]
    
    for key, name in doc_types:
        if key in results:
            json_path = os.path.join(json_dir, f"{safe_name}_{key}.json")
            md_path = os.path.join(md_dir, f"{safe_name}_{key}.md")
            
            exporter.export_to_json(results[key], json_path)
            print(f"    ✓ JSON: {os.path.basename(json_path)}")
            
            exporter.export_to_markdown(results[key], md_path, key)
            print(f"    ✓ Markdown: {os.path.basename(md_path)}")
            
            if key == 'test_cases':
                html_path = os.path.join(html_dir, f"{safe_name}_{key}_mindmap.html")
                exporter.export_to_html(results[key], html_path, 'test_cases')
                print(f"    ✓ HTML脑图: {os.path.basename(html_path)}")

def run_test(input_dir, output_dir):
    """
    执行全流程测试
    """
    print("="*80)
    print("通用需求文档全流程测试")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    
    if not os.path.exists(input_dir):
        print(f"\n错误: 输入目录不存在 - {input_dir}")
        return False
    
    input_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.md')])
    
    if not input_files:
        print(f"\n错误: 目录中没有找到Markdown文件")
        return False
    
    print(f"\n找到 {len(input_files)} 个需求文档:")
    for f in input_files:
        print(f"    - {f}")
    
    total = len(input_files)
    success = 0
    failed = 0
    results_summary = []
    
    for filename in input_files:
        file_path = os.path.join(input_dir, filename)
        project_name = filename.replace('.md', '').replace('req_', '').replace('_', ' ').replace('req', '').strip()
        
        results = process_single_document(file_path, project_name)
        
        if results:
            save_results(project_name, results, output_dir)
            success += 1
            results_summary.append({
                'project': project_name,
                'status': 'success',
                'docs': len(results)
            })
            print(f"\n    ✓ 项目 [{project_name}] 处理完成")
        else:
            failed += 1
            results_summary.append({
                'project': project_name,
                'status': 'failed',
                'docs': 0
            })
            print(f"\n    ✗ 项目 [{project_name}] 处理失败")
    
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    print(f"总项目数: {total}")
    print(f"成功: {success}")
    print(f"失败: {failed}")
    print(f"成功率: {(success/total*100):.1f}%")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n详细结果:")
    for item in results_summary:
        status_icon = "✓" if item['status'] == 'success' else "✗"
        print(f"    {status_icon} {item['project']}: {item['status']} ({item['docs']}个文档)")
    
    print(f"\n结果文件保存位置: {output_dir}")
    
    if failed == 0:
        print("\n" + "✓✓✓ 所有项目处理成功！全流程验证通过！")
    else:
        print(f"\n" + f"✗✗✗ 有 {failed} 个项目处理失败，请检查错误信息")
    
    return failed == 0

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='通用需求文档全流程测试脚本')
    parser.add_argument('-i', '--input', 
                        help='输入目录，包含需求文档（默认为 docs/requirements）',
                        default=os.path.join(os.path.dirname(__file__), '..', 'docs', 'requirements'))
    parser.add_argument('-o', '--output',
                        help='输出目录，保存生成的文档（默认为 docs/requirements/results）',
                        default=os.path.join(os.path.dirname(__file__), '..', 'docs', 'requirements', 'results'))
    
    args = parser.parse_args()
    
    input_dir = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output)
    
    success = run_test(input_dir, output_dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()