# AI智能体系统

## 项目概述

AI智能体系统是一个功能完整的智能体平台，以可配置化方式支持集成不同的大语言模型，具备高度的可扩展性、系统健壮性，并符合当前主流的AI Agent架构设计标准。系统采用模块化设计原则，确保各功能模块间低耦合高内聚，具备良好的可扩展性和可维护性。

## 核心功能

### 1. 需求文档处理模块
- 支持常见文档格式（.docx、.pdf、.md）的读取与内容提取，准确率不低于95%
- 实现对输入需求文档的结构化解析与语义理解
- 准确识别并分类文档中的功能需求、非功能需求、业务规则及约束条件
- 实现文档内容的结构化存储，支持后续模块的高效数据访问

### 2. 需求澄清文档生成模块
- 基于解析后的需求内容，自动识别潜在的需求模糊点、冲突点及缺失信息
- 生成标准化的需求澄清文档，包含待澄清问题列表、需求确认项及建议补充内容
- 问题识别准确率需达到85%以上，确保覆盖关键需求点
- 支持澄清结果的版本管理与追踪

### 3. 技术方案文档生成模块
- 根据已澄清的需求，自动生成专业的技术方案文档
- 内容包括：系统架构设计图、技术栈选型依据及对比分析、核心模块划分、接口设计规范、数据流程设计及关键技术难点解决方案
- 技术方案需符合行业最佳实践，具备可行性与先进性
- 支持方案文档的导出与协作评审

### 4. 编码任务文档生成模块
- 将技术方案转化为可执行的编码任务，按功能模块拆分任务单元
- 明确每个任务的目标、输入输出、技术要求、时间预估及依赖关系
- 生成结构化的开发任务清单，支持导入主流项目管理工具
- 任务拆分粒度需适中，单个任务工作量不超过8小时

### 5. 测试案例脑图生成模块
- 基于需求文档和技术方案，系统性地生成测试案例脑图
- 涵盖功能测试、性能测试、兼容性测试及安全测试等维度
- 明确每个测试点的测试步骤、预期结果、优先级及测试环境要求
- 支持导出为常见脑图格式（.xmind、.mm），导出格式完整度不低于98%

### 6. 知识库系统
- 支持多种知识类型：需求、技术方案、澄清文档、编码任务、测试用例
- 知识提取：从文档中自动提取知识实体
- 向量搜索：集成FAISS向量数据库实现语义搜索
- 混合查询：支持关键词和语义混合查询
- 知识关系：支持知识实体之间的关系管理

### 7. 反馈系统
- 反馈收集：支持多种反馈类型和分类
- 反馈分析：自动分析反馈趋势和问题
- 反馈管理：支持反馈的增删改查
- 反馈统计：提供反馈统计和分析报告

### 8. 增强AI服务
- 智能路由：根据性能、成本、可用性选择最优模型
- 缓存机制：缓存常用请求，减少API调用
- 性能跟踪：跟踪模型性能指标
- 负载均衡：支持多模型负载均衡

### 9. 提示词工程
- 基础提示词生成：提供多种任务类型的提示词模板
- 知识增强：基于知识库生成增强提示词
- 自适应生成：根据用户偏好自适应调整提示词
- 反馈改进：基于反馈改进提示词质量
- 提示词优化：支持质量、效率、平衡三种优化模式

### 10. AI Loop引擎
- 完整的AI Loop流程实现
- 数据收集 → 知识检索 → 提示词生成 → 模型推理 → 结果验证 → 反馈收集 → 知识更新
- 性能指标跟踪
- 自动知识更新
- 错误处理和回退机制

## 技术架构

### 系统架构
- **微服务架构**：支持服务独立部署与扩展
- **API接口**：提供开放的RESTful API接口
- **用户权限管理**：实现JWT认证和基于角色的权限控制
- **操作审计**：记录用户操作历史和系统事件
- **前端界面**：响应式设计，适配不同设备
- **容器化部署**：支持Docker容器化部署
- **AI Loop架构**：实现持续学习和改进的闭环系统

### 技术栈
- **后端**：Python Flask框架
- **数据库**：PostgreSQL
- **AI集成**：支持OpenAI API，可配置化集成不同大语言模型
- **向量数据库**：FAISS（可选）
- **文本嵌入**：sentence-transformers（可选）
- **前端**：HTML5 + CSS3 + JavaScript
- **部署**：Docker + Docker Compose

