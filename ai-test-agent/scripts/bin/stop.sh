#!/bin/bash
# 服务停止脚本

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

# 检查服务是否运行
check_service_running() {
    if [ -f "$SERVICE_PID_FILE" ]; then
        local pid=$(cat "$SERVICE_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log "INFO" "服务正在运行，PID: $pid"
            return 0
        else
            log "WARN" "PID文件存在但进程不存在，清理PID文件"
            rm -f "$SERVICE_PID_FILE"
            return 1
        fi
    fi
    log "INFO" "服务未运行"
    return 1
}

# 停止服务
stop_service() {
    if [ ! -f "$SERVICE_PID_FILE" ]; then
        log "INFO" "服务未运行，无需停止"
        return 0
    fi
    
    local pid=$(cat "$SERVICE_PID_FILE")
    log "INFO" "开始停止服务，PID: $pid"
    
    # 尝试正常停止
    log "INFO" "发送SIGTERM信号..."
    kill -15 "$pid"
    
    # 等待服务停止
    local countdown=$STOP_TIMEOUT
    while [ $countdown -gt 0 ]; do
        if ! ps -p "$pid" > /dev/null 2>&1; then
            log "INFO" "服务已正常停止"
            rm -f "$SERVICE_PID_FILE"
            return 0
        fi
        sleep 1
        countdown=$((countdown - 1))
    done
    
    # 超时强制停止
    log "WARN" "服务停止超时，尝试强制停止..."
    log "INFO" "发送SIGKILL信号..."
    kill -9 "$pid" > /dev/null 2>&1
    
    # 再次检查
    sleep 2
    if ! ps -p "$pid" > /dev/null 2>&1; then
        log "INFO" "服务已强制停止"
        rm -f "$SERVICE_PID_FILE"
        return 0
    else
        log "ERROR" "服务强制停止失败"
        return 1
    fi
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
    
    # 检查服务是否运行
    if ! check_service_running; then
        exit 0
    fi
    
    # 停止服务
    if stop_service; then
        log "INFO" "服务停止成功"
        exit 0
    else
        log "ERROR" "服务停止失败"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "服务停止脚本"
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -h, --help    显示帮助信息"
    echo "  -v, --verbose 显示详细信息"
    echo "  -f, --force   强制停止服务"
}

# 解析命令行参数
FORCE_STOP=false
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            set -x
            ;;
        -f|--force)
            FORCE_STOP=true
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