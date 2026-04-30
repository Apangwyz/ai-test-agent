# AI智能体系统 API 文档

## 1. 概述

本文档提供了AI智能体系统的完整API参考，包括所有可用的API端点、请求参数、响应结构和错误处理机制。系统采用RESTful API设计风格，使用JSON格式进行数据交换。

## 2. 认证方式

系统使用JWT (JSON Web Token) 进行身份验证。用户通过登录获取访问令牌，然后在后续请求中通过Authorization头传递此令牌。

**认证头格式：**
```
Authorization: Bearer {access_token}
```

## 3. 错误处理

API响应使用标准HTTP状态码，并在响应体中包含详细的错误信息。

### 常见错误状态码：

| 状态码 | 描述 | 含义 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 认证失败 |
| 500 | Internal Server Error | 服务器内部错误 |

### 错误响应格式：

```json
{
  "error": "错误描述信息"
}
```

## 4. API端点

### 4.1 认证相关

#### 4.1.1 用户注册

**端点：** `POST /api/auth/register`

**描述：** 注册新用户

**请求参数：**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| email | string | 是 | 邮箱地址 |
| password | string | 是 | 密码 |

**请求示例：**

```json
{
  "username": "测试用户",
  "email": "test@example.com",
  "password": "password123"
}
```

**响应示例：**

```json
{
  "status": "success",
  "user": {
    "id": 1,
    "username": "测试用户",
    "email": "test@example.com"
  }
}
```

**状态码：**
- 201 Created - 注册成功
- 400 Bad Request - 请求参数错误
- 500 Internal Server Error - 服务器内部错误

#### 4.1.2 用户登录

**端点：** `POST /api/auth/login`

**描述：** 用户登录并获取访问令牌

**请求参数：**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| email | string | 是 | 邮箱地址 |
| password | string | 是 | 密码 |

**请求示例：**

```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

**响应示例：**

```json
{
  "status": "success",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "测试用户",
    "email": "test@example.com"
  }
}
```

**状态码：**
- 200 OK - 登录成功
- 401 Unauthorized - 认证失败
- 500 Internal Server Error - 服务器内部错误

### 4.2 文档处理

#### 4.2.1 处理文档

**端点：** `POST /api/documents/process`

**描述：** 处理上传的文档文件并返回结构化内容

**请求参数：**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| file | file | 是 | 上传的文档文件（支持DOCX、PDF、MD格式） |

**请求示例：**

```
Content-Type: multipart/form-data