### 核心模块
1. **文档处理模块**：负责解析不同格式的需求文档
2. **需求澄清模块**：识别需求中的模糊点和缺失信息
3. **技术方案模块**：生成专业的技术方案文档
4. **编码任务模块**：将技术方案转化为可执行的编码任务
5. **测试案例模块**：生成测试案例脑图
6. **API模块**：提供RESTful API接口
7. **认证模块**：实现用户认证和权限管理
8. **审计模块**：记录用户操作和系统事件
9. **知识库模块**：管理和检索知识实体
10. **反馈模块**：收集和分析用户反馈
11. **AI服务模块**：提供智能路由和缓存功能
12. **提示词工程模块**：生成和优化提示词
13. **AI Loop模块**：实现知识增强的推理流程

## 环境要求

- **Docker** 和 **Docker Compose**（推荐）
- **Python 3.9+**（本地开发）
- **PostgreSQL 13+**（本地开发）
- **足够的存储空间**（至少 2GB）
- **有效的API密钥**（OpenAI或Qwen）

## 安装与配置

### 方法一：使用 Docker Compose 部署

1. **克隆代码仓库**
   ```bash
   git clone <repository-url>
   cd ai-test-agent
   ```

2. **配置环境变量**
   编辑 `.env` 文件，设置以下环境变量：
   ```
   # Server Configuration
   FLASK_APP=app.py
   FLASK_ENV=development
   PORT=5000

   # Database Configuration
   DATABASE_URL=postgresql://admin:password@localhost:5432/example_db

   # JWT Configuration
   JWT_SECRET_KEY=your-secret-key-here
   JWT_ACCESS_TOKEN_EXPIRES=3600

   # AI Model Configuration
   OPENAI_API_KEY=your-openai-api-key
   MODEL_NAME=gpt-3.5-turbo
   
   # Qwen Configuration
   QWEN_API_KEY=your-qwen-api-key
   QWEN_MODEL_NAME=qwen-turbo
   QWEN_API_BASE=https://api.dashscope.aliyuncs.com/api/v1
   QWEN_TIMEOUT=60

   # Cache Configuration
   CACHE_ENABLED=true
   CACHE_TTL=3600

   # Routing Configuration
   ROUTING_STRATEGY=performance
   LOAD_BALANCING=true

   # Logging Configuration
   LOG_LEVEL=INFO
   LOG_FILE=app.log
   ```

3. **构建和启动服务**
   ```bash
   docker-compose up -d --build
   ```

4. **验证服务状态**
   ```bash
   docker-compose ps
   ```

### 方法二：本地开发部署

1. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **安装可选依赖**
   ```bash
   # 向量数据库支持
   pip install faiss-cpu
   
   # 文本嵌入支持
   pip install sentence-transformers
   
   # 性能监控支持
   pip install psutil
   ```

4. **初始化数据库**
   ```bash
   python -c "from src.auth.database import init_db; init_db()"
   ```

5. **启动开发服务器**
   ```bash
   flask run
   ```

## 使用指南

### 前端界面

打开浏览器，访问 `http://localhost:5000`，使用前端界面进行操作：

1. **文档处理**：上传需求文档，系统自动解析并提取结构化信息
2. **需求澄清**：基于解析结果，生成需求澄清文档
3. **技术方案**：根据澄清后的需求，生成技术方案文档
4. **编码任务**：将技术方案转化为可执行的编码任务
5. **测试案例**：基于需求和技术方案，生成测试案例脑图

### API接口

系统提供RESTful API接口，可通过HTTP请求调用：

- **文档处理**：`POST /api/documents/process`
- **需求澄清**：`POST /api/clarification/generate`
- **技术方案**：`POST /api/tech-doc/generate`
- **编码任务**：`POST /api/tasks/generate`
- **测试案例**：`POST /api/test-cases/generate`
- **用户注册**：`POST /api/auth/register`
- **用户登录**：`POST /api/auth/login`

### 常见操作示例

#### 1. 文档处理

**示例请求**：
```bash
curl -X POST http://localhost:5000/api/documents/process \
  -F "file=@requirements.md"
```

**示例响应**：
```json
{
  "status": "success",
  "content": "文档内容",
  "structured_data": {
    "sections": ["项目概述", "功能需求"],
    "requirements": ["支持用户登录", "支持数据导出"],
    "constraints": ["响应时间不超过2秒"]
  }
}
```

#### 2. 需求澄清

