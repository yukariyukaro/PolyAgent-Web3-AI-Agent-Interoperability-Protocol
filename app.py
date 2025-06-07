import os
import sys
import threading
import queue
import asyncio
from flask import Flask, request, jsonify, Response, stream_with_context
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
class StreamToQueue:
    """一个辅助类，将标准输出重定向到队列，用于捕获Agent的打印输出。"""
    def __init__(self, q):
        self.q = q
    
    def write(self, msg):
        if msg:
            self.q.put(msg)
    
    def flush(self):
        pass

def stream_agent_response(agent_instance, user_message):
    """
    通用函数，用于执行Agent并流式返回其响应。
    它通过重定向stdout来捕获并流式传输CAMEL-AI库中的打印信息。
    """
    q = queue.Queue()
    
    def worker():
        original_stdout = sys.stdout
        sys.stdout = StreamToQueue(q)
        try:
            result = agent_instance.step(user_message)
            # 最终的 return 结果也放入队列
            q.put(result.msgs[0].content if result and result.msgs else "未能获取响应")
        except Exception as e:
            error_msg = f"--- AGENT_EXECUTION_ERROR ---\n处理请求时出错: {e}"
            print(error_msg)
        finally:
            sys.stdout = original_stdout
            q.put(None)  # 使用 None 作为流结束的信号

    threading.Thread(target=worker).start()

    while True:
        chunk = q.get()
        if chunk is None:
            break
        yield f"{chunk}\n"

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
        """专门为 MarketMonitorAgent 设计的流式响应生成器。"""
        q = queue.Queue()
        
        def worker():
            original_stdout = sys.stdout
            sys.stdout = StreamToQueue(q)
            try:
                # MarketMonitorAgent 使用 'run' 方法并直接返回字符串
                result = market_monitor.run(message)
                q.put(result)
            except Exception as e:
                error_msg = f"--- AGENT_EXECUTION_ERROR ---\n处理 Market Monitor 请求时出错: {e}"
                print(error_msg)
            finally:
                sys.stdout = original_stdout
                q.put(None)  # 流结束信号

        threading.Thread(target=worker).start()

        while True:
            chunk = q.get()
            if chunk is None:
                break
            yield f"{chunk}\n"

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
        q = queue.Queue()
        
        def worker():
            original_stdout = sys.stdout
            sys.stdout = StreamToQueue(q)
            try:
                # 直接让AI Agent处理用户消息，不进行文本过滤
                # 根据用户消息智能路由到不同的Agent功能
                
                # 检查是否是支付确认消息
                if "确认执行支付" in message or "确认支付" in message:
                    # 用户确认支付，调用支付确认处理方法
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(agent_manager.handle_payment_confirmation())
                    loop.close()
                    q.put(result)
                    
                elif any(keyword in message.lower() for keyword in ["支付", "付款", "购买", "订单", "创建", "查询", "状态"]):
                    # 支付相关请求，路由到支付宝Agent
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(agent_manager.run_alipay_query(message))
                    loop.close()
                    
                    # 调试：输出原始结果
                    print(f"🔍 支付宝原始响应: {result}")
                    
                    # 处理支付结果并格式化
                    if result and isinstance(result, str):
                        # 检查是否包含支付链接
                    import re
                        url_pattern = r'(https://[^\s\)\<\>\,\[\]]+)'
                        urls = re.findall(url_pattern, result)
                        
                        if urls:
                            payment_url = urls[0]
                            # 生成唯一按钮ID
                            import time
                            import random
                            button_id = f"btn_{int(time.time())}_{random.randint(1000, 9999)}"
                            
                            # 构建详细的支付信息展示
                            formatted_result = f"""💰 Payment Order Created Successfully!

<div class="payment-info-card">
    <div class="payment-card-header">
        <div class="payment-card-icon">📱</div>
        <div>
            <h3 class="payment-card-title">Payment Order Details</h3>
            
        </div>
    </div>
    
    <div class="payment-info-item">
        <div class="payment-info-label">Order ID</div>
        <div class="payment-info-value">ORDER20250606001</div>
    </div>
    
    <div class="payment-info-item">
        <div class="payment-info-label">Amount</div>
        <div class="payment-info-value amount">¥99.99</div>
        </div>
    
    <div class="payment-info-item">
        <div class="payment-info-label">Description</div>
        <div class="payment-info-value">Cryptocurrency Payment</div>
        </div>
    
    <div class="payment-info-item">
        <div class="payment-info-label">Status</div>
        <div class="payment-info-value">Pending Payment</div>
    </div>
    
    <div style="text-align: center; margin: 24px 0; padding-top: 16px; border-top: 1px solid rgba(0, 255, 209, 0.1);">
        <a href="#" onclick="showTransferForm('{button_id}'); return false;" class="confirm-btn-purple" id="{button_id}" style="
        display: inline-flex;
        align-items: center;
            gap: 12px;
            padding: 16px 32px;
            background: linear-gradient(135deg, #00FFD1 0%, #6C40F7 100%);
            color: white !important;
        text-decoration: none;
            border-radius: 12px;
            font-weight: 700 !important;
            font-size: 18px;
            box-shadow: 
                0 8px 24px rgba(0, 255, 209, 0.3),
                0 2px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(0, 255, 209, 0.5);
            min-width: 240px;
        justify-content: center;
            position: relative;
            overflow: hidden;
    ">
            确认
    </a>
</div>

    <div style="color: #A0A0B4; font-size: 14px; text-align: center; line-height: 1.5; margin-top: 16px;">
        🔒 安全支付 · 点击上方按钮完成支付<br>
        <span style="color: #6B7280; font-size: 12px;">支付成功后将自动进行代币转换</span>
    </div>
</div>

<details class="technical-details" style="
    margin-top: 24px;
    background: rgba(75, 85, 99, 0.05);
    border: 1px solid rgba(75, 85, 99, 0.2);
    border-radius: 12px;
    overflow: hidden;
">
    <summary style="
        color: #9CA3AF; 
        font-size: 16px; 
        font-weight: 500;
        cursor: pointer; 
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: all 0.2s ease;
        user-select: none;
    ">
        <span style="font-size: 18px;">🔧</span>
        <span>技术详情</span>
        <span style="margin-left: auto; font-size: 12px; opacity: 0.7;">(点击展开)</span>
    </summary>
    <div style="
        margin-top: 0;
        padding: 20px; 
        background: rgba(31, 31, 42, 0.8); 
        border-top: 1px solid rgba(75, 85, 99, 0.2);
        font-size: 14px; 
        color: #9CA3AF; 
        font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
        line-height: 1.6;
        white-space: pre-wrap;
        word-break: break-word;
    ">
        {result}
    </div>
</details>"""
                            q.put(formatted_result)
                        else:
                            # 没有支付链接，可能是查询结果或错误信息
                            formatted_result = f"""📊 支付查询结果：

<div style="
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05));
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin: 1rem 0;
    color: #E6E6ED;
    line-height: 1.6;
">
    {result.replace('交易状态:', '<br><strong style="color: #8B5CF6;">交易状态:</strong>').replace('交易金额:', '<br><strong style="color: #10B981;">交易金额:</strong>').replace('支付宝交易号:', '<br><strong style="color: #1677FF;">支付宝交易号:</strong>')}
</div>"""
                            q.put(formatted_result)
                    else:
                        # 处理空结果或非字符串结果
                        error_msg = f"""❌ 支付处理异常

<div style="
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 1rem 0;
    color: #E6E6ED;
">
    支付系统暂时无法响应，请稍后重试。<br>
    <small style="color: #9CA3AF;">错误详情: {str(result) if result else '无响应'}</small>
</div>"""
                        q.put(error_msg)
                    
                elif any(keyword in message.lower() for keyword in ["故事", "写", "创作", "生成"]):
                    # 故事创作相关请求，路由到故事Agent
                    response = agent_manager.story_agent.step(message)
                    if response and response.msgs:
                        q.put(response.msgs[0].content)
                    else:
                        q.put("未能生成故事内容")
                        
                    else:
                    # 其他请求，路由到IoTeX区块链Agent
                    response = agent_manager.iotex_agent.step(message)
                    if response and response.msgs:
                        q.put(response.msgs[0].content)
                    else:
                        q.put("未能处理您的请求")
                        
            except Exception as e:
                error_msg = f"处理请求时出错: {e}"
                q.put(error_msg)
            finally:
                sys.stdout = original_stdout
                q.put(None)  # 使用 None 作为流结束的信号

        threading.Thread(target=worker).start()

        while True:
            chunk = q.get()
            if chunk is None:
                break
            yield f"{chunk}\n"
    
    return Response(stream_with_context(stream_agent_response()), mimetype="text/plain")

