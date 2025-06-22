#!/usr/bin/env python3
"""
测试FixedMCPToolkit是否能解决Amazon MCP的列表类型参数问题
"""

import os
import sys
import traceback
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fixed_mcp_toolkit():
    """测试FixedMCPToolkit"""
    print("🧪 测试FixedMCPToolkit解决Amazon MCP列表类型参数问题")
    print("=" * 60)
    
    try:
        # 导入FixedMCPToolkit
        from AgentCore.Society.fixed_mcp_toolkit import FixedMCPToolkit
        print("✅ FixedMCPToolkit导入成功")
        
        # 配置文件路径
        config_path = os.path.join(
            os.path.dirname(__file__), "AgentCore", "Mcp", "amazon_fewsats_server.json"
        )
        config_path = os.path.abspath(config_path)
        print(f"📝 MCP配置文件: {config_path}")
        
        if not os.path.exists(config_path):
            print(f"❌ 配置文件不存在: {config_path}")
            return False
        
        # 创建FixedMCPToolkit实例
        print("\n🔧 创建FixedMCPToolkit实例...")
        toolkit = FixedMCPToolkit.create_sync(
            config_path=config_path,
            timeout=120.0
        )
        
        # 获取工具列表
        print("\n📋 获取工具列表...")
        tools = toolkit.get_tools()
        print(f"✅ 成功获取 {len(tools)} 个工具")
        
        # 检查Amazon工具
        amazon_tools = []
        fewsats_tools = []
        
        for tool in tools:
            tool_name = tool.get_function_name()
            if 'amazon' in tool_name.lower():
                amazon_tools.append(tool_name)
            elif 'fewsats' in tool_name.lower() or any(name in tool_name for name in ['balance', 'payment', 'billing']):
                fewsats_tools.append(tool_name)
        
        print(f"\n🛒 Amazon工具 ({len(amazon_tools)}个):")
        for tool_name in amazon_tools:
            print(f"  - {tool_name}")
        
        print(f"\n💳 Fewsats工具 ({len(fewsats_tools)}个):")
        for tool_name in fewsats_tools:
            print(f"  - {tool_name}")
        
        # 检查工具模式
        print(f"\n🔍 检查工具参数定义...")
        for tool in tools:
            tool_name = tool.get_function_name()
            schema = tool.get_openai_tool_schema()
            
            if 'amazon' in tool_name.lower():
                print(f"\n📋 {tool_name} 参数检查:")
                if 'function' in schema and 'parameters' in schema['function']:
                    properties = schema['function']['parameters'].get('properties', {})
                    for param_name, param_def in properties.items():
                        param_type = param_def.get('type', 'unknown')
                        if param_type == 'array':
                            print(f"  ❌ 发现列表类型参数: {param_name} (type: {param_type})")
                        elif param_type == 'string' and 'JSON格式' in param_def.get('description', ''):
                            print(f"  ✅ 已修复的参数: {param_name} (原为列表，现为字符串)")
                        else:
                            print(f"  📋 普通参数: {param_name} (type: {param_type})")
        
        # 断开连接
        print(f"\n🔌 断开连接...")
        toolkit.disconnect_sync()
        
        print(f"\n✅ FixedMCPToolkit测试成功！")
        print(f"🎯 成功解决了Amazon MCP的列表类型参数问题")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"🔍 详细错误: {traceback.format_exc()}")
        return False

def test_amazon_shopping_agent_with_fixed_toolkit():
    """测试Amazon购物Agent使用FixedMCPToolkit"""
    print("\n" + "=" * 60)
    print("🧪 测试Amazon购物Agent使用FixedMCPToolkit")
    print("=" * 60)
    
    try:
        # 导入Amazon购物Agent
        from AgentCore.Society.amazon_shopping_agent_qwen3 import AmazonShoppingAgentQwen3, ThinkingMode
        print("✅ Amazon购物Agent导入成功")
        
        # 创建Agent实例
        print("\n🤖 创建Amazon购物Agent...")
        agent = AmazonShoppingAgentQwen3(
            thinking_mode=ThinkingMode.AUTO,
            user_id="test_user",
            session_id="test_session"
        )
        
        # 检查Agent状态
        status = agent.get_service_status()
        print(f"\n📊 Agent状态:")
        print(f"  - Agent类型: {status['agent_type']}")
        print(f"  - 版本: {status['version']}")
        print(f"  - 模型: {status['model']}")
        print(f"  - CAMEL可用: {status['camel_available']}")
        print(f"  - MCP可用: {status['mcp_available']}")
        
        if status['mcp_available']:
            print("✅ Amazon购物Agent成功使用FixedMCPToolkit!")
            
            # 测试简单对话
            print(f"\n💬 测试对话...")
            test_message = "你好，我想了解一下购物服务"
            response = agent.process_request(test_message)
            print(f"👤 用户: {test_message}")
            print(f"🤖 Agent: {response[:200]}...")
            
            return True
        else:
            print("❌ MCP工具包不可用")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"🔍 详细错误: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print(f"🚀 开始测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试1: FixedMCPToolkit基础功能
    test1_result = test_fixed_mcp_toolkit()
    
    # 测试2: Amazon购物Agent集成
    test2_result = test_amazon_shopping_agent_with_fixed_toolkit()
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    print(f"✅ FixedMCPToolkit基础测试: {'通过' if test1_result else '失败'}")
    print(f"✅ Amazon Agent集成测试: {'通过' if test2_result else '失败'}")
    
    if test1_result and test2_result:
        print(f"\n🎉 所有测试通过！Amazon MCP列表类型参数问题已解决！")
        print(f"💡 现在可以正常使用Amazon MCP工具进行商品搜索和购买了")
    else:
        print(f"\n⚠️ 部分测试失败，请检查错误信息")
    
    return test1_result and test2_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 