**示例请求**：
```bash
curl -X POST http://localhost:5000/api/clarification/generate \
  -H "Content-Type: application/json" \
  -d '{
    "structured_data": {
      "sections": ["项目概述", "功能需求"],
      "requirements": ["支持用户登录", "支持数据导出"],
      "constraints": ["响应时间不超过2秒"]
    }
  }'
```

**示例响应**：
```json
{
  "status": "success",
  "clarification_doc": {
    "version": "1.0",
    "timestamp": 1234567890,
    "ambiguous_points": ["用户登录方式未明确"],
    "conflicts": [],
    "missing_information": ["数据导出格式未指定"],
    "suggestions": ["建议明确登录方式和导出格式"]
  }
}
```

#### 3. 技术方案

**示例请求**：
```bash
curl -X POST http://localhost:5000/api/tech-doc/generate \
  -H "Content-Type: application/json" \
  -d '{
    "structured_data": {
      "sections": ["项目概述", "功能需求"],
      "requirements": ["支持用户登录", "支持数据导出"],
      "constraints": ["响应时间不超过2秒"]
    },
    "clarification_doc": {
      "ambiguous_points": ["用户登录方式未明确"],
      "conflicts": [],
      "missing_information": ["数据导出格式未指定"],
      "suggestions": ["建议明确登录方式和导出格式"]
    }
  }'
```

**示例响应**：
```json
{
  "status": "success",
  "tech_doc": {
    "version": "1.0",
    "timestamp": 1234567890,
    "architecture": {
      "type": "微服务架构",
      "components": ["用户服务", "数据服务"]
    },
    "tech_stack": {
      "backend": "Python Flask",
      "database": "PostgreSQL"
    },
    "core_modules": ["认证模块", "导出模块"],
    "interface_design": {
      "rest_api": true,
      "graphql": false
    },
    "data_flow": {
      "login": "用户 → 认证服务 → 数据库",
      "export": "用户 → 导出服务 → 存储"
    },
    "challenges": ["响应时间优化"],
    "implementation": {
      "estimated_time": "2周"
    },
    "deployment": {
      "docker": true,
      "kubernetes": false
    }
  }
}
```

## API文档

### 详细API文档

完整的API文档可通过以下方式访问：

- **本地部署**：访问 `http://localhost:5000/api/docs`
- **在线文档**：<https://example.com/api/docs>（占位）

### API接口列表

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/documents/process` | `POST` | 处理上传的文档 |
| `/api/clarification/generate` | `POST` | 生成需求澄清文档 |
| `/api/tech-doc/generate` | `POST` | 生成技术方案文档 |
| `/api/tasks/generate` | `POST` | 生成编码任务 |
| `/api/test-cases/generate` | `POST` | 生成测试案例 |
| `/api/auth/register` | `POST` | 用户注册 |
| `/api/auth/login` | `POST` | 用户登录 |

## 项目资产管理

### 资产文件夹结构

项目使用结构化的资产文件夹 `assets/` 来系统保存项目全生命周期中的各类变更资产：

```
assets/
├── requirements/     # 需求文档
├── development/      # 开发报告和变更记录
├── testing/          # 测试报告
└── others/           # 其他相关资产
```

### 资产存放规范

1. **需求文档** (`assets/requirements/`)
   - 存放原始需求文档
   - 存放需求澄清文档
   - 命名规范：`YYYY-MM-DD-需求标题.md`

2. **开发报告** (`assets/development/`)
   - 存放开发报告
   - 存放变更记录
   - 存放技术方案文档
   - 命名规范：`YYYY-MM-DD-报告类型.md`

3. **测试报告** (`assets/testing/`)
   - 存放功能测试报告
   - 存放性能测试报告
   - 存放兼容性测试报告
   - 命名规范：`YYYY-MM-DD-测试类型.md`

4. **其他资产** (`assets/others/`)
   - 存放会议记录
   - 存放设计文档
   - 存放其他相关资料
   - 命名规范：`YYYY-MM-DD-资产名称.md`

### 查阅指引

1. **需求文档**：查看 `assets/requirements/` 目录下的文件
2. **开发报告**：查看 `assets/development/` 目录下的文件
3. **测试报告**：查看 `assets/testing/` 目录下的文件
4. **其他资产**：查看 `assets/others/` 目录下的文件

## 测试指南

### 运行测试

1. **功能测试**
   ```bash
   python tests/test_ai_loop_integration.py
   ```

2. **性能测试**
   ```bash
   python tests/test_performance.py
   ```

3. **兼容性测试**
   ```bash
   python tests/test_compatibility.py
   ```

4. **所有测试**
   ```bash
   python tests/test_ai_loop_integration.py && python tests/test_performance.py && python tests/test_compatibility.py
   ```

### 测试覆盖范围

- **功能测试**：验证所有核心功能是否正常工作
- **性能测试**：测试系统在不同负载下的性能表现
- **兼容性测试**：确保与现有功能的兼容性
- **集成测试**：验证各模块间的集成是否正常

## 故障排除

### 常见问题

1. **服务启动失败**
   - 检查Docker服务是否运行
   - 查看容器日志：`docker-compose logs`
   - 检查端口是否被占用

2. **API调用失败**
   - 检查环境变量配置，特别是API密钥
   - 验证网络连接
   - 查看服务日志

3. **数据库连接失败**
   - 检查PostgreSQL服务是否运行
   - 验证数据库连接字符串
   - 检查数据库用户权限

4. **前端无法访问**
   - 检查服务是否正常启动
   - 验证端口配置
   - 检查防火墙设置

5. **AI模型调用超时**
   - 检查API密钥是否有效
   - 验证网络连接
   - 调整超时设置

## 贡献指南

### 开发流程

1. **克隆代码仓库**
   ```bash
   git clone <repository-url>
   cd ai-test-agent
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **安装依赖**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **编写代码**
   - 遵循项目的代码风格和命名规范
   - 为新功能编写单元测试
   - 确保代码覆盖率不低于70%

