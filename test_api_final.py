import requests
import time
import json

def test_api():
    print("🧪 测试修复后的API...")
    time.sleep(3)  # 等待Flask启动
    
    try:
        # 测试1: 黑笔搜索
        print("📝 测试1: 我想买一盒黑笔")
        response = requests.post('http://localhost:5000/api/chat', 
                               json={'message': '我想买一盒黑笔'})
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data['success']}")
            print(f"Response (前200字): {data['response'][:200]}...")
            print(f"MCP可用: {data['shopping_state']['mcp_available']}")
            print()
        
        # 测试2: iPhone搜索
        print("📝 测试2: 我想买iPhone 15")
        response2 = requests.post('http://localhost:5000/api/chat', 
                                json={'message': '我想买iPhone 15'})
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"Response (前200字): {data2['response'][:200]}...")
            print(f"对话轮次: {data2['conversation_stats']['total_turns']}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == '__main__':
    test_api() 