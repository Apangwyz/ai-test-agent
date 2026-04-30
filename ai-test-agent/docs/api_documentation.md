# 测试智能体 API 接口文档

## 概述

本API提供需求文档解析、测试案例生成等智能分析服务，用于与Java技术栈的测试管理平台对接。

## 基础配置

- **基础路径**: `http://localhost:5002/api`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

---

## 1. 认证接口

### 1.1 用户登录

**POST** `/auth/login`

用户通过测试管理平台登录，获取访问令牌。

**请求体**:
```json
{
  "email": "string (必填, 用户邮箱)",
  "password": "string (必填, 用户密码)"
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "access_token": "string (JWT访问令牌)",
  "user": {
    "id": "integer (用户ID)",
    "username": "string (用户名)",
    "email": "string (邮箱)"
  },
  "expires_in": "integer (过期时间，秒)"
}
```

**失败响应** (401):
```json
{
  "status": "error",
  "message": "string (错误信息)"
}
```

### 1.2 用户注册

**POST** `/auth/register`

**请求体**:
```json
{
  "username": "string (必填, 用户名)",
  "email": "string (必填, 邮箱)",
  "password": "string (必填, 密码)"
}
```

**成功响应** (201):
```json
{
  "status": "success",
  "user": {
    "id": "integer",
    "username": "string",
    "email": "string"
  }
}
```

### 1.3 Token刷新

**POST** `/auth/refresh`

**请求头**: `Authorization: Bearer <refresh_token>`

**成功响应** (200):
```json
{
  "status": "success",
  "access_token": "string",
  "expires_in": "integer"
}
```

---

## 2. 需求文档处理接口

### 2.1 全流程处理（推荐）

**POST** `/document/process-full`

上传需求文档并执行完整流程：解析 → 需求澄清 → 技术方案 → 任务清单 → 测试案例 → 存入知识库

**请求头**: `Authorization: Bearer <access_token>`

**请求体** (multipart/form-data):
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 需求文档 (.md, .docx, .pdf) |
| project_name | String | 否 | 项目名称（默认从文件名提取） |
| save_to_knowledge_base | Boolean | 否 | 是否存入知识库（默认true） |

**成功响应** (200):
```json
{
  "status": "success",
  "project_id": "string (项目标识)",
  "project_name": "string (项目名称)",
  "processed_at": "string (ISO8601时间戳)",
  "results": {
    "structured_data": {
      "version": "string",
      "timestamp": "number",
      "sections": ["string"],
      "requirements": ["string"],
      "constraints": ["string"]
    },
    "clarification_doc": {
      "version": "string",
      "timestamp": "number",
      "ambiguous_points": ["string"],
      "conflicts": ["string"],
      "missing_information": ["string"],
      "suggestions": ["string"]
    },
    "tech_doc": {
      "version": "string",
      "timestamp": "number",
      "architecture": {"content": "string"},
      "tech_stack": {"content": "string"},
      "core_modules": ["string"],
      "interface_design": {"content": "string"},
      "data_flow": {"content": "string"},
      "challenges": ["string"],
      "implementation": {"content": "string"},
      "deployment": {"content": "string"}
    },
    "tasks": {
      "version": "string",
      "timestamp": "number",
      "tasks": [
        {
          "id": "integer",
          "name": "string",
          "description": "string",
          "technical_requirements": "string",
          "inputs_outputs": "string",
          "estimated_time": "number",
          "dependencies": ["integer"],
          "priority": "string (high/medium/low)"
        }
      ]
    },
    "test_cases": {
      "version": "string",
      "timestamp": "number",
      "test_cases": [
        {
          "id": "integer",
          "name": "string",
          "type": "string (functional/performance/compatibility/security)",
          "steps": ["string"],
          "expected_results": ["string"],
          "priority": "string (high/medium/low)",
          "environment": "string"
        }
      ]
    }
  },
  "knowledge_base_saved": "boolean",
  "knowledge_base_id": "string (知识库记录ID)"
}
```

### 2.2 仅解析文档

**POST** `/document/parse`

**请求头**: `Authorization: Bearer <access_token>`

**请求体**: `multipart/form-data`
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 需求文档 |

**成功响应** (200):
```json
{
  "status": "success",
  "content": "string (原始内容)",
  "structured_data": {
    "version": "string",
    "sections": ["string"],
    "requirements": ["string"],
    "constraints": ["string"]
  }
}
```

---

## 3. 文档生成接口

### 3.1 生成需求澄清文档

**POST** `/generate/clarification`

**请求头**: `Authorization: Bearer <access_token>`

**请求体**:
```json
{
  "structured_data": "object (必填, 结构化数据)",
  "save_to_kb": "boolean (可选, 是否存入知识库)"
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "clarification_doc": "object"
}
```

### 3.2 生成技术方案文档

**POST** `/generate/tech-doc`

**请求体**:
```json
{
  "structured_data": "object (必填)",
  "clarification_doc": "object (可选)",
  "save_to_kb": "boolean (可选)"
}
```

### 3.3 生成编码任务清单

**POST** `/generate/tasks`

