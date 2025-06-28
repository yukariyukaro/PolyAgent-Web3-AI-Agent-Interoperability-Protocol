from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import traceback
from datetime import datetime
import logging
import threading
import time
import re
from typing import Dict, Any, Optional, List
from enum import Enum
import asyncio
import nest_asyncio

# 设置nest_asyncio以支持嵌套事件循环
nest_asyncio.apply()

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 导入所有Agent的业务逻辑类
try:
    from AgentCore.Society.user_agent_a2a import AmazonServiceManager as UserServiceManager
    from AgentCore.Society.payment import AlipayOrderService
    # 导入正确的Amazon Agent (文件名有空格需要特殊处理)
    import importlib.util
    amazon_agent_path = os.path.join(os.path.dirname(__file__), "AgentCore", "Society", "a2a amazon agent.py")
    spec = importlib.util.spec_from_file_location("amazon_agent", amazon_agent_path)
    amazon_agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(amazon_agent_module)
    AmazonShoppingServiceManager = amazon_agent_module.AmazonShoppingServiceManager
    ThinkingMode = amazon_agent_module.ThinkingMode
    ALL_AGENTS_AVAILABLE = True
    print("✅ 所有Agent模块导入成功")
except ImportError as e:
    print(f"⚠️ Agent导入失败: {e}")
    ALL_AGENTS_AVAILABLE = False
    UserServiceManager = None
    AlipayOrderService = None
    AmazonShoppingServiceManager = None
    ThinkingMode = None

try:
    from python_a2a import A2AClient
    A2A_CLIENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ A2A客户端导入失败: {e}")
    A2A_CLIENT_AVAILABLE = False

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

class WorkflowState(Enum):
    """固定工作流状态枚举"""
    INITIAL = "initial"                           # 等待用户购买意图输入
    PRODUCT_SEARCH = "product_search"             # User Agent搜索商品中
    PRODUCT_SELECTION = "product_selection"       # 等待用户选择商品
    PAYMENT_CREATION = "payment_creation"         # Payment Agent创建订单中  
    PAYMENT_CONFIRMATION = "payment_confirmation" # 等待用户确认支付
    PAYMENT_VERIFICATION = "payment_verification" # Payment Agent验证支付状态
    ADDRESS_COLLECTION = "address_collection"     # Amazon Agent收集地址信息
    ORDER_PROCESSING = "order_processing"         # Amazon Agent处理最终订单
    WORKFLOW_COMPLETE = "workflow_complete"       # 工作流完成

