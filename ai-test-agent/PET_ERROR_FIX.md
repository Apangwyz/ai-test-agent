# PET 工具错误修复指南

## 错误分析

从日志中找到根本问题：

```
Process error: 发生了系统错误 (spawn /Users/apang/.trae-cn/extensions/ms-python.python-2026.4.0-universal/python-env-tools/bin/pet ENOENT)
```

**问题原因**：PET (Python Environment Tools) 二进制文件不存在。

## 解决方案

### 方案 1：重新安装 Python 扩展（推荐）

1. **打开 Trae IDE**
2. **进入扩展面板**：`Cmd+Shift+X`
3. **找到 Python 扩展**（ms-python.python）
4. **点击卸载**
5. **重新安装 Python 扩展**
6. **重启 Trae IDE**

### 方案 2：手动下载 PET 工具

如果重新安装扩展无效，可以手动下载 PET 工具：

```bash
# 创建目录
mkdir -p ~/.trae-cn/extensions/ms-python.python-2026.4.0-universal/python-env-tools/bin

# 下载 PET 工具（需要根据您的系统架构选择合适的版本）
# macOS ARM64 (Apple Silicon)
curl -L -o ~/.trae-cn/extensions/ms-python.python-2026.4.0-universal/python-env-tools/bin/pet \
  https://github.com/microsoft/python-environment-tools/releases/latest/download/pet-aarch64-apple-darwin

# 添加执行权限
chmod +x ~/.trae-cn/extensions/ms-python.python-2026.4.0-universal/python-env-tools/bin/pet
```

### 方案 3：使用 VS Code 替代

如果 Trae IDE 的 Python 扩展持续出现问题，可以：
1. 使用 VS Code 打开项目
2. 安装 Python 扩展
3. 选择虚拟环境解释器

### 方案 4：禁用 PET 工具

在 Trae IDE 设置中禁用 PET 工具：

1. 打开设置：`Cmd+,`
2. 搜索 `python.environment`
3. 禁用相关选项

## 当前状态

- ✅ Python 虚拟环境已正确配置
- ✅ 所有依赖项已安装
- ✅ 应用可以正常运行
- ❌ Trae IDE 的 PET 工具二进制文件缺失

## 临时解决方案

虽然 PET 工具报错，但您仍然可以使用终端运行 Python 代码：

```bash
cd ai-agent-system
source venv/bin/activate
python app.py
```

## 验证 PET 工具是否修复

修复后，运行以下命令验证：

```bash
ls -la ~/.trae-cn/extensions/ms-python.python-2026.4.0-universal/python-env-tools/bin/pet
```

如果文件存在，重启 Trae IDE 即可。
