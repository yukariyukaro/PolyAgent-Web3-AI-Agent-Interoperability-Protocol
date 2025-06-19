from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import asyncio
import sys
import os
import traceback
from datetime import datetime
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 修改为导入Amazon Agent
from AgentCore.Society.amazon_shopping_agent_qwen3 import AmazonShoppingAgentQwen3, ThinkingMode

app = Flask(__name__)
CORS(app)

# 配置JSON以正确显示中文，避免Unicode转义
app.config['JSON_AS_ASCII'] = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局agent实例，支持多轮对话
shopping_agent = None

def get_shopping_agent():
    """获取或创建Amazon购物助手实例"""
    global shopping_agent
    if shopping_agent is None:
        try:
            # 使用Amazon Agent替代优选Agent
            shopping_agent = AmazonShoppingAgentQwen3(thinking_mode=ThinkingMode.AUTO)
            
            logger.info("🤖 创建新的Amazon购物助手实例")
            print("🤖 创建新的Amazon购物助手实例")
        except Exception as e:
            logger.error(f"❌ 创建Amazon购物助手失败: {e}")
            print(f"❌ 创建Amazon购物助手失败: {e}")
            # 即使创建失败，也返回None，后续会有处理
            return None
    return shopping_agent

@app.route('/')
def index():
    """主页"""
    return jsonify({
        'status': 'ok',
        'message': 'PolyAgent Amazon购物助手 - Qwen3增强版',
        'version': '3.0',
        'agent_type': 'Amazon Shopping Agent with Qwen3',
        'features': [
            'Amazon商品搜索与购买',
            'MCP工具集成(12个工具)',
            'Qwen3-32B智能推理',
            '多思考模式支持',
            '多轮对话支持',
            '购物状态管理',
            '支付流程集成'
        ],
        'endpoints': {
            'chat': '/api/chat',
            'history': '/api/conversation/history',
            'clear': '/api/conversation/clear',
            'health': '/api/health',
            'status': '/api/status'
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求，支持多轮对话和Amazon购物功能"""
    try:
        # 验证请求格式
        data = request.get_json()
        if not data or 'message' not in data:
            logger.warning("❌ 请求格式错误，缺少message字段")
            return jsonify({
                'success': False,
                'error': '请求格式错误，缺少message字段',
                'error_type': 'invalid_request'
            }), 400

        user_message = data['message'].strip()
        if not user_message:
            logger.warning("❌ 消息内容为空")
            return jsonify({
                'success': False,
                'error': '消息内容不能为空',
                'error_type': 'empty_message'
            }), 400

        logger.info(f"🔍 [{datetime.now().strftime('%H:%M:%S')}] 收到用户消息: {user_message}")
        print(f"🔍 [{datetime.now().strftime('%H:%M:%S')}] 收到用户消息: {user_message}")

        # 获取Amazon购物助手实例
        agent = get_shopping_agent()
        
        if agent is None:
            logger.error("❌ Amazon购物助手初始化失败")
            return jsonify({
                'success': False,
                'error': 'Amazon购物助手服务暂时不可用，请稍后重试',
                'error_type': 'agent_unavailable'
            }), 503
        
        # 处理用户请求（增加超时时间到90秒，因为Amazon Agent可能需要调用MCP工具）
        try:
            response_future = agent.process_request(user_message)
            result = asyncio.run(asyncio.wait_for(response_future, timeout=90.0))
            
            logger.info(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Amazon Agent响应生成完成")
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Amazon Agent响应生成完成")
            
            # 获取对话历史统计和购物状态
            history = agent.get_conversation_history()
            shopping_state = agent.get_shopping_state()
            
            conversation_stats = {
                'total_turns': len(history),
                'mcp_available': shopping_state.get('mcp_available', False),
                'thinking_mode': shopping_state.get('thinking_mode', 'auto'),
                'current_state': shopping_state.get('current_state', 'browsing')
            }
            
            return jsonify({
                'success': True,
                'response': result,
                'conversation_stats': conversation_stats,
                'shopping_state': shopping_state,
                'timestamp': datetime.now().isoformat()
            })

        except asyncio.TimeoutError:
            logger.warning(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] Amazon Agent请求超时")
            print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] Amazon Agent请求超时")
            
            # 超时的简单响应
            fallback_response = f"""抱歉，处理您的请求"{user_message}"时超时。请稍后重试或简化您的问题。"""

            # 记录到对话历史（如果可能）
            try:
                agent.conversation_manager.add_turn(user_message, fallback_response)
            except:
                pass
            
            return jsonify({
                'success': True,
                'response': fallback_response,
                'conversation_stats': {'total_turns': len(agent.get_conversation_history())},
                'shopping_state': {'timeout': True},
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Amazon Agent处理请求时出错: {e}")
            print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Amazon Agent处理请求时出错: {e}")
            print(f"🔍 详细错误信息: {traceback.format_exc()}")
            
            # 生成简单的错误响应
            fallback_response = f"""抱歉，处理您的请求"{user_message}"时遇到技术问题。请稍后重试或重新描述您的需求。"""

            # 尝试记录对话历史
            try:
                agent.conversation_manager.add_turn(user_message, fallback_response)
            except:
                pass
            
            # 根据错误类型提供不同的错误信息
            error_msg = str(e).lower()
            if "mcp" in error_msg or "toolkit" in error_msg:
                error_type = "mcp_connection_error"
            elif "model" in error_msg or "qwen" in error_msg:
                error_type = "model_error"
            elif "connection" in error_msg or "network" in error_msg:
                error_type = "connection_error"
            elif "timeout" in error_msg:
                error_type = "timeout"
            else:
                error_type = "processing_error"
            
            return jsonify({
                'success': True,  # 仍然返回success=True因为我们提供了有用的响应
                'response': fallback_response,
                'conversation_stats': {'total_turns': len(agent.get_conversation_history())},
                'shopping_state': {'error': True, 'error_type': error_type},
                'timestamp': datetime.now().isoformat()
            })

    except Exception as e:
        logger.error(f"❌ [{datetime.now().strftime('%H:%M:%S')}] API错误: {e}")
        print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] API错误: {e}")
        print(f"🔍 详细错误信息: {traceback.format_exc()}")
        
        # 最后的兜底响应
        return jsonify({
            'success': False,
            'error': 'Amazon购物助手服务暂时不可用，请稍后重试',
            'error_type': 'server_error',
            'fallback_response': '您好！Amazon购物助手当前遇到技术问题，请稍后重试。',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/conversation/history', methods=['GET'])
def get_conversation_history():
    """获取对话历史"""
    try:
        agent = get_shopping_agent()
        if agent is None:
            return jsonify({
                'success': False,
                'error': 'Amazon购物助手服务不可用'
            }), 503
            
        history = agent.get_conversation_history()
        
        # 转换为可序列化的格式
        history_data = []
        for turn in history:
            history_data.append({
                'user_input': turn.user_input,
                'ai_response': turn.ai_response,
                'timestamp': turn.timestamp.isoformat(),
                'shopping_state': turn.shopping_state.value,
                'tools_used': turn.tools_used,
                'thinking_content': turn.thinking_content[:200] + "..." if len(turn.thinking_content) > 200 else turn.thinking_content
            })
        
        return jsonify({
            'success': True,
            'history': history_data,
            'total_turns': len(history_data),
            'shopping_state': agent.get_shopping_state()
        })
        
    except Exception as e:
        logger.error(f"❌ 获取对话历史失败: {e}")
        print(f"❌ 获取对话历史失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取对话历史失败: {str(e)}'
        }), 500

@app.route('/api/conversation/clear', methods=['POST'])
def clear_conversation():
    """清除对话历史"""
    try:
        agent = get_shopping_agent()
        if agent is None:
            return jsonify({
                'success': False,
                'error': 'Amazon购物助手服务不可用'
            }), 503
            
        agent.clear_conversation_history()
        
        logger.info("🧹 Amazon购物助手对话历史已清除")
        print("🧹 Amazon购物助手对话历史已清除")
        return jsonify({
            'success': True,
            'message': 'Amazon购物助手对话历史已清除，开始新的购物之旅吧！'
        })
        
    except Exception as e:
        logger.error(f"❌ 清除对话历史失败: {e}")
        print(f"❌ 清除对话历史失败: {e}")
        return jsonify({
            'success': False,
            'error': f'清除对话历史失败: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        agent = get_shopping_agent()
        
        if agent is None:
            return jsonify({
                'success': False,
                'status': 'unhealthy',
                'error': 'Amazon购物助手初始化失败',
                'timestamp': datetime.now().isoformat()
            }), 503
            
        history_count = len(agent.get_conversation_history())
        shopping_state = agent.get_shopping_state()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'agent_type': 'Amazon Shopping Agent Qwen3',
            'conversation_turns': history_count,
            'shopping_state': shopping_state,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取详细的服务状态"""
    try:
        agent = get_shopping_agent()
        
        basic_status = {
            'timestamp': datetime.now().isoformat(),
            'agent_initialized': agent is not None,
            'agent_type': 'Amazon Shopping Agent Qwen3',
            'uptime': 'running'
        }
        
        if agent is not None:
            shopping_state = agent.get_shopping_state()
            basic_status.update(shopping_state)
            basic_status['conversation_turns'] = len(agent.get_conversation_history())
        
        return jsonify({
            'success': True,
            'status': basic_status
        })
        
    except Exception as e:
        logger.error(f"❌ 获取状态失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# 兼容旧的API端点
@app.route("/youxuan-shopping", methods=["POST"])
def handle_youxuan_shopping():
    """兼容旧的购物请求端点，现在使用Amazon Agent"""
    try:
        data = request.json
        if not data or "message" not in data:
            return jsonify({"error": "请求体中缺少'message'字段"}), 400
        
        # 重定向到新的chat API（现在使用Amazon Agent）
        return chat()
        
    except Exception as e:
        logger.error(f"❌ 处理旧接口请求失败: {e}")
        return jsonify({"error": f"处理请求失败: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': '请求的资源不存在',
        'available_endpoints': [
            '/api/chat',
            '/api/conversation/history',
            '/api/conversation/clear',
            '/api/health',
            '/api/status'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '服务器内部错误，请稍后重试',
        'timestamp': datetime.now().isoformat()
    }), 500

@app.errorhandler(503)
def service_unavailable(error):
    return jsonify({
        'success': False,
        'error': '服务暂时不可用，请稍后重试',
        'timestamp': datetime.now().isoformat()
    }), 503

if __name__ == '__main__':
    print("🚀 启动Amazon购物助手服务 (Qwen3增强版)...")
    print("🛒 支持Amazon商品搜索、购买和MCP工具集成")
    print("🧠 基于Qwen3-32B模型的智能推理")
    print("🔧 支持多思考模式和购物状态管理")
    print("⏰ 请求超时时间: 90秒")
    print("🌐 访问地址: http://localhost:5000")
    print("🔧 API端点:")
    print("   POST /api/chat - Amazon购物对话")
    print("   GET  /api/conversation/history - 获取对话历史")
    print("   POST /api/conversation/clear - 清除对话历史")
    print("   GET  /api/health - 健康检查")
    print("   GET  /api/status - 详细状态")
    print("   GET  / - 服务信息")
    
    logger.info("🚀 Amazon购物助手服务启动")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    ) 