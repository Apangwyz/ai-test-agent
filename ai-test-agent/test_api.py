#!/usr/bin/env python3
"""
Test script to verify API functionality
"""

import requests
import json

BASE_URL = "http://localhost:5002/api"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Services: {json.dumps(data.get('services', {}), indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_register():
    """Test user registration"""
    try:
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        print(f"\nRegister: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"User registered: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True, data
        else:
            print(f"Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"Registration failed: {e}")
        return False, None

def test_login():
    """Test user login"""
    try:
        payload = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        print(f"\nLogin: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Login successful")
            print(f"Access Token: {data.get('access_token', '')[:20]}...")
            return True, data.get('access_token')
        else:
            print(f"Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"Login failed: {e}")
        return False, None

def test_process_document(access_token):
    """Test document processing"""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Create a simple test document
        test_content = """# 测试项目需求文档

## 项目名称
测试管理系统

## 项目背景
为了提升测试效率，需要开发一套测试管理系统。

## 核心功能需求
1. 用户管理
2. 测试用例管理
3. 测试执行
4. 缺陷管理

## 非功能需求
- 性能要求：支持1000并发用户
- 兼容性：支持主流浏览器
- 安全性：数据加密存储
"""
        
        # Save to temp file
        with open('/tmp/test_req.md', 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        with open('/tmp/test_req.md', 'rb') as f:
            files = {'file': ('test_req.md', f, 'text/markdown')}
            data = {
                'project_name': '测试管理系统',
                'save_to_knowledge_base': False
            }
            response = requests.post(
                f"{BASE_URL}/document/process-full",
                headers=headers,
                files=files,
                data=data
            )
        
        print(f"\nDocument Processing: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Project ID: {data.get('project_id')}")
            print(f"Project Name: {data.get('project_name')}")
            print(f"Results generated successfully")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Document processing failed: {e}")
        return False

def main():
    print("=" * 60)
    print("API Integration Test")
    print("=" * 60)
    
    # Test health endpoint
    if not test_health():
        print("\nHealth check failed. Exiting...")
        return
    
    # Test registration
    reg_success, _ = test_register()
    if not reg_success:
        print("\nRegistration failed. Continuing with login test...")
    
    # Test login
    login_success, access_token = test_login()
    if not login_success:
        print("\nLogin failed. Exiting...")
        return
    
    # Test document processing
    if access_token:
        test_process_document(access_token)
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)

if __name__ == "__main__":
    main()
