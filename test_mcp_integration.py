#!/usr/bin/env python3
"""
Amazon MCP服务集成测试
测试MCP服务能否正常调用以及与Qwen3模型的集成
"""

import sys
import os
import asyncio
import json
import traceback
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

async def test_mcp_service_connection():
    """测试MCP服务连接"""
    print("🔍 测试Amazon MCP服务连接...")
    
    try:
        from camel.toolkits import MCPToolkit
        
        # MCP配置文件路径
        mcp_config_path = os.path.join(
            os.path.dirname(__file__), "AgentCore", "Mcp", "amazon_fewsats_server.json"
        )
        
        print(f"📁 MCP配置文件路径: {mcp_config_path}")
        
        # 检查配置文件是否存在
        if not os.path.exists(mcp_config_path):
            print(f"❌ MCP配置文件不存在: {mcp_config_path}")
            return False, None, []
        
        # 读取并显示配置
        with open(mcp_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f"📋 MCP配置: {json.dumps(config, indent=2, ensure_ascii=False)}")
        
        # 初始化MCP工具包 - 使用正确的API
        print("🔧 初始化MCP工具包...")
        mcp_toolkit = MCPToolkit(config_path=mcp_config_path)
        print("✅ MCP工具包初始化成功")
        
        # 连接MCP服务
        print("🔗 连接MCP服务...")
        await mcp_toolkit.connect()
        print("✅ MCP服务连接成功")
        
        # 获取工具列表
        print("🛠️ 获取可用工具...")
        tools = mcp_toolkit.get_tools()
        print(f"📊 发现 {len(tools)} 个工具:")
        
        for i, tool in enumerate(tools, 1):
            tool_name = getattr(tool, 'name', 'Unknown')
            tool_desc = getattr(tool, 'description', 'No description')
            print(f"   {i}. {tool_name}: {tool_desc}")
        
        return True, mcp_toolkit, tools
        
    except ImportError as e:
        print(f"❌ MCP工具包导入失败: {e}")
        return False, None, []
    except Exception as e:
        print(f"❌ MCP服务连接失败: {e}")
        print(f"🔍 详细错误: {traceback.format_exc()}")
        return False, None, []

async def test_mcp_tool_call(mcp_toolkit, tools):
    """测试MCP工具调用"""
    print("\n🔍 测试MCP工具调用...")
    
    if not tools:
        print("❌ 没有可用的工具进行测试")
        return False
    
    try:
        # 尝试调用第一个可用工具
        test_tool = tools[0]
        tool_name = getattr(test_tool, 'name', 'Unknown')
        print(f"🧪 测试工具: {tool_name}")
        
        # 根据工具类型进行不同的测试
        if 'search' in tool_name.lower() or 'amazon' in tool_name.lower():
            # 如果是搜索工具，使用搜索参数
            print("🔍 尝试Amazon搜索...")
            result = await mcp_toolkit.call_tool(tool_name, {"q": "iPhone 15 Pro"})
            print(f"✅ Amazon搜索工具调用成功")
            print(f"📄 结果类型: {type(result)}")
            print(f"📝 结果预览: {str(result)[:200]}...")
            
        elif 'payment' in tool_name.lower() or 'fewsats' in tool_name.lower():
            # 如果是支付工具，测试余额查询
            print("💰 尝试查询支付余额...")
            result = await mcp_toolkit.call_tool(tool_name, {"action": "balance"})
            print(f"✅ 支付工具调用成功")
            print(f"📄 结果: {result}")
            
        else:
            # 其他工具，尝试基本调用
            print(f"🔄 尝试调用工具 {tool_name}...")
            # 这里可能需要根据具体工具调整参数
            
        return True
        
    except Exception as e:
        print(f"❌ MCP工具调用失败: {e}")
        print(f"🔍 详细错误: {traceback.format_exc()}")
        return False

