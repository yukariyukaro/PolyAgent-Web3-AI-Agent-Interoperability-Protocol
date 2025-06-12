# file: app.py (refactored as API Gateway)

import os
import sys
from flask import Flask, request, jsonify, Response, stream_with_context, send_file
from flask_cors import CORS
from pprint import pprint
# --- 路径和配置初始化 ---
# 将项目根目录添加到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from AgentCore.config import config
    # 导入A2A客户端，这是与后台服务通信的唯一方式
    from python_a2a import A2AClient
except ImportError as e:
    print(f"❌ 关键模块导入失败: {e}")
    print("🖐️ 请确保已在项目根目录运行 `pip install -r requirements.txt`")
    sys.exit(1)

# --- Flask 应用初始化 ---
app = Flask(__name__)
CORS(app)


# --- A2A 客户端初始化 ---
# app.py 不再持有 Agent 实例，而是持有指向后台 Agent 服务器的客户端
# ==============================================================================
# 核心变化：不再初始化 MarketMonitorAgent 和 AgentManager
# 而是创建两个 A2AClient 实例
# ==============================================================================
print("🔌 正在初始化A2A客户端以连接后台Agent服务...")
market_monitor_client = None
market_trade_client = None
try:
    # 从配置中读取后台服务的URL
    # 使用 getattr 提供一个默认端口，增加健壮性
    MONITOR_PORT = getattr(config, 'MARKET_MONITOR_PORT', 5002)
    TRADE_PORT = getattr(config, 'MARKET_TRADE_PORT', 5003)
    
    MONITOR_URL = f"http://localhost:{MONITOR_PORT}"
    TRADE_URL = f"http://localhost:{TRADE_PORT}"
    
    market_monitor_client = A2AClient(endpoint_url=MONITOR_URL)
    market_trade_client = A2AClient(endpoint_url=TRADE_URL)
    
    print("✅ A2A客户端已配置:")
    print(f"   - Market Monitor Service at: {MONITOR_URL}")
    print(f"   - Market Trade Service at:   {TRADE_URL}")
except Exception as e:
    print(f"❌ A2A客户端初始化失败: {e}")
    print("   请确保后台A2A服务正在运行，并且端口配置正确。")

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
    return jsonify({"status": "ok", "message": "PolyAgent API Gateway is running."})

@app.route("/config")
def get_app_config():
    """向前端提供服务器配置信息。"""
    # 这里的逻辑保持不变，因为这些配置对前端可能仍然有用
    return jsonify({
        "openai_api_configured": bool(config.OPENAI_API_KEY and "sk-" in config.OPENAI_API_KEY),
        "iotex_rpc_url": config.IOTEX_RPC_URL,
    })

@app.route("/agents/status")
def get_agents_status():
    """
    检查并返回所有核心Agent服务器的运行状态。
    这个端点现在会真实地通过网络检查后台服务的健康状况。
    """
    monitor_status = "error"
    trade_status = "error"
    
    # 检查 Market Monitor 服务
    try:
        if market_monitor_client and market_monitor_client.get_agent_card():
            # get_agent_card() 会发起一次网络请求，如果成功，说明服务在线
            monitor_status = "ok"
    except Exception as e:
        print(f"⚠️无法连接到 Market Monitor 服务: {e}")

    # 检查 Market Trade 服务
    try:
        if market_trade_client and market_trade_client.get_agent_card():
            trade_status = "ok"
    except Exception as e:
        print(f"⚠️无法连接到 Market Trade 服务: {e}")
        
    return jsonify({
        "market_monitor_service": monitor_status,
        "market_trade_service": trade_status,
    })

@app.route("/market-monitor", methods=["POST"])
def handle_market_monitor():
    """
    处理来自前端的市场监控请求。
    此函数现在将请求通过 A2A 客户端转发给 market_monitor_server.py。
    """
    data = request.json
    message = data.get("message")
    if not message:
        return jsonify({"error": "请求体中缺少'message'字段"}), 400
    if not market_monitor_client:
         return jsonify({"error": "Market Monitor client 未成功初始化或无法连接到服务"}), 503 # 503 Service Unavailable

    def stream_response():
        """通过A2A客户端请求后台服务，并流式返回结果"""
        try:
            # 使用 A2A 客户端的 ask 方法，它会处理所有网络通信
            response_text = market_monitor_client.ask(message)
            
            clean_result = clean_agent_output(response_text)
            
            # 逐行输出，提供更好的流式体验
            lines = clean_result.split('\n')
            for line in lines:
                if line.strip():  # 只输出非空行
                    yield f"{line}\n"
            
        except Exception as e:
            error_message = f"与 Market Monitor 服务通信时出错: {e}"
            print(f"❌ {error_message}")
            yield f"{error_message}\n"

    return Response(stream_with_context(stream_response()), mimetype="text/plain")

@app.route("/market-trade", methods=["POST"])
def handle_market_trade():
    """
    处理来自前端的跨境支付桥接请求。
    此函数现在将请求通过 A2A 客户端转发给 market_trade_server.py。
    """
    data = request.json
    message = data.get("message")
    if not message:
        return jsonify({"error": "请求体中缺少'message'字段"}), 400
    if not market_trade_client:
        return jsonify({"error": "Market Trade client 未成功初始化或无法连接到服务"}), 503
        
    def stream_response():
        try:
            # ask() 方法现在直接返回我们需要的HTML字符串
            response_text = market_trade_client.ask(message)
            
            # (可选) 打印一下，确认收到的就是HTML
            print("\n" + "="*20 + " A2A Client Received " + "="*20)
            print(response_text)
            print("="*60 + "\n")

            # 清理函数现在可能不是必需的，但保留也无妨
            clean_result = clean_agent_output(response_text)
            
            # 直接流式传输结果，不再需要复杂的解析
            lines = clean_result.split('\n')
            for line in lines:
                # 即使是HTML代码，我们也逐行发送，前端会拼接起来
                if line.strip():
                    yield f"{line}\n"
                    
        except Exception as e:
            error_message = f"与 Market Trade 服务通信时出错: {e}"
            print(f"❌ {error_message}")
            import traceback
            traceback.print_exc()
            yield f"{error_message}\n"
    
    return Response(stream_with_context(stream_response()), mimetype="text/plain")

@app.route("/download/<filename>")
def download_file(filename):
    """提供文件下载服务。此功能与Agent无关，保持不变。"""
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
    print("🚀 启动 PolyAgent API Gateway...")
    if not (config.OPENAI_API_KEY and "sk-" in config.OPENAI_API_KEY):
        print("⚠️ 警告: OpenAI API 密钥未配置或格式不正确。")
        print("   (此配置现在由后台服务使用，但网关仍可进行检查)")
    
    print(f"🔗 服务地址: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"🔧 调试模式: {'开启' if config.FLASK_DEBUG else '关闭'}")
    print("   此网关将请求路由到后台的A2A Agent服务。")
    print("   请确保后台服务已启动！")
    print("=" * 60)
    
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG)