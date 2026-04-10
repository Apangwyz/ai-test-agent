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

## 技术架构

### 系统架构
- **微服务架构**：支持服务独立部署与扩展
- **API接口**：提供开放的RESTful API接口
- **用户权限管理**：实现JWT认证和基于角色的权限控制
- **操作审计**：记录用户操作历史和系统事件
- **前端界面**：响应式设计，适配不同设备
- **容器化部署**：支持Docker容器化部署

### 技术栈
- **后端**：Python Flask框架
- **数据库**：PostgreSQL
- **AI集成**：支持OpenAI API，可配置化集成不同大语言模型
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

## 安装与配置

### 环境要求
- Docker 和 Docker Compose
- Python 3.9+
- PostgreSQL 13+
- 足够的存储空间（至少 2GB）

### 安装步骤

#### 方法一：使用 Docker Compose 部署

1. **克隆代码仓库**
   ```bash
   git clone <repository-url>
   cd ai-agent-system
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

#### 方法二：本地开发部署

1. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **初始化数据库**
   ```bash
   python -c "from src.auth.database import init_db; init_db()"
   ```

4. **启动开发服务器**
   ```bash
   flask run
   ```

## 使用方法

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

## API参考

### 1. 文档处理接口

**端点**：`POST /api/documents/process`

**请求**：
```
Content-Type: multipart/form-data

file: <文档文件>
```

**响应**：
```json
{
  "status": "success",
  "content": "文档内容",
  "structured_data": {
    "sections": [],
    "requirements": [],
    "constraints": []
  }
}
```

### 2. 需求澄清接口

**端点**：`POST /api/clarification/generate`

**请求**：
```json
Content-Type: application/json

{
  "structured_data": {
    "sections": [],
    "requirements": [],
    "constraints": []
  }
}
```

**响应**：
```json
{
  "status": "success",
  "clarification_doc": {
    "version": "1.0",
    "timestamp": 1234567890,
    "ambiguous_points": [],
    "conflicts": [],
    "missing_information": [],
    "suggestions": []
  }
}
```

### 3. 技术方案接口

**端点**：`POST /api/tech-doc/generate`

**请求**：
```json
Content-Type: application/json

{
  "structured_data": {
    "sections": [],
    "requirements": [],
    "constraints": []
  },
  "clarification_doc": {
    "ambiguous_points": [],
    "conflicts": [],
    "missing_information": [],
    "suggestions": []
  }
}
```

**响应**：
```json
{
  "status": "success",
  "tech_doc": {
    "version": "1.0",
    "timestamp": 1234567890,
    "architecture": {},
    "tech_stack": {},
    "core_modules": [],
    "interface_design": {},
    "data_flow": {},
    "challenges": [],
    "implementation": {},
    "deployment": {}
  }
}
```

### 4. 编码任务接口

**端点**：`POST /api/tasks/generate`

**请求**：
```json
Content-Type: application/json

{
  "tech_doc": {
    "architecture": {},
    "tech_stack": {},
    "core_modules": [],
    "interface_design": {},
    "data_flow": {},
    "challenges": [],
    "implementation": {},
    "deployment": {}
  }
}
```

**响应**：
```json
{
  "status": "success",
  "tasks": {
    "version": "1.0",
    "timestamp": 1234567890,
    "tasks": [
      {
        "id": 1,
        "name": "任务名称",
        "description": "任务描述",
        "technical_requirements": "技术要求",
        "inputs_outputs": "输入输出",
        "estimated_time": 4,
        "dependencies": [],
        "priority": "high"
      }
    ]
  }
}
```

### 5. 测试案例接口

**端点**：`POST /api/test-cases/generate`

**请求**：
```json
Content-Type: application/json

{
  "structured_data": {
    "sections": [],
    "requirements": [],
    "constraints": []
  },
  "tech_doc": {
    "architecture": {},
    "tech_stack": {},
    "core_modules": [],
    "interface_design": {},
    "data_flow": {},
    "challenges": [],
    "implementation": {},
    "deployment": {}
  }
}
```

**响应**：
```json
{
  "status": "success",
  "test_cases": {
    "version": "1.0",
    "timestamp": 1234567890,
    "test_cases": [
      {
        "id": 1,
        "name": "测试案例名称",
        "type": "functional",
        "steps": [],
        "expected_results": [],
        "priority": "high",
        "environment": "测试环境"
      }
    ]
  }
}
```

### 6. 用户认证接口

**注册端点**：`POST /api/auth/register`

**请求**：
```json
Content-Type: application/json

{
  "username": "用户名",
  "email": "邮箱",
  "password": "密码"
}
```

**响应**：
```json
{
  "status": "success",
  "user": {
    "id": 1,
    "username": "用户名",
    "email": "邮箱"
  }
}
```

**登录端点**：`POST /api/auth/login`

**请求**：
```json
Content-Type: application/json

{
  "email": "邮箱",
  "password": "密码"
}
```

**响应**：
```json
{
  "status": "success",
  "access_token": "JWT令牌",
  "user": {
    "id": 1,
    "username": "用户名",
    "email": "邮箱"
  }
}
```

## 贡献指南

### 开发流程
1. **克隆代码仓库**
   ```bash
   git clone <repository-url>
   cd ai-agent-system
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
   pytest
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

## 许可证信息

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 快速开始

### 环境要求
- Docker 和 Docker Compose
- Git

### 安装步骤

1. **克隆代码仓库**
   ```bash
   git clone <repository-url>
   cd ai-agent-system
   ```

2. **配置环境变量**
   复制 `.env` 文件并修改配置：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置 OPENAI_API_KEY 等参数
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

4. **验证服务**
   ```bash
   docker-compose ps
   ```

5. **访问系统**
   打开浏览器，访问 `http://localhost:5000`

### 测试验证

1. **上传需求文档**
   - 在前端界面的"文档处理"部分，上传一个需求文档（支持 .md、.docx、.pdf 格式）
   - 点击"处理文档"按钮
   - 查看处理结果，确认文档被正确解析

2. **生成需求澄清文档**
   - 在"需求澄清"部分，使用上一步的解析结果
   - 点击"生成澄清文档"按钮
   - 查看生成的澄清文档，确认识别出了模糊点和缺失信息

3. **生成技术方案**
   - 在"技术方案"部分，使用解析结果和澄清文档
   - 点击"生成技术方案"按钮
   - 查看生成的技术方案文档，确认包含了系统架构、技术栈等内容

4. **生成编码任务**
   - 在"编码任务"部分，使用技术方案文档
   - 点击"生成编码任务"按钮
   - 查看生成的编码任务，确认任务拆分合理

5. **生成测试案例**
   - 在"测试案例"部分，使用解析结果和技术方案文档
   - 点击"生成测试案例"按钮
   - 查看生成的测试案例，确认覆盖了功能、性能、兼容性和安全测试

### 故障排除

- **服务启动失败**：检查Docker服务是否运行，查看容器日志
- **API调用失败**：检查环境变量配置，特别是OPENAI_API_KEY
- **数据库连接失败**：检查PostgreSQL服务是否运行，验证数据库连接字符串
- **前端无法访问**：检查端口是否被占用，确认服务是否正常启动

## 联系方式

- 项目维护者：<maintainer@example.com>
- 技术支持：<support@example.com>
- 文档地址：<https://example.com/docs>

---

**注意**：本系统需要有效的OpenAI API密钥才能使用AI功能。在生产环境部署时，应确保API密钥的安全存储和使用。