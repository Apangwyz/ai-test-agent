#!/bin/bash
# 服务管理脚本 - 统一入口

# 脚本目录
SCRIPT_DIR="$(dirname "$0")"

# 显示帮助信息
show_help() {
    echo "服务管理脚本"
    echo "用法: $0 [命令] [选项]"
    echo "命令:"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  status    查看服务状态"
    echo "  logs      管理日志"
    echo "  backup    备份恢复"
    echo "  help      显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start              # 启动服务"
    echo "  $0 stop               # 停止服务"
    echo "  $0 restart            # 重启服务"
    echo "  $0 status            # 查看服务状态"
    echo "  $0 logs --view 100    # 查看最近100行日志"
    echo "  $0 backup --full      # 执行完整备份"
}

# 主函数
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    local command=$1
    shift
    
    case "$command" in
        start)
            "$SCRIPT_DIR/start.sh" "$@"
            ;;
        stop)
            "$SCRIPT_DIR/stop.sh" "$@"
            ;;
        restart)
            "$SCRIPT_DIR/restart.sh" "$@"
            ;;
        status)
            "$SCRIPT_DIR/status.sh" "$@"
            ;;
        logs)
            "$SCRIPT_DIR/logs.sh" "$@"
            ;;
        backup)
            "$SCRIPT_DIR/backup.sh" "$@"
            ;;
        help)
            show_help
            ;;
        *)
            echo "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"