@app.route("/payment/create", methods=["POST"])
def handle_payment_create():
    """步骤1: 创建支付订单"""
    if not agent_manager:
        return jsonify({"error": "Agent Manager 未成功初始化"}), 500
        
    def async_payment():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(agent_manager.run_alipay_query("支付"))
            yield f"🔄 正在处理您的支付请求\n\n"
            yield f"{result}\n\n"
            yield f"正在为您处理货币转换，请稍等片刻...\n"
            yield f"您的付款将自动转换为等值稳定币并发送给商家。\n"
        except Exception as e:
            yield f"抱歉，支付处理遇到问题: {str(e)}\n请稍后重试或联系客服。\n"
        finally:
            loop.close()
    
    return Response(stream_with_context(async_payment()), mimetype="text/plain")

@app.route("/payment/query", methods=["POST"])
def handle_payment_query():
    """步骤2: 查询支付状态"""
    if not agent_manager:
        return jsonify({"error": "Agent Manager 未成功初始化"}), 500
        
    def async_query():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(agent_manager.run_alipay_query("查询订单"))
            yield f"📊 支付状态查询结果\n\n"
            yield f"{result}\n\n"
            yield f"📊 当前订单处理进度：\n"
            yield f"✅ 支付宝付款 - 已确认\n"
            yield f"🔄 货币转换 - 处理中\n"
            yield f"⏳ 商家收款 - 准备中\n"
            yield f"⏳ 服务交付 - 等待中\n"
        except Exception as e:
            yield f"抱歉，暂时无法查询订单状态: {str(e)}\n请稍后重试。\n"
        finally:
            loop.close()
    
    return Response(stream_with_context(async_query()), mimetype="text/plain")

