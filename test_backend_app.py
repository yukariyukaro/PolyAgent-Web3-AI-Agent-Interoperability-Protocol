#!/usr/bin/env python3
"""
测试后端Flask应用
"""

import sys
import os
import requests
import time
import subprocess
import threading

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def start_backend():
    """启动后端服务"""
    try:
        print("🔄 启动后端Flask应用...")
        # 启动Flask应用（在后台运行）
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务启动
        time.sleep(5)
        
        return process
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        return None

def test_backend_api():
    """测试后端API"""
    try:
        print("\n🧪 测试后端API连接...")
        
        # 测试健康检查端点
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✅ 健康检查端点正常")
                print(f"   响应: {response.json()}")
            else:
                print(f"⚠️ 健康检查端点状态: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ 健康检查端点失败: {e}")
        
        # 测试聊天API
        try:
            chat_data = {
                "message": "你好，我想买一个iPhone",
                "user_id": "test_user_001"
            }
            
            response = requests.post(
                "http://localhost:5000/api/chat",
                json=chat_data,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ 聊天API正常")
                data = response.json()
                print(f"   Agent响应: {data.get('response', 'No response')}")
                print(f"   状态: {data.get('status', 'Unknown')}")
            else:
                print(f"⚠️ 聊天API状态: {response.status_code}")
                print(f"   错误: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 聊天API失败: {e}")
        
        # 测试Agent状态API
        try:
            response = requests.get("http://localhost:5000/api/agent/status", timeout=5)
            if response.status_code == 200:
                print("✅ Agent状态API正常")
                data = response.json()
                print(f"   Agent状态: {data}")
            else:
                print(f"⚠️ Agent状态API状态: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Agent状态API失败: {e}")
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")

def test_frontend_connection():
    """测试前端连接"""
    try:
        print("\n🌐 测试前端连接...")
        
        # 检查前端是否在运行
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code == 200:
                print("✅ 前端服务正常运行")
            else:
                print(f"⚠️ 前端服务状态: {response.status_code}")
        except requests.exceptions.RequestException:
            print("⚠️ 前端服务未运行（3000端口）")
        
        # 检查Vite代理配置
        try:
            response = requests.get("http://localhost:3000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Vite代理配置正常")
            else:
                print(f"⚠️ Vite代理状态: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Vite代理测试失败: {e}")
            
    except Exception as e:
        print(f"❌ 前端连接测试失败: {e}")

if __name__ == "__main__":
    print("🧪 开始后端API测试...")
    
    # 启动后端
    backend_process = start_backend()
    
    if backend_process:
        try:
            # 测试API
            test_backend_api()
            
            # 测试前端连接
            test_frontend_connection()
            
        finally:
            # 清理后端进程
            print("\n🧹 清理后端进程...")
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
                print("✅ 后端进程已关闭")
            except subprocess.TimeoutExpired:
                backend_process.kill()
                print("✅ 后端进程已强制关闭")
    
    print("🎉 测试完成!") 