5. **运行测试**
   ```bash
   python tests/test_ai_loop_integration.py
   ```

6. **提交代码**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   git push origin feature/your-feature-name
   ```

7. **创建Pull Request**
   - 描述功能的详细信息
   - 提供测试结果
   - 等待代码审查

### 代码规范

- 遵循PEP 8代码风格
- 为所有函数和类添加文档字符串
- 使用类型提示
- 保持代码简洁明了
- 遵循模块化设计原则

## 许可证信息

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

- **项目维护者**：<maintainer@example.com>
- **技术支持**：<support@example.com>
- **文档地址**：<https://example.com/docs>
- **GitHub仓库**：<https://github.com/example/ai-test-agent>

## 项目计划

### 中期计划（3-6个月）

| 任务 | 描述 | 预期完成时间 | 负责人 |
|------|------|------------|-------|
| 前端界面优化 | 开发现代化的响应式前端界面，提升用户体验 | 2026-06-30 | 前端团队 |
| 多语言支持 | 实现系统的多语言支持，包括中英文界面切换 | 2026-07-15 | 全栈团队 |
| 模型扩展 | 集成更多大语言模型，如Claude、LLaMA等 | 2026-07-31 | AI团队 |
| 自动化测试 | 建立完整的自动化测试体系，提高代码质量 | 2026-08-15 | 测试团队 |
| 性能优化 | 优化系统性能，提高响应速度和处理能力 | 2026-08-31 | 后端团队 |
| 安全加固 | 加强系统安全，防止常见的安全漏洞 | 2026-09-15 | 安全团队 |

### 长期计划（6个月以上）

| 任务 | 描述 | 预期完成时间 | 负责人 |
|------|------|------------|-------|
| 自主学习系统 | 实现系统的自主学习能力，持续优化模型性能 | 2026-12-31 | AI团队 |
| 多模态支持 | 支持图像、音频等多模态输入和处理 | 2027-02-28 | 全栈团队 |
| 分布式部署 | 实现系统的分布式部署，支持大规模应用 | 2027-03-31 | 架构团队 |
| 行业解决方案 | 开发针对不同行业的专业解决方案 | 2027-04-30 | 产品团队 |
| 移动端应用 | 开发移动端应用，提供随时随地的访问能力 | 2027-05-31 | 移动开发团队 |
| 生态系统建设 | 建立完整的生态系统，支持第三方插件和集成 | 2027-06-30 | 架构团队 |

## 版本历史

- **1.0.0** (2026-04-22)：初始版本，包含完整的AI智能体系统功能

---

**注意**：本系统需要有效的API密钥才能使用AI功能。在生产环境部署时，应确保API密钥的安全存储和使用。

**免责声明**：本系统仅供参考和学习使用，实际生产环境部署时请根据具体需求进行适当调整。