**请求体**:
```json
{
  "structured_data": "object (必填)",
  "tech_doc": "object (可选)",
  "save_to_kb": "boolean (可选)"
}
```

### 3.4 生成测试案例

**POST** `/generate/test-cases`

**请求体**:
```json
{
  "structured_data": "object (必填)",
  "tech_doc": "object (可选)",
  "save_to_kb": "boolean (可选)"
}
```

---

## 4. 项目管理接口

### 4.1 查询项目列表

**GET** `/projects`

**请求头**: `Authorization: Bearer <access_token>`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | Integer | 否 | 页码，默认1 |
| limit | Integer | 否 | 每页数量，默认20 |
| keyword | String | 否 | 搜索关键词 |

**成功响应** (200):
```json
{
  "status": "success",
  "data": [
    {
      "project_id": "string",
      "project_name": "string",
      "processed_at": "string",
      "status": "string (completed/failed)"
    }
  ],
  "pagination": {
    "page": "integer",
    "limit": "integer",
    "total": "integer",
    "pages": "integer"
  }
}
```

### 4.2 查询项目详情

**GET** `/projects/{project_id}`

**请求头**: `Authorization: Bearer <access_token>`

**成功响应** (200):
```json
{
  "status": "success",
  "project": {
    "project_id": "string",
    "project_name": "string",
    "processed_at": "string",
    "results": "object (完整的处理结果)"
  }
}
```

### 4.3 删除项目

**DELETE** `/projects/{project_id}`

**请求头**: `Authorization: Bearer <access_token>`

**成功响应** (200):
```json
{
  "status": "success",
  "message": "项目已删除"
}
```

---

## 5. 知识库接口

### 5.1 查询知识库

**GET** `/knowledge-base/search`

**请求头**: `Authorization: Bearer <access_token>`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | String | 是 | 搜索关键词 |
| limit | Integer | 否 | 返回数量，默认10 |

**成功响应** (200):
```json
{
  "status": "success",
  "results": [
    {
      "id": "string",
      "title": "string",
      "content": "string",
      "type": "string (document/clarification/tech_doc/tasks/test_cases)",
      "created_at": "string",
      "score": "number (匹配分数)"
    }
  ]
}
```

### 5.2 获取知识库详情

**GET** `/knowledge-base/{kb_id}`

**请求头**: `Authorization: Bearer <access_token>`

**成功响应** (200):
```json
{
  "status": "success",
  "record": {
    "id": "string",
    "title": "string",
    "content": "object",
    "type": "string",
    "created_at": "string",
    "project_id": "string"
  }
}
```

### 5.3 删除知识库记录

**DELETE** `/knowledge-base/{kb_id}`

**请求头**: `Authorization: Bearer <access_token>`

---

## 6. AI Loop引擎接口

### 6.1 获取性能指标

**GET** `/ai-loop/metrics`

获取AI Loop引擎的性能统计数据。

**请求头**: `Authorization: Bearer <access_token>`

**成功响应** (200):
```json
{
  "status": "success",
  "metrics": {
    "total_requests": "integer (总请求数)",
    "successful_requests": "integer (成功请求数)",
    "failed_requests": "integer (失败请求数)",
    "average_response_time": "number (平均响应时间，毫秒)",
    "success_rate": "number (成功率，0-1)",
    "knowledge_hit_rate": "number (知识库命中率，0-1)",
    "auto_correction_count": "integer (自动修正次数)",
    "total_iterations": "integer (总迭代次数)",
    "average_iterations_per_request": "number (每次请求平均迭代次数)"
  }
}
```

### 6.2 重置性能指标

**POST** `/ai-loop/metrics/reset`

重置所有性能指标统计。

**请求头**: `Authorization: Bearer <access_token>`

**成功响应** (200):
```json
{
  "status": "success",
  "message": "性能指标已重置"
}
```

---

## 7. 知识库管理接口

### 7.1 查询知识库

**GET** `/knowledge-base/search`

**请求头**: `Authorization: Bearer <access_token>`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | String | 是 | 搜索关键词 |
| limit | Integer | 否 | 返回数量，默认10 |
| threshold | Number | 否 | 匹配阈值，默认0.5 |

**成功响应** (200):
```json
{
  "status": "success",
  "results": [
    {
      "id": "string",
      "title": "string",
      "content": "string",
      "type": "string (document/clarification/tech_doc/tasks/test_cases)",
      "created_at": "string",
      "score": "number (匹配分数)"
    }
  ]
}
```

### 7.2 获取知识库详情

**GET** `/knowledge-base/{kb_id}`

**请求头**: `Authorization: Bearer <access_token>`

**成功响应** (200):
```json
{
  "status": "success",
  "record": {
    "id": "string",
    "title": "string",
    "content": "object",
    "type": "string",
    "created_at": "string",
    "project_id": "string"
  }
}
```

### 7.3 删除知识库记录

**DELETE** `/knowledge-base/{kb_id}`

**请求头**: `Authorization: Bearer <access_token>`

### 7.4 获取实体版本历史

**GET** `/knowledge-base/{kb_id}/versions`

获取实体的所有版本历史。

**请求头**: `Authorization: Bearer <access_token>`

