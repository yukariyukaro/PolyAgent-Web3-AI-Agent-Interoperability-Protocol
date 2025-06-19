#!/usr/bin/env python3
"""
Amazon MCP服务直接测试脚本
专门测试Amazon和Fewsats MCP服务的连接和调用
"""

import sys
import os
import asyncio
import json
import traceback
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def test_mcp_imports():
    """测试MCP相关导入"""
    print("🔍 测试MCP导入...")
    
    try:
        from camel.toolkits import MCPToolkit
        print("✅ MCPToolkit 导入成功")
        return True
    except ImportError as e:
        print(f"❌ MCPToolkit 导入失败: {e}")
        return False

async def test_mcp_connection():
    """测试MCP服务连接"""
    print("\n🔍 测试Amazon MCP服务连接...")
    
    try:
        from camel.toolkits import MCPToolkit
        
        mcp_config_path = os.path.join(
            os.path.dirname(__file__), "AgentCore", "Mcp", "amazon_fewsats_server.json"
        )
        
        if not os.path.exists(mcp_config_path):
            print(f"❌ MCP配置文件不存在: {mcp_config_path}")
            return False
        
        print(f"📄 使用配置文件: {mcp_config_path}")
        
        # 读取并显示配置
        with open(mcp_config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            print(f"📋 MCP配置内容: {json.dumps(config_data, indent=2, ensure_ascii=False)}")
        
        # 测试连接
        print("⏳ 正在连接Amazon MCP服务...")
        
        try:
            async with MCPToolkit(config_path=mcp_config_path) as mcp_toolkit:
                print("✅ MCP连接建立成功")
                
                # 获取可用工具
                tools = mcp_toolkit.get_tools()
                print(f"🔧 发现 {len(tools)} 个可用工具:")
                
                for i, tool in enumerate(tools, 1):
                    tool_name = getattr(tool, 'name', 'Unknown')
                    tool_desc = getattr(tool, 'description', 'No description')
                    print(f"   {i}. {tool_name}: {tool_desc[:80]}...")
                
                # 测试一个简单的工具调用
                print("\n🔍 测试Amazon搜索工具...")
                
                # 寻找Amazon搜索工具
                amazon_search_tool = None
                for tool in tools:
                    tool_name = getattr(tool, 'name', '')
                    if 'amazon' in tool_name.lower() and 'search' in tool_name.lower():
                        amazon_search_tool = tool
                        break
                
                if amazon_search_tool:
                    print(f"✅ 找到Amazon搜索工具: {amazon_search_tool.name}")
                    
                    # 尝试简单的搜索测试
                    try:
                        print("⏳ 测试搜索 'iPhone'...")
                        
                        # 这里我们只是验证工具可以被调用，不一定要成功返回结果
                        # 因为可能需要网络连接或认证
                        search_result = await amazon_search_tool.acall(q="iPhone", domain="amazon.com")
                        print(f"✅ 搜索测试成功: {str(search_result)[:200]}...")
                        
                    except Exception as search_error:
                        print(f"⚠️ 搜索测试失败: {search_error}")
                        print("   这可能是正常的，因为需要网络连接或认证")
                
                else:
                    print("⚠️ 未找到Amazon搜索工具")
                    print("   可用工具名称:")
                    for tool in tools:
                        print(f"     - {getattr(tool, 'name', 'Unknown')}")
                
                return True
                
        except Exception as mcp_error:
            print(f"❌ MCP连接失败: {mcp_error}")
            print(f"🔍 详细错误: {traceback.format_exc()}")
            return False
            
    except Exception as e:
        print(f"❌ MCP测试失败: {e}")
        print(f"🔍 详细错误: {traceback.format_exc()}")
        return False

async def test_individual_mcp_servers():
    """分别测试Amazon和Fewsats MCP服务"""
    print("\n🔍 分别测试各个MCP服务...")
    
    # 测试Amazon MCP
    print("\n--- Amazon MCP 测试 ---")
    amazon_config = {
        "mcpServers": {
            "Amazon": {
                "command": "uvx",
                "args": ["amazon-mcp"]
            }
        }
    }
    
    temp_amazon_config = "temp_amazon_config.json"
    try:
        with open(temp_amazon_config, 'w', encoding='utf-8') as f:
            json.dump(amazon_config, f, indent=2)
        
        print("📄 创建临时Amazon配置文件")
        
        try:
            from camel.toolkits import MCPToolkit
            async with MCPToolkit(config_path=temp_amazon_config) as mcp_toolkit:
                tools = mcp_toolkit.get_tools()
                print(f"✅ Amazon MCP: 发现 {len(tools)} 个工具")
                for tool in tools:
                    print(f"   - {getattr(tool, 'name', 'Unknown')}")
        except Exception as e:
            print(f"❌ Amazon MCP连接失败: {e}")
            
    finally:
        if os.path.exists(temp_amazon_config):
            os.remove(temp_amazon_config)
    
    # 测试Fewsats MCP
    print("\n--- Fewsats MCP 测试 ---")
    fewsats_config = {
        "mcpServers": {
            "Fewsats": {
                "command": "C:\\Users\\J\\AppData\\Roaming\\Python\\Python311\\Scripts\\fewsats-mcp.exe",
                "env": {
                    "FEWSATS_API_KEY": "3q-t95sj95DywRNY4v4QsShXfyS1Gs4uvYRnwipK4Hg"
                }
            }
        }
    }
    
    temp_fewsats_config = "temp_fewsats_config.json"
    try:
        with open(temp_fewsats_config, 'w', encoding='utf-8') as f:
            json.dump(fewsats_config, f, indent=2)
        
        print("📄 创建临时Fewsats配置文件")
        
        try:
            from camel.toolkits import MCPToolkit
            async with MCPToolkit(config_path=temp_fewsats_config) as mcp_toolkit:
                tools = mcp_toolkit.get_tools()
                print(f"✅ Fewsats MCP: 发现 {len(tools)} 个工具")
                for tool in tools:
                    print(f"   - {getattr(tool, 'name', 'Unknown')}")
        except Exception as e:
            print(f"❌ Fewsats MCP连接失败: {e}")
            
    finally:
        if os.path.exists(temp_fewsats_config):
            os.remove(temp_fewsats_config)

def check_mcp_prerequisites():
    """检查MCP前置条件"""
    print("\n🔍 检查MCP前置条件...")
    
    # 检查uvx命令
    try:
        import subprocess
        result = subprocess.run(['uvx', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ uvx 可用: {result.stdout.strip()}")
        else:
            print(f"❌ uvx 不可用: {result.stderr}")
    except Exception as e:
        print(f"❌ uvx 检查失败: {e}")
    
    # 检查amazon-mcp包
    try:
        result = subprocess.run(['uvx', '--help'], capture_output=True, text=True, timeout=10)
        if 'amazon-mcp' in result.stdout:
            print("✅ amazon-mcp 包可能可用")
        else:
            print("⚠️ amazon-mcp 包状态未知")
    except Exception as e:
        print(f"⚠️ amazon-mcp 包检查失败: {e}")
    
    # 检查Fewsats可执行文件
    fewsats_exe = "C:\\Users\\J\\AppData\\Roaming\\Python\\Python311\\Scripts\\fewsats-mcp.exe"
    if os.path.exists(fewsats_exe):
        print(f"✅ Fewsats MCP可执行文件存在: {fewsats_exe}")
    else:
        print(f"❌ Fewsats MCP可执行文件不存在: {fewsats_exe}")

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 Amazon MCP服务直接测试")
    print("=" * 60)
    
    # 1. 检查前置条件
    check_mcp_prerequisites()
    
    # 2. 测试导入
    if not test_mcp_imports():
        print("❌ 导入测试失败，无法继续")
        return
    
    # 3. 测试MCP连接
    if await test_mcp_connection():
        print("\n✅ 主要MCP测试通过")
    else:
        print("\n❌ 主要MCP测试失败")
    
    # 4. 分别测试各服务
    await test_individual_mcp_servers()
    
    print("\n" + "=" * 60)
    print("🏁 Amazon MCP测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 