import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class PermissionLevel(Enum):
    """权限级别枚举"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

class PermissionManager:
    """
    知识库权限管理器
    提供实体级访问控制和用户角色权限管理
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_roles = {}  # {user_id: role}
        self.entity_permissions = {}  # {entity_id: {user_id: PermissionLevel}}
        self.role_permissions = {
            'anonymous': PermissionLevel.READ,
            'user': PermissionLevel.READ,
            'editor': PermissionLevel.WRITE,
            'admin': PermissionLevel.ADMIN
        }
    
    def set_user_role(self, user_id: str, role: str):
        """
        设置用户角色
        
        Args:
            user_id: 用户ID
            role: 角色名称 (anonymous, user, editor, admin)
        """
        if role in self.role_permissions:
            self.user_roles[user_id] = role
            self.logger.info(f"Set user {user_id} role to {role}")
        else:
            self.logger.warning(f"Unknown role: {role}")
    
    def get_user_role(self, user_id: str) -> str:
        """
        获取用户角色
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户角色名称
        """
        return self.user_roles.get(user_id, 'anonymous')
    
    def has_permission(self, user_id: str, required_permission: PermissionLevel) -> bool:
        """
        检查用户是否具有指定权限级别
        
        Args:
            user_id: 用户ID
            required_permission: 所需权限级别
            
        Returns:
            是否具有权限
        """
        role = self.get_user_role(user_id)
        user_permission = self.role_permissions.get(role, PermissionLevel.NONE)
        
        permission_order = [
            PermissionLevel.NONE,
            PermissionLevel.READ,
            PermissionLevel.WRITE,
            PermissionLevel.ADMIN
        ]
        
        return permission_order.index(user_permission) >= permission_order.index(required_permission)
    
    def has_entity_permission(self, user_id: str, entity_id: str, action: str) -> bool:
        """
        检查用户对特定实体的权限
        
        Args:
            user_id: 用户ID
            entity_id: 实体ID
            action: 操作类型 (read, write, delete)
            
        Returns:
            是否具有权限
        """
        # 管理员具有所有权限
        if self.has_permission(user_id, PermissionLevel.ADMIN):
            return True
        
        # 检查实体级权限
        entity_perms = self.entity_permissions.get(entity_id, {})
        if user_id in entity_perms:
            entity_perm = entity_perms[user_id]
        else:
            entity_perm = self.role_permissions.get(self.get_user_role(user_id), PermissionLevel.NONE)
        
        # 根据操作类型检查权限
        permission_order = [
            PermissionLevel.NONE,
            PermissionLevel.READ,
            PermissionLevel.WRITE,
            PermissionLevel.ADMIN
        ]
        
        required_level = PermissionLevel.READ
        if action in ['write', 'update']:
            required_level = PermissionLevel.WRITE
        elif action == 'delete':
            required_level = PermissionLevel.ADMIN
        
        return permission_order.index(entity_perm) >= permission_order.index(required_level)
    
    def set_entity_permission(self, entity_id: str, user_id: str, permission: PermissionLevel):
        """
        设置用户对实体的权限
        
        Args:
            entity_id: 实体ID
            user_id: 用户ID
            permission: 权限级别
        """
        if entity_id not in self.entity_permissions:
            self.entity_permissions[entity_id] = {}
        
        self.entity_permissions[entity_id][user_id] = permission
        self.logger.info(f"Set permission {permission.value} for user {user_id} on entity {entity_id}")
    
    def get_entity_permission(self, entity_id: str, user_id: str) -> PermissionLevel:
        """
        获取用户对实体的权限
        
        Args:
            entity_id: 实体ID
            user_id: 用户ID
            
        Returns:
            权限级别
        """
        entity_perms = self.entity_permissions.get(entity_id, {})
        if user_id in entity_perms:
            return entity_perms[user_id]
        
        # 返回角色默认权限
        role = self.get_user_role(user_id)
        return self.role_permissions.get(role, PermissionLevel.NONE)
    
    def remove_entity_permission(self, entity_id: str, user_id: str):
        """
        移除用户对实体的权限
        
        Args:
            entity_id: 实体ID
            user_id: 用户ID
        """
        if entity_id in self.entity_permissions and user_id in self.entity_permissions[entity_id]:
            del self.entity_permissions[entity_id][user_id]
            self.logger.info(f"Removed permission for user {user_id} on entity {entity_id}")
    
    def can_read(self, user_id: str, entity_id: str = None) -> bool:
        """
        检查用户是否具有读取权限
        
        Args:
            user_id: 用户ID
            entity_id: 实体ID（可选）
            
        Returns:
            是否具有读取权限
        """
        if entity_id is None:
            return self.has_permission(user_id, PermissionLevel.READ)
        return self.has_entity_permission(user_id, entity_id, 'read')
    
    def can_write(self, user_id: str, entity_id: str = None) -> bool:
        """
        检查用户是否具有写入权限
        
        Args:
            user_id: 用户ID
            entity_id: 实体ID（可选）
            
        Returns:
            是否具有写入权限
        """
        if entity_id is None:
            return self.has_permission(user_id, PermissionLevel.WRITE)
        return self.has_entity_permission(user_id, entity_id, 'write')
    
    def can_delete(self, user_id: str, entity_id: str = None) -> bool:
        """
        检查用户是否具有删除权限
        
        Args:
            user_id: 用户ID
            entity_id: 实体ID（可选）
            
        Returns:
            是否具有删除权限
        """
        if entity_id is None:
            return self.has_permission(user_id, PermissionLevel.ADMIN)
        return self.has_entity_permission(user_id, entity_id, 'delete')
    
    def get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户的所有权限信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户权限信息字典
        """
        role = self.get_user_role(user_id)
        role_permission = self.role_permissions.get(role, PermissionLevel.NONE)
        
        return {
            'user_id': user_id,
            'role': role,
            'role_permission': role_permission.value,
            'can_read': self.can_read(user_id),
            'can_write': self.can_write(user_id),
            'can_delete': self.can_delete(user_id),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_entity_access_list(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        获取实体的访问控制列表
        
        Args:
            entity_id: 实体ID
            
        Returns:
            访问控制列表
        """
        access_list = []
        entity_perms = self.entity_permissions.get(entity_id, {})
        
        for user_id, permission in entity_perms.items():
            access_list.append({
                'user_id': user_id,
                'permission': permission.value,
                'role': self.get_user_role(user_id)
            })
        
        return access_list
    
    def validate_access(self, user_id: str, entity_id: str, action: str) -> bool:
        """
        验证用户访问权限
        
        Args:
            user_id: 用户ID
            entity_id: 实体ID
            action: 操作类型
            
        Returns:
            是否允许访问
        """
        if not self.has_entity_permission(user_id, entity_id, action):
            self.logger.warning(f"Access denied: user={user_id}, entity={entity_id}, action={action}")
            return False
        
        self.logger.debug(f"Access granted: user={user_id}, entity={entity_id}, action={action}")
        return True

# 创建全局权限管理器实例
permission_manager = PermissionManager()
