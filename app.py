import os
import sys
import asyncio
from flask import Flask, request, jsonify, Response, stream_with_context, send_file
from flask_cors import CORS

# --- 路径和配置初始化 ---
# 将项目根目录添加到Python路径，以便能正确导入AgentCore
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from AgentCore.config import config
    from AgentCore.Society.market_monitor import MarketMonitorAgent
    from AgentCore.Society.market_trade import AgentManager
    from camel.models import ModelFactory
    from camel.types import ModelPlatformType, ModelType
except ImportError as e:
    print(f"❌ 关键模块导入失败: {e}")
    print("🖐️ 请确保已在项目根目录运行 `pip install -r requirements.txt`")
    sys.exit(1)

# --- Flask 应用初始化 ---
app = Flask(__name__)
# 允许所有来源的跨域请求，方便前端调试
CORS(app)

# --- AI模型和Agent初始化 ---
# 创建一个统一的AI模型实例，供所有Agent使用，避免资源浪费
print("🧠 正在初始化AI模型...")
try:
    # 优先尝试使用 ModelScope Qwen 模型
    try:
        model = ModelFactory.create(
            model_platform=ModelPlatformType.MODELSCOPE,
            model_type='Qwen/Qwen2.5-72B-Instruct',
            model_config_dict={'temperature': 0.2},
            api_key='9d3aed4d-eca1-4e0c-9805-cb923ccbbf21',
        )
        print("✅ ModelScope Qwen 模型初始化成功。")
    except Exception as modelscope_error:
        print(f"⚠️ ModelScope 模型不可用: {modelscope_error}")
        print("🔄 回退到 OpenAI 模型...")
        
        # 回退到 OpenAI 模型
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4_1,
            url=config.OPENAI_API_URL,
            api_key=config.OPENAI_API_KEY,
        )
        print("✅ OpenAI 模型初始化成功。")
except Exception as e:
    print(f"❌ 所有模型初始化失败: {e}")
    model = None

# 初始化核心的两个Agent
print("🤖 正在加载AI Agents...")
market_monitor = MarketMonitorAgent(model) if model else None
agent_manager = AgentManager()
print("✅ AI Agents 已加载。")


# --- 流式响应辅助工具 ---
def clean_agent_output(text):
    """清理Agent输出，移除ANSI颜色代码和多余空行"""
    import re
    if not text:
        return ""
    
    # 移除 ANSI 颜色代码
    clean_text = re.sub(r'\x1b\[[0-9;]*m', '', str(text))
    # 移除过多的空行
    clean_text = re.sub(r'\n\s*\n\s*\n', '\n\n', clean_text)
    
    return clean_text.strip()

# --- API 端点定义 ---

@app.route("/")
def health_check():
    """基础的健康检查端点。"""
    return jsonify({"status": "ok", "message": "PolyAgent server is running."})

@app.route("/config")
def get_app_config():
    """向前端提供服务器配置信息。"""
    return jsonify({
        "openai_api_configured": bool(config.OPENAI_API_KEY and "sk-" in config.OPENAI_API_KEY),
        "iotex_rpc_url": config.IOTEX_RPC_URL,
    })

@app.route("/agents/status")
def get_agents_status():
    """检查并返回所有核心Agent的运行状态。"""
    return jsonify({
        "market_monitor": "ok" if market_monitor and model else "error",
        "agent_manager": "ok" if agent_manager else "error",
    })

@app.route("/market-monitor", methods=["POST"])
def handle_market_monitor():
    """处理来自前端的市场监控请求。"""
    data = request.json
    message = data.get("message")
    if not message:
        return jsonify({"error": "请求体中缺少'message'字段"}), 400
    if not market_monitor:
         return jsonify({"error": "Market Monitor Agent 未成功初始化"}), 500

    def stream_monitor_response():
        """优化的 MarketMonitorAgent 流式响应生成器。"""
        try:
            # 直接运行 MarketMonitorAgent
            result = market_monitor.run(message)
            
            # 清理结果输出
            if result:
                clean_result = clean_agent_output(result)
                
                # 逐行输出，提供更好的流式体验
                lines = clean_result.split('\n')
                for line in lines:
                    if line.strip():  # 只输出非空行
                        yield f"{line}\n"
            else:
                yield "未能获取市场监控信息，请稍后重试。\n"
                
        except Exception as e:
            yield f"处理市场监控请求时出错: {e}\n"

    return Response(stream_with_context(stream_monitor_response()), mimetype="text/plain")

@app.route("/market-trade", methods=["POST"])
def handle_market_trade():
    """处理来自前端的跨境支付桥接请求"""
    data = request.json
    message = data.get("message")
    if not message:
        return jsonify({"error": "请求体中缺少'message'字段"}), 400
    if not agent_manager:
        return jsonify({"error": "Agent Manager 未成功初始化"}), 500
        
    def stream_agent_response():
        try:
            # 使用新的智能路由系统处理用户消息
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(agent_manager.smart_route_request(message))
            loop.close()
            
            # 清理结果输出
            if result:
                clean_result = clean_agent_output(result)
                
                # 逐行输出
                lines = clean_result.split('\n')
                for line in lines:
                    if line.strip():
                        yield f"{line}\n"
            else:
                yield "无法处理您的请求，请稍后重试。\n"
                    
        except Exception as e:
            yield f"处理请求时出错: {e}\n"
    
    return Response(stream_with_context(stream_agent_response()), mimetype="text/plain")

@app.route("/download/<filename>")
def download_file(filename):
    """提供文件下载服务"""
    try:
        file_path = os.path.join("downloads", filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({"error": "文件不存在"}), 404
    except Exception as e:
        return jsonify({"error": f"下载失败: {str(e)}"}), 500

# --- 服务器启动 ---
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 启动 PolyAgent 服务器...")
    if not (config.OPENAI_API_KEY and "sk-" in config.OPENAI_API_KEY):
        print("⚠️ 警告: OpenAI API 密钥未配置或格式不正确。")
        print("   请在 `AgentCore/config.py` 或环境变量中设置 `OPENAI_API_KEY`。")
    
    print(f"🔗 服务地址: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"🔧 调试模式: {'开启' if config.FLASK_DEBUG else '关闭'}")
    print("=" * 60)
    
    # 使用 gunicorn 启动时，不会执行这里的 app.run
    # 直接运行 `python app.py` 时会使用 Flask 的开发服务器
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG) 