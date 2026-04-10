# 运维脚本集合

本目录包含AI智能体系统的运维脚本集合，提供服务管理、监控、日志管理和备份恢复等功能。

## 目录结构

```
scripts/
├── bin/              # 脚本执行文件
│   ├── start.sh      # 服务启动脚本
│   ├── stop.sh       # 服务停止脚本
│   ├── restart.sh    # 服务重启脚本
│   ├── status.sh     # 状态监控脚本
│   ├── logs.sh       # 日志管理脚本
│   ├── backup.sh     # 备份恢复脚本
│   └── service.sh    # 统一管理脚本（主入口）
├── config/           # 配置文件
│   └── service.conf  # 服务配置文件
├── logs/             # 日志目录
└── backups/          # 备份目录
```

## 脚本功能

### 1. 服务启动脚本 (`start.sh`)
- 实现服务的初始化启动
- 包含环境检查、依赖验证、配置加载和启动状态确认功能
- 支持虚拟环境自动创建和依赖安装

### 2. 服务停止脚本 (`stop.sh`)
- 实现服务的安全停止
- 支持正常关闭和超时强制终止机制
- 清理PID文件和资源

### 3. 服务重启脚本 (`restart.sh`)
- 支持优雅重启和强制重启两种模式
- 包含进程检查、资源释放、重启执行和健康检查流程

### 4. 状态监控脚本 (`status.sh`)
- 提供服务运行状态查询
- 资源占用统计（CPU、内存、磁盘）
- 关键指标监控和健康检查

### 5. 日志管理脚本 (`logs.sh`)
- 实现日志轮转、压缩归档和清理功能
- 支持按大小或时间策略执行
- 提供日志查看和搜索功能

### 6. 备份恢复脚本 (`backup.sh`)
- 提供配置文件和关键数据的定时备份
- 支持完整备份和差异备份
- 备份验证和恢复功能

### 7. 统一管理脚本 (`service.sh`)
- 作为所有运维脚本的统一入口
- 提供简洁的命令行界面
- 支持所有脚本的功能调用

## 使用方法

### 基本用法

```bash
# 启动服务
./scripts/bin/service.sh start

# 停止服务
./scripts/bin/service.sh stop

# 重启服务
./scripts/bin/service.sh restart

# 查看服务状态
./scripts/bin/service.sh status

# 管理日志
./scripts/bin/service.sh logs --view 100  # 查看最近100行日志

# 执行备份
./scripts/bin/service.sh backup --full    # 执行完整备份
```

### 详细命令

#### 启动服务
```bash
# 基本启动
./scripts/bin/service.sh start

# 详细模式
./scripts/bin/service.sh start --verbose
```

#### 停止服务
```bash
# 基本停止
./scripts/bin/service.sh stop

# 强制停止
./scripts/bin/service.sh stop --force
```

#### 重启服务
```bash
# 基本重启
./scripts/bin/service.sh restart

# 强制重启
./scripts/bin/service.sh restart --force
```

#### 状态监控
```bash
# 完整状态
./scripts/bin/service.sh status

# 只查看服务状态
./scripts/bin/service.sh status --status

# 只查看资源监控
./scripts/bin/service.sh status --resources

# 只查看日志监控
./scripts/bin/service.sh status --logs
```

#### 日志管理
```bash
# 自动管理（轮转和清理）
./scripts/bin/service.sh logs

# 强制轮转日志
./scripts/bin/service.sh logs --rotate

# 清理旧日志
./scripts/bin/service.sh logs --cleanup

# 查看日志
./scripts/bin/service.sh logs --view 200

# 搜索日志
./scripts/bin/service.sh logs --search "error"
```

#### 备份恢复
```bash
# 执行完整备份
./scripts/bin/service.sh backup --full

# 执行差异备份
./scripts/bin/service.sh backup --diff

# 恢复备份
./scripts/bin/service.sh backup --restore /path/to/backup.tar.gz

# 列出备份文件
./scripts/bin/service.sh backup --list
```

## 配置管理

所有脚本的配置参数都存储在 `scripts/config/service.conf` 文件中，包括：

- 服务基本信息（名称、目录、端口等）
- 环境配置（Python执行文件、虚拟环境等）
- 超时设置（启动、停止、重启超时）
- 日志配置（大小阈值、保留天数）
- 备份配置（目录、保留天数、间隔）
- 健康检查配置（URL、超时）
- 资源监控阈值（CPU、内存、磁盘）

## 安全最佳实践

1. **权限管理**：确保脚本文件权限设置正确（755）
2. **配置安全**：敏感信息（如API密钥）应通过环境变量或加密配置文件管理
3. **日志安全**：确保日志文件权限设置正确，避免敏感信息泄露
4. **备份安全**：备份文件应存储在安全位置，定期验证备份完整性
5. **执行安全**：避免使用root权限执行脚本，使用最小权限原则

## 故障排除

### 常见问题

1. **服务启动失败**
   - 检查配置文件中的服务目录和端口设置
   - 检查Python环境和依赖安装
   - 查看日志文件中的错误信息

2. **备份失败**
   - 检查备份目录权限
   - 确保磁盘空间充足
   - 检查备份文件路径是否正确

3. **日志管理失败**
   - 检查日志目录权限
   - 确保磁盘空间充足
   - 检查日志文件权限

4. **监控功能异常**
   - 检查系统工具是否安装（如top、df、lsof等）
   - 确保服务PID文件存在且有效
   - 检查网络连接和健康检查URL

## 定时任务设置

建议设置以下定时任务：

1. **日志管理**：每天执行一次日志轮转和清理
   ```bash
   0 0 * * * /path/to/ai-agent-system/scripts/bin/logs.sh
   ```

2. **备份**：每天执行一次完整备份
   ```bash
   0 1 * * * /path/to/ai-agent-system/scripts/bin/backup.sh --full
   ```

3. **状态监控**：每小时执行一次状态检查
   ```bash
   0 * * * * /path/to/ai-agent-system/scripts/bin/status.sh
   ```

## 脚本扩展

### 添加新脚本

1. 在 `bin/` 目录中创建新脚本
2. 在 `service.sh` 中添加对应的命令处理
3. 在 `config/service.conf` 中添加必要的配置参数
4. 为新脚本添加执行权限

### 自定义配置

可以通过修改 `config/service.conf` 文件来自定义脚本行为，或者通过环境变量覆盖默认配置。

## 注意事项

1. 所有脚本应在服务目录下执行
2. 首次运行前应检查配置文件中的路径设置
3. 定期检查日志和备份文件，确保系统正常运行
4. 生产环境中应适当调整配置参数以满足实际需求

## 版本信息

- 脚本版本：1.0.0
- 支持平台：Linux、macOS
- 依赖工具：bash、tar、gzip、curl、ps、lsof等

---

**维护者**：<maintainer@example.com>
**文档更新时间**：2026-04-09