import logging
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

class AuditAction(Enum):
    """审计操作类型"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"
    EXPORT = "export"
    IMPORT = "import"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHANGE = "permission_change"
    ADAPTER_SWITCH = "adapter_switch"

class AuditLogEntry:
    """
    审计日志条目
    """
    
    def __init__(self, action: AuditAction, user_id: str, resource_type: str, 
                 resource_id: str, details: Dict[str, Any] = None):
        self.id = f"audit_{datetime.now().timestamp()}_{hash(f'{user_id}_{action}_{resource_id}')}"
        self.action = action.value
        self.user_id = user_id
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.details = details or {}
        self.timestamp = datetime.now()
        self.ip_address = ""
        self.user_agent = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'action': self.action,
            'user_id': self.user_id,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }

class AuditLogger:
    """
    审计日志记录器
    记录所有对知识库的操作
    """
    
    def __init__(self, log_dir: str = "data/knowledge_base/audit"):
        self.logger = logging.getLogger(__name__)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 当前日志文件（按日期命名）
        self.current_log_file = self._get_today_log_file()
        
        # 内存缓存最近的日志条目（用于快速查询）
        self.recent_logs = []
        self.max_recent_logs = 1000
    
    def _get_today_log_file(self) -> Path:
        """获取今日的日志文件路径"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"audit_{today}.json"
    
    def _rotate_log_file(self):
        """检查并切换日志文件（每日一个文件）"""
        new_log_file = self._get_today_log_file()
        if new_log_file != self.current_log_file:
            self.current_log_file = new_log_file
            # 清空最近日志缓存
            self.recent_logs = []
    
    def log(self, action: AuditAction, user_id: str, resource_type: str, 
            resource_id: str, details: Dict[str, Any] = None):
        """
        记录审计日志
        
        Args:
            action: 操作类型
            user_id: 操作用户ID
            resource_type: 资源类型
            resource_id: 资源ID
            details: 额外详情
        """
        # 检查日志文件是否需要切换
        self._rotate_log_file()
        
        # 创建日志条目
        entry = AuditLogEntry(action, user_id, resource_type, resource_id, details)
        
        # 添加到内存缓存
        self.recent_logs.append(entry)
        
        # 限制缓存大小
        if len(self.recent_logs) > self.max_recent_logs:
            self.recent_logs = self.recent_logs[-self.max_recent_logs:]
        
        # 写入文件
        self._write_log(entry)
        
        self.logger.debug(f"Audit log: {action.value} by {user_id} on {resource_type}:{resource_id}")
    
    def _write_log(self, entry: AuditLogEntry):
        """将日志条目写入文件"""
        try:
            # 读取现有日志
            if self.current_log_file.exists():
                with open(self.current_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # 添加新日志
            logs.append(entry.to_dict())
            
            # 写入文件
            with open(self.current_log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error writing audit log: {e}")
    
    def get_recent_logs(self, limit: int = 50) -> List[AuditLogEntry]:
        """
        获取最近的日志条目
        
        Args:
            limit: 返回数量限制
            
        Returns:
            日志条目列表
        """
        return self.recent_logs[-limit:]
    
    def search_logs(self, filters: Dict[str, Any]) -> List[AuditLogEntry]:
        """
        搜索日志条目
        
        Args:
            filters: 过滤条件（action, user_id, resource_type, resource_id, start_time, end_time）
            
        Returns:
            匹配的日志条目列表
        """
        results = []
        
        # 先搜索内存缓存
        for entry in self.recent_logs:
            if self._matches_filter(entry, filters):
                results.append(entry)
        
        # 如果需要更多结果，搜索文件
        if len(results) < filters.get('limit', 100):
            # 获取日期范围
            start_time = filters.get('start_time')
            end_time = filters.get('end_time')
            
            # 确定需要搜索的日期范围
            dates_to_search = self._get_dates_to_search(start_time, end_time)
            
            for date_str in dates_to_search:
                log_file = self.log_dir / f"audit_{date_str}.json"
                if log_file.exists():
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            logs_data = json.load(f)
                        
                        for log_data in logs_data:
                            entry = AuditLogEntry(
                                action=AuditAction(log_data['action']),
                                user_id=log_data['user_id'],
                                resource_type=log_data['resource_type'],
                                resource_id=log_data['resource_id'],
                                details=log_data.get('details', {})
                            )
                            entry.id = log_data['id']
                            entry.timestamp = datetime.fromisoformat(log_data['timestamp'])
                            entry.ip_address = log_data.get('ip_address', '')
                            entry.user_agent = log_data.get('user_agent', '')
                            
                            if self._matches_filter(entry, filters):
                                results.append(entry)
                    except Exception as e:
                        self.logger.error(f"Error reading audit log file {log_file}: {e}")
        
        # 按时间排序
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 应用限制
        limit = filters.get('limit', 100)
        return results[:limit]
    
    def _matches_filter(self, entry: AuditLogEntry, filters: Dict[str, Any]) -> bool:
        """检查日志条目是否匹配过滤条件"""
        if 'action' in filters and entry.action != filters['action'].value:
            return False
        
        if 'user_id' in filters and entry.user_id != filters['user_id']:
            return False
        
        if 'resource_type' in filters and entry.resource_type != filters['resource_type']:
            return False
        
        if 'resource_id' in filters and entry.resource_id != filters['resource_id']:
            return False
        
        if 'start_time' in filters and entry.timestamp < filters['start_time']:
            return False
        
        if 'end_time' in filters and entry.timestamp > filters['end_time']:
            return False
        
        return True
    
    def _get_dates_to_search(self, start_time: datetime = None, end_time: datetime = None) -> List[str]:
        """获取需要搜索的日期列表"""
        dates = []
        
        start = start_time or datetime.now() - timedelta(days=30)
        end = end_time or datetime.now()
        
        current = start
        while current <= end:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        return dates
    
    def get_log_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        获取日志统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            统计信息字典
        """
        from datetime import timedelta
        
        start_time = datetime.now() - timedelta(days=days)
        end_time = datetime.now()
        
        logs = self.search_logs({
            'start_time': start_time,
            'end_time': end_time
        })
        
        action_counts = {}
        user_counts = {}
        resource_type_counts = {}
        
        for entry in logs:
            action_counts[entry.action] = action_counts.get(entry.action, 0) + 1
            user_counts[entry.user_id] = user_counts.get(entry.user_id, 0) + 1
            resource_type_counts[entry.resource_type] = resource_type_counts.get(entry.resource_type, 0) + 1
        
        return {
            'total_logs': len(logs),
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'action_distribution': action_counts,
            'user_distribution': user_counts,
            'resource_type_distribution': resource_type_counts,
            'generated_at': datetime.now().isoformat()
        }
    
    def export_logs(self, output_file: str, filters: Dict[str, Any] = None) -> bool:
        """
        导出日志到文件
        
        Args:
            output_file: 输出文件路径
            filters: 过滤条件
            
        Returns:
            是否成功
        """
        try:
            logs = self.search_logs(filters or {})
            logs_data = [entry.to_dict() for entry in logs]
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(logs_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Exported {len(logs)} audit logs to {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting audit logs: {e}")
            return False

# 创建全局审计日志记录器实例
audit_logger = AuditLogger()
