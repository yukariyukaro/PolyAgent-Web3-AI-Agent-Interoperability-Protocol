#!/usr/bin/env python3
"""
测试Amazon购物Agent的功能
"""

import sys
import os
import asyncio

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from AgentCore.Society.amazon_shopping_agent_qwen3 import AmazonShoppingAgentQwen3, ThinkingMode
    print('✅ Amazon Agent导入成功')
except Exception as e:
    print('❌ Amazon Agent导入失败:', str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)

async def test_amazon_agent():
    """测试Amazon Agent基本功能"""
    try:
        print("\n🔄 创建Amazon Agent实例...")
        agent = AmazonShoppingAgentQwen3(ThinkingMode.AUTO)
        print('✅ Amazon Agent实例创建成功')
        
        print("\n🔄 获取Agent状态...")
        status = agent.get_service_status()
        print('✅ Agent状态获取成功:')
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        print("\n🔄 初始化Agent...")
        await agent.initialize()
        print('✅ Agent初始化完成')
        
        print("\n🔄 测试Agent响应...")
        response = await agent.process_request("你好")
        print('✅ Agent响应测试成功:')
        print(f"  用户: 你好")
        print(f"  Agent: {response}")
        
        print("\n🔄 测试购物查询...")
        response = await agent.process_request("我想买一个iPhone 15")
        print('✅ 购物查询测试成功:')
        print(f"  用户: 我想买一个iPhone 15")
        print(f"  Agent: {response}")
        
        print("\n🔄 获取对话历史...")
        history = agent.get_conversation_history()
        print(f'✅ 对话历史获取成功，共{len(history)}轮对话')
        
        print("\n🧹 清理资源...")
        await agent.cleanup()
        print('✅ 资源清理完成')
        
    except Exception as e:
        print(f'❌ 测试失败: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 开始测试Amazon购物Agent...")
    asyncio.run(test_amazon_agent())
    print("🎉 测试完成!") 