@app.route("/payment/allowance", methods=["POST"])
def handle_allowance_check():
    """步骤3: 查询ERC20代币授权额度"""
    if not agent_manager:
        return jsonify({"error": "Agent Manager 未成功初始化"}), 500
        
    def check_allowance():
        yield f"正在查询代币授权额度...\n\n"
        try:
            response = agent_manager.iotex_agent.step("帮我查询一下ERC20代币的授权额度。")
            if response and response.msgs:
                yield f"{response.msgs[0].content}\n"
            else:
                yield f"未能获取授权额度信息\n"
        except Exception as e:
            yield f"查询授权额度时出错: {str(e)}\n"
    
    return Response(stream_with_context(check_allowance()), mimetype="text/plain")

@app.route("/payment/approve", methods=["POST"])
def handle_token_approve():
    """步骤4: 授权ERC20代币"""
    if not agent_manager:
        return jsonify({"error": "Agent Manager 未成功初始化"}), 500
        
    def approve_tokens():
        yield f"正在执行代币授权...\n\n"
        try:
            response = agent_manager.iotex_agent.step("我想给0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE地址授权200个代币，请帮我执行该操作")
            if response and response.msgs:
                yield f"{response.msgs[0].content}\n\n"
                yield f"✅ 代币授权完成！\n"
                yield f"现在可以进行转账操作...\n"
            else:
                yield f"未能完成代币授权\n"
        except Exception as e:
            yield f"代币授权时出错: {str(e)}\n"
    
    return Response(stream_with_context(approve_tokens()), mimetype="text/plain")

@app.route("/payment/transfer", methods=["POST"])
def handle_token_transfer():
    """步骤5: 执行稳定币转账"""
    if not agent_manager:
        return jsonify({"error": "Agent Manager 未成功初始化"}), 500
        
    def transfer_tokens():
        yield f"正在执行稳定币转账...\n\n"
        try:
            response = agent_manager.iotex_agent.step("我想给0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE地址转账5个代币，请帮我执行该操作")
            if response and response.msgs:
                yield f"{response.msgs[0].content}\n\n"
                yield f"✅ 转账已完成！\n"
                yield f"📋 转账详情：\n"
                yield f"   • 金额: 5 USDT\n"
                yield f"   • 收款方: 0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE\n"
                yield f"   • 网络: IoTeX 测试网\n"
                yield f"   • 状态: 已确认\n\n"
                yield f"商家已收到您的付款，正在为您准备服务...\n"
            else:
                yield f"未能完成转账操作\n"
        except Exception as e:
            yield f"转账时出错: {str(e)}\n"
    
    return Response(stream_with_context(transfer_tokens()), mimetype="text/plain")

