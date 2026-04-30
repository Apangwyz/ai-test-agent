import os
import json
from datetime import datetime
from typing import Dict, Any

class DocumentExporter:
    def __init__(self):
        self.logger = None

    def export_to_markdown(self, data: Dict[str, Any], output_path: str, doc_type: str = 'general') -> bool:
        try:
            content = self._convert_to_markdown(data, doc_type)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"导出Markdown失败: {e}")
            return False

    def export_to_json(self, data: Dict[str, Any], output_path: str) -> bool:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出JSON失败: {e}")
            return False

    def export_to_html(self, data: Dict[str, Any], output_path: str, doc_type: str = 'general') -> bool:
        try:
            content = self._convert_to_html(data, doc_type)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"导出HTML失败: {e}")
            return False

    def _convert_to_markdown(self, data: Dict[str, Any], doc_type: str) -> str:
        if doc_type == 'clarification':
            return self._clarification_to_markdown(data)
        elif doc_type == 'tech_doc':
            return self._tech_doc_to_markdown(data)
        elif doc_type == 'tasks':
            return self._tasks_to_markdown(data)
        elif doc_type == 'test_cases':
            return self._test_cases_to_markdown(data)
        elif doc_type == 'structured_data':
            return self._structured_data_to_markdown(data)
        else:
            return self._general_to_markdown(data)

    def _convert_to_html(self, data: Dict[str, Any], doc_type: str) -> str:
        if doc_type == 'test_cases':
            return self._test_cases_to_html(data)
        else:
            return self._general_to_html(data)

    def _clarification_to_markdown(self, data: Dict[str, Any]) -> str:
        md = "# 需求澄清文档\n\n"
        md += f"**版本**: {data.get('version', '1.0')}\n\n"
        timestamp = data.get('timestamp', 0)
        if timestamp:
            md += f"**生成时间**: {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        else:
            md += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        if data.get('ambiguous_points'):
            md += "## 模糊点\n\n"
            for point in data['ambiguous_points']:
                md += f"- {point}\n"
            md += "\n"

        if data.get('conflicts'):
            md += "## 冲突点\n\n"
            for conflict in data['conflicts']:
                md += f"- {conflict}\n"
            md += "\n"

        if data.get('missing_information'):
            md += "## 缺失信息\n\n"
            for info in data['missing_information']:
                md += f"- {info}\n"
            md += "\n"

        if data.get('suggestions'):
            md += "## 建议\n\n"
            for suggestion in data['suggestions']:
                md += f"- {suggestion}\n"

        return md

    def _tech_doc_to_markdown(self, data: Dict[str, Any]) -> str:
        md = "# 技术方案文档\n\n"
        md += f"**版本**: {data.get('version', '1.0')}\n\n"
        timestamp = data.get('timestamp', 0)
        if timestamp:
            md += f"**生成时间**: {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        else:
            md += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        if data.get('architecture'):
            md += "## 系统架构\n\n"
            arch_content = data['architecture'].get('content', '') if isinstance(data['architecture'], dict) else str(data['architecture'])
            md += f"{arch_content}\n\n"

        if data.get('tech_stack'):
            md += "## 技术栈\n\n"
            tech_content = data['tech_stack'].get('content', '') if isinstance(data['tech_stack'], dict) else str(data['tech_stack'])
            md += f"{tech_content}\n\n"

        if data.get('core_modules'):
            md += "## 核心模块\n\n"
            for module in data['core_modules']:
                md += f"- {module}\n"
            md += "\n"

        if data.get('interface_design'):
            md += "## 接口设计\n\n"
            interface_content = data['interface_design'].get('content', '') if isinstance(data['interface_design'], dict) else str(data['interface_design'])
            md += f"{interface_content}\n\n"

        if data.get('data_flow'):
            md += "## 数据流\n\n"
            flow_content = data['data_flow'].get('content', '') if isinstance(data['data_flow'], dict) else str(data['data_flow'])
            md += f"{flow_content}\n\n"

        if data.get('challenges'):
            md += "## 技术挑战\n\n"
            for challenge in data['challenges']:
                md += f"- {challenge}\n"
            md += "\n"

        if data.get('implementation'):
            md += "## 实施计划\n\n"
            impl_content = data['implementation'].get('content', '') if isinstance(data['implementation'], dict) else str(data['implementation'])
            md += f"{impl_content}\n\n"

        if data.get('deployment'):
            md += "## 部署策略\n\n"
            deploy_content = data['deployment'].get('content', '') if isinstance(data['deployment'], dict) else str(data['deployment'])
            md += f"{deploy_content}\n"

        return md

    def _tasks_to_markdown(self, data: Dict[str, Any]) -> str:
        md = "# 编码任务清单\n\n"
        md += f"**版本**: {data.get('version', '1.0')}\n\n"
        timestamp = data.get('timestamp', 0)
        if timestamp:
            md += f"**生成时间**: {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        else:
            md += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        if data.get('tasks'):
            for i, task in enumerate(data['tasks'], 1):
                title = task.get('title', task.get('name', '未命名任务'))
                md += f"## 任务 {i}: {title}\n\n"
                md += f"**描述**: {task.get('description', '无描述')}\n\n"
                md += f"**优先级**: {task.get('priority', 'medium')}\n\n"
                md += f"**预估时间**: {task.get('estimated_time', '未预估')}\n\n"
                md += "---\n\n"

        return md

    def _test_cases_to_markdown(self, data: Dict[str, Any]) -> str:
        md = "# 测试案例文档\n\n"
        md += f"**版本**: {data.get('version', '1.0')}\n\n"
        timestamp = data.get('timestamp', 0)
        if timestamp:
            md += f"**生成时间**: {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        else:
            md += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        if data.get('test_cases'):
            test_cases = data['test_cases']
            md += "## 测试案例\n\n"

            for test in test_cases:
                md += f"### {test.get('id', '')}. {test.get('name', '未命名测试')}\n\n"
                md += f"- **类型**: {test.get('type', 'functional')}\n"
                md += f"- **优先级**: {test.get('priority', 'medium')}\n"
                md += f"- **测试环境**: {test.get('environment', '标准测试环境')}\n\n"

                md += "**测试步骤**:\n"
                for step in test.get('steps', []):
                    md += f"  {step}\n"
                md += "\n"

                md += "**预期结果**:\n"
                for result in test.get('expected_results', []):
                    md += f"  - {result}\n"
                md += "\n---\n\n"

        return md

    def _test_cases_to_html(self, data: Dict[str, Any]) -> str:
        version = data.get('version', '1.0')
        timestamp = datetime.fromtimestamp(data.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')
        tree_data = self._build_mindmap_data(data)
        tree_data_json = json.dumps(tree_data, ensure_ascii=False)

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试案例脑图</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{
            font-family: Microsoft YaHei, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .meta-info {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        #mindmap {{
            width: 100%;
            height: 800px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>测试案例脑图</h1>
        <div class="meta-info">
            <p>版本: {version} | 生成时间: {timestamp}</p>
        </div>
        <div id="mindmap"></div>
    </div>
    <script>
        var chartDom = document.getElementById('mindmap');
        var myChart = echarts.init(chartDom);
        var option = {tree_data_json};
        myChart.setOption(option);
        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
    </script>
</body>
</html>"""

        return html

    def _build_mindmap_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        tree_data = {
            'name': '测试案例',
            'children': [],
            'symbol': 'circle',
            'symbolSize': 70,
            'itemStyle': {
                'color': '#4CAF50'
            }
        }

        if data.get('test_cases'):
            test_cases = data['test_cases']
            test_cases_by_type = {}

            for test in test_cases:
                test_type = test.get('type', 'functional')
                if test_type not in test_cases_by_type:
                    test_cases_by_type[test_type] = []
                test_cases_by_type[test_type].append(test)

            type_colors = {
                'functional': '#2196F3',
                'performance': '#FF9800',
                'compatibility': '#9C27B0',
                'security': '#F44336'
            }

            for test_type, tests in test_cases_by_type.items():
                type_node = {
                    'name': self._translate_test_type(test_type),
                    'children': [],
                    'symbol': 'circle',
                    'symbolSize': 50,
                    'itemStyle': {
                        'color': type_colors.get(test_type, '#607D8B')
                    }
                }

                for test in tests:
                    test_node = {
                        'name': f"{test.get('id', '')}. {test.get('name', '未命名测试')}",
                        'children': [
                            {
                                'name': '测试步骤',
                                'children': [{'name': step} for step in test.get('steps', [])]
                            },
                            {
                                'name': '预期结果',
                                'children': [{'name': result} for result in test.get('expected_results', [])]
                            },
                            {
                                'name': f"优先级: {test.get('priority', 'medium')}"
                            },
                            {
                                'name': f"环境: {test.get('environment', '标准环境')}"
                            }
                        ],
                        'symbol': 'circle',
                        'symbolSize': 40,
                        'itemStyle': {
                            'color': '#00BCD4'
                        }
                    }
                    type_node['children'].append(test_node)

                tree_data['children'].append(type_node)

        return {
            'series': [{
                'type': 'tree',
                'data': [tree_data],
                'top': '5%',
                'left': '10%',
                'bottom': '5%',
                'right': '20%',
                'symbolSize': 10,
                'label': {
                    'position': 'left',
                    'verticalAlign': 'middle',
                    'align': 'right',
                    'fontSize': 14
                },
                'leaves': {
                    'label': {
                        'position': 'right',
                        'verticalAlign': 'middle',
                        'align': 'left'
                    }
                },
                'emphasis': {
                    'focus': 'descendant'
                },
                'expandAndCollapse': True,
                'animationDuration': 550,
                'animationDurationUpdate': 750
            }]
        }

    def _translate_test_type(self, test_type: str) -> str:
        translations = {
            'functional': '功能测试',
            'performance': '性能测试',
            'compatibility': '兼容性测试',
            'security': '安全测试'
        }
        return translations.get(test_type, test_type)

    def _structured_data_to_markdown(self, data: Dict[str, Any]) -> str:
        md = "# 结构化需求数据\n\n"
        md += f"**项目名称**: {data.get('title', '未命名项目')}\n\n"

        if data.get('sections'):
            md += "## 章节内容\n\n"
            for section in data['sections']:
                section_title = section.get('title', '未命名章节') if isinstance(section, dict) else '未命名章节'
                section_content = section.get('content', '') if isinstance(section, dict) else str(section)
                md += f"### {section_title}\n\n"
                md += f"{section_content}\n\n"

        if data.get('requirements'):
            md += "## 功能需求\n\n"
            for req in data['requirements']:
                md += f"- {req}\n"
            md += "\n"

        if data.get('constraints'):
            md += "## 约束条件\n\n"
            for constraint in data['constraints']:
                md += f"- {constraint}\n"

        return md

    def _general_to_markdown(self, data: Dict[str, Any]) -> str:
        md = "# 文档\n\n"
        md += json.dumps(data, indent=2, ensure_ascii=False)
        return md

    def _general_to_html(self, data: Dict[str, Any]) -> str:
        content = json.dumps(data, indent=2, ensure_ascii=False)
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文档</title>
    <style>
        body {{
            font-family: Microsoft YaHei, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>文档</h1>
        <pre>{content}</pre>
    </div>
</body>
</html>"""
        return html