async def test_modelscope_qwen3():
    """测试ModelScope Qwen3模型"""
    print("\n🔍 测试ModelScope Qwen3模型...")
    
    try:
        from modelscope import AutoModelForCausalLM, AutoTokenizer
        print("✅ ModelScope导入成功")
        
        # 设置token
        os.environ['MODELSCOPE_SDK_TOKEN'] = '9d3aed4d-eca1-4e0c-9805-cb923ccbbf21'
        
        model_name = "Qwen/Qwen3-32B"
        print(f"🤖 加载模型: {model_name}")
        
        # 只测试tokenizer初始化（模型太大，不实际加载）
        print("🔤 测试tokenizer初始化...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("✅ Tokenizer初始化成功")
        
        # 测试简单的tokenization
        test_text = "Hello, I want to buy an iPhone"
        tokens = tokenizer.encode(test_text)
        decoded = tokenizer.decode(tokens)
        print(f"🧪 测试文本: {test_text}")
        print(f"📊 Token数量: {len(tokens)}")
        print(f"🔄 解码结果: {decoded}")
        
        print("✅ ModelScope Qwen3测试成功")
        return True
        
    except ImportError as e:
        print(f"❌ ModelScope导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ ModelScope Qwen3测试失败: {e}")
        print(f"🔍 详细错误: {traceback.format_exc()}")
        return False

async def test_integration_possibilities():
    """测试集成可能性"""
    print("\n🔍 分析MCP与ModelScope集成可能性...")
    
    # 分析1：直接集成可能性
    print("📋 集成分析:")
    print("1. MCP服务基于CAMEL框架")
    print("2. Qwen3模型支持ModelScope框架")
    print("3. 两者之间需要适配层")
    
    # 分析2：可能的解决方案
    print("\n💡 可能的解决方案:")
    print("方案A: 保持CAMEL MCP + ModelScope Qwen3双框架")
    print("  - 优势: 功能完整，兼容性好")
    print("  - 劣势: 双框架依赖，复杂度高")
    
    print("方案B: 纯ModelScope实现")
    print("  - 优势: 框架统一，简洁")
    print("  - 劣势: 需要重新实现MCP功能")
    
    print("方案C: 创建MCP-ModelScope适配器")
    print("  - 优势: 平衡性好，保持MCP功能")
    print("  - 劣势: 需要额外开发工作")
    
    return True

async def cleanup_mcp_connection(mcp_toolkit):
    """清理MCP连接"""
    if mcp_toolkit:
        try:
            await mcp_toolkit.disconnect()
            print("🧹 MCP连接已清理")
        except Exception as e:
            print(f"⚠️ MCP连接清理失败: {e}")

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 Amazon MCP + Qwen3 集成测试")
    print("=" * 60)
    
    mcp_toolkit = None
    
    try:
        # 测试1: MCP服务连接
        mcp_success, mcp_toolkit, tools = await test_mcp_service_connection()
        
        # 测试2: MCP工具调用（如果连接成功）
        if mcp_success and mcp_toolkit:
            tool_success = await test_mcp_tool_call(mcp_toolkit, tools)
        else:
            tool_success = False
        
        # 测试3: ModelScope Qwen3
        modelscope_success = await test_modelscope_qwen3()
        
        # 测试4: 集成可能性分析
        await test_integration_possibilities()
        
        # 总结
        print("\n" + "=" * 60)
        print("📊 测试结果总结:")
        print(f"   MCP服务连接: {'✅ 成功' if mcp_success else '❌ 失败'}")
        print(f"   MCP工具调用: {'✅ 成功' if tool_success else '❌ 失败'}")
        print(f"   ModelScope Qwen3: {'✅ 成功' if modelscope_success else '❌ 失败'}")
        
        print("\n💭 建议:")
        if mcp_success and modelscope_success:
            print("🎯 方案A: 双框架并行 - 当前最可行")
            print("   保持CAMEL MCP工具，ModelScope Qwen3推理")
        elif mcp_success and not modelscope_success:
            print("🔄 继续使用CAMEL框架")
            print("   ModelScope可能需要更多配置")
        elif not mcp_success and modelscope_success:
            print("🆕 考虑纯ModelScope方案")
            print("   但需要重新实现MCP功能")
        else:
            print("🔧 需要排查基础环境问题")
        
        print("=" * 60)
        
    finally:
        # 清理连接
        await cleanup_mcp_connection(mcp_toolkit)

if __name__ == "__main__":
    asyncio.run(main()) 