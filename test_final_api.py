import requests
import json

def test_final_api():
    print("🧪 最终API测试...")
    
    try:
        # 测试购买黑笔
        response = requests.post(
            'http://localhost:5000/api/chat',
            json={'message': '我想买一盒黑笔'},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API调用成功!")
            print(f"Success: {data['success']}")
            print(f"响应长度: {len(data['response'])}")
            print(f"响应内容: {data['response'][:300]}...")
            
            # 检查是否使用了工具
            shopping_state = data.get('shopping_state', {})
            print(f"\\n📊 购物状态:")
            print(f"  - MCP可用: {shopping_state.get('mcp_available')}")
            print(f"  - 当前状态: {shopping_state.get('current_state')}")
            print(f"  - 对话轮次: {shopping_state.get('conversation_turns')}")
            
            # 分析响应内容判断是否调用了工具
            if 'Paper Mate' in data['response'] or '搜索' in data['response'] or 'amazon' in data['response'].lower():
                print("✅ AI似乎调用了Amazon搜索工具!")
            else:
                print("⚠️ AI可能没有调用工具")
                
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == '__main__':
    test_final_api() 