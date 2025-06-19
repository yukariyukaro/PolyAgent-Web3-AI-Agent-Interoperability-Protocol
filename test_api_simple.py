#!/usr/bin/env python3
"""
简单的API测试脚本，验证后端服务是否正常工作
"""

import requests
import json
import time

def test_backend_status():
    """测试后端服务状态"""
    print("🔍 测试后端服务状态...")
    
    # 测试服务是否启动
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            data = response.json()
            print(f"   版本: {data.get('version', 'N/A')}")
            print(f"   Agent: {data.get('agent_type', 'N/A')}")
            return True
        else:
            print(f"❌ 后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务 (http://localhost:5000)")
        print("💡 请确保后端服务已启动：python app.py")
        return False
    except Exception as e:
        print(f"❌ 测试后端服务失败: {e}")
        return False

def test_chat_api():
    """测试聊天API"""
    print("\n🔍 测试 /api/chat 接口...")
    
    try:
        # 测试请求数据
        test_data = {
            "message": "你好，我想买一个苹果手机"
        }
        
        response = requests.post(
            "http://localhost:5000/api/chat",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ /api/chat 接口正常")
            print(f"   success: {data.get('success')}")
            print(f"   response前50字符: {data.get('response', '')[:50]}...")
            return True
        else:
            print(f"❌ /api/chat 接口响应异常: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试 /api/chat 接口失败: {e}")
        return False

def test_agent_api():
    """测试修改后的Agent API"""
    print("🧪 测试修改后的Amazon购物Agent API...")
    
    # 等待Flask启动
    print("⏰ 等待Flask服务启动...")
    time.sleep(3)
    
    try:
        # 测试购物请求
        test_cases = [
            "我想买一盒黑笔",
            "我要第一款",
            "我叫张三"
        ]
        
        for i, message in enumerate(test_cases, 1):
            print(f"\n📝 测试 {i}: {message}")
            
            response = requests.post(
                'http://localhost:5000/api/chat',
                json={'message': message},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 请求成功")
                print(f"📤 响应长度: {len(data['response'])} 字符")
                print(f"📊 响应预览: {data['response'][:200]}...")
                
                # 检查购物状态
                state = data.get('shopping_state', {})
                print(f"🛍️ 购物状态: {state.get('current_state', 'unknown')}")
                print(f"🔧 MCP可用: {state.get('mcp_available', False)}")
                print(f"💬 对话轮次: {state.get('conversation_turns', 0)}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误内容: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Flask服务，请确保app.py正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主测试函数"""
    print("=" * 50)
    print("🚀 开始API测试")
    print("=" * 50)
    
    # 测试后端状态
    backend_ok = test_backend_status()
    
    if backend_ok:
        # 测试聊天API
        chat_ok = test_chat_api()
        
        print("\n" + "=" * 50)
        if backend_ok and chat_ok:
            print("✅ 所有测试通过！后端API正常工作")
        else:
            print("❌ 部分测试失败")
    else:
        print("\n❌ 后端服务未启动，请先启动后端：python app.py")
    
    print("=" * 50)

if __name__ == "__main__":
    test_agent_api() 