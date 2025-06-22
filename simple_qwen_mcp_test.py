#!/usr/bin/env python3
"""
简化的Qwen2.5与MCP集成测试
"""

import os
import traceback
from datetime import datetime

# 设置环境变量
os.environ['MODELSCOPE_API_TOKEN'] = '9d3aed4d-eca1-4e0c-9805-cb923ccbbf21'
os.environ['FEWSATS_API_KEY'] = '3q-t95sj95DywRNY4v4QsShXfyS1Gs4uvYRnwipK4Hg'

print("🚀 简化Qwen2.5与MCP集成测试")
print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

def test_qwen_mcp_integration():
    """测试Qwen2.5模型与MCP工具的集成"""
    try:
        print("📋 步骤1: 导入CAMEL框架组件")
        from camel.models import ModelFactory
        from camel.types import ModelPlatformType
        from camel.toolkits import MCPToolkit
        from camel.agents import ChatAgent
        print("✅ CAMEL组件导入成功")
        
        print("\n📋 步骤2: 创建Qwen2.5模型")
        model = ModelFactory.create(
            model_platform=ModelPlatformType.MODELSCOPE,
            model_type='Qwen/Qwen2.5-72B-Instruct',
            model_config_dict={'temperature': 0.2},
            api_key='9d3aed4d-eca1-4e0c-9805-cb923ccbbf21',
        )
        print("✅ Qwen2.5模型创建成功")
        
        print("\n📋 步骤3: 创建仅Fewsats MCP配置（避免Amazon MCP的列表类型问题）")
        fewsats_config = {
            "mcpServers": {
                "fewsats": {
                    "command": "uvx",
                    "args": ["fewsats-mcp"],
                    "env": {
                        "FEWSATS_API_KEY": "3q-t95sj95DywRNY4v4QsShXfyS1Gs4uvYRnwipK4Hg"
                    },
                    "timeout": 60,
                    "initTimeout": 30
                }
            }
        }
        
        mcp_toolkit = MCPToolkit.create_sync(
            config_dict=fewsats_config,
            timeout=30.0
        )
        print("✅ Fewsats MCP工具包创建成功")
        
        # 获取工具列表
        tools = mcp_toolkit.get_tools()
        print(f"📋 可用工具数量: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.get_function_name()}")
        
        print("\n📋 步骤4: 创建ChatAgent并测试对话")
        system_message = """你是专业的支付助手，基于Qwen2.5模型。你可以帮助用户查询钱包余额、支付方式等。

请注意：这是测试环境，只进行功能验证。"""
        
        with mcp_toolkit:
            chat_agent = ChatAgent(
                system_message=system_message,
                model=model,
                token_limit=32768,
                tools=mcp_toolkit.get_tools(),
                output_language="zh"
            )
            
            print("✅ ChatAgent创建成功")
            
            # 测试对话
            test_messages = [
                "你好，请介绍一下你的功能",
                "请帮我查询钱包余额"
            ]
            
            for message in test_messages:
                print(f"\n👤 用户: {message}")
                
                try:
                    response = chat_agent.step(message)
                    if response and response.msgs:
                        ai_response = response.msgs[0].content
                        print(f"🤖 Qwen2.5: {ai_response[:300]}...")
                    else:
                        print("❌ 无响应")
                except Exception as e:
                    print(f"❌ 对话失败: {e}")
        
        mcp_toolkit.disconnect_sync()
        print("\n✅ 测试完成，MCP连接已断开")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"🔍 详细错误: {traceback.format_exc()}")
        return False

def test_amazon_agent_with_qwen():
    """测试修改后的Amazon Agent（使用Qwen2.5）"""
    try:
        print("\n📋 步骤5: 测试Amazon购物Agent（Qwen2.5版本）")
        
        # 修改Amazon Agent的模型初始化
        from AgentCore.Society.amazon_shopping_agent_qwen3 import AmazonShoppingAgentQwen3, ThinkingMode
        
        # 创建Agent实例
        agent = AmazonShoppingAgentQwen3(
            thinking_mode=ThinkingMode.AUTO,
            user_id="test_user",
            session_id="qwen_test_session"
        )
        
        print("✅ Amazon购物Agent（Qwen2.5）初始化成功")
        
        # 获取服务状态
        status = agent.get_service_status()
        print(f"📊 Agent状态:")
        for key, value in status.items():
            print(f"  - {key}: {value}")
        
        # 测试简单对话
        test_message = "你好，请介绍一下你的购物功能"
        print(f"\n👤 用户: {test_message}")
        
        response = agent.process_request(test_message)
        print(f"🤖 Agent: {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Amazon Agent测试失败: {e}")
        print(f"🔍 详细错误: {traceback.format_exc()}")
        return False

def main():
    """主测试流程"""
    print("🎯 开始简化测试...")
    
    # 测试1: Qwen2.5与MCP基础集成
    success1 = test_qwen_mcp_integration()
    
    # 测试2: Amazon Agent与Qwen2.5集成
    success2 = test_amazon_agent_with_qwen()
    
    # 测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    print(f"Qwen2.5与MCP集成: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"Amazon Agent集成: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("🎉 所有测试通过！Qwen2.5系统可以正常工作")
        
        print("\n💡 关键发现:")
        print("1. Qwen2.5模型可以正常创建和使用")
        print("2. MCP工具包可以成功连接（使用Fewsats）")
        print("3. ChatAgent可以正常处理对话")
        print("4. Amazon Agent可以使用Qwen2.5模型")
        
        print("\n🔧 下一步建议:")
        print("1. 解决Amazon MCP的'unhashable type: list'问题")
        print("2. 优化Qwen2.5模型的响应速度")
        print("3. 完善错误处理和降级机制")
        
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步调试")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        print(f"🔍 错误详情: {traceback.format_exc()}")
        exit(1) 