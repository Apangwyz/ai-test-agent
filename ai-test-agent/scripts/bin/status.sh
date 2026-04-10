#!/bin/bash
# 服务状态监控脚本

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

# 检查服务状态
check_service_status() {
    log "INFO" "检查服务状态..."
    
    if [ -f "$SERVICE_PID_FILE" ]; then
        local pid=$(cat "$SERVICE_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log "INFO" "服务状态: 运行中"
            log "INFO" "服务PID: $pid"
            
            # 检查服务端口
            if lsof -i :"$SERVICE_PORT" > /dev/null 2>&1; then
                log "INFO" "服务端口: $SERVICE_PORT (监听中)"
            else
                log "WARN" "服务端口: $SERVICE_PORT (未监听)"
            fi
            
            # 健康检查
            local http_code=$(curl -s -o /dev/null -w "%{http_code}" -m "$HEALTH_CHECK_TIMEOUT" "$HEALTH_CHECK_URL")
            if [ "$http_code" -eq 200 ]; then
                log "INFO" "健康检查: 正常 (HTTP $http_code)"
            else
                log "WARN" "健康检查: 异常 (HTTP $http_code)"
            fi
            
            return 0
        else
            log "WARN" "服务状态: 已停止 (PID文件存在但进程不存在)"
            rm -f "$SERVICE_PID_FILE"
            return 1
        fi
    else
        log "INFO" "服务状态: 未启动"
        return 1
    fi
}

# 监控系统资源
monitor_resources() {
    log "INFO" "监控系统资源..."
    
    # CPU使用率
    local cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
    log "INFO" "CPU使用率: ${cpu_usage}%"
    
    if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l) )); then
        log "WARN" "CPU使用率超过阈值 ($CPU_THRESHOLD%)"
    fi
    
    # 内存使用率
    local memory_usage=$(top -l 1 | grep "PhysMem" | awk '{print $2}' | sed 's/%//')
    log "INFO" "内存使用率: ${memory_usage}%"
    
    if (( $(echo "$memory_usage > $MEMORY_THRESHOLD" | bc -l) )); then
        log "WARN" "内存使用率超过阈值 ($MEMORY_THRESHOLD%)"
    fi
    
    # 磁盘使用率
    local disk_usage=$(df -h / | tail -n 1 | awk '{print $5}' | sed 's/%//')
    log "INFO" "磁盘使用率: ${disk_usage}%"
    
    if (( disk_usage > DISK_THRESHOLD )); then
        log "WARN" "磁盘使用率超过阈值 ($DISK_THRESHOLD%)"
    fi
    
    # 服务进程资源使用
    if [ -f "$SERVICE_PID_FILE" ]; then
        local pid=$(cat "$SERVICE_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            local proc_cpu=$(ps -p "$pid" -o %cpu= | awk '{print $1}')
            local proc_mem=$(ps -p "$pid" -o %mem= | awk '{print $1}')
            log "INFO" "服务进程CPU使用率: ${proc_cpu}%"
            log "INFO" "服务进程内存使用率: ${proc_mem}%"
        fi
    fi
}

# 监控日志
monitor_logs() {
    log "INFO" "监控日志..."
    
    # 检查日志文件大小
    if [ -f "$SERVICE_LOG_FILE" ]; then
        local log_size=$(stat -f "%z" "$SERVICE_LOG_FILE")
        log "INFO" "日志文件大小: $(echo "scale=2; $log_size / 1024 / 1024" | bc) MB"
        
        if (( log_size > LOG_MAX_SIZE )); then
            log "WARN" "日志文件大小超过阈值 ($(echo "scale=2; $LOG_MAX_SIZE / 1024 / 1024" | bc) MB)"
        fi
    fi
    
    # 检查错误日志
    if [ -f "$SERVICE_LOG_FILE" ]; then
        local error_count=$(grep -i "error" "$SERVICE_LOG_FILE" | wc -l)
        local warn_count=$(grep -i "warn" "$SERVICE_LOG_FILE" | wc -l)
        log "INFO" "错误日志数量: $error_count"
        log "INFO" "警告日志数量: $warn_count"
    fi
}

# 显示详细状态
show_detailed_status() {
    log "INFO" "显示详细状态..."
    
    # 系统信息
    log "INFO" "系统信息: $(uname -a)"
    log "INFO" "当前时间: $(date)"
    
    # 服务配置
    log "INFO" "服务名称: $SERVICE_NAME"
    log "INFO" "服务目录: $SERVICE_DIR"
    log "INFO" "服务端口: $SERVICE_PORT"
    
    # 环境信息
    if [ -f "$PYTHON_EXEC" ]; then
        log "INFO" "Python版本: $($PYTHON_EXEC --version 2>&1)"
    fi
    
    # 依赖状态
    if [ -f "${SERVICE_DIR}/requirements.txt" ]; then
        local installed_packages=$(${VENV_DIR}/bin/pip list 2>/dev/null | wc -l)
        log "INFO" "已安装依赖包数量: $installed_packages"
    fi
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
    
    log "INFO" "开始状态监控..."
    
    # 检查服务状态
    check_service_status
    
    # 监控资源
    monitor_resources
    
    # 监控日志
    monitor_logs
    
    # 显示详细状态
    show_detailed_status
    
    log "INFO" "状态监控完成"
}

# 显示帮助信息
show_help() {
    echo "服务状态监控脚本"
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -h, --help    显示帮助信息"
    echo "  -v, --verbose 显示详细信息"
    echo "  -s, --status  只显示服务状态"
    echo "  -r, --resources 只显示资源监控"
    echo "  -l, --logs    只显示日志监控"
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
        -s|--status)
            # 创建日志目录
            mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
            check_service_status
            exit 0
            ;;
        -r|--resources)
            # 创建日志目录
            mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
            monitor_resources
            exit 0
            ;;
        -l|--logs)
            # 创建日志目录
            mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
            monitor_logs
            exit 0
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