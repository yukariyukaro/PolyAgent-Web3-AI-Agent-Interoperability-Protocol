#!/usr/bin/env python3
"""
直接测试MCP连接
"""

import asyncio
import os
import sys
import json
from pathlib import Path

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from camel.toolkits import MCPToolkit
    print('✅ MCPToolkit导入成功')
except Exception as e:
    print('❌ MCPToolkit导入失败:', str(e))
    sys.exit(1)

async def test_mcp_connection():
    """测试MCP连接"""
    try:
        # 获取MCP配置文件路径
        config_path = Path(__file__).parent / "AgentCore" / "Mcp" / "amazon_fewsats_server.json"
        config_path = config_path.resolve()
        
        print(f"🔄 MCP配置文件路径: {config_path}")
        
        if not config_path.exists():
            print(f"❌ MCP配置文件不存在: {config_path}")
            return
        
        # 读取配置文件内容
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        print("📋 MCP配置内容:")
        print(json.dumps(config_data, indent=2, ensure_ascii=False))
        
        print("\n🔄 尝试连接MCP服务...")
        
        # 创建MCP工具包
        mcp_toolkit = MCPToolkit(config_path=str(config_path))
        
        print("🔄 连接中...")
        await mcp_toolkit.connect()
        print("✅ MCP连接成功")
        
        # 获取工具列表
        print("\n🔄 获取工具列表...")
        tools = mcp_toolkit.get_tools()
        print(f"✅ 发现 {len(tools)} 个工具:")
        
        for i, tool in enumerate(tools):
            print(f"  {i+1}. {tool}")
        
        # 测试工具调用（如果有工具的话）
        if tools:
            print("\n🔄 测试工具调用...")
            try:
                # 尝试调用第一个工具
                first_tool = tools[0]
                print(f"📞 尝试调用工具: {first_tool}")
                
                # 这里可以根据具体工具调整参数
                # result = await mcp_toolkit.call_tool(first_tool.name, {"test": "value"})
                # print(f"✅ 工具调用成功: {result}")
                print("ℹ️ 跳过实际工具调用测试")
                
            except Exception as e:
                print(f"⚠️ 工具调用失败: {e}")
        
        print("\n🧹 断开连接...")
        await mcp_toolkit.disconnect()
        print("✅ 连接已断开")
        
    except Exception as e:
        print(f'❌ MCP连接测试失败: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 开始MCP连接测试...")
    asyncio.run(test_mcp_connection())
    print("🎉 测试完成!") 