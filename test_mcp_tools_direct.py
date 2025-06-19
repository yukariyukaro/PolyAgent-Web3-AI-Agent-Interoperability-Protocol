import asyncio
import sys
import os
sys.path.append('.')
from AgentCore.Society.amazon_shopping_agent_qwen3 import AmazonShoppingAgentQwen3, ThinkingMode

async def test_direct_mcp():
    print('🔍 直接测试MCP工具调用...')
    agent = AmazonShoppingAgentQwen3(ThinkingMode.AUTO)
    await agent.initialize()
    
    print(f'✅ Agent初始化完成')
    print(f'   - MCP可用: {agent.mcp_available}')
    print(f'   - 模型状态: {agent.model is not None}')
    print(f'   - MCP配置路径: {agent.mcp_config_path}')
    
    # 直接测试MCP工具
    if agent.mcp_available:
        print('\\n🔧 直接测试MCP工具连接...')
        try:
            from camel.toolkits import MCPToolkit
            
            # 创建MCP工具包
            print(f'📁 MCP配置文件路径: {agent.mcp_config_path}')
            async with MCPToolkit(config_path=agent.mcp_config_path) as mcp_toolkit:
                tools = mcp_toolkit.get_tools()
                print(f'🛠️  发现工具: {len(tools)}个')
                
                for i, tool in enumerate(tools):
                    print(f'   {i+1}. {tool.get_tool_name()} - {type(tool).__name__}')
                
                # 手动测试amazon_search工具
                print('\\n🔍 手动测试amazon_search工具...')
                amazon_search_tool = None
                for tool in tools:
                    if 'amazon_search' in tool.get_tool_name():
                        amazon_search_tool = tool
                        break
                
                if amazon_search_tool:
                    print(f'✅ 找到amazon_search工具: {amazon_search_tool.get_tool_name()}')
                    print(f'   工具描述: {amazon_search_tool.get_tool_description()}')
                    print(f'   工具参数: {amazon_search_tool.get_parameters()}')
                    
                    # 尝试调用工具
                    try:
                        print('\\n🚀 尝试调用amazon_search(q="black pen")...')
                        result = amazon_search_tool.func(q="black pen")
                        print(f'✅ 工具调用成功!')
                        print(f'   结果类型: {type(result)}')
                        if isinstance(result, str):
                            print(f'   结果预览: {result[:200]}...')
                        else:
                            print(f'   结果: {result}')
                    except Exception as e:
                        print(f'❌ 工具调用失败: {e}')
                        import traceback
                        traceback.print_exc()
                else:
                    print('❌ 未找到amazon_search工具')
                    
        except Exception as e:
            print(f'❌ MCP工具测试失败: {e}')
            import traceback
            traceback.print_exc()
    
    # 测试ChatAgent配置
    print('\\n🤖 测试ChatAgent配置...')
    try:
        from camel.agents import ChatAgent
        from camel.toolkits import MCPToolkit
        
        async with MCPToolkit(config_path=agent.mcp_config_path) as mcp_toolkit:
            tools = mcp_toolkit.get_tools()
            
            # 创建ChatAgent
            chat_agent = ChatAgent(
                system_message="你是测试助手。当用户说'测试工具'时，你应该调用amazon_search工具搜索'black pen'。",
                model=agent.model,
                tools=tools,
                output_language="zh"
            )
            
            print(f'✅ ChatAgent创建成功')
            print(f'   - 工具数量: {len(tools)}')
            print(f'   - 模型: {type(agent.model)}')
            
            # 测试简单的工具调用提示
            print('\\n🧪 测试工具调用提示...')
            response = await chat_agent.astep("请调用amazon_search工具搜索black pen")
            
            print(f'✅ ChatAgent响应生成')
            if response and response.msgs:
                print(f'   响应内容: {response.msgs[0].content[:200]}...')
            
            if hasattr(response, 'info') and response.info:
                print(f'   响应信息: {response.info}')
                if 'tool_calls' in response.info:
                    print(f'   工具调用: {response.info["tool_calls"]}')
            else:
                print('   ⚠️ 响应中没有info字段')
                
    except Exception as e:
        print(f'❌ ChatAgent测试失败: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_direct_mcp()) 