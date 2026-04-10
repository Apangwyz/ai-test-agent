#!/bin/bash
# 服务启动脚本

# 加载配置文件
CONFIG_FILE="$(dirname "$(dirname "$0")")/config/service.conf"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 日志函数
log() {
    local level=$1
    local message=$2
    local timestamp=$(date "%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] $message" >> "$SERVICE_LOG_FILE"
    echo "[$timestamp] [$level] $message"
}

# 检查环境
check_environment() {
    log "INFO" "开始检查环境..."
    
    # 检查Python环境
    if [ ! -f "$PYTHON_EXEC" ]; then
        log "ERROR" "Python执行文件不存在: $PYTHON_EXEC"
        log "INFO" "尝试创建虚拟环境..."
        
        # 尝试创建虚拟环境
        if python3 -m venv "$VENV_DIR"; then
            log "INFO" "虚拟环境创建成功"
            # 安装依赖
            log "INFO" "安装依赖..."
            if "${VENV_DIR}/bin/pip" install -r "${SERVICE_DIR}/requirements.txt"; then
                log "INFO" "依赖安装成功"
                PYTHON_EXEC="${VENV_DIR}/bin/python"
            else
                log "ERROR" "依赖安装失败"
                return 1
            fi
        else
            log "ERROR" "虚拟环境创建失败"
            return 1
        fi
    fi
    
    # 检查服务目录
    if [ ! -d "$SERVICE_DIR" ]; then
        log "ERROR" "服务目录不存在: $SERVICE_DIR"
        return 1
    fi
    
    # 检查配置文件
    if [ ! -f "${SERVICE_DIR}/.env" ]; then
        log "WARN" ".env 文件不存在，将使用默认配置"
    fi
    
    log "INFO" "环境检查完成"
    return 0
}

# 检查服务是否已启动
check_service_running() {
    if [ -f "$SERVICE_PID_FILE" ]; then
        local pid=$(cat "$SERVICE_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log "INFO" "服务已经在运行，PID: $pid"
            return 0
        else
            log "WARN" "PID文件存在但进程不存在，清理PID文件"
            rm -f "$SERVICE_PID_FILE"
            return 1
        fi
    fi
    return 1
}

# 启动服务
start_service() {
    log "INFO" "开始启动服务..."
    
    # 切换到服务目录
    cd "$SERVICE_DIR" || {
        log "ERROR" "无法切换到服务目录: $SERVICE_DIR"
        return 1
    }
    
    # 设置环境变量
    export FLASK_APP="$FLASK_APP"
    export FLASK_ENV="$FLASK_ENV"
    
    # 启动服务
    log "INFO" "启动服务，监听 ${SERVICE_HOST}:${SERVICE_PORT}"
    nohup "$PYTHON_EXEC" -m flask run --host="$SERVICE_HOST" --port="$SERVICE_PORT" > "$SERVICE_LOG_FILE" 2>&1 &
    
    # 记录PID
    local pid=$!
    echo "$pid" > "$SERVICE_PID_FILE"
    log "INFO" "服务启动，PID: $pid"
    
    # 等待服务启动
    local countdown=$START_TIMEOUT
    while [ $countdown -gt 0 ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$HEALTH_CHECK_URL" | grep -q "200"; then
            log "INFO" "服务启动成功，健康检查通过"
            return 0
        fi
        sleep 1
        countdown=$((countdown - 1))
    done
    
    log "ERROR" "服务启动超时，健康检查失败"
    return 1
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
    
    # 检查环境
    if ! check_environment; then
        log "ERROR" "环境检查失败"
        exit 1
    fi
    
    # 检查服务是否已运行
    if check_service_running; then
        exit 0
    fi
    
    # 启动服务
    if start_service; then
        log "INFO" "服务启动成功"
        exit 0
    else
        log "ERROR" "服务启动失败"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "服务启动脚本"
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -h, --help    显示帮助信息"
    echo "  -v, --verbose 显示详细信息"
}

# 解析命令行参数
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            set -x
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
    shift
 done

# 执行主函数
main