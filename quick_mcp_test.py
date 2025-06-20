#!/usr/bin/env python3
"""
快速MCP测试脚本 - 验证Amazon MCP调用修复
"""

import os
import sys
import json
import traceback
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.abspath('.'))

def test_environment_setup():
    """测试环境变量设置"""
    print("🔧 环境变量检查:")
    
    # 检查设置前
    print(f"  设置前 MODELSCOPE_SDK_TOKEN: {'已设置' if os.environ.get('MODELSCOPE_SDK_TOKEN') else '未设置'}")
    print(f"  设置前 FEWSATS_API_KEY: {'已设置' if os.environ.get('FEWSATS_API_KEY') else '未设置'}")
    
    # 导入agent（会触发环境变量设置）
    try:
        from AgentCore.Society.amazon_shopping_agent_qwen3 import AmazonShoppingAgentQwen3, ThinkingMode
        print("✅ Agent导入成功")
    except Exception as e:
        print(f"❌ Agent导入失败: {e}")
        return False
    
    # 检查设置后
    print(f"  设置后 MODELSCOPE_SDK_TOKEN: {'已设置' if os.environ.get('MODELSCOPE_SDK_TOKEN') else '未设置'}")
    print(f"  设置后 FEWSATS_API_KEY: {'已设置' if os.environ.get('FEWSATS_API_KEY') else '未设置'}")
    
    return True

def test_agent_initialization():
    """测试Agent初始化"""
    print("\n🎯 测试Agent初始化:")
    
    try:
        from AgentCore.Society.amazon_shopping_agent_qwen3 import AmazonShoppingAgentQwen3, ThinkingMode
        
        # 创建Agent
        print("🔄 创建Amazon购物Agent...")
        agent = AmazonShoppingAgentQwen3(ThinkingMode.AUTO)
        
        # 检查服务状态
        status = agent.get_service_status()
        print("📊 服务状态:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 重点检查MCP状态
        mcp_available = status.get('mcp_available', False)
        qwen_agent_available = status.get('qwen_agent_available', False)
        
        if mcp_available:
            print("✅ MCP服务可用")
            return agent, True
        elif qwen_agent_available:
            print("⚠️ qwen-agent可用但MCP不可用")
            return agent, False
        else:
            print("❌ qwen-agent和MCP都不可用")
            return agent, False
            
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")
        return None, False

def test_simple_amazon_search(agent):
    """测试简单的Amazon搜索"""
    print("\n🛒 测试Amazon搜索:")
    
    try:
        # 简单的搜索请求
        search_query = "I want to buy black pens"
        print(f"👤 用户输入: {search_query}")
        
        # 发送请求
        response = agent.process_request(search_query)
        
        # 分析响应
        print(f"🤖 AI响应长度: {len(response)} 字符")
        print(f"🤖 AI响应预览: {response[:200]}...")
        
        # 检查使用的工具
        if agent.conversation_manager.conversation_history:
            last_turn = agent.conversation_manager.conversation_history[-1]
            tools_used = last_turn.tools_used
            print(f"🔧 使用的工具: {tools_used}")
            
            if 'qwen_agent_mcp' in tools_used:
                print("✅ 成功使用qwen-agent MCP（真实工具调用）")
                success = True
            elif 'openai_api_fallback' in tools_used:
                print("⚠️ 回退到OpenAI API（可能产生虚拟信息）")
                success = False
            else:
                print(f"🔍 使用了其他工具: {tools_used}")
                success = False
        else:
            print("⚠️ 没有对话历史记录")
            success = False
        
        # 检查购物上下文
        context = agent.conversation_manager.shopping_context.get_context_summary()
        if context:
            print(f"📦 购物上下文: 有数据")
            print(f"📦 搜索结果数量: {len(agent.conversation_manager.shopping_context.search_results)}")
            
            # 显示解析的商品信息
            if agent.conversation_manager.shopping_context.search_results:
                print("📦 解析出的商品:")
                for i, product in enumerate(agent.conversation_manager.shopping_context.search_results[:3]):
                    print(f"  {i+1}. {product.title[:50]} - {product.price} (ASIN: {product.asin})")
                success = True
            else:
                print("⚠️ 无商品解析结果")
        else:
            print("⚠️ 无购物上下文数据")
        
        return success
        
    except Exception as e:
        print(f"❌ Amazon搜索测试失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")
        return False

def test_multiple_searches(agent):
    """测试多次搜索以验证稳定性"""
    print("\n🔄 测试多次搜索稳定性:")
    
    test_queries = [
        "Search for iPhone 15 Pro",
        "Find wireless headphones", 
        "Look for laptop bags"
    ]
    
    success_count = 0
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- 测试 {i}/3: {query} ---")
        
        try:
            response = agent.process_request(query)
            
            # 检查工具使用
            if agent.conversation_manager.conversation_history:
                last_turn = agent.conversation_manager.conversation_history[-1]
                tools_used = last_turn.tools_used
                
                if 'qwen_agent_mcp' in tools_used:
                    print(f"✅ 测试{i}: 成功使用MCP")
                    success_count += 1
                else:
                    print(f"⚠️ 测试{i}: 未使用MCP，工具: {tools_used}")
            else:
                print(f"⚠️ 测试{i}: 无对话历史")
                
        except Exception as e:
            print(f"❌ 测试{i}失败: {e}")
    
    print(f"\n📊 多次测试结果: {success_count}/{len(test_queries)} 成功")
    return success_count == len(test_queries)

def main():
    """主测试流程"""
    print("="*60)
    print("  快速MCP修复验证测试")
    print("="*60)
    print(f"开始时间: {datetime.now()}")
    
    # 1. 环境变量测试
    if not test_environment_setup():
        print("\n❌ 环境设置测试失败，退出")
        return
    
    # 2. Agent初始化测试
    agent, mcp_available = test_agent_initialization()
    if not agent:
        print("\n❌ Agent初始化失败，退出")
        return
    
    # 3. 如果MCP可用，进行搜索测试
    if mcp_available:
        print("\n✅ MCP可用，进行搜索测试")
        
        # 单次搜索测试
        search_success = test_simple_amazon_search(agent)
        
        if search_success:
            print("\n✅ 单次搜索测试成功")
            
            # 多次搜索稳定性测试
            stability_success = test_multiple_searches(agent)
            
            if stability_success:
                print("\n🎉 所有测试通过！Amazon MCP调用已修复！")
                final_status = "FIXED"
            else:
                print("\n⚠️ MCP调用不稳定")
                final_status = "UNSTABLE"
        else:
            print("\n❌ 搜索测试失败")
            final_status = "FAILED"
    else:
        print("\n❌ MCP不可用")
        final_status = "MCP_UNAVAILABLE"
    
    # 生成简要报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "final_status": final_status,
        "mcp_available": mcp_available,
        "environment_variables": {
            "MODELSCOPE_SDK_TOKEN": "SET" if os.environ.get('MODELSCOPE_SDK_TOKEN') else "NOT_SET",
            "FEWSATS_API_KEY": "SET" if os.environ.get('FEWSATS_API_KEY') else "NOT_SET"
        }
    }
    
    print("\n" + "="*60)
    print(f"  最终状态: {final_status}")
    print("="*60)
    
    # 保存简要报告
    try:
        with open("quick_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📝 测试报告已保存到: quick_test_report.json")
    except Exception as e:
        print(f"⚠️ 保存报告失败: {e}")

if __name__ == "__main__":
    main() 