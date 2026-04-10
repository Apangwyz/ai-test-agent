#!/bin/bash
# 备份恢复脚本

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

# 检查备份目录
check_backup_dir() {
    log "INFO" "检查备份目录..."
    
    # 确保备份目录存在
    mkdir -p "$BACKUP_DIR"
    log "INFO" "备份目录: $BACKUP_DIR"
}

# 执行备份
perform_backup() {
    local backup_type=${1:-"full"}  # 默认为完整备份
    log "INFO" "开始${backup_type}备份..."
    
    # 生成时间戳
    local timestamp=$(date "%Y%m%d_%H%M%S")
    local backup_file="${BACKUP_DIR}/${SERVICE_NAME}_${backup_type}_${timestamp}.tar.gz"
    
    # 定义要备份的文件和目录
    local backup_items=(
        "${SERVICE_DIR}/.env"
        "${SERVICE_DIR}/config"
        "${SERVICE_DIR}/src"
        "${SERVICE_DIR}/requirements.txt"
        "${SERVICE_DIR}/app.py"
    )
    
    # 检查备份项是否存在
    local existing_items=()
    for item in "${backup_items[@]}"; do
        if [ -e "$item" ]; then
            existing_items+=("$item")
        else
            log "WARN" "备份项不存在: $item"
        fi
    done
    
    if [ ${#existing_items[@]} -eq 0 ]; then
        log "ERROR" "没有找到可备份的文件或目录"
        return 1
    fi
    
    # 执行备份
    log "INFO" "创建备份文件: $backup_file"
    
    if tar -czf "$backup_file" -C "${SERVICE_DIR}" "${existing_items[@]/#${SERVICE_DIR}\//}"; then
        log "INFO" "备份成功: $backup_file"
        log "INFO" "备份大小: $(du -h "$backup_file" | awk '{print $1}')"
        
        # 验证备份文件
        verify_backup "$backup_file"
        
        # 清理旧备份
        cleanup_backups
        
        return 0
    else
        log "ERROR" "备份失败"
        return 1
    fi
}

# 验证备份
verify_backup() {
    local backup_file=$1
    log "INFO" "验证备份文件: $backup_file"
    
    if tar -tzf "$backup_file" > /dev/null 2>&1; then
        log "INFO" "备份文件验证成功"
        local file_count=$(tar -tzf "$backup_file" | wc -l)
        log "INFO" "备份文件包含 $file_count 个文件/目录"
    else
        log "ERROR" "备份文件验证失败"
    fi
}

# 清理旧备份
cleanup_backups() {
    log "INFO" "清理旧备份文件..."
    
    # 清理超过保留天数的备份文件
    local cutoff_date=$(date "-v-${BACKUP_RETENTION_DAYS}d" +"%s")
    log "INFO" "清理 ${BACKUP_RETENTION_DAYS} 天前的备份文件"
    
    # 查找并删除旧备份文件
    find "$BACKUP_DIR" -name "*.tar.gz" -type f | while read -r file; do
        local file_date=$(stat -f "%m" "$file")
        if [ "$file_date" -lt "$cutoff_date" ]; then
            log "INFO" "删除旧备份文件: $file"
            rm -f "$file"
        fi
    done
    
    log "INFO" "旧备份清理完成"
}

# 恢复备份
restore_backup() {
    local backup_file=$1
    if [ -z "$backup_file" ]; then
        log "ERROR" "请指定备份文件"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log "ERROR" "备份文件不存在: $backup_file"
        return 1
    fi
    
    log "INFO" "开始恢复备份: $backup_file"
    
    # 停止服务
    log "INFO" "停止服务..."
    "$(dirname "$0")/stop.sh"
    
    # 恢复备份
    log "INFO" "从备份文件恢复..."
    if tar -xzf "$backup_file" -C "${SERVICE_DIR}"; then
        log "INFO" "备份恢复成功"
        
        # 启动服务
        log "INFO" "启动服务..."
        "$(dirname "$0")/start.sh"
        
        return 0
    else
        log "ERROR" "备份恢复失败"
        return 1
    fi
}

# 列出备份
list_backups() {
    log "INFO" "列出备份文件..."
    
    if [ -d "$BACKUP_DIR" ]; then
        local backups=($(ls -t "$BACKUP_DIR"/*.tar.gz 2>/dev/null))
        if [ ${#backups[@]} -eq 0 ]; then
            log "INFO" "没有找到备份文件"
        else
            log "INFO" "找到 ${#backups[@]} 个备份文件"
            for backup in "${backups[@]}"; do
                local size=$(du -h "$backup" | awk '{print $1}')
                local date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$backup")
                log "INFO" "$backup (${size}) - $date"
            done
        fi
    else
        log "ERROR" "备份目录不存在: $BACKUP_DIR"
    fi
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
    
    # 检查备份目录
    check_backup_dir
    
    # 执行完整备份
    perform_backup "full"
}

# 显示帮助信息
show_help() {
    echo "备份恢复脚本"
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -h, --help    显示帮助信息"
    echo "  -v, --verbose 显示详细信息"
    echo "  -f, --full    执行完整备份"
    echo "  -d, --diff    执行差异备份"
    echo "  -r, --restore 恢复备份 [备份文件]"
    echo "  -l, --list    列出备份文件"
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
        -f|--full)
            # 创建日志目录
            mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
            # 检查备份目录
            check_backup_dir
            # 执行完整备份
            perform_backup "full"
            exit 0
            ;;
        -d|--diff)
            # 创建日志目录
            mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
            # 检查备份目录
            check_backup_dir
            # 执行差异备份
            perform_backup "diff"
            exit 0
            ;;
        -r|--restore)
            shift
            local backup_file=$1
            if [ -z "$backup_file" ]; then
                echo "请指定备份文件"
                show_help
                exit 1
            fi
            # 创建日志目录
            mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
            # 恢复备份
            restore_backup "$backup_file"
            exit 0
            ;;
        -l|--list)
            # 创建日志目录
            mkdir -p "$(dirname "$SERVICE_LOG_FILE")"
            # 列出备份
            list_backups
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