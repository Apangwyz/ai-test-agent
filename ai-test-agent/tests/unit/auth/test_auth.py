import pytest
from unittest.mock import Mock, patch
from src.auth.auth_service import AuthService
from src.auth.models import User

class TestAuthService:
    """测试认证服务"""

    def setup_method(self):
        """设置测试环境"""
        self.auth_service = AuthService()

    @patch('src.auth.auth_service.User')
    @patch('src.auth.auth_service.db')
    def test_register_success(self, mock_db, mock_user):
        """测试成功注册用户"""
        # 模拟数据库查询结果（用户不存在）
        mock_user.query.filter_by.return_value.first.return_value = None
        
        # 模拟数据库会话
        mock_session = Mock()
        mock_db.session = mock_session
        
        # 执行注册
        user = self.auth_service.register('testuser', 'test@example.com', 'password123')
        
        # 验证结果
        assert user is not None
        mock_user.assert_called_once()
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('src.auth.auth_service.User')
    def test_register_existing_email(self, mock_user):
        """测试注册已存在的邮箱"""
        # 模拟数据库查询结果（用户已存在）
        existing_user = Mock()
        mock_user.query.filter_by.return_value.first.return_value = existing_user
        
        # 执行注册，应该抛出异常
        with pytest.raises(ValueError, match='Email already registered'):
            self.auth_service.register('testuser', 'test@example.com', 'password123')

    @patch('src.auth.auth_service.User')
    @patch('src.auth.auth_service.db')
    def test_register_error(self, mock_db, mock_user):
        """测试注册过程中的错误处理"""
        # 模拟数据库查询结果（用户不存在）
        mock_user.query.filter_by.return_value.first.return_value = None
        
        # 模拟数据库会话并设置异常
        mock_session = Mock()
        mock_session.add.side_effect = Exception("Database error")
        mock_db.session = mock_session
        
        # 执行注册，应该抛出异常
        with pytest.raises(Exception, match='Database error'):
            self.auth_service.register('testuser', 'test@example.com', 'password123')
        
        # 验证回滚被调用
        mock_session.rollback.assert_called_once()

    @patch('src.auth.auth_service.User')
    def test_login_success(self, mock_user):
        """测试成功登录"""
        # 模拟用户对象
        mock_user_instance = Mock()
        mock_user_instance.password_hash = '$pbkdf2:sha256:150000$abcdef$123456'  # 模拟哈希密码
        mock_user.query.filter_by.return_value.first.return_value = mock_user_instance
        
        # 模拟密码验证
        with patch('src.auth.auth_service.check_password_hash', return_value=True):
            user = self.auth_service.login('test@example.com', 'password123')
            assert user == mock_user_instance

    @patch('src.auth.auth_service.User')
    def test_login_invalid_email(self, mock_user):
        """测试登录时邮箱不存在"""
        # 模拟数据库查询结果（用户不存在）
        mock_user.query.filter_by.return_value.first.return_value = None
        
        # 执行登录，应该抛出异常
        with pytest.raises(ValueError, match='Invalid email or password'):
            self.auth_service.login('test@example.com', 'password123')

    @patch('src.auth.auth_service.User')
    def test_login_invalid_password(self, mock_user):
        """测试登录时密码错误"""
        # 模拟用户对象
        mock_user_instance = Mock()
        mock_user_instance.password_hash = '$pbkdf2:sha256:150000$abcdef$123456'  # 模拟哈希密码
        mock_user.query.filter_by.return_value.first.return_value = mock_user_instance
        
        # 模拟密码验证失败
        with patch('src.auth.auth_service.check_password_hash', return_value=False):
            with pytest.raises(ValueError, match='Invalid email or password'):
                self.auth_service.login('test@example.com', 'wrongpassword')

    @patch('src.auth.auth_service.User')
    def test_get_user_by_id_success(self, mock_user):
        """测试成功获取用户"""
        # 模拟用户对象
        mock_user_instance = Mock()
        mock_user.query.get.return_value = mock_user_instance
        
        # 执行获取用户
        user = self.auth_service.get_user_by_id(1)
        assert user == mock_user_instance
        mock_user.query.get.assert_called_once_with(1)

    @patch('src.auth.auth_service.User')
    def test_get_user_by_id_not_found(self, mock_user):
        """测试获取不存在的用户"""
        # 模拟数据库查询结果（用户不存在）
        mock_user.query.get.return_value = None
        
        # 执行获取用户，应该抛出异常
        with pytest.raises(ValueError, match='User not found'):
            self.auth_service.get_user_by_id(999)

    @patch('src.auth.auth_service.User')
    @patch('src.auth.auth_service.db')
    def test_update_user_role_success(self, mock_db, mock_user):
        """测试成功更新用户角色"""
        # 模拟用户对象
        mock_user_instance = Mock()
        mock_user.query.get.return_value = mock_user_instance
        
        # 模拟数据库会话
        mock_session = Mock()
        mock_db.session = mock_session
        
        # 执行更新角色
        updated_user = self.auth_service.update_user_role(1, 'admin')
        
        # 验证结果
        assert updated_user == mock_user_instance
        assert updated_user.role == 'admin'
        mock_user.query.get.assert_called_once_with(1)
        mock_session.commit.assert_called_once()

    @patch('src.auth.auth_service.User')
    def test_update_user_role_not_found(self, mock_user):
        """测试更新不存在用户的角色"""
        # 模拟数据库查询结果（用户不存在）
        mock_user.query.get.return_value = None
        
        # 执行更新角色，应该抛出异常
        with pytest.raises(ValueError, match='User not found'):
            self.auth_service.update_user_role(999, 'admin')

    @patch('src.auth.auth_service.User')
    @patch('src.auth.auth_service.db')
    def test_update_user_role_error(self, mock_db, mock_user):
        """测试更新角色过程中的错误处理"""
        # 模拟用户对象
        mock_user_instance = Mock()
        mock_user.query.get.return_value = mock_user_instance
        
        # 模拟数据库会话并设置异常
        mock_session = Mock()
        mock_session.commit.side_effect = Exception("Database error")
        mock_db.session = mock_session
        
        # 执行更新角色，应该抛出异常
        with pytest.raises(Exception, match='Database error'):
            self.auth_service.update_user_role(1, 'admin')
        
        # 验证回滚被调用
        mock_session.rollback.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])