**成功响应** (200):
```json
{
  "status": "success",
  "entity_id": "string",
  "versions": [
    {
      "version": "string (版本号)",
      "operation": "string (create/update/delete)",
      "created_at": "string",
      "user_id": "string",
      "changes": "object (变更内容)"
    }
  ]
}
```

### 7.5 回滚到指定版本

**POST** `/knowledge-base/{kb_id}/rollback`

将实体回滚到指定版本。

**请求头**: `Authorization: Bearer <access_token>`

**请求体**:
```json
{
  "version": "string (必填, 目标版本号)"
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "message": "已回滚到版本 {version}",
  "entity": "object (回滚后的实体)"
}
```

### 7.6 查询审计日志

**GET** `/knowledge-base/audit-logs`

查询知识库操作审计日志。

**请求头**: `Authorization: Bearer <access_token>`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | String | 否 | 用户ID筛选 |
| action | String | 否 | 操作类型 (create/update/delete) |
| resource_type | String | 否 | 资源类型 |
| limit | Integer | 否 | 返回数量，默认20 |

**成功响应** (200):
```json
{
  "status": "success",
  "logs": [
    {
      "id": "string",
      "action": "string",
      "user_id": "string",
      "resource_type": "string",
      "resource_id": "string",
      "details": "object",
      "created_at": "string"
    }
  ]
}
```

### 7.7 获取缓存统计

**GET** `/knowledge-base/cache/stats`

获取知识库缓存统计信息。

**请求头**: `Authorization: Bearer <access_token>`

**成功响应** (200):
```json
{
  "status": "success",
  "stats": {
    "hits": "integer (缓存命中次数)",
    "misses": "integer (缓存未命中次数)",
    "evictions": "integer (缓存驱逐次数)",
    "hit_rate": "number (命中率，0-1)",
    "memory_usage": "string (内存使用量)"
  }
}
```

### 7.8 清除缓存

**POST** `/knowledge-base/cache/clear`

清除知识库缓存。

**请求头**: `Authorization: Bearer <access_token>`

**成功响应** (200):
```json
{
  "status": "success",
  "message": "缓存已清除"
}
```

---

## 8. 健康检查

### 8.1 服务状态

**GET** `/health`

**成功响应** (200):
```json
{
  "status": "healthy",
  "timestamp": "string",
  "version": "string",
  "services": {
    "ai_service": "string (online/offline)",
    "database": "string (online/offline)",
    "knowledge_base": "string (online/offline)",
    "cache": "string (online/offline)"
  },
  "ai_loop_metrics": {
    "success_rate": "number",
    "average_response_time": "number"
  }
}
```

---

## 错误响应格式

### 通用错误响应

```json
{
  "status": "error",
  "code": "string (错误码)",
  "message": "string (错误信息)",
  "timestamp": "string (ISO8601时间戳)"
}
```

### 错误码说明

| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| AUTH_INVALID_TOKEN | 401 | 无效的访问令牌 |
| AUTH_EXPIRED_TOKEN | 401 | 令牌已过期 |
| AUTH_UNAUTHORIZED | 403 | 未授权访问 |
| VALIDATION_ERROR | 400 | 请求参数验证失败 |
| FILE_INVALID | 400 | 无效的文件格式 |
| PROCESSING_ERROR | 500 | 处理过程中发生错误 |
| KB_ERROR | 500 | 知识库操作失败 |

---

## 认证说明

### JWT Token 使用方式

所有需要认证的接口，需在请求头中携带：

```
Authorization: Bearer <access_token>
```

### Token 有效期

- 访问令牌 (Access Token): 默认1小时
- 刷新令牌 (Refresh Token): 默认7天

---

## 第三方知识库对接

### 支持的知识库类型

1. **内部知识库** (默认)
2. **Milvus**
3. **Pinecone**
4. **Weaviate**
5. **自定义API**

### 配置方式

通过环境变量配置：

```env
# 知识库类型: internal/milvus/pinecone/weaviate/custom
KNOWLEDGE_BASE_TYPE=internal

# Milvus配置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# Pinecone配置
PINECONE_API_KEY=your_api_key
PINECONE_ENVIRONMENT=us-west1-gcp

# Weaviate配置
WEAVIATE_HOST=localhost
WEAVIATE_PORT=8080

# 自定义API配置
CUSTOM_KB_API_URL=https://your-kb-service/api
CUSTOM_KB_API_KEY=your_api_key
```

---

## 数据流转图

```
用户(测试管理平台) → [POST /document/process-full] → API服务
                                                      │
                    ┌─────────────────────────────────┼─────────────────────────────────┐
                    ▼                                 ▼                                 ▼
           文档解析模块                          大模型分析                          知识库存储
           (DocumentProcessor)                  (AI Service)                   (KnowledgeBase)
                    │                                 │                                 │
                    └─────────────────────────────────┼─────────────────────────────────┘
                                                      ▼
                                               结果返回给前端
```

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.1 | 2026-05-01 | AI Loop引擎优化，添加多轮迭代优化、动态提示词调整、重试机制 |
| v1.0 | 2026-04-30 | 初始版本，支持文档全流程处理 |
