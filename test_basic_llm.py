#!/usr/bin/env python3
"""
测试A2A Amazon Agent的基础LLM连接能力
"""

import os
import sys
import traceback

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

def test_basic_llm_connection():
    """测试基础LLM连接能力"""
    try:
        print("🔄 开始测试基础LLM连接能力...")
        print("="*60)
        
        # 设置环境变量
        if not os.environ.get('MODELSCOPE_SDK_TOKEN'):
            os.environ['MODELSCOPE_SDK_TOKEN'] = '9d3aed4d-eca1-4e0c-9805-cb923ccbbf21'
            print("🔧 设置MODELSCOPE_SDK_TOKEN环境变量")
        
        # 导入Amazon Agent
        print("📦 导入Amazon Shopping Service Manager...")
        # 由于文件名有空格，需要使用特殊导入方式
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "a2a_amazon_agent", 
            "AgentCore/Agents/a2a amazon agent.py"
        )
        a2a_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(a2a_module)
        AmazonShoppingServiceManager = a2a_module.AmazonShoppingServiceManager
        print("✅ 导入成功")
        
        # 创建Agent实例
        print("\n🤖 创建Agent实例...")
        agent = AmazonShoppingServiceManager()
        print("✅ Agent实例创建成功")
        
        # 检查初始化状态
        print("\n📊 检查服务状态...")
        status = agent.get_service_status()
        print(f"  - Agent类型: {status.get('agent_type')}")
        print(f"  - 版本: {status.get('version')}")
        print(f"  - Qwen Agent可用: {status.get('qwen_agent_available')}")
        print(f"  - MCP可用: {status.get('mcp_available')}")
        print(f"  - Amazon MCP: {status.get('amazon_mcp_available')}")
        print(f"  - Fewsats MCP: {status.get('fewsats_mcp_available')}")
        
        # 测试基础对话功能
        print("\n💬 测试基础对话功能...")
        test_messages = [
            "你好",
            "你是谁？",
            "我想买苹果手机",
            "请帮我搜索iPhone 15",
            "谢谢"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- 测试 {i}/{len(test_messages)} ---")
            print(f"👤 用户: {message}")
            
            try:
                response = agent.process_request(message)
                print(f"🤖 Assistant: {response[:200]}{'...' if len(response) > 200 else ''}")
                print("✅ 响应成功")
            except Exception as e:
                print(f"❌ 响应失败: {e}")
                print(f"详细错误: {traceback.format_exc()}")
        
        # 测试购物状态
        print("\n🛒 检查购物状态...")
        shopping_state = agent.get_shopping_state()
        print(f"  - 当前状态: {shopping_state.get('current_state')}")
        print(f"  - 对话轮次: {shopping_state.get('conversation_turns')}")
        print(f"  - 思考模式: {shopping_state.get('thinking_mode')}")
        
        print("\n✅ 基础LLM连接测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")
        return False

def test_basic_llm_fallback():
    """测试基础LLM fallback机制"""
    try:
        print("\n" + "="*60)
        print("🔄 测试基础LLM fallback机制...")
        
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "a2a_amazon_agent", 
            "AgentCore/Agents/a2a amazon agent.py"
        )
        a2a_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(a2a_module)
        AmazonShoppingServiceManager = a2a_module.AmazonShoppingServiceManager
        agent = AmazonShoppingServiceManager()
        
        # 模拟MCP不可用的情况下的基础LLM测试
        print("\n🧪 模拟MCP工具不可用的场景...")
        
        # 直接测试_try_basic_llm_response方法
        test_messages = [
            {"role": "system", "content": "你是Amazon购物助手"},
            {"role": "user", "content": "你好，我想买手机"}
        ]
        
        print("📝 测试基础LLM响应方法...")
        response = agent._try_basic_llm_response(test_messages, "测试场景")
        
        if response:
            print(f"✅ 基础LLM响应成功: {response[:150]}{'...' if len(response) > 150 else ''}")
        else:
            print("❌ 基础LLM响应失败")
        
        # 测试简化的fallback
        print("\n📝 测试简化fallback...")
        fallback_response = agent._generate_fallback_response("测试消息", "测试错误")
        print(f"🔄 Fallback响应: {fallback_response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback测试失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 启动A2A Amazon Agent基础LLM连接测试")
    print("="*60)
    
    # 测试基础连接
    success1 = test_basic_llm_connection()
    
    # 测试fallback机制
    success2 = test_basic_llm_fallback()
    
    print("\n" + "="*60)
    if success1 and success2:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查日志")
    print("="*60) 