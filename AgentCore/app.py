# app.py
import time
import threading
import queue
import sys
import asyncio
from flask import Flask, request, stream_with_context, Response, jsonify
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import agent
from AgentCore.crypto_society import get_crypto_agent_data
from AgentCore.Society.market_trade import AgentManager
from AgentCore.Society.market_monitor import run_crypto_insight_agent
from AgentCore.config import get_config

# 获取配置
config = get_config()

app = Flask(__name__)

# 跨域
CORS(app)

class StreamToQueue:
    def __init__(self, q):
        self.q = q
    
    def write(self, msg):
        if msg:
            self.q.put(msg)
    
    def flush(self):
        pass

def get_market_trade_response(message):
    """处理market trade agent的流式响应"""
    q = queue.Queue()
    
    def worker():
        sys_stdout = sys.stdout
        sys.stdout = StreamToQueue(q)
        try:
            # 创建AgentManager实例并处理用户输入
            agent_manager = AgentManager()
            response = agent_manager.iotex_agent.step(message)
            
            # 输出agent的回复
            if response.msgs:
                content = response.msgs[0].content
                print(content)
            
        except Exception as e:
            error_msg = f"{config.ERROR_MESSAGES['market_trade_error']}: {str(e)}"
            print(error_msg)
        finally:
            sys.stdout = sys_stdout
            q.put(None)  # 结束标志
    
    threading.Thread(target=worker, daemon=True).start()
    
    while True:
        msg = q.get()
        if msg is None:
            break
        yield msg

def get_market_monitor_response(message):
    """处理market monitor agent的流式响应"""
    q = queue.Queue()
    
    def worker():
        sys_stdout = sys.stdout
        sys.stdout = StreamToQueue(q)
        try:
            # 调用market monitor agent
            result = run_crypto_insight_agent(message)
            print(result)
            
        except Exception as e:
            error_msg = f"{config.ERROR_MESSAGES['market_monitor_error']}: {str(e)}"
            print(error_msg)
        finally:
            sys.stdout = sys_stdout
            q.put(None)  # 结束标志
    
    threading.Thread(target=worker, daemon=True).start()
    
    while True:
        msg = q.get()
        if msg is None:
            break
        yield msg

@app.route("/polyPost", methods=["POST"])
def run_agent():
    """原有的接口，保持兼容性"""
    data = request.get_json()
    message = data.get('message', '') if data else ''
    return Response(stream_with_context(get_crypto_agent_data(message)), mimetype='text/plain')

@app.route("/market-trade", methods=["POST"])
def market_trade():
    """Market Trade Agent 接口 - 处理IoTeX区块链交易相关请求"""
    data = request.get_json()
    message = data.get('message', '') if data else ''
    return Response(stream_with_context(get_market_trade_response(message)), mimetype='text/plain')

@app.route("/market-monitor", methods=["POST"])
def market_monitor():
    """Market Monitor Agent 接口 - 处理加密货币市场监控相关请求"""
    data = request.get_json()
    message = data.get('message', '') if data else ''
    return Response(stream_with_context(get_market_monitor_response(message)), mimetype='text/plain')

@app.route("/agents/status", methods=["GET"])
def agents_status():
    """检查两个agent的状态"""
    try:
        # 尝试初始化AgentManager
        agent_manager = AgentManager()
        market_trade_status = "正常" if agent_manager.iotex_agent else "异常"
    except Exception as e:
        market_trade_status = f"错误: {str(e)}"
    
    try:
        # 测试market monitor函数是否可用
        test_result = run_crypto_insight_agent("测试")
        market_monitor_status = "正常" if test_result else "异常"
    except Exception as e:
        market_monitor_status = f"错误: {str(e)}"
    
    return jsonify({
        "market_trade": market_trade_status,
        "market_monitor": market_monitor_status
    })

if __name__ == "__main__":
    print("=" * 50)
    print("PolyAgent Web3 AI Agent API Server")
    print("=" * 50)
    print(f"启动配置: {config.__name__}")
    print(f"服务地址: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print("\n可用的API端点:")
    for name, url in config.get_api_endpoints().items():
        print(f"  {name}: {url}")
    print("\n配置验证:", "✓ 通过" if config.validate_config() else "✗ 失败")
    print("=" * 50)
    
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG)