file: [选择文件]
```

**响应示例：**

```json
{
  "status": "success",
  "content": "文档内容...",
  "structured_data": {
    "title": "文档标题",
    "sections": [
      {
        "title": "章节1",
        "content": "章节内容..."
      }
    ]
  }
}
```

**状态码：**
- 200 OK - 处理成功
- 400 Bad Request - 请求参数错误
- 500 Internal Server Error - 服务器内部错误

### 4.3 需求澄清

#### 4.3.1 生成澄清文档

**端点：** `POST /api/clarification/generate`

**描述：** 根据结构化需求数据生成澄清文档

**请求参数：**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| structured_data | object | 是 | 结构化需求数据 |

**请求示例：**

```json
{
  "structured_data": {
    "title": "项目需求",
    "sections": [
      {
        "title": "功能需求",
        "content": "系统需要实现用户管理功能..."
      }
    ]
  }
}
```

**响应示例：**

```json
{
  "status": "success",
  "clarification_doc": {
    "title": "需求澄清文档",
    "sections": [
      {
        "title": "功能需求澄清",
        "content": "用户管理功能的具体实现细节..."
      }
    ]
  }
}
```

**状态码：**
- 200 OK - 生成成功
- 400 Bad Request - 请求参数错误
- 500 Internal Server Error - 服务器内部错误

### 4.4 技术方案

#### 4.4.1 生成技术方案文档

**端点：** `POST /api/tech-doc/generate`

**描述：** 根据结构化需求和澄清文档生成技术方案文档

**请求参数：**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| structured_data | object | 是 | 结构化需求数据 |
| clarification_doc | object | 否 | 澄清文档 |

**请求示例：**

```json
{
  "structured_data": {
    "title": "项目需求",
    "sections": [
      {
        "title": "功能需求",
        "content": "系统需要实现用户管理功能..."
      }
    ]
  },
  "clarification_doc": {
    "title": "需求澄清文档",
    "sections": [
      {
        "title": "功能需求澄清",
        "content": "用户管理功能的具体实现细节..."
      }
    ]
  }
}
```

**响应示例：**

```json
{
  "status": "success",
  "tech_doc": {
    "title": "技术方案文档",
    "architecture": "系统架构设计...",
    "technology_stack": "技术栈选择...",
    "implementation_plan": "实现计划..."
  }
}
```

**状态码：**
- 200 OK - 生成成功
- 400 Bad Request - 请求参数错误
- 500 Internal Server Error - 服务器内部错误

### 4.5 编码任务

#### 4.5.1 生成编码任务

**端点：** `POST /api/tasks/generate`

**描述：** 根据技术方案文档生成编码任务

**请求参数：**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| tech_doc | object | 是 | 技术方案文档 |

**请求示例：**

```json
{
  "tech_doc": {
    "title": "技术方案文档",
    "architecture": "系统架构设计...",
    "technology_stack": "技术栈选择...",
    "implementation_plan": "实现计划..."
  }
}
```

**响应示例：**

```json
{
  "status": "success",
  "tasks": [
    {
      "id": "task-1",
      "title": "实现用户注册功能",
      "description": "实现用户注册接口和数据库模型",
      "priority": "high",
      "estimated_time": "4h"
    },
    {
      "id": "task-2",
      "title": "实现用户登录功能",
      "description": "实现用户登录接口和JWT认证",
      "priority": "high",
      "estimated_time": "3h"
    }
  ]
}
```

**状态码：**
- 200 OK - 生成成功
- 400 Bad Request - 请求参数错误
- 500 Internal Server Error - 服务器内部错误

### 4.6 测试案例

#### 4.6.1 生成测试案例

**端点：** `POST /api/test-cases/generate`

**描述：** 根据结构化需求和技术方案生成测试案例

**请求参数：**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| structured_data | object | 是 | 结构化需求数据 |
| tech_doc | object | 是 | 技术方案文档 |

**请求示例：**

```json
{
  "structured_data": {
    "title": "项目需求",
    "sections": [
      {
        "title": "功能需求",
        "content": "系统需要实现用户管理功能..."
      }
    ]
  },
  "tech_doc": {
    "title": "技术方案文档",
    "architecture": "系统架构设计...",
    "technology_stack": "技术栈选择...",
    "implementation_plan": "实现计划..."
  }
}
```

**响应示例：**

```json
{
  "status": "success",
  "test_cases": {
    "title": "测试案例脑图",
    "sections": [
      {
        "title": "用户管理模块",
        "cases": [
          {
            "id": "test-1",
            "title": "用户注册测试",
            "description": "测试用户注册功能的正确性",
            "priority": "high"
          },
          {
            "id": "test-2",
            "title": "用户登录测试",
            "description": "测试用户登录功能的正确性",
            "priority": "high"
          }
        ]
      }
    ]
  }
}
```

**状态码：**
- 200 OK - 生成成功
- 400 Bad Request - 请求参数错误
- 500 Internal Server Error - 服务器内部错误

## 5. 速率限制

系统对API请求实施速率限制，以防止滥用。默认限制为：

- 未认证用户：每IP每分钟60个请求
- 已认证用户：每用户每分钟100个请求

## 6. 版本控制

API版本通过URL路径进行控制，当前版本为v1。未来版本将通过修改URL路径实现，例如：

```
/api/v2/auth/login
```

## 7. 最佳实践

1. **认证令牌管理**：
   - 安全存储访问令牌
   - 定期更新令牌
   - 在请求头中正确传递令牌

2. **错误处理**：
   - 正确处理API返回的错误状态码
   - 实现重试机制处理临时错误
   - 记录详细的错误日志

3. **请求优化**：
   - 批量处理相关请求
   - 合理设置请求超时
   - 使用适当的缓存策略

4. **数据验证**：
   - 在客户端进行数据验证
   - 遵循API文档中的参数约束
   - 处理边界情况和异常输入

## 8. 支持与反馈

如有API使用问题或建议，请联系系统管理员：

- 邮箱：support@ai-agent-system.com
- 电话：+86 123 4567 8910
- 文档更新日期：2026-04-27

---

*本文档由AI智能体系统自动生成，如有任何疑问，请参考最新版本。*