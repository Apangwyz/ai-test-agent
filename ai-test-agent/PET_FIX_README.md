# PET工具问题修复指南

## 问题根本原因

Python Environment Tools (PET) 失败的根本原因是 **PYTHONPATH 环境变量冲突**。

### 具体问题
- 系统的 `PYTHONPATH` 环境变量包含了 Python 3.11 的路径
- 这导致 PET 工具在检测 Python 环境时产生混淆
- 虚拟环境的 Python 3.10 被错误地混合了 Python 3.11 的 site-packages 路径

## 修复方法

### 方法1：临时修复（当前终端会话）
```bash
cd ai-agent-system
unset PYTHONPATH
source venv/bin/activate
python app.py
```

### 方法2：永久修复（推荐）

1. **检查当前 PYTHONPATH**：
   ```bash
   echo $PYTHONPATH
   ```

2. **从 shell 配置中移除 PYTHONPATH**：
   
   编辑 `~/.zshrc` 或 `~/.bash_profile`：
   ```bash
   # 找到并注释掉或删除以下行
   # export PYTHONPATH=/opt/homebrew/lib/python3.11/site-packages
   ```

3. **重新加载配置**：
   ```bash
   source ~/.zshrc  # 或 source ~/.bash_profile
   ```

4. **验证修复**：
   ```bash
   cd ai-agent-system
   source venv/bin/activate
   python -c "import sys; print(all('3.11' not in p for p in sys.path))"
   # 应该输出: True
   ```

## 当前环境状态

### ✅ 已完成的修复
1. 创建了虚拟环境 `venv`
2. 安装了所有依赖项到虚拟环境
3. 修复了 `requirements.txt` 中的错误依赖
4. 修复了 Python 代码中的 f-string 语法错误
5. 配置了正确的 Python 解释器路径
6. 解决了 PYTHONPATH 冲突问题

### ✅ 应用运行状态
- 应用成功运行在: http://192.168.1.53:5001/
- 调试模式已开启
- 虚拟环境隔离正确

## 验证步骤

运行以下命令验证环境是否正确：

```bash
cd ai-agent-system
source venv/bin/activate
python test_pet.py
```

预期输出：
```
Python executable: /Users/apang/Documents/trae_projects/test-weaver/ai-agent-system/venv/bin/python
Python version: 3.10.17
Flask version: 2.0.1
OpenAI imported successfully
PET test completed successfully!
```

## 注意事项

1. **不要设置全局 PYTHONPATH**：这会导致各种 Python 版本冲突问题
2. **使用虚拟环境**：每个项目使用独立的虚拟环境
3. **Trae IDE 重启**：修复后可能需要重启 Trae IDE 窗口

## 故障排除

如果 PET 工具仍然报错：

1. **重启 Trae IDE**：
   - 关闭 Trae IDE
   - 确保 PYTHONPATH 已清除
   - 重新打开 Trae IDE

2. **手动选择解释器**：
   - 在 Trae IDE 中按 `Cmd+Shift+P`
   - 选择 "Python: Select Interpreter"
   - 选择 `./venv/bin/python`

3. **清除缓存**：
   ```bash
   rm -rf ~/Library/Application\ Support/Trae/
   ```

## 联系支持

如果问题仍然存在，请提供：
1. `echo $PYTHONPATH` 的输出
2. `which python` 的输出
3. Trae IDE 的版本信息
