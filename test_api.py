#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_amazon_agent_api():
    """测试Amazon Agent API"""
    print("🔍 测试Amazon Agent API...")
    
    # 测试基本API端点
    base_url = "http://localhost:5000"
    
    # 1. 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"健康检查状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"健康检查响应: {response.json()}")
        else:
            print(f"健康检查失败: {response.text}")
    except Exception as e:
        print(f"健康检查请求失败: {e}")
    
    # 2. 测试主页
    print("\n2. 测试主页...")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"主页状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"服务信息: {data.get('message', 'N/A')}")
            print(f"Agent类型: {data.get('agent_type', 'N/A')}")
            print(f"版本: {data.get('version', 'N/A')}")
    except Exception as e:
        print(f"主页请求失败: {e}")
    
    # 3. 测试聊天API
    print("\n3. 测试聊天API...")
    test_messages = [
        "你好",
        "我想买一支黑色圆珠笔",
        "搜索Amazon上的蓝牙耳机"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n测试消息 {i}: {message}")
        try:
            response = requests.post(
                f"{base_url}/api/chat", 
                json={"message": message},
                timeout=95  # 给足够的时间处理
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"成功: {data.get('success', False)}")
                if data.get('success'):
                    response_text = data.get('response', '')
                    print(f"响应长度: {len(response_text)} 字符")
                    print(f"响应预览: {response_text[:200]}...")
                    
                    # 显示购物状态
                    shopping_state = data.get('shopping_state', {})
                    print(f"购物状态: {shopping_state.get('current_state', 'N/A')}")
                    print(f"MCP可用: {shopping_state.get('mcp_available', 'N/A')}")
                    print(f"思考模式: {shopping_state.get('thinking_mode', 'N/A')}")
                else:
                    print(f"API错误: {data.get('error', 'Unknown error')}")
            else:
                print(f"HTTP错误: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ 请求超时 (95秒)")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
        
        # 测试之间等待一下
        if i < len(test_messages):
            print("等待2秒...")
            time.sleep(2)
    
    # 4. 测试对话历史
    print("\n4. 测试对话历史...")
    try:
        response = requests.get(f"{base_url}/api/conversation/history", timeout=10)
        print(f"对话历史状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"对话轮次: {data.get('total_turns', 0)}")
    except Exception as e:
        print(f"对话历史请求失败: {e}")

if __name__ == "__main__":
    test_amazon_agent_api() 