@app.route("/payment/story", methods=["POST"])
def handle_story_service():
    """步骤6: 提供故事服务"""
    if not agent_manager:
        return jsonify({"error": "Agent Manager 未成功初始化"}), 500
        
    data = request.json
    story_demand = data.get("story_demand", "勇士拯救公主")
    
    def create_story():
        yield f"🎉 您的定制故事已完成！\n\n"
        try:
            response = agent_manager.story_agent.step(f"我希望写一个{story_demand}的故事")
            if response and response.msgs:
                yield f"{response.msgs[0].content}\n\n"
                yield f"📋 订单完成摘要：\n"
                yield f"• 支付方式: 支付宝 ¥99.99\n"
                yield f"• 转换金额: 5 USDT\n"
                yield f"• 商家收款: 已到账\n"
                yield f"• 服务状态: 已交付\n\n"
                yield f"感谢您选择我们的服务！这就是未来支付的体验 - 您用熟悉的支付宝，商家收到数字货币，双方都很满意。\n\n"
                yield f"有任何问题请随时联系我们！\n"
            else:
                yield f"未能生成故事内容\n"
        except Exception as e:
            yield f"故事生成时出错: {str(e)}\n"
    
    return Response(stream_with_context(create_story()), mimetype="text/plain")

@app.route("/demo/payment-flow", methods=["GET"])
def get_demo_payment_flow():
    """获取演示用的支付流程步骤指导"""
    demo_flow = {
        "title": "🌐 跨境支付桥接演示流程",
        "description": "演示支付宝付款 → 稳定币转换 → 商家收款 → 服务交付的完整流程",
        "scenario": {
            "customer": "用户想购买定制故事服务，偏好支付宝付款",
            "merchant": "商家提供故事服务，偏好接收稳定币",
            "bridge": "使用区块链稳定币作为跨支付方式的桥梁"
        },
        "steps": [
            {
                "step": 1,
                "title": "创建支付订单",
                "endpoint": "/payment/create",
                "method": "POST",
                "description": "启动支付宝付款流程，创建订单"
            },
            {
                "step": 2,
                "title": "查询支付状态",
                "endpoint": "/payment/query",
                "method": "POST",
                "description": "查看支付状态和流程进度"
            },
            {
                "step": 3,
                "title": "查询授权额度",
                "endpoint": "/payment/allowance",
                "method": "POST",
                "description": "检查ERC20代币授权额度"
            },
            {
                "step": 4,
                "title": "授权代币使用",
                "endpoint": "/payment/approve",
                "method": "POST",
                "description": "授权代币进行转账操作"
            },
            {
                "step": 5,
                "title": "执行稳定币转账",
                "endpoint": "/payment/transfer",
                "method": "POST",
                "description": "执行稳定币转账给商家"
            },
            {
                "step": 6,
                "title": "获得定制服务",
                "endpoint": "/payment/story",
                "method": "POST",
                "description": "商家收款后提供定制故事服务"
            }
        ]
    }
    return jsonify(demo_flow)

@app.route("/demo/quick-test", methods=["POST"])
def handle_quick_demo():
    """快速演示模式：自动执行完整支付流程"""
    if not agent_manager:
        return jsonify({"error": "Agent Manager 未成功初始化"}), 500
    
    def quick_demo_flow():
        steps = [
            ("步骤 1/6: 创建支付订单", "支付"),
            ("步骤 2/6: 查询支付状态", "查询订单"),
            ("步骤 3/6: 检查授权额度", None),
            ("步骤 4/6: 授权代币", None),
            ("步骤 5/6: 执行转账", None),
            ("步骤 6/6: 提供服务", None)
        ]
        
        for i, (step_title, query) in enumerate(steps):
            yield f"\n{'='*50}\n{step_title}\n{'='*50}\n"
            
            try:
                if i == 0 or i == 1:  # 支付相关步骤
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(agent_manager.run_alipay_query(query))
                    yield f"{result}\n\n"
                    loop.close()
                elif i == 2:  # 查询授权额度
                    response = agent_manager.iotex_agent.step("帮我查询一下ERC20代币的授权额度。")
                    if response and response.msgs:
                        yield f"{response.msgs[0].content}\n\n"
                elif i == 3:  # 授权代币
                    response = agent_manager.iotex_agent.step("我想给0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE地址授权200个代币，请帮我执行该操作")
                    if response and response.msgs:
                        yield f"{response.msgs[0].content}\n\n"
                elif i == 4:  # 转账
                    response = agent_manager.iotex_agent.step("我想给0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE地址转账5个代币，请帮我执行该操作")
                    if response and response.msgs:
                        yield f"{response.msgs[0].content}\n\n"
                elif i == 5:  # 故事服务
                    response = agent_manager.story_agent.step("我希望写一个勇士拯救公主的故事")
                    if response and response.msgs:
                        yield f"{response.msgs[0].content}\n\n"
                
                yield "⏳ 等待 2 秒...\n"
                import time
                time.sleep(2)
            except Exception as e:
                yield f"❌ 执行错误: {e}\n"
        
        yield "\n🎉 完整演示流程结束！\n"
    
    return Response(stream_with_context(quick_demo_flow()), mimetype="text/plain")

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