class FixedWorkflowOrchestrator:
    """固定工作流编排器 - 实现多Agent协作的固定购物流程"""
    
    def __init__(self):
        self.user_agents = {}       # User Agent实例
        self.payment_agents = {}    # Payment Agent实例
        self.amazon_agents = {}     # Amazon Agent实例
        
        # A2A Agent配置（如果A2A服务可用）
        self.a2a_config = {
            "user_agent": {"url": "http://localhost:5011", "available": False},
            "payment_agent": {"url": "http://localhost:5005", "available": False},
            "amazon_agent": {"url": "http://localhost:5012", "available": False}
        }
        
        # 启动A2A服务器检查线程
        self._check_a2a_services()
    
    def _check_a2a_services(self):
        """检查A2A服务是否可用"""
        if not A2A_CLIENT_AVAILABLE:
            return
            
        def check_service(agent_type: str, url: str):
            try:
                client = A2AClient(url)
                response = client.ask("health check")
                if response:
                    self.a2a_config[agent_type]["available"] = True
                    logger.info(f"✅ {agent_type} A2A服务可用: {url}")
            except Exception as e:
                logger.warning(f"⚠️ {agent_type} A2A服务不可用: {e}")
        
        # 并发检查所有A2A服务
        threads = []
        for agent_type, config in self.a2a_config.items():
            thread = threading.Thread(target=check_service, args=(agent_type, config["url"]))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # 等待检查完成
        for thread in threads:
            thread.join(timeout=5)
    
    def get_user_agent(self, user_id: str = "default_user", session_id: str = None):
        """获取或创建User Agent实例"""
        agent_key = f"{user_id}:{session_id}" if session_id else f"{user_id}:default"
        
        if agent_key not in self.user_agents:
            try:
                if not ALL_AGENTS_AVAILABLE or UserServiceManager is None:
                    logger.error("❌ User Agent类未正确导入")
                    return None
                    
                self.user_agents[agent_key] = UserServiceManager()
                logger.info(f"🤖 创建User Agent实例: {agent_key}")
            except Exception as e:
                logger.error(f"❌ 创建User Agent失败: {e}")
                return None
                
        return self.user_agents[agent_key]
    
    def get_payment_agent(self, user_id: str = "default_user", session_id: str = None):
        """获取或创建Payment Agent实例"""
        agent_key = f"{user_id}:{session_id}" if session_id else f"{user_id}:default"
        
        if agent_key not in self.payment_agents:
            try:
                if not ALL_AGENTS_AVAILABLE or AlipayOrderService is None:
                    logger.error("❌ Payment Agent类未正确导入")
                    return None
                    
                self.payment_agents[agent_key] = AlipayOrderService()
                logger.info(f"💳 创建Payment Agent实例: {agent_key}")
            except Exception as e:
                logger.error(f"❌ 创建Payment Agent失败: {e}")
                return None
                
        return self.payment_agents[agent_key]
    
    def get_amazon_agent(self, user_id: str = "default_user", session_id: str = None):
        """获取或创建Amazon Agent实例"""
        agent_key = f"{user_id}:{session_id}" if session_id else f"{user_id}:default"
        
        if agent_key not in self.amazon_agents:
            try:
                if not ALL_AGENTS_AVAILABLE or AmazonShoppingServiceManager is None or ThinkingMode is None:
                    logger.error("❌ Amazon Agent类未正确导入")
                    return None
                    
                self.amazon_agents[agent_key] = AmazonShoppingServiceManager(
                    thinking_mode=ThinkingMode.AUTO,
                    user_id=user_id,
                    session_id=session_id
                )
                logger.info(f"🛒 创建Amazon Agent实例: {agent_key}")
            except Exception as e:
                logger.error(f"❌ 创建Amazon Agent失败: {e}")
                return None
                
        return self.amazon_agents[agent_key]
    
    def _call_agent_a2a_or_local(self, agent_type: str, message: str, user_id: str, session_id: str) -> str:
        """调用Agent（优先A2A，降级到本地）"""
        try:
            # 尝试A2A调用
            if self.a2a_config[agent_type]["available"]:
                client = A2AClient(self.a2a_config[agent_type]["url"])
                response = client.ask(message)
                if response:
                    logger.info(f"✅ {agent_type} A2A调用成功")
                    return response
                    
            # 降级到本地Agent
            logger.info(f"🔄 {agent_type} 降级到本地调用")
            
            if agent_type == "user_agent":
                agent = self.get_user_agent(user_id, session_id)
                if agent:
                    # User Agent的autonomous_purchase方法是异步的
                    result = asyncio.run(agent.autonomous_purchase(message))
                    return result.get("response", "User Agent处理完成")
                    
            elif agent_type == "payment_agent":
                agent = self.get_payment_agent(user_id, session_id)
                if agent:
                    result = asyncio.run(agent.run_alipay_query(message))
                    return result.get("response_content", "Payment Agent处理完成")
                    
            elif agent_type == "amazon_agent":
                agent = self.get_amazon_agent(user_id, session_id)
                if agent:
                    return agent.process_request(message)
            
            return f"{agent_type}服务暂时不可用"
            
        except Exception as e:
            logger.error(f"❌ 调用{agent_type}失败: {e}")
            return f"{agent_type}调用失败: {str(e)}"
    
    def initialize_session_state(self, session_state: Dict[str, Any]):
        """初始化会话状态"""
        if 'workflow_state' not in session_state:
            session_state.update({
                'workflow_state': WorkflowState.INITIAL.value,
                'user_intent': '',
                'search_results': '',
                'selected_product': {},
                'payment_order': {},
                'payment_status': '',
                'user_address': {},
                'final_order': {},
                'conversation_history': []
            })
    
    def handle_initial_state(self, user_input: str, session_state: Dict[str, Any], user_id: str, session_id: str) -> Dict[str, Any]:
        """处理初始状态 - 等待用户购买意图"""
        logger.info("🔄 处理初始状态 - 用户购买意图分析")
        
        # 检查是否包含购买意图
        purchase_keywords = ["买", "购买", "下单", "订购", "want", "buy", "purchase", "order"]
        if any(keyword in user_input.lower() for keyword in purchase_keywords):
            # 有购买意图，转到商品搜索状态
            session_state['user_intent'] = user_input
            session_state['workflow_state'] = WorkflowState.PRODUCT_SEARCH.value
            
            # 调用User Agent进行商品搜索
            response = self._call_agent_a2a_or_local("user_agent", user_input, user_id, session_id)
            
            # 如果搜索成功，更新状态
            if "error" not in response.lower() and "失败" not in response:
                session_state['search_results'] = response
                session_state['workflow_state'] = WorkflowState.PRODUCT_SELECTION.value
                
            return {
                "success": True,
                "response": response,
                "workflow_state": session_state['workflow_state'],
                "next_action": "请选择您想要的商品，说明商品编号或名称"
            }
        else:
            # 没有购买意图，让User Agent自由回复
            response = self._call_agent_a2a_or_local("user_agent", user_input, user_id, session_id)
            return {
                "success": True,
                "response": response,
                "workflow_state": session_state['workflow_state'],
                "next_action": "请告诉我您想购买什么商品"
            }
    
    def handle_product_selection(self, user_input: str, session_state: Dict[str, Any], user_id: str, session_id: str) -> Dict[str, Any]:
        """处理商品选择状态"""
        logger.info("🔄 处理商品选择状态")
        
        # 检查用户是否确认购买
        confirm_keywords = ["确认", "买", "选择", "要", "confirm", "yes", "选"]
        
        if any(keyword in user_input.lower() for keyword in confirm_keywords):
            # 用户确认购买，提取商品信息并创建支付订单
            session_state['workflow_state'] = WorkflowState.PAYMENT_CREATION.value
            
            # 构造支付请求消息，包含用户选择和搜索结果
            payment_message = f"""用户确认购买决定：{user_input}

之前的商品搜索结果：
{session_state.get('search_results', '')}

请为用户选择的商品创建支付宝支付订单。"""
            
            # 调用Payment Agent创建订单
            response = self._call_agent_a2a_or_local("payment_agent", payment_message, user_id, session_id)
            
            # 保存选择的商品信息和支付订单
            session_state['selected_product'] = {'selection': user_input}
            session_state['payment_order'] = response
            session_state['workflow_state'] = WorkflowState.PAYMENT_CONFIRMATION.value
            
            return {
                "success": True,
                "response": response,
                "workflow_state": session_state['workflow_state'],
                "next_action": "请确认支付订单信息"
            }
        else:
            # 用户没有确认购买，让User Agent处理
            response = self._call_agent_a2a_or_local("user_agent", user_input, user_id, session_id)
            return {
                "success": True,
                "response": response,
                "workflow_state": session_state['workflow_state'],
                "next_action": "请选择您想要的商品"
            }
    
    def handle_payment_confirmation(self, user_input: str, session_state: Dict[str, Any], user_id: str, session_id: str) -> Dict[str, Any]:
        """处理支付确认状态"""
        logger.info("🔄 处理支付确认状态")
        
        # 检查用户是否确认支付
        payment_keywords = ["确认支付", "支付", "付款", "确认", "pay", "confirm"]
        
        if any(keyword in user_input.lower() for keyword in payment_keywords):
            # 用户确认支付，转到支付验证状态
            session_state['workflow_state'] = WorkflowState.PAYMENT_VERIFICATION.value
            
            # 调用Payment Agent查询支付状态
            verification_message = f"""用户确认支付：{user_input}

请查询以下订单的支付状态：
{session_state.get('payment_order', '')}

请使用MCP工具查询实际的支付状态。"""
            
            response = self._call_agent_a2a_or_local("payment_agent", verification_message, user_id, session_id)
            session_state['payment_status'] = response
            
            # 检查支付是否成功
            if "成功" in response or "success" in response.lower() or "completed" in response.lower():
                # 支付成功，转到地址收集状态
                session_state['workflow_state'] = WorkflowState.ADDRESS_COLLECTION.value
                
                # 准备Amazon Agent的地址收集请求
                address_message = f"""支付已完成，请收集用户的完整地址信息以便处理订单：

用户购买商品：{session_state.get('selected_product', {})}
支付订单信息：{session_state.get('payment_order', '')}

请向用户收集完整的收货地址信息（包括姓名、地址、城市、州/省、国家、邮编）。"""
                
                amazon_response = self._call_agent_a2a_or_local("amazon_agent", address_message, user_id, session_id)
                
                return {
                    "success": True,
                    "response": f"{response}\n\n{amazon_response}",
                    "workflow_state": session_state['workflow_state'],
                    "next_action": "请提供完整的收货地址信息"
                }
            else:
                # 支付失败或待处理
                return {
                    "success": False,
                    "response": response,
                    "workflow_state": session_state['workflow_state'],
                    "next_action": "请检查支付状态或重新支付"
                }
        else:
            # 用户没有确认支付，让Payment Agent处理
            response = self._call_agent_a2a_or_local("payment_agent", user_input, user_id, session_id)
            return {
                "success": True,
                "response": response,
                "workflow_state": session_state['workflow_state'],
                "next_action": "请确认支付订单"
            }
    
    def handle_address_collection(self, user_input: str, session_state: Dict[str, Any], user_id: str, session_id: str) -> Dict[str, Any]:
        """处理地址收集状态"""
        logger.info("🔄 处理地址收集状态")
        
        # 调用Amazon Agent处理地址输入
        address_message = f"""用户提供的地址信息：{user_input}

请验证地址信息是否完整，如果完整则进入一键支付流程：

已选商品：{session_state.get('selected_product', {})}
支付订单：{session_state.get('payment_order', '')}
支付状态：{session_state.get('payment_status', '')}

如果地址信息完整，请使用MCP工具进行Amazon一键支付流程。"""
        
        response = self._call_agent_a2a_or_local("amazon_agent", address_message, user_id, session_id)
        
        # 检查是否收集完整或进入订单处理
        if "完整" in response or "一键支付" in response or "订单" in response:
            session_state['user_address'] = user_input
            session_state['workflow_state'] = WorkflowState.ORDER_PROCESSING.value
            
            return {
                "success": True,
                "response": response,
                "workflow_state": session_state['workflow_state'],
                "next_action": "正在处理您的订单..."
            }
        else:
            # 地址信息不完整，继续收集
            return {
                "success": True,
                "response": response,
                "workflow_state": session_state['workflow_state'],
                "next_action": "请提供完整的地址信息"
            }
    
    def handle_order_processing(self, user_input: str, session_state: Dict[str, Any], user_id: str, session_id: str) -> Dict[str, Any]:
        """处理订单处理状态"""
        logger.info("🔄 处理订单处理状态")
        
        # 调用Amazon Agent完成最终订单处理
        final_message = f"""请完成最终的订单处理和确认：

用户消息：{user_input}
选择商品：{session_state.get('selected_product', {})}
支付订单：{session_state.get('payment_order', '')}
收货地址：{session_state.get('user_address', '')}
支付状态：{session_state.get('payment_status', '')}

请使用MCP工具完成Amazon订单的最终处理并返回订单确认信息。"""
        
        response = self._call_agent_a2a_or_local("amazon_agent", final_message, user_id, session_id)
        
        # 保存最终订单信息并完成工作流
        session_state['final_order'] = response
        session_state['workflow_state'] = WorkflowState.WORKFLOW_COMPLETE.value
        
        return {
            "success": True,
            "response": response,
            "workflow_state": session_state['workflow_state'],
            "next_action": "订单处理完成！您可以开始新的购物流程。"
        }
    
    def handle_workflow_complete(self, user_input: str, session_state: Dict[str, Any], user_id: str, session_id: str) -> Dict[str, Any]:
        """处理工作流完成状态"""
        logger.info("🔄 处理工作流完成状态")
        
        # 检查是否要开始新的购买流程
        restart_keywords = ["新", "重新", "再次", "开始", "new", "restart", "again"]
        
        if any(keyword in user_input.lower() for keyword in restart_keywords):
            # 重置工作流状态
            session_state.update({
                'workflow_state': WorkflowState.INITIAL.value,
                'user_intent': '',
                'search_results': '',
                'selected_product': {},
                'payment_order': {},
                'payment_status': '',
                'user_address': {},
                'final_order': {}
            })
            
            response = self._call_agent_a2a_or_local("user_agent", user_input, user_id, session_id)
            
            return {
                "success": True,
                "response": f"新的购物流程已开始！\n\n{response}",
                "workflow_state": session_state['workflow_state'],
                "next_action": "请告诉我您想购买什么商品"
            }
        else:
            # 提供订单查询或其他服务
            response = self._call_agent_a2a_or_local("user_agent", user_input, user_id, session_id)
            
            return {
                "success": True,
                "response": response,
                "workflow_state": session_state['workflow_state'],
                "next_action": "您可以查询订单状态，或说'开始新购物'进行新的购买"
            }
    
    def process_workflow(self, user_input: str, user_id: str = "default_user", session_id: str = None) -> Dict[str, Any]:
        """处理工作流的主入口"""
        try:
            # 创建或获取会话状态
            session_key = f"{user_id}:{session_id}" if session_id else f"{user_id}:default"
            
            # 模拟会话状态存储（实际应用中应该使用Redis或数据库）
            if not hasattr(self, 'session_states'):
                self.session_states = {}
            
            if session_key not in self.session_states:
                self.session_states[session_key] = {}
                
            session_state = self.session_states[session_key]
            self.initialize_session_state(session_state)
            
            # 记录对话历史
            session_state['conversation_history'].append({
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'workflow_state': session_state['workflow_state']
            })
            
            # 根据当前工作流状态分发处理
            current_state = WorkflowState(session_state['workflow_state'])
            
            if current_state == WorkflowState.INITIAL:
                result = self.handle_initial_state(user_input, session_state, user_id, session_id)
            elif current_state == WorkflowState.PRODUCT_SELECTION:
                result = self.handle_product_selection(user_input, session_state, user_id, session_id)
            elif current_state == WorkflowState.PAYMENT_CONFIRMATION:
                result = self.handle_payment_confirmation(user_input, session_state, user_id, session_id)
            elif current_state == WorkflowState.ADDRESS_COLLECTION:
                result = self.handle_address_collection(user_input, session_state, user_id, session_id)
            elif current_state == WorkflowState.ORDER_PROCESSING:
                result = self.handle_order_processing(user_input, session_state, user_id, session_id)
            elif current_state == WorkflowState.WORKFLOW_COMPLETE:
                result = self.handle_workflow_complete(user_input, session_state, user_id, session_id)
            else:
                # 未知状态，重置到初始状态
                session_state['workflow_state'] = WorkflowState.INITIAL.value
                result = self.handle_initial_state(user_input, session_state, user_id, session_id)
            
            # 更新对话历史记录
            session_state['conversation_history'][-1]['response'] = result.get('response', '')
            session_state['conversation_history'][-1]['new_workflow_state'] = result.get('workflow_state', '')
            
            # 添加工作流信息到返回结果
            result.update({
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id,
                'user_id': user_id,
                'conversation_turn': len(session_state['conversation_history'])
            })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 工作流处理失败: {e}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "response": f"系统处理请求时遇到错误：{str(e)}",
                "workflow_state": WorkflowState.INITIAL.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 全局固定工作流编排器实例
