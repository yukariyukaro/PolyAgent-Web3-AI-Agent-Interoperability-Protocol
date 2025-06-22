#!/usr/bin/env python3
"""
MCP工具诊断脚本
检查Amazon MCP和Fewsats MCP工具定义，诊断"unhashable type: 'list'"错误
"""

import os
import json
import traceback
import asyncio
from datetime import datetime

# 设置环境变量
os.environ['MODELSCOPE_API_TOKEN'] = '9d3aed4d-eca1-4e0c-9805-cb923ccbbf21'
os.environ['FEWSATS_API_KEY'] = '3q-t95sj95DywRNY4v4QsShXfyS1Gs4uvYRnwipK4Hg'

print("🔍 MCP工具诊断开始")
print(f"⏰ 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

def diagnose_step(step_name: str):
    """诊断步骤装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"\n📋 诊断步骤: {step_name}")
            print("-" * 40)
            try:
                result = func(*args, **kwargs)
                print(f"✅ {step_name} - 完成")
                return result
            except Exception as e:
                print(f"❌ {step_name} - 失败: {e}")
                print(f"🔍 错误详情: {traceback.format_exc()}")
                return False
        return wrapper
    return decorator

@diagnose_step("检查MCPToolkit基础功能")
def step_1_check_mcp_toolkit():
    """检查MCPToolkit的基础导入和创建"""
    try:
        from camel.toolkits import MCPToolkit
        print("✅ MCPToolkit导入成功")
        
        # 检查配置文件
        config_path = os.path.join("AgentCore", "Mcp", "amazon_fewsats_server.json")
        config_path = os.path.abspath(config_path)
        
        if not os.path.exists(config_path):
            print(f"❌ 配置文件不存在: {config_path}")
            return False
        
        print(f"✅ 配置文件存在: {config_path}")
        
        # 读取配置内容
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ 配置文件格式正确")
        print(f"📋 配置的MCP服务器: {list(config.get('mcpServers', {}).keys())}")
        
        return config_path
        
    except Exception as e:
        print(f"❌ MCPToolkit基础检查失败: {e}")
        return False

@diagnose_step("尝试创建MCPToolkit（详细错误捕获）")
def step_2_create_mcp_toolkit(config_path):
    """尝试创建MCPToolkit并捕获详细错误"""
    try:
        from camel.toolkits import MCPToolkit
        
        print(f"🔄 尝试创建MCPToolkit...")
        print(f"配置文件: {config_path}")
        
        # 使用较短的超时时间进行快速测试
        toolkit = MCPToolkit.create_sync(
            config_path=config_path,
            timeout=30.0  # 30秒超时
        )
        
        print("✅ MCPToolkit创建成功")
        return toolkit
        
    except Exception as e:
        print(f"❌ MCPToolkit创建失败: {e}")
        print(f"🔍 详细错误: {traceback.format_exc()}")
        
        # 检查是否是特定的工具转换错误
        error_str = str(e)
        if "unhashable type: 'list'" in error_str:
            print("🎯 检测到'unhashable type: 'list''错误")
            print("这通常表示MCP工具定义中包含列表类型参数，需要特殊处理")
        
        return False

@diagnose_step("检查单个MCP服务器连接")
def step_3_check_individual_servers():
    """分别检查Amazon和Fewsats MCP服务器"""
    try:
        from camel.toolkits import MCPToolkit
        from camel.toolkits.mcp_toolkit import MCPClient
        
        print("🔄 尝试单独连接Amazon MCP服务器...")
        
        # 创建Amazon MCP配置
        amazon_config = {
            "mcpServers": {
                "amazon": {
                    "command": "uvx",
                    "args": ["amazon-mcp"],
                    "timeout": 60,
                    "initTimeout": 30
                }
            }
        }
        
        try:
            amazon_toolkit = MCPToolkit.create_sync(
                config_dict=amazon_config,
                timeout=30.0
            )
            print("✅ Amazon MCP服务器连接成功")
            
            # 尝试获取工具
            amazon_tools = amazon_toolkit.get_tools()
            print(f"📋 Amazon工具数量: {len(amazon_tools)}")
            
            for tool in amazon_tools:
                tool_name = tool.get_function_name()
                print(f"  - Amazon工具: {tool_name}")
            
            amazon_toolkit.disconnect_sync()
            
        except Exception as e:
            print(f"❌ Amazon MCP连接失败: {e}")
            if "unhashable type: 'list'" in str(e):
                print("🎯 Amazon MCP工具定义包含列表类型参数")
        
        print("\n🔄 尝试单独连接Fewsats MCP服务器...")
        
        # 创建Fewsats MCP配置
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
        
        try:
            fewsats_toolkit = MCPToolkit.create_sync(
                config_dict=fewsats_config,
                timeout=30.0
            )
            print("✅ Fewsats MCP服务器连接成功")
            
            # 尝试获取工具
            fewsats_tools = fewsats_toolkit.get_tools()
            print(f"📋 Fewsats工具数量: {len(fewsats_tools)}")
            
            for tool in fewsats_tools:
                tool_name = tool.get_function_name()
                print(f"  - Fewsats工具: {tool_name}")
            
            fewsats_toolkit.disconnect_sync()
            
        except Exception as e:
            print(f"❌ Fewsats MCP连接失败: {e}")
            if "unhashable type: 'list'" in str(e):
                print("🎯 Fewsats MCP工具定义包含列表类型参数")
        
        return True
        
    except Exception as e:
        print(f"❌ 单个服务器检查失败: {e}")
        return False

@diagnose_step("检查工具定义结构")
def step_4_inspect_tool_definitions():
    """检查工具定义的详细结构，找出列表类型参数"""
    try:
        from camel.toolkits import MCPToolkit
        
        print("🔄 深入检查工具定义结构...")
        
        # 尝试逐个服务器检查
        servers_to_check = [
            ("amazon", {
                "mcpServers": {
                    "amazon": {
                        "command": "uvx",
                        "args": ["amazon-mcp"],
                        "timeout": 30,
                        "initTimeout": 15
                    }
                }
            }),
            ("fewsats", {
                "mcpServers": {
                    "fewsats": {
                        "command": "uvx",
                        "args": ["fewsats-mcp"],
                        "env": {
                            "FEWSATS_API_KEY": "3q-t95sj95DywRNY4v4QsShXfyS1Gs4uvYRnwipK4Hg"
                        },
                        "timeout": 30,
                        "initTimeout": 15
                    }
                }
            })
        ]
        
        for server_name, config in servers_to_check:
            print(f"\n🔍 检查 {server_name} 服务器...")
            
            try:
                # 使用更底层的方式检查
                toolkit = MCPToolkit(config_dict=config, timeout=20.0)
                toolkit.connect_sync()
                
                print(f"✅ {server_name} 连接成功")
                
                # 获取原始客户端
                for i, client in enumerate(toolkit.clients):
                    print(f"  客户端 {i}: {client}")
                    
                    # 尝试获取工具列表
                    try:
                        tools = client.list_tools_sync()
                        print(f"  原始工具数量: {len(tools.tools) if tools else 0}")
                        
                        if tools and tools.tools:
                            for tool in tools.tools:
                                print(f"    工具名称: {tool.name}")
                                
                                # 检查工具参数定义
                                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                                    schema = tool.inputSchema
                                    print(f"    参数模式: {type(schema)}")
                                    
                                    # 检查是否包含列表类型
                                    if isinstance(schema, dict):
                                        properties = schema.get('properties', {})
                                        for prop_name, prop_def in properties.items():
                                            if isinstance(prop_def, dict):
                                                prop_type = prop_def.get('type')
                                                if prop_type == 'array' or isinstance(prop_def.get('items'), list):
                                                    print(f"      🎯 发现列表类型参数: {prop_name} (type: {prop_type})")
                    
                    except Exception as tool_error:
                        print(f"    ❌ 获取工具列表失败: {tool_error}")
                
                toolkit.disconnect_sync()
                
            except Exception as server_error:
                print(f"❌ {server_name} 服务器检查失败: {server_error}")
                if "unhashable type: 'list'" in str(server_error):
                    print(f"🎯 {server_name} 确实存在列表类型参数问题")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具定义检查失败: {e}")
        return False

@diagnose_step("尝试解决方案：修改工具定义")
def step_5_try_workaround():
    """尝试使用解决方案处理列表类型参数问题"""
    try:
        print("🔄 尝试实施解决方案...")
        
        # 方案1: 使用更新的CAMEL版本或配置
        print("方案1: 检查CAMEL版本兼容性")
        import camel
        print(f"当前CAMEL版本: {camel.__version__}")
        
        # 方案2: 尝试使用自定义工具转换
        print("方案2: 实施自定义工具转换逻辑")
        
        from camel.toolkits import MCPToolkit
        
        # 创建一个修改过的配置，只包含Fewsats（通常更稳定）
        stable_config = {
            "mcpServers": {
                "fewsats": {
                    "command": "uvx",
                    "args": ["fewsats-mcp"],
                    "env": {
                        "FEWSATS_API_KEY": "3q-t95sj95DywRNY4v4QsShXfyS1Gs4uvYRnwipK4Hg"
                    },
                    "timeout": 30,
                    "initTimeout": 15
                }
            }
        }
        
        print("🔄 测试仅使用Fewsats MCP...")
        fewsats_only_toolkit = MCPToolkit.create_sync(
            config_dict=stable_config,
            timeout=20.0
        )
        
        tools = fewsats_only_toolkit.get_tools()
        print(f"✅ 仅Fewsats配置成功，工具数量: {len(tools)}")
        
        for tool in tools:
            print(f"  - {tool.get_function_name()}")
        
        fewsats_only_toolkit.disconnect_sync()
        
        return True
        
    except Exception as e:
        print(f"❌ 解决方案测试失败: {e}")
        return False

def main():
    """主诊断流程"""
    print("🎯 开始MCP工具诊断...")
    
    # 步骤1: 检查基础功能
    config_path = step_1_check_mcp_toolkit()
    if not config_path:
        print("💥 基础检查失败，终止诊断")
        return False
    
    # 步骤2: 尝试创建MCPToolkit
    toolkit = step_2_create_mcp_toolkit(config_path)
    
    # 步骤3: 检查单个服务器
    step_3_check_individual_servers()
    
    # 步骤4: 深入检查工具定义
    step_4_inspect_tool_definitions()
    
    # 步骤5: 尝试解决方案
    step_5_try_workaround()
    
    # 诊断总结
    print("\n" + "=" * 60)
    print("📊 诊断总结")
    print("=" * 60)
    
    print("🔍 问题分析:")
    print("1. 'unhashable type: 'list'' 错误通常由以下原因引起:")
    print("   - MCP工具参数定义中包含列表类型")
    print("   - CAMEL框架期望可哈希的参数类型")
    print("   - 工具模式转换过程中的兼容性问题")
    
    print("\n💡 建议解决方案:")
    print("1. 暂时仅使用Fewsats MCP（更稳定）")
    print("2. 升级CAMEL框架到最新版本")
    print("3. 修改Amazon MCP工具定义，避免列表类型参数")
    print("4. 实施自定义工具转换逻辑")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ 诊断被用户中断")
    except Exception as e:
        print(f"\n💥 诊断过程中发生错误: {e}")
        print(f"🔍 错误详情: {traceback.format_exc()}") 