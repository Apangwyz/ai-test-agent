# AI智能体系统部署指南

## 1. 系统要求

- Docker 和 Docker Compose
- Python 3.9+
- PostgreSQL 13+
- 足够的存储空间（至少 2GB）

## 2. 部署方式

### 2.1 使用 Docker Compose 部署

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

5. **访问系统**
   打开浏览器，访问 `http://localhost:5000`

### 2.2 本地开发部署

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

5. **访问系统**
   打开浏览器，访问 `http://localhost:5000`

## 3. 系统配置

### 3.1 数据库配置
- 默认使用 PostgreSQL 数据库
- 数据库连接信息：
  - 用户名：admin
  - 密码：password
  - 数据库名：example_db
  - 端口：5432

### 3.2 AI模型配置
- 默认使用 OpenAI 的 gpt-3.5-turbo 模型
- 需要设置有效的 OpenAI API Key

### 3.3 安全配置
- JWT 密钥需要设置为强随机字符串
- 生产环境中应使用 HTTPS

## 4. 系统维护

### 4.1 查看日志
```bash
docker-compose logs app
```

### 4.2 数据库备份
```bash
docker-compose exec db pg_dump -U admin example_db > backup.sql
```

### 4.3 系统更新
```bash
git pull
docker-compose up -d --build
```

## 5. 故障排除

### 5.1 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否正常运行
   - 验证数据库连接字符串是否正确

2. **API Key 错误**
   - 检查 OpenAI API Key 是否有效
   - 验证 API Key 是否有足够的配额

3. **服务启动失败**
   - 查看容器日志：`docker-compose logs app`
   - 检查端口是否被占用

### 5.2 性能优化

1. **增加容器资源限制**
   在 docker-compose.yml 中添加资源限制：
   ```yaml
   app:
     # ...
     deploy:
       resources:
         limits:
           cpus: "2"
           memory: "2G"
   ```

2. **启用缓存**
   考虑使用 Redis 作为缓存，提高系统性能

## 6. 监控和日志

### 6.1 系统日志
- 应用日志：`app.log`
- Docker 容器日志：`docker-compose logs`

### 6.2 监控建议
- 使用 Prometheus 和 Grafana 监控系统性能
- 设置告警机制，及时发现系统异常

## 7. 扩展建议

### 7.1 水平扩展
- 使用 Docker Swarm 或 Kubernetes 进行集群部署
- 配置负载均衡，提高系统可用性

### 7.2 功能扩展
- 添加更多文档格式支持
- 集成更多 AI 模型
- 增加自动化测试和 CI/CD 流程

## 8. 联系支持

- 问题反馈：<contact@example.com>
- 技术支持：<support@example.com>
- 文档地址：<https://example.com/docs>

---

**注意**：本部署指南适用于开发和测试环境。生产环境部署需要额外的安全措施和性能优化。