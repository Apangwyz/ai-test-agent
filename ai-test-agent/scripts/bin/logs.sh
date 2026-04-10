#!/bin/bash
# 日志管理脚本

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

# 检查日志文件
check_log_files() {
    log "INFO" "检查日志文件..."
    
    # 确保日志目录存在
    mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
    
    # 检查主日志文件
    if [ ! -f "$SERVICE_LOG_FILE" ]; then
        log "INFO" "创建主日志文件: $SERVICE_LOG_FILE"
        touch "$SERVICE_LOG_FILE"
    fi
    
    log "INFO" "主日志文件: $SERVICE_LOG_FILE"
    log "INFO" "日志文件大小: $(echo "scale=2; $(stat -f "%z" "$SERVICE_LOG_FILE") / 1024 / 1024" | bc) MB"
}

# 轮转日志
rotate_logs() {
    log "INFO" "开始日志轮转..."
    
    # 检查日志文件大小
    local log_size=$(stat -f "%z" "$SERVICE_LOG_FILE")
    
    # 如果日志文件超过阈值，进行轮转
    if (( log_size > LOG_MAX_SIZE )); then
        log "INFO" "日志文件超过阈值，进行轮转"
        
        # 生成时间戳
        local timestamp=$(date "%Y%m%d_%H%M%S")
        local rotated_log="${SERVICE_LOG_FILE}.${timestamp}"
        
        # 重命名日志文件
        log "INFO" "将日志文件重命名为: $rotated_log"
        mv "$SERVICE_LOG_FILE" "$rotated_log"
        
        # 创建新的日志文件
        touch "$SERVICE_LOG_FILE"
        log "INFO" "创建新的日志文件: $SERVICE_LOG_FILE"
        
        # 压缩轮转的日志文件
        compress_log "$rotated_log"
    else
        log "INFO" "日志文件大小未超过阈值，无需轮转"
    fi
}

# 压缩日志
compress_log() {
    local log_file=$1
    log "INFO" "压缩日志文件: $log_file"
    
    if gzip "$log_file"; then
        log "INFO" "日志文件压缩成功: ${log_file}.gz"
    else
        log "ERROR" "日志文件压缩失败"
    fi
}

# 清理旧日志
cleanup_logs() {
    log "INFO" "清理旧日志文件..."
    
    # 清理超过保留天数的日志文件
    local cutoff_date=$(date "-v-${LOG_RETENTION_DAYS}d" +"%Y%m%d")
    log "INFO" "清理 ${LOG_RETENTION_DAYS} 天前的日志文件"
    
    # 查找并删除旧日志文件
    find "$(dirname "$SERVICE_LOG_FILE")" -name "*.log.*.gz" -o -name "*.log.*" | while read -r file; do
        # 提取文件中的日期
        local file_date=$(echo "$file" | grep -o "[0-9]8")
        if [ -n "$file_date" ] && [ "$file_date" -lt "$cutoff_date" ]; then
            log "INFO" "删除旧日志文件: $file"
            rm -f "$file"
        fi
    done
    
    log "INFO" "旧日志清理完成"
}

# 查看日志
view_logs() {
    local lines=${1:-100}
    log "INFO" "查看最近 $lines 行日志"
    
    if [ -f "$SERVICE_LOG_FILE" ]; then
        tail -n "$lines" "$SERVICE_LOG_FILE"
    else
        log "ERROR" "日志文件不存在: $SERVICE_LOG_FILE"
    fi
}

# 搜索日志
search_logs() {
    local pattern=$1
    if [ -z "$pattern" ]; then
        log "ERROR" "请指定搜索模式"
        return 1
    fi
    
    log "INFO" "搜索日志中的模式: $pattern"
    
    if [ -f "$SERVICE_LOG_FILE" ]; then
        grep -n "$pattern" "$SERVICE_LOG_FILE"
    else
        log "ERROR" "日志文件不存在: $SERVICE_LOG_FILE"
    fi
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
    
    log "INFO" "开始日志管理..."
    
    # 检查日志文件
    check_log_files
    
    # 轮转日志
    rotate_logs
    
    # 清理旧日志
    cleanup_logs
    
    log "INFO" "日志管理完成"
}

# 显示帮助信息
show_help() {
    echo "日志管理脚本"
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -h, --help    显示帮助信息"
    echo "  -v, --verbose 显示详细信息"
    echo "  -r, --rotate  强制轮转日志"
    echo "  -c, --cleanup 清理旧日志"
    echo "  -v, --view    查看日志 [行数]"
    echo "  -s, --search  搜索日志 [模式]"
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
        -r|--rotate)
            # 创建日志目录
            mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
            log "INFO" "强制轮转日志"
            # 生成时间戳
            local timestamp=$(date "%Y%m%d_%H%M%S")
            local rotated_log="${SERVICE_LOG_FILE}.${timestamp}"
            # 重命名日志文件
            mv "$SERVICE_LOG_FILE" "$rotated_log" 2>/dev/null || true
            # 创建新的日志文件
            touch "$SERVICE_LOG_FILE"
            # 压缩轮转的日志文件
            compress_log "$rotated_log" 2>/dev/null || true
            exit 0
            ;;
        -c|--cleanup)
            # 创建日志目录
            mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
            cleanup_logs
            exit 0
            ;;
        -v|--view)
            shift
            local lines=${1:-100}
            view_logs "$lines"
            exit 0
            ;;
        -s|--search)
            shift
            local pattern=$1
            if [ -z "$pattern" ]; then
                echo "请指定搜索模式"
                show_help
                exit 1
            fi
            search_logs "$pattern"
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