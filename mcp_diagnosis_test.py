#!/usr/bin/env python3
"""
MCP服务诊断测试脚本
用于深度检测Amazon MCP和Fewsats MCP的连接状态、配置问题和调用失败原因
"""

import os
import sys
import json
import time
import traceback
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional

# 添加项目路径
sys.path.append(os.path.abspath('.'))

def print_header(title: str):
    """打印测试段落标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_section(title: str):
    """打印小节标题"""
    print(f"\n🔍 {title}")
    print("-" * 40)

def test_environment():
    """测试环境依赖"""
    print_header("环境依赖检测")
    
    # 检查Python版本
    print_section("Python环境")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    # 检查关键依赖包
    print_section("依赖包检测")
    required_packages = [
        'qwen_agent',
        'openai', 
        'requests',
        'json',
        'traceback'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: 已安装")
        except ImportError as e:
            print(f"❌ {package}: 未安装 - {e}")
    
    # 检查环境变量
    print_section("环境变量")
    env_vars = [
        'MODELSCOPE_SDK_TOKEN',
        'FEWSATS_API_KEY'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: 已设置 ({value[:20]}...)")
        else:
            print(f"⚠️ {var}: 未设置")

def test_mcp_services():
    """测试MCP服务可用性"""
    print_header("MCP服务状态检测")
    
    print_section("uvx命令检测")
    try:
        result = subprocess.run(['uvx', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ uvx可用: {result.stdout.strip()}")
        else:
            print(f"❌ uvx不可用: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️ uvx命令超时")
    except FileNotFoundError:
        print("❌ uvx命令未找到")
    except Exception as e:
        print(f"❌ uvx检测失败: {e}")
    
    print_section("Amazon MCP服务检测")
    try:
        # 尝试启动amazon-mcp服务（超时检测）
        print("🔄 尝试启动amazon-mcp...")
        result = subprocess.run(['uvx', 'amazon-mcp', '--help'], 
                               capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ amazon-mcp服务可用")
            print(f"帮助信息: {result.stdout[:200]}...")
        else:
            print(f"❌ amazon-mcp启动失败: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️ amazon-mcp启动超时（30秒）")
    except Exception as e:
        print(f"❌ amazon-mcp检测失败: {e}")
    
    print_section("Fewsats MCP服务检测")
    try:
        # 尝试启动fewsats-mcp服务
        print("🔄 尝试启动fewsats-mcp...")
        env = os.environ.copy()
        env['FEWSATS_API_KEY'] = '3q-t95sj95DywRNY4v4QsShXfyS1Gs4uvYRnwipK4Hg'
        
        result = subprocess.run(['uvx', 'fewsats-mcp', '--help'], 
                               capture_output=True, text=True, timeout=30, env=env)
        if result.returncode == 0:
            print("✅ fewsats-mcp服务可用")
            print(f"帮助信息: {result.stdout[:200]}...")
        else:
            print(f"❌ fewsats-mcp启动失败: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️ fewsats-mcp启动超时（30秒）")
    except Exception as e:
        print(f"❌ fewsats-mcp检测失败: {e}")

def test_qwen_agent_import():
    """测试qwen-agent导入和基本功能"""
    print_header("qwen-agent功能检测")
    
    print_section("导入测试")
    try:
        from qwen_agent.agents import Assistant
        print("✅ qwen-agent导入成功")
        
        # 检查版本信息
        try:
            import qwen_agent
            if hasattr(qwen_agent, '__version__'):
                print(f"版本: {qwen_agent.__version__}")
        except:
            print("无法获取版本信息")
            
    except ImportError as e:
        print(f"❌ qwen-agent导入失败: {e}")
        return False
    
    print_section("基础Assistant创建测试")
    try:
        llm_cfg = {
            'model': 'Qwen/Qwen3-32B',
            'model_server': 'https://api-inference.modelscope.cn/v1/',
            'api_key': '9d3aed4d-eca1-4e0c-9805-cb923ccbbf21',
            'generate_cfg': {
                'temperature': 0.7,
                'max_tokens': 100,
                'timeout': 60,
            }
        }
        
        assistant = Assistant(llm=llm_cfg)
        print("✅ 基础Assistant创建成功")
        
        # 测试简单对话
        print_section("基础对话测试")
        messages = [{"role": "user", "content": "Hello, please say 'MCP test successful'"}]
        responses = list(assistant.run(messages=messages))
        
        if responses:
            print("✅ 基础对话测试成功")
            print(f"响应数量: {len(responses)}")
            if responses and len(responses) > 0:
                last_response = responses[-1]
                if isinstance(last_response, list) and len(last_response) > 0:
                    for item in last_response:
                        if isinstance(item, dict) and 'content' in item:
                            print(f"响应内容: {item['content'][:100]}...")
                            break
        else:
            print("⚠️ 基础对话测试无响应")
            
    except Exception as e:
        print(f"❌ 基础Assistant测试失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")
        return False
        
    return True

def test_mcp_configurations():
    """测试不同的MCP配置"""
    print_header("MCP配置测试")
    
    try:
        from qwen_agent.agents import Assistant
    except ImportError:
        print("❌ qwen-agent不可用，跳过MCP配置测试")
        return
    
    llm_cfg = {
        'model': 'Qwen/Qwen3-32B',
        'model_server': 'https://api-inference.modelscope.cn/v1/',
        'api_key': '9d3aed4d-eca1-4e0c-9805-cb923ccbbf21',
        'generate_cfg': {
            'temperature': 0.7,
            'max_tokens': 500,
            'timeout': 120,
        }
    }
    
    # 配置1: 标准MCP配置
    print_section("配置1: 标准MCP配置（Amazon + Fewsats）")
    tools_config_1 = [{
        "mcpServers": {
            "amazon": {
                "command": "uvx",
                "args": ["amazon-mcp"],
                "timeout": 180,
                "initTimeout": 60
            },
            "fewsats": {
                "command": "uvx",
                "args": ["fewsats-mcp"],
                "env": {
                    "FEWSATS_API_KEY": "3q-t95sj95DywRNY4v4QsShXfyS1Gs4uvYRnwipK4Hg"
                },
                "timeout": 180,
                "initTimeout": 60
            }
        }
    }]
    
    try:
        print("🔄 创建带MCP的Assistant...")
        assistant1 = Assistant(llm=llm_cfg, function_list=tools_config_1)
        print("✅ 配置1成功")
        
        # 测试Amazon搜索
        print("🔄 测试Amazon搜索...")
        messages = [{"role": "user", "content": "Search for black pen on Amazon"}]
        responses = list(assistant1.run(messages=messages))
        
        if responses:
            print("✅ Amazon搜索测试执行")
            # 分析响应内容
            all_content = ""
            for response in responses:
                if isinstance(response, list):
                    for item in response:
                        if isinstance(item, dict) and 'content' in item:
                            all_content += item['content'] + "\n"
            
            print(f"响应内容长度: {len(all_content)} 字符")
            if 'asin' in all_content.lower() or 'amazon' in all_content.lower():
                print("🎯 检测到Amazon搜索数据")
                # 尝试解析商品数据
                from AgentCore.Society.amazon_shopping_agent_qwen3 import MCPResponseParser
                products = MCPResponseParser.parse_amazon_search_response(all_content)
                print(f"解析出 {len(products)} 个商品")
            else:
                print("⚠️ 未检测到Amazon搜索数据")
                print(f"内容预览: {all_content[:300]}...")
        else:
            print("⚠️ 无响应")
            
    except Exception as e:
        print(f"❌ 配置1失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")
    
    # 配置2: 仅Amazon
    print_section("配置2: 仅Amazon MCP")
    tools_config_2 = [{
        "mcpServers": {
            "amazon": {
                "command": "uvx",
                "args": ["amazon-mcp"]
            }
        }
    }]
    
    try:
        assistant2 = Assistant(llm=llm_cfg, function_list=tools_config_2)
        print("✅ 配置2成功")
        
        # 简单测试
        messages = [{"role": "user", "content": "Help me search for iPhone on Amazon"}]
        responses = list(assistant2.run(messages=messages))
        
        if responses:
            print("✅ 仅Amazon配置测试执行")
        else:
            print("⚠️ 仅Amazon配置无响应")
            
    except Exception as e:
        print(f"❌ 配置2失败: {e}")

def test_agent_integration():
    """测试完整的Agent集成"""
    print_header("Agent集成测试")
    
    try:
        from AgentCore.Society.amazon_shopping_agent_qwen3 import AmazonShoppingAgentQwen3, ThinkingMode
        
        print_section("创建Amazon购物Agent")
        agent = AmazonShoppingAgentQwen3(ThinkingMode.AUTO)
        
        # 检查初始化状态
        status = agent.get_service_status()
        print("📊 服务状态:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 检查MCP是否可用
        if status['mcp_available']:
            print("✅ MCP服务可用")
            
            print_section("测试真实Amazon搜索")
            test_messages = [
                "I want to buy black pens",
                "Search for iPhone 15 Pro on Amazon", 
                "Help me find wireless headphones"
            ]
            
            for message in test_messages:
                print(f"\n👤 用户: {message}")
                try:
                    response = agent.process_request(message)
                    print(f"🤖 Assistant: {response[:200]}...")
                    
                    # 检查是否使用了真实工具
                    last_turn = agent.conversation_manager.conversation_history[-1] if agent.conversation_manager.conversation_history else None
                    if last_turn:
                        print(f"🔧 使用工具: {last_turn.tools_used}")
                        
                        if 'qwen_agent_mcp' in last_turn.tools_used:
                            print("✅ 成功使用qwen-agent MCP")
                        elif 'openai_api_fallback' in last_turn.tools_used:
                            print("⚠️ 回退到OpenAI API（可能生成虚拟信息）")
                        else:
                            print(f"🔍 其他工具: {last_turn.tools_used}")
                    
                    # 检查购物上下文
                    context = agent.conversation_manager.shopping_context.get_context_summary()
                    if context:
                        print(f"📦 购物上下文: {context[:100]}...")
                    else:
                        print("⚠️ 无购物上下文数据")
                        
                except Exception as e:
                    print(f"❌ 请求处理失败: {e}")
                
                print("-" * 40)
                
        else:
            print("❌ MCP服务不可用")
            print("🔧 调试信息:")
            print(f"  qwen_agent状态: {status.get('qwen_agent_available', 'Unknown')}")
            print(f"  openai状态: {status.get('openai_available', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Agent集成测试失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")

def test_manual_mcp_call():
    """手动测试MCP工具调用"""
    print_header("手动MCP调用测试")
    
    try:
        from qwen_agent.agents import Assistant
        
        print_section("手动构建MCP调用")
        
        llm_cfg = {
            'model': 'Qwen/Qwen3-32B',
            'model_server': 'https://api-inference.modelscope.cn/v1/',
            'api_key': '9d3aed4d-eca1-4e0c-9805-cb923ccbbf21',
            'generate_cfg': {
                'temperature': 0.1,  # 降低随机性
                'max_tokens': 2000,
                'timeout': 180,
            }
        }
        
        # 仅Amazon配置
        tools_config = [{
            "mcpServers": {
                "amazon": {
                    "command": "uvx",
                    "args": ["amazon-mcp"]
                }
            }
        }]
        
        assistant = Assistant(llm=llm_cfg, function_list=tools_config)
        print("✅ Assistant创建成功")
        
        # 明确的Amazon搜索指令
        explicit_messages = [
            {
                "role": "system", 
                "content": "You are an Amazon shopping assistant. Use amazon_search tool to search for products. Always call the amazon_search function when users ask to search for items."
            },
            {
                "role": "user", 
                "content": "Please use amazon_search to search for 'black pen' on Amazon. Call the amazon_search function with q='black pen'."
            }
        ]
        
        print("🔄 发送明确的Amazon搜索指令...")
        responses = list(assistant.run(messages=explicit_messages))
        
        print(f"📄 响应数量: {len(responses)}")
        
        # 详细分析响应
        for i, response in enumerate(responses):
            print(f"\n--- 响应 {i+1} ---")
            print(f"类型: {type(response)}")
            print(f"内容: {response}")
            
            if isinstance(response, list):
                for j, item in enumerate(response):
                    print(f"  项目 {j+1}: {type(item)} - {item}")
                    
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if key == 'content' and isinstance(value, str):
                                print(f"    内容长度: {len(value)} 字符")
                                if len(value) > 100:
                                    print(f"    内容预览: {value[:200]}...")
                                else:
                                    print(f"    完整内容: {value}")
                            else:
                                print(f"    {key}: {value}")
        
        # 检查是否包含Amazon数据
        all_content = ""
        for response in responses:
            if isinstance(response, list):
                for item in response:
                    if isinstance(item, dict) and 'content' in item:
                        all_content += str(item['content']) + "\n"
        
        print(f"\n📊 总内容长度: {len(all_content)} 字符")
        
        # 关键词检测
        amazon_keywords = ['asin', 'amazon.com', 'position', 'rating', 'reviews', 'price', '$']
        found_keywords = [kw for kw in amazon_keywords if kw.lower() in all_content.lower()]
        
        if found_keywords:
            print(f"🎯 检测到Amazon关键词: {found_keywords}")
            
            # 尝试解析
            from AgentCore.Society.amazon_shopping_agent_qwen3 import MCPResponseParser
            products = MCPResponseParser.parse_amazon_search_response(all_content)
            print(f"📦 解析出商品数量: {len(products)}")
            
            for i, product in enumerate(products[:3]):  # 显示前3个
                print(f"  商品{i+1}: {product.title[:50]} - {product.price} (ASIN: {product.asin})")
        else:
            print("⚠️ 未检测到Amazon数据关键词")
            print(f"内容示例: {all_content[:500]}...")
            
    except Exception as e:
        print(f"❌ 手动MCP调用测试失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")

def generate_diagnostic_report():
    """生成诊断报告"""
    print_header("生成诊断报告")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "environment_variables": {
            "MODELSCOPE_SDK_TOKEN": "SET" if os.environ.get('MODELSCOPE_SDK_TOKEN') else "NOT_SET",
            "FEWSATS_API_KEY": "SET" if os.environ.get('FEWSATS_API_KEY') else "NOT_SET"
        }
    }
    
    # 保存报告
    report_file = "mcp_diagnostic_report.json"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"✅ 诊断报告已保存到: {report_file}")
    except Exception as e:
        print(f"⚠️ 保存诊断报告失败: {e}")

def main():
    """主测试流程"""
    print_header("MCP服务深度诊断开始")
    print(f"开始时间: {datetime.now()}")
    
    try:
        # 1. 环境检测
        test_environment()
        
        # 2. MCP服务检测
        test_mcp_services()
        
        # 3. qwen-agent基础功能测试
        qwen_available = test_qwen_agent_import()
        
        if qwen_available:
            # 4. MCP配置测试
            test_mcp_configurations()
            
            # 5. 手动MCP调用测试
            test_manual_mcp_call()
            
            # 6. Agent集成测试
            test_agent_integration()
        else:
            print("\n⚠️ qwen-agent不可用，跳过后续测试")
        
        # 7. 生成诊断报告
        generate_diagnostic_report()
        
        print_header("诊断完成")
        print(f"结束时间: {datetime.now()}")
        
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断测试")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        print(f"详细错误: {traceback.format_exc()}")

if __name__ == "__main__":
    main() 