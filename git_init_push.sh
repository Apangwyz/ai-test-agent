#!/bin/bash
# Git 初始化和推送脚本
# 用于一次性完成代码的初次提交到 GitHub 远端仓库

# 颜色定义
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# 显示帮助信息
show_help() {
    echo "Git 初始化和推送脚本"
    echo "用法: $0 [GitHub 仓库 URL]"
    echo ""
    echo "示例: $0 https://github.com/username/repository.git"
    echo ""
    echo "功能:"
    echo "  1. 初始化 Git 仓库（如果尚未初始化）"
    echo "  2. 添加所有文件到暂存区"
    echo "  3. 提交代码"
    echo "  4. 添加远端仓库"
    echo "  5. 推送代码到远端仓库"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}错误: $1 命令未找到${NC}"
        exit 1
    fi
}

# 主函数
main() {
    # 检查参数
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi
    
    local repo_url=$1
    local current_dir=$(pwd)
    local repo_name=$(basename "$current_dir")
    
    echo -e "${GREEN}=== 开始 Git 初始化和推送 ===${NC}"
    echo -e "当前目录: ${YELLOW}$current_dir${NC}"
    echo -e "仓库 URL: ${YELLOW}$repo_url${NC}"
    
    # 检查必要的命令
    check_command git
    
    # 检查是否已经是 Git 仓库
    if [ ! -d ".git" ]; then
        echo -e "${GREEN}初始化 Git 仓库...${NC}"
        git init
        if [ $? -ne 0 ]; then
            echo -e "${RED}初始化 Git 仓库失败${NC}"
            exit 1
        fi
        echo -e "${GREEN}Git 仓库初始化成功${NC}"
    else
        echo -e "${YELLOW}Git 仓库已存在，跳过初始化${NC}"
    fi
    
    # 创建 .gitignore 文件（如果不存在）
    if [ ! -f ".gitignore" ]; then
        echo -e "${GREEN}创建 .gitignore 文件...${NC}"
        cat > .gitignore << EOF
# 虚拟环境
venv/
env/

# 日志文件
*.log
logs/

# 临时文件
*.tmp
*.temp

# 配置文件
.env
.env.local
.env.*.local

# 编辑器文件
.vscode/
.idea/
*.swp
*.swo
*~

# 操作系统文件
.DS_Store
Thumbs.db

# 构建文件
build/
dist/

# 数据库文件
*.db
*.sqlite3

# 测试文件
.pytest_cache/
EOF
        echo -e "${GREEN}.gitignore 文件创建成功${NC}"
    else
        echo -e "${YELLOW}.gitignore 文件已存在，跳过创建${NC}"
    fi
    
    # 添加所有文件到暂存区
    echo -e "${GREEN}添加所有文件到暂存区...${NC}"
    git add .
    if [ $? -ne 0 ]; then
        echo -e "${RED}添加文件失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}文件添加成功${NC}"
    
    # 提交代码
    echo -e "${GREEN}提交代码...${NC}"
    git commit -m "Initial commit: 初始化项目"
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}提交失败，可能没有需要提交的更改${NC}"
    else
        echo -e "${GREEN}代码提交成功${NC}"
    fi
    
    # 添加远端仓库
    echo -e "${GREEN}添加远端仓库...${NC}"
    git remote add origin "$repo_url"
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}远端仓库已存在，跳过添加${NC}"
    else
        echo -e "${GREEN}远端仓库添加成功${NC}"
    fi
    
    # 推送代码到远端仓库
    echo -e "${GREEN}推送代码到远端仓库...${NC}"
    git push -u origin master
    if [ $? -ne 0 ]; then
        # 尝试推送 main 分支
        echo -e "${YELLOW}推送 master 分支失败，尝试推送 main 分支...${NC}"
        git push -u origin main
        if [ $? -ne 0 ]; then
            echo -e "${RED}推送失败，请检查仓库 URL 和网络连接${NC}"
            exit 1
        else
            echo -e "${GREEN}代码推送成功（main 分支）${NC}"
        fi
    else
        echo -e "${GREEN}代码推送成功（master 分支）${NC}"
    fi
    
    echo -e "${GREEN}=== Git 初始化和推送完成 ===${NC}"
    echo -e "项目已成功提交到 GitHub 仓库: ${YELLOW}$repo_url${NC}"
}

# 执行主函数
main "$@"