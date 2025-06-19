import requests
import time

def test_purchase_flow():
    """测试完整的购买流程"""
    print("🛒 测试完整购买流程...")
    
    # 步骤1: 搜索商品
    print("\\n步骤1: 搜索商品")
    response1 = requests.post(
        'http://localhost:5000/api/chat',
        json={'message': '我想买一盒黑笔'},
        timeout=60
    )
    print(f"✅ 搜索响应: {response1.json()['response'][:150]}...")
    
    # 步骤2: 选择商品
    print("\\n步骤2: 选择商品")
    response2 = requests.post(
        'http://localhost:5000/api/chat',
        json={'message': '我要第一款Paper Mate InkJoy'},
        timeout=60
    )
    print(f"✅ 选择响应: {response2.json()['response'][:150]}...")
    
    # 步骤3: 提供用户信息
    print("\\n步骤3: 提供姓名")
    response3 = requests.post(
        'http://localhost:5000/api/chat',
        json={'message': '我叫张三'},
        timeout=60
    )
    print(f"✅ 姓名响应: {response3.json()['response'][:150]}...")
    
    # 步骤4: 提供邮箱
    print("\\n步骤4: 提供邮箱")
    response4 = requests.post(
        'http://localhost:5000/api/chat',
        json={'message': 'zhangsan@email.com'},
        timeout=60
    )
    print(f"✅ 邮箱响应: {response4.json()['response'][:150]}...")
    
    # 步骤5: 提供地址
    print("\\n步骤5: 提供地址")
    response5 = requests.post(
        'http://localhost:5000/api/chat',
        json={'message': '北京市朝阳区xxx街道123号'},
        timeout=60
    )
    print(f"✅ 地址响应: {response5.json()['response'][:150]}...")
    
    # 查看最终状态
    final_state = response5.json().get('shopping_state', {})
    print(f"\\n📊 最终购物状态:")
    print(f"  - 当前状态: {final_state.get('current_state')}")
    print(f"  - 用户信息完整: {final_state.get('user_info_complete')}")
    print(f"  - 商品已选择: {final_state.get('product_selected')}")
    print(f"  - 对话轮次: {final_state.get('conversation_turns')}")

if __name__ == '__main__':
    test_purchase_flow() 