#!/usr/bin/env python3
"""
创建测试用户账户脚本

此脚本用于在系统数据库中创建一个测试用户账户，包含完整的用户信息字段，
具有预设的角色权限，并符合系统的数据模型规范。
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.auth.models import User
from src.auth.database import Base


def create_test_user():
    """
    创建测试用户账户
    """
    try:
        # 从环境变量获取数据库URL
        from dotenv import load_dotenv
        load_dotenv()
        
        DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://admin:password@localhost:5432/example_db')
        
        # 创建数据库引擎
        engine = create_engine(DATABASE_URL)
        
        # 创建所有表（如果不存在）
        Base.metadata.create_all(bind=engine)
        
        # 创建会话
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # 检查测试用户是否已存在
            test_user = db.query(User).filter_by(email='test@example.com').first()
            
            if test_user:
                print("测试用户已存在，更新信息...")
                # 更新现有用户信息
                test_user.username = '测试用户'
                test_user.password_hash = generate_password_hash('password123', method='pbkdf2:sha256')
                test_user.role = 'admin'  # 设置为管理员角色
                db.commit()
                print("测试用户信息已更新")
            else:
                # 创建新的测试用户
                hashed_password = generate_password_hash('password123', method='pbkdf2:sha256')
                new_user = User(
                    username='测试用户',
                    email='test@example.com',
                    password_hash=hashed_password,
                    role='admin'  # 设置为管理员角色
                )
                
                db.add(new_user)
                db.commit()
                print("测试用户创建成功")
                print(f"用户ID: {new_user.id}")
                print(f"用户名: {new_user.username}")
                print(f"邮箱: {new_user.email}")
                print(f"角色: {new_user.role}")
                print(f"创建时间: {new_user.created_at}")
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"创建测试用户失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("开始创建测试用户账户...")
    create_test_user()
    print("测试用户账户创建完成！")
    print("\n测试用户信息：")
    print("邮箱: test@example.com")
    print("密码: password123")
    print("角色: admin")
    print("\n您可以使用以上凭证登录系统进行测试。")