workflow_orchestrator = FixedWorkflowOrchestrator()

@app.route('/')
def index():
    """主页"""
    return jsonify({
        'status': 'ok',
        'message': '固定工作流购物助手 - 多Agent协作系统',
        'version': '5.0-fixed-workflow',
        'system_type': 'Fixed Workflow Multi-Agent System',
        'workflow_states': [state.value for state in WorkflowState],
        'features': [
            '固定购物工作流程',
            'User Agent: 商品搜索和意图理解',
            'Payment Agent: 支付宝订单创建和验证',
            'Amazon Agent: 地址收集和一键支付',
            'A2A协议支持 + 本地降级',
            '真实LLM响应（无预设回复）',
            '状态驱动的用户体验'
        ],
        'workflow_flow': [
            '1. 用户输入购买意图 → User Agent搜索商品',
            '2. 用户选择商品 → Payment Agent创建订单',
            '3. 用户确认支付 → Payment Agent验证支付',
            '4. 支付成功 → Amazon Agent收集地址',
            '5. Amazon Agent执行一键支付完成订单'
        ],
        'endpoints': {
            'chat': '/api/chat',
            'health': '/api/health',
            'status': '/api/status'
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求 - 固定工作流版本"""
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

        # 获取用户ID和会话ID
        user_id = data.get('user_id', 'default_user')
        session_id = data.get('session_id', None)

        logger.info(f"🔍 [{datetime.now().strftime('%H:%M:%S')}] 固定工作流处理请求")
        logger.info(f"📝 用户: {user_id}, 会话: {session_id}, 消息: {user_message}")

        # 使用固定工作流编排器处理请求
        result = workflow_orchestrator.process_workflow(user_message, user_id, session_id)
        
        if result["success"]:
            logger.info(f"✅ [{datetime.now().strftime('%H:%M:%S')}] 工作流处理成功 - 状态: {result.get('workflow_state')}")
        else:
            logger.warning(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] 工作流处理失败")

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ [{datetime.now().strftime('%H:%M:%S')}] API错误: {e}")
        logger.error(f"🔍 详细错误信息: {traceback.format_exc()}")
        
        return jsonify({
            'success': False,
            'error': '固定工作流系统暂时不可用，请稍后重试',
            'error_type': 'server_error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查 - 检查所有Agent和工作流状态"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'system_type': 'Fixed Workflow Multi-Agent',
            'agents': {},
            'workflow_system': 'operational'
        }
        
        # 检查各个Agent的健康状态
        try:
            user_agent = workflow_orchestrator.get_user_agent()
            health_status['agents']['user_agent'] = {
                'status': 'healthy' if user_agent else 'unavailable',
                'a2a_available': workflow_orchestrator.a2a_config["user_agent"]["available"]
            }
        except Exception as e:
            health_status['agents']['user_agent'] = {'status': 'error', 'error': str(e)}
        
        try:
            payment_agent = workflow_orchestrator.get_payment_agent()
            health_status['agents']['payment_agent'] = {
                'status': 'healthy' if payment_agent else 'unavailable',
                'a2a_available': workflow_orchestrator.a2a_config["payment_agent"]["available"]
            }
        except Exception as e:
            health_status['agents']['payment_agent'] = {'status': 'error', 'error': str(e)}
        
        try:
            amazon_agent = workflow_orchestrator.get_amazon_agent()
            health_status['agents']['amazon_agent'] = {
                'status': 'healthy' if amazon_agent else 'unavailable',
                'a2a_available': workflow_orchestrator.a2a_config["amazon_agent"]["available"]
            }
        except Exception as e:
            health_status['agents']['amazon_agent'] = {'status': 'error', 'error': str(e)}
        
        # 判断整体健康状态
        agent_statuses = [agent['status'] for agent in health_status['agents'].values()]
        if 'healthy' not in agent_statuses:
            health_status['status'] = 'unhealthy'
            return jsonify(health_status), 503
        elif 'error' in agent_statuses or 'unavailable' in agent_statuses:
            health_status['status'] = 'degraded'
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取详细的服务状态"""
    try:
        status = {
            'timestamp': datetime.now().isoformat(),
            'system_type': 'Fixed Workflow Multi-Agent Orchestrator',
            'version': '5.0-fixed-workflow',
            'total_agents': {
                'user_agents': len(workflow_orchestrator.user_agents),
                'payment_agents': len(workflow_orchestrator.payment_agents),
                'amazon_agents': len(workflow_orchestrator.amazon_agents)
            },
            'a2a_services': workflow_orchestrator.a2a_config,
            'workflow_states': [state.value for state in WorkflowState],
            'active_sessions': len(getattr(workflow_orchestrator, 'session_states', {})),
            'capabilities': {
                'fixed_workflow': True,
                'real_llm_responses': True,
                'a2a_communication': True,
                'local_fallback': True,
                'state_management': True,
                'multi_session_support': True
            }
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"❌ 获取状态失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': '请求的资源不存在',
        'available_endpoints': ['/api/chat', '/api/health', '/api/status']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '服务器内部错误，请稍后重试',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    print("🚀 启动固定工作流购物助手服务...")
    print("🔄 工作流程:")
    print("   1️⃣ 用户购买意图输入 → User Agent商品搜索")
    print("   2️⃣ 用户选择商品 → Payment Agent创建订单")
    print("   3️⃣ 用户确认支付 → Payment Agent验证支付状态")
    print("   4️⃣ 支付成功 → Amazon Agent收集地址信息")
    print("   5️⃣ Amazon Agent执行一键支付完成订单")
    print()
    print("🤖 Agent协作:")
    print("   • User Agent: 意图理解、商品搜索、购买决策")
    print("   • Payment Agent: 订单创建、支付验证、状态查询")
    print("   • Amazon Agent: 地址收集、一键支付、订单处理")
    print()
    print("🔧 系统特性:")
    print("   • 固定工作流状态管理")
    print("   • 真实LLM响应（无预设回复）")
    print("   • A2A协议 + 本地降级")
    print("   • 多用户多会话支持")
    print()
    print("🌐 访问地址: http://localhost:5000")
    print("📡 主要API: POST /api/chat")
    print()
    print("💡 使用示例:")
    print("   curl -X POST http://localhost:5000/api/chat \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"message\":\"我想买iPhone 15\",\"user_id\":\"user123\"}'")
    
    logger.info("🚀 固定工作流购物助手服务启动")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True  # 启用多线程支持异步调用和A2A通信
    ) 