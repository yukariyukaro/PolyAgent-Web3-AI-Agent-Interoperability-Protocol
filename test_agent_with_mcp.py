#!/usr/bin/env python3
"""
测试Amazon Agent与MCP的完整集成
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from AgentCore.Society.amazon_shopping_agent_qwen3 import AmazonShoppingAgentQwen3, ThinkingMode
    from camel.toolkits import MCPToolkit
    print('✅ 所有依赖导入成功')
except Exception as e:
    print('❌ 依赖导入失败:', str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)

async def test_agent_mcp_integration():
    """测试Agent与MCP的完整集成"""
    try:
        print("\n🔄 创建Amazon Agent实例（启用MCP）...")
        agent = AmazonShoppingAgentQwen3(ThinkingMode.AUTO)
        print('✅ Agent创建成功')
        
        print("\n🔄 初始化Agent（包括MCP）...")
        await agent.initialize()
        print('✅ Agent初始化完成')
        
        print("\n🔄 获取Agent状态...")
        status = agent.get_service_status()
        print('Agent状态:')
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 测试基本对话
        print("\n🔄 测试基本对话...")
        response = await agent.process_request("你好，我想购买一些商品")
        print(f"✅ 基本对话测试成功:")
        print(f"  用户: 你好，我想购买一些商品")
        print(f"  Agent: {response}")
        
        # 测试商品搜索
        print("\n🔄 测试商品搜索功能...")
        response = await agent.process_request("我想买一台MacBook Pro 16英寸的")
        print(f"✅ 商品搜索测试:")
        print(f"  用户: 我想买一台MacBook Pro 16英寸的")
        print(f"  Agent: {response}")
        
        # 测试更具体的搜索
        print("\n🔄 测试更具体的商品搜索...")
        response = await agent.process_request("帮我在Amazon上搜索iPhone 15 Pro Max")
        print(f"✅ 具体搜索测试:")
        print(f"  用户: 帮我在Amazon上搜索iPhone 15 Pro Max")
        print(f"  Agent: {response}")
        
        # 测试支付相关功能
        print("\n🔄 测试支付相关功能...")
        response = await agent.process_request("我想了解一下支付方式和流程")
        print(f"✅ 支付功能测试:")
        print(f"  用户: 我想了解一下支付方式和流程")
        print(f"  Agent: {response}")
        
        # 获取对话历史
        print("\n🔄 获取对话历史...")
        history = agent.get_conversation_history()
        print(f'✅ 对话历史获取成功，共{len(history)}轮对话')
        
        # 显示对话历史
        for i, turn in enumerate(history):
            print(f"  第{i+1}轮:")
            print(f"    用户: {turn.user_input}")
            print(f"    Agent: {turn.ai_response}")
            print(f"    状态: {turn.shopping_state}")
            print(f"    工具: {turn.tools_used}")
        
        print("\n🧹 清理资源...")
        await agent.cleanup()
        print('✅ 资源清理完成')
        
    except Exception as e:
        print(f'❌ 集成测试失败: {str(e)}')
        import traceback
        traceback.print_exc()

async def test_mcp_tools_detail():
    """详细测试MCP工具功能"""
    try:
        print("\n🔧 详细测试MCP工具...")
        
        # 获取MCP配置文件路径
        config_path = Path(__file__).parent / "AgentCore" / "Mcp" / "amazon_fewsats_server.json"
        config_path = config_path.resolve()
        
        # 创建MCP工具包
        mcp_toolkit = MCPToolkit(config_path=str(config_path))
        await mcp_toolkit.connect()
        
        # 获取工具列表
        tools = mcp_toolkit.get_tools()
        print(f"✅ 发现 {len(tools)} 个MCP工具:")
        
        for i, tool in enumerate(tools):
            print(f"  {i+1}. 工具名称: {getattr(tool, 'name', 'Unknown')}")
            print(f"     工具描述: {getattr(tool, 'description', 'No description')}")
            if hasattr(tool, 'func') and hasattr(tool.func, '__name__'):
                print(f"     函数名: {tool.func.__name__}")
        
        # 尝试调用Amazon搜索工具
        print("\n🔄 测试Amazon搜索工具...")
        try:
            # 查找Amazon搜索工具
            search_tool = None
            for tool in tools:
                if hasattr(tool, 'func') and 'search' in getattr(tool.func, '__name__', '').lower():
                    search_tool = tool
                    break
            
            if search_tool:
                print(f"📞 找到搜索工具: {getattr(search_tool, 'name', 'Unknown')}")
                # 这里可以尝试调用工具，但先跳过以避免实际购买
                print("ℹ️ 跳过实际搜索调用以避免意外购买")
            else:
                print("⚠️ 未找到Amazon搜索工具")
                
        except Exception as e:
            print(f"⚠️ 搜索工具测试失败: {e}")
        
        await mcp_toolkit.disconnect()
        print("✅ MCP工具测试完成")
        
    except Exception as e:
        print(f'❌ MCP工具测试失败: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 开始Agent和MCP完整集成测试...")
    
    # 运行集成测试
    asyncio.run(test_agent_mcp_integration())
    
    # 运行MCP工具详细测试
    asyncio.run(test_mcp_tools_detail())
    
    print("🎉 所有测试完成!") 