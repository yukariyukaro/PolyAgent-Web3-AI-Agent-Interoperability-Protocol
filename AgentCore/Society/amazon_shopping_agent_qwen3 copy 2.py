#!/usr/bin/env python3
"""
Amazon购物Agent - Qwen3增强版 (重构)
支持ModelScope Qwen3 API + CAMEL MCP工具集成
修复：使用API调用而非本地模型，正确的MCP远程调用
"""

import os
import asyncio
import traceback
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple

# 设置环境变量（必须在导入ModelScope之前）
os.environ['MODELSCOPE_SDK_TOKEN'] = '9d3aed4d-eca1-4e0c-9805-cb923ccbbf21'

# CAMEL框架导入（用于MCP工具和API模型）
try:
    from camel.agents import ChatAgent
    from camel.toolkits import MCPToolkit
    from camel.models import ModelFactory
    from camel.types import ModelPlatformType, ModelType
    from camel.messages import BaseMessage
    from camel.types import RoleType
    CAMEL_AVAILABLE = True
    print("✅ CAMEL框架导入成功")
except ImportError as e:
    print(f"⚠️ CAMEL框架导入失败: {e}")
    CAMEL_AVAILABLE = False

# 项目配置导入
try:
    from AgentCore.config import config
except ImportError:
    print("⚠️ 配置文件导入失败，使用默认配置")
    config = None

class ShoppingState(Enum):
    """购物状态枚举"""
    BROWSING = "browsing"           # 浏览商品
    SELECTED = "selected"           # 已选择商品
    COLLECTING_INFO = "collecting_info"  # 收集用户信息
    ORDERING = "ordering"           # 创建订单
    PAYING = "paying"              # 支付处理
    COMPLETED = "completed"        # 完成购买
    TRACKING = "tracking"          # 订单追踪

class ThinkingMode(Enum):
    """思考模式配置"""
    ENABLED = "enabled"     # 启用思考模式（复杂推理）
    DISABLED = "disabled"   # 禁用思考模式（快速响应）
    AUTO = "auto"          # 自动切换（根据任务复杂度）

@dataclass
class UserInfo:
    """用户信息数据结构"""
    full_name: str = ""
    email: str = ""
    shipping_address: Dict[str, str] = None
    
    def __post_init__(self):
        if self.shipping_address is None:
            self.shipping_address = {
                "full_name": "",
                "address": "",
                "city": "",
                "state": "",
                "country": "",
                "postal_code": ""
            }
    
    def is_complete(self) -> bool:
        """检查用户信息是否完整"""
        return (
            bool(self.full_name and self.email) and
            all(self.shipping_address.values())
        )

@dataclass
class ProductInfo:
    """商品信息数据结构"""
    asin: str = ""
    title: str = ""
    url: str = ""
    price: str = ""
    rating: str = ""
    reviews_count: str = ""
    image_url: str = ""
    description: str = ""
    availability: str = ""
    
    def to_display_dict(self) -> Dict[str, Any]:
        """转换为显示格式"""
        return {
            "商品标题": self.title,
            "价格": self.price,
            "评分": self.rating,
            "评论数": self.reviews_count,
            "可用性": self.availability,
            "商品链接": self.url
        }

@dataclass
class PaymentInfo:
    """支付信息数据结构"""
    order_id: str = ""
    payment_offers: Dict[str, Any] = None
    payment_status: str = "pending"
    external_id: str = ""
    payment_context_token: str = ""
    
    def __post_init__(self):
        if self.payment_offers is None:
            self.payment_offers = {}

@dataclass
class ConversationTurn:
    """对话轮次数据结构"""
    user_input: str
    ai_response: str
    timestamp: datetime
    shopping_state: ShoppingState
    tools_used: List[str]
    thinking_content: str = ""  # Qwen3思考内容

class ModelConfigManager:
    """Qwen3模型配置管理器"""
    
    @staticmethod
    def get_thinking_config(mode: ThinkingMode = ThinkingMode.AUTO) -> Dict[str, Any]:
        """获取思考模式配置"""
        if mode == ThinkingMode.ENABLED:
            # 思考模式：适用于复杂推理任务
            return {
                'temperature': 0.6,
                'top_p': 0.95,
                'top_k': 20,
                'do_sample': True,
                'max_new_tokens': 32768,
                'enable_thinking': True
            }
        elif mode == ThinkingMode.DISABLED:
            # 非思考模式：适用于快速响应
            return {
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 20,
                'do_sample': True,
                'max_new_tokens': 8192,
                'enable_thinking': False
            }
        else:  # AUTO模式
            # 平衡配置：根据任务自动调整
            return {
                'temperature': 0.65,
                'top_p': 0.9,
                'top_k': 20,
                'do_sample': True,
                'max_new_tokens': 16384,
                'enable_thinking': None  # 由系统自动决定
            }

class ConversationManager:
    """对话管理器 - 增强版"""
    
    def __init__(self, max_history: int = 10):
        self.conversation_history: List[ConversationTurn] = []
        self.max_history = max_history
        self.current_state = ShoppingState.BROWSING
        self.user_intent_history: List[str] = []
    
    def add_turn(self, user_input: str, ai_response: str, tools_used: List[str] = None, thinking_content: str = ""):
        """添加对话轮次"""
        turn = ConversationTurn(
            user_input=user_input,
            ai_response=ai_response,
            timestamp=datetime.now(),
            shopping_state=self.current_state,
            tools_used=tools_used or [],
            thinking_content=thinking_content
        )
        
        self.conversation_history.append(turn)
        
        # 保持历史记录在限制范围内
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def update_state(self, new_state: ShoppingState):
        """更新购物状态"""
        self.current_state = new_state
    
    def get_recent_context(self, turns: int = 3) -> str:
        """获取最近的对话上下文"""
        if not self.conversation_history:
            return ""
        
        recent_turns = self.conversation_history[-turns:]
        context_parts = [f"当前状态: {self.current_state.value}"]
        
        for turn in recent_turns:
            context_parts.append(f"用户: {turn.user_input}")
            if turn.thinking_content:
                context_parts.append(f"AI思考: {turn.thinking_content[:200]}...")
            context_parts.append(f"AI回复: {turn.ai_response[:300]}...")
            if turn.tools_used:
                context_parts.append(f"使用工具: {', '.join(turn.tools_used)}")
        
        return "\\n".join(context_parts)

class AmazonShoppingAgentQwen3:
    """
    Amazon购物Agent - Qwen3增强版 (重构)
    
    主要改进：
    1. 使用ModelScope API而非本地模型加载
    2. 正确的CAMEL MCP远程工具调用
    3. 保持原有的对话管理和状态追踪
    """
    
    def __init__(self, thinking_mode: ThinkingMode = ThinkingMode.AUTO):
        # 初始化基本参数
        self.thinking_mode = thinking_mode
        self._initialized = False
        
        # AI模型相关
        self.model = None
        self.chat_agent = None
        
        # MCP工具相关
        self.mcp_available = False
        self.mcp_tools = []
        
        # 组件初始化
        self.conversation_manager = ConversationManager()
        self.user_info = UserInfo()
        self.selected_product = ProductInfo()
        self.payment_info = PaymentInfo()
        
        # MCP配置路径
        self.mcp_config_path = os.path.join(
            os.path.dirname(__file__), "..", "Mcp", "amazon_fewsats_server.json"
        )
        
        # 设置系统提示词
        self._setup_system_messages()
        
        print("🎯 Amazon购物Agent初始化（使用API模式）")
    
    async def initialize(self):
        """异步初始化方法"""
        if self._initialized:
            return
        
        print("🔄 开始异步初始化...")
        
        # 初始化Qwen3 API模型
        await self._initialize_qwen3_api_model()
        
        # 测试MCP工具可用性
        await self._test_mcp_availability()
        
        self._initialized = True
        print("✅ Amazon购物Agent异步初始化完成")
    
    async def _initialize_qwen3_api_model(self):
        """初始化Qwen3 API模型（而非本地加载）"""
        if not CAMEL_AVAILABLE:
            print("⚠️ CAMEL框架不可用，跳过模型初始化")
            return
        
        try:
            print("🔄 尝试初始化Qwen3-32B API模型...")
            
            # 方案一：尝试Qwen3-32B（修复enable_thinking问题）
            try:
                from openai import OpenAI
                
                # 创建OpenAI客户端用于Qwen3-32B
                self.openai_client = OpenAI(
                    base_url='https://api-inference.modelscope.cn/v1/',
                    api_key='9d3aed4d-eca1-4e0c-9805-cb923ccbbf21'
                )
                
                # 测试Qwen3-32B API调用
                test_response = self.openai_client.chat.completions.create(
                    model='Qwen/Qwen3-32B',
                    messages=[{'role': 'user', 'content': '你好'}],
                    max_tokens=50,
                    temperature=0.2,
                    extra_body={'enable_thinking': False}  # 显式禁用thinking
                )
                
                print("✅ Qwen3-32B API直接调用成功")
                
                # 即使直接调用成功，也要创建CAMEL模型对象用于ChatAgent
                try:
                    self.model = ModelFactory.create(
                        model_platform=ModelPlatformType.MODELSCOPE,
                        model_type='Qwen/Qwen2.5-72B-Instruct',  # 使用兼容模型
                        model_config_dict={
                            'temperature': 0.2,
                            'max_tokens': 8192,
                        },
                        api_key='9d3aed4d-eca1-4e0c-9805-cb923ccbbf21'
                    )
                    print("✅ ChatAgent用CAMEL模型对象创建成功")
                    self.model_type = 'qwen3_camel_hybrid'  # 混合模式
                except Exception as camel_error:
                    print(f"⚠️ CAMEL模型对象创建失败，但可以使用直接API: {camel_error}")
                    self.model_type = 'qwen3_openai_only'  # 仅直接调用模式
                
            except Exception as e:
                print(f"⚠️ Qwen3-32B直接调用失败: {e}")
                print("🔄 切换到CAMEL ModelFactory备用方案...")
                
                # 方案二：使用CAMEL ModelFactory + 兼容模型
                self.model = ModelFactory.create(
                    model_platform=ModelPlatformType.MODELSCOPE,
                    model_type='Qwen/Qwen2.5-72B-Instruct',  # 备用兼容模型
                    model_config_dict={
                        'temperature': 0.2,
                        'max_tokens': 8192,
                    },
                    api_key='9d3aed4d-eca1-4e0c-9805-cb923ccbbf21'
                )
                self.model_type = 'camel_qwen25'  # 标记使用CAMEL框架
                print("✅ Qwen2.5-72B-Instruct备用模型初始化成功")
                
        except Exception as e:
            print(f"❌ 模型初始化失败: {e}")
            print("📝 详细错误信息:")
            traceback.print_exc()
            self.model = None
            self.openai_client = None
            self.model_type = None
    
    async def _test_mcp_availability(self) -> bool:
        """测试MCP服务可用性"""
        try:
            print("🔄 测试MCP服务可用性...")
            
            if not os.path.exists(self.mcp_config_path):
                print(f"⚠️ MCP配置文件不存在: {self.mcp_config_path}")
                return False
            
            # 快速测试MCP连接
            async with MCPToolkit(config_path=self.mcp_config_path) as mcp_toolkit:
                tools = mcp_toolkit.get_tools()
                if tools and len(tools) > 0:
                    self.mcp_available = True
                    self.mcp_tools = tools
                    print(f"✅ MCP服务可用，发现 {len(tools)} 个工具")
                    return True
                else:
                    print("⚠️ MCP服务连接成功但无可用工具")
                    return False
                    
        except Exception as e:
            print(f"❌ MCP服务不可用: {e}")
            self.mcp_available = False
            return False
    
    def _setup_system_messages(self):
        """设置系统提示词 - 完整版Amazon购物助手"""
        self.system_message = """
你是专业的Amazon购物助手，基于Qwen3模型，具备完整的商品搜索、购买和支付功能。你能帮助用户从搜索商品到完成购买的整个流程。

🎯 **核心使命**：
为用户提供完整的Amazon购物服务，包括商品搜索、比价分析、订单创建、支付处理和订单追踪。

🛠️ **可用MCP工具详解**：

## 🛒 Amazon MCP工具

### 1. amazon_search - 商品搜索
**功能**：在Amazon上搜索商品
**参数**：
- q (必需)：搜索关键词或产品ASIN
- domain (可选)：Amazon域名，默认amazon.com
**使用场景**：用户表达购买意图时立即调用
**示例调用**：用户说"我想买黑笔"→ 调用amazon_search(q="black pen")

### 2. amazon_get_payment_offers - 获取支付报价
**功能**：为选定商品生成支付报价信息
**参数**：
- product_url (必需)：Amazon商品链接
- shipping_address (必需)：收货地址对象
  ```json
  {
    "full_name": "收件人姓名",
    "address": "详细地址",
    "city": "城市",
    "state": "州/省",
    "country": "国家代码(如US)",
    "postal_code": "邮政编码"
  }
  ```
- user (必需)：用户信息对象
  ```json
  {
    "full_name": "用户姓名",
    "email": "邮箱地址"
  }
  ```
- asin (可选)：商品ASIN编号
- quantity (可选)：购买数量，默认1

### 3. pay_with_x402 - X402协议支付
**功能**：使用X402协议完成支付
**参数**：
- x_payment (必需)：X-PAYMENT头信息
- product_url (必需)：商品链接
- shipping_address (必需)：收货地址
- user (必需)：用户信息
- asin (可选)：商品ASIN
- quantity (可选)：数量

### 4. get_order_by_external_id - 通过外部ID查询订单
**功能**：根据外部订单ID查询订单状态
**参数**：
- external_id (必需)：外部订单ID

### 5. get_order_by_payment_token - 通过支付令牌查询订单
**功能**：根据支付上下文令牌查询订单
**参数**：
- payment_context_token (必需)：支付上下文令牌

### 6. get_user_orders - 获取用户所有订单
**功能**：查询当前用户的所有订单
**参数**：
- random_string (必需)：虚拟参数（无参数工具的技术要求，使用"check_orders"）

## 💳 Fewsats MCP工具

### 1. balance - 查询钱包余额
**功能**：获取用户钱包余额信息
**参数**：
- random_string (必需)：虚拟参数（使用"check_balance"）

### 2. payment_methods - 查询支付方式
**功能**：获取用户可用的支付方式列表
**参数**：
- random_string (必需)：虚拟参数（使用"check_methods"）

### 3. pay_offer - 支付报价
**功能**：支付指定的报价订单
**参数**：
- offer_id (必需)：报价ID字符串
- l402_offer (必需)：L402报价对象，包含：
  ```json
  {
    "offers": [
      {
        "id": "报价标识符",
        "amount": 金额数值,
        "currency": "货币代码",
        "description": "描述",
        "title": "标题"
      }
    ],
    "payment_context_token": "支付上下文令牌",
    "payment_request_url": "支付请求URL",
    "version": "API版本"
  }
  ```

### 4. payment_info - 查询支付详情
**功能**：获取特定支付的详细信息
**参数**：
- pid (必需)：支付ID
**注意**：如果状态为needs_review，用户需要到app.fewsats.com审批

### 5. billing_info - 查询账单信息
**功能**：获取用户的账单信息，也可作为收货地址使用
**参数**：
- random_string (必需)：虚拟参数（使用"get_billing"）

### 6. create_x402_payment_header - 创建X402支付头
**功能**：为X402协议创建支付头信息
**参数**：
- chain (必需)：区块链网络（如"base-sepolia"、"base"）
- x402_payload (必需)：X402载荷对象，包含：
  ```json
  {
    "accepts": ["接受的支付方式数组"],
    "error": "错误信息",
    "x402Version": "X402版本"
  }
  ```

🔄 **完整购买流程**：

### 阶段1：商品搜索与选择
1. **接收用户需求** → 立即调用 `amazon_search`
2. **展示搜索结果** → 提供详细的商品信息、价格、评分
3. **用户选择商品** → 记录product_url和相关信息

### 阶段2：用户信息收集
4. **收集用户基本信息**：
   - 姓名："请告诉我您的姓名"
   - 邮箱："请提供您的邮箱地址"
5. **收集收货地址**：
   - "请提供您的详细收货地址"
   - "请告诉我城市和州/省"
   - "请提供邮政编码"
   - "请确认国家（默认为US）"

### 阶段3：生成支付报价
6. **调用amazon_get_payment_offers** → 生成包含支付信息的报价

### 阶段4：执行支付
7. **调用pay_offer** → 使用从payment_offers获得的l402_offer数据
8. **处理支付结果** → 根据返回结果引导用户

### 阶段5：订单追踪
9. **查询订单状态** → 使用get_order_by_external_id或get_user_orders

💡 **智能参数收集策略**：

### 商品搜索优化
- 用户说"我想买X"时，直接调用amazon_search(q="X")
- 自动优化搜索词：中文→英文，通用词→具体词
- 例如："黑笔"→"black pen"，"手机"→"smartphone"

### 地址信息收集
- **分步骤收集**，避免一次性要求所有信息
- **使用自然对话**，不要表单式提问
- **智能验证**，检查地址格式的合理性
- **提供示例**，帮助用户理解格式要求

### 错误处理与重试
- **工具调用失败**：解释原因，提供替代方案
- **参数缺失**：明确指出缺少什么信息
- **用户拒绝**：尊重用户选择，提供其他选项

📋 **对话示例**：

**用户**："我想买一盒黑笔"
**AI**：我来为您搜索黑笔产品。*[调用amazon_search(q="black pen")]*
为您找到以下热销黑笔：
1. Paper Mate InkJoy 黑色中性笔 14支装 - $13.39 (4.8分)
2. FIOVER 0.5mm快干黑色中性笔 5支装 - $7.99 (4.6分)
请告诉我您对哪款感兴趣？

**用户**："我要第一款"
**AI**：好的，您选择了Paper Mate InkJoy黑笔。为了完成订单，我需要收集一些信息：
首先，请告诉我您的姓名？

**用户**："张三"
**AI**：谢谢张先生。请提供您的邮箱地址？

**用户**："zhangsan@email.com"
**AI**：请提供您的详细收货地址？

（继续收集地址信息，然后调用amazon_get_payment_offers，最后执行pay_offer）

🎯 **核心指导原则**：

1. **工具优先策略**：任何商品相关请求都要尝试使用工具
2. **完整流程执行**：确保从搜索到支付的每个步骤都完整执行
3. **智能参数管理**：通过对话自然收集必要参数
4. **用户体验优化**：保持对话流畅，避免技术术语
5. **错误优雅处理**：工具失败时提供清晰解释和替代方案
6. **状态追踪**：记住对话中的重要信息（选中商品、用户信息等）

🚨 **重要提醒**：
- **永远尝试使用工具**：不要因为担心参数不完整就跳过工具调用
- **分步收集信息**：通过多轮对话逐步完善参数
- **保持状态连续性**：记住之前收集的信息，避免重复询问
- **处理支付状态**：注意needs_review状态需要用户手动审批
- **错误信息要具体**：明确告诉用户缺少什么信息或发生了什么问题

你的目标是为用户提供流畅、完整、高效的Amazon购物体验！
"""
    
    # def _analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
    #     """分析用户意图 - 已废弃，改为让AI模型自主决定工具使用"""
    #     # 不再使用关键词判断，让AI模型自己决定是否使用工具
    #     pass
    
    async def _process_with_mcp_tools(self, user_input: str) -> Tuple[str, List[str]]:
        """使用MCP工具处理请求 - 修复为正确的远程调用"""
        tools_used = []
        
        if not self.mcp_available or not self.model:
            return "工具服务暂时不可用", tools_used
        
        try:
            print("🔍 使用CAMEL ChatAgent + MCP工具处理请求...")
            
            # 使用正确的CAMEL模式：ChatAgent + MCPToolkit
            async with MCPToolkit(config_path=self.mcp_config_path) as mcp_toolkit:
                # 创建带工具的ChatAgent
                chat_agent = ChatAgent(
                    system_message=self.system_message,
                    model=self.model,
                    token_limit=32768,
                    tools=mcp_toolkit.get_tools(),  # 使用MCP工具
                    output_language="zh"
                )
                
                print("🤖 ChatAgent正在处理用户请求...")
                
                # 使用ChatAgent.astep()进行对话和工具调用
                response = await chat_agent.astep(user_input)
                
                if response and response.msgs:
                    ai_response = response.msgs[0].content
                    
                    # 提取工具调用信息 - 修复：直接从response.info中获取工具调用记录
                    if hasattr(response, 'info') and response.info and 'tool_calls' in response.info:
                        # 从info中获取工具调用记录
                        tool_calls = response.info['tool_calls']
                        if tool_calls:
                            tools_used = [call.tool_name if hasattr(call, 'tool_name') else 'unknown' for call in tool_calls]
                        else:
                            tools_used = []
                    else:
                        tools_used = []
                    
                    print(f"🔧 MCP工具调用成功，使用了工具: {tools_used}")
                    return ai_response, tools_used
                else:
                    return "抱歉，我暂时无法处理您的请求。", tools_used
                    
        except Exception as e:
            print(f"❌ MCP工具处理失败: {e}")
            print(f"🔍 详细错误: {traceback.format_exc()}")
            return f"搜索服务遇到问题：{str(e)}", tools_used
    
    async def _generate_basic_response(self, user_input: str, context: str = "") -> Tuple[str, str]:
        """生成基础响应（不使用工具）"""
        try:
            if not self.model:
                return self._get_fallback_response(user_input), ""
            
            print("🤖 使用基础ChatAgent生成响应...")
            
            # 创建无工具的ChatAgent
            chat_agent = ChatAgent(
                system_message=self.system_message + f"\n\n对话上下文：{context}",
                model=self.model,
                token_limit=32768,
                tools=[],  # 无工具
                output_language="zh"
            )
            
            response = await chat_agent.astep(user_input)
            
            if response and response.msgs:
                return response.msgs[0].content, ""
            else:
                return self._get_fallback_response(user_input), ""
                
        except Exception as e:
            print(f"❌ 基础响应生成失败: {e}")
            return self._get_fallback_response(user_input), ""
    
    async def process_request(self, user_input: str) -> str:
        """处理用户请求 - 主入口"""
        try:
            # 确保已初始化
            await self.initialize()
            
            print(f"📝 处理用户请求: {user_input}")
            
            # 获取对话上下文
            context = self.conversation_manager.get_recent_context()
            
            # 优先尝试使用MCP工具，让AI模型自己决定是否使用工具
            if self.mcp_available:
                print("🔧 MCP工具可用，让AI模型决定是否使用工具...")
                # 使用MCP工具处理 - 让AI自主决定工具使用
                response, tools_used = await self._process_with_mcp_tools(user_input)
                thinking_content = ""
                
                # 如果MCP处理成功且有实际响应，使用MCP结果
                if response and response != "工具服务暂时不可用" and response != "抱歉，我暂时无法处理您的请求。":
                    print(f"✅ MCP工具处理成功，使用了工具: {tools_used}")
                else:
                    print("⚠️ MCP工具处理未成功，尝试基础响应...")
                    # MCP处理失败时，使用基础模型响应
                    response, thinking_content = await self._generate_basic_response(user_input, context)
                    tools_used = []
            else:
                print("❌ MCP工具不可用，使用基础模型响应...")
                # 使用基础模型响应
                response, thinking_content = await self._generate_basic_response(user_input, context)
                tools_used = []
            
            # 记录对话轮次
            self.conversation_manager.add_turn(
                user_input=user_input,
                ai_response=response,
                tools_used=tools_used,
                thinking_content=thinking_content
            )
            
            print(f"✅ 响应生成完成")
            return response
            
        except Exception as e:
            print(f"❌ 请求处理失败: {e}")
            print(f"🔍 详细错误: {traceback.format_exc()}")
            return self._get_fallback_response(user_input)
    
    def _get_fallback_response(self, user_input: str) -> str:
        """获取最终备用响应"""
        return "您好！我是Amazon购物助手，可以帮您搜索和购买Amazon商品。请告诉我您想要购买什么商品，我会为您搜索相关产品。"
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态 - 兼容方法"""
        return {
            "agent_type": "Amazon Shopping Agent Qwen3 (Refactored)",
            "version": "2.0.0",
            "thinking_mode": self.thinking_mode.value,
            "camel_available": CAMEL_AVAILABLE,
            "mcp_available": self.mcp_available,
            "qwen3_model_ready": self.model is not None,
            "mcp_tools_count": len(self.mcp_tools),
            "conversation_turns": len(self.conversation_manager.conversation_history),
            "current_state": self.conversation_manager.current_state.value
        }
    
    def get_shopping_state(self) -> Dict[str, Any]:
        """获取购物状态"""
        return {
            "current_state": self.conversation_manager.current_state.value,
            "user_info_complete": self.user_info.is_complete(),
            "product_selected": bool(self.selected_product.asin),
            "conversation_turns": len(self.conversation_manager.conversation_history),
            "mcp_available": self.mcp_available,
            "thinking_mode": self.thinking_mode.value
        }
    
    def get_conversation_history(self) -> List[ConversationTurn]:
        """获取对话历史"""
        return self.conversation_manager.conversation_history
    
    def clear_conversation_history(self):
        """清除对话历史"""
        self.conversation_manager.conversation_history.clear()
        print("🧹 对话历史已清除")
    
    async def cleanup(self):
        """清理资源"""
        print("🧹 清理Agent资源...")

# 异步测试函数
async def test_qwen3_agent():
    """测试Qwen3 Agent"""
    print("🧪 测试Amazon Shopping Agent Qwen3...")
    
    agent = AmazonShoppingAgentQwen3(ThinkingMode.AUTO)
    
    try:
        # 测试请求
        test_messages = [
            "你好",
            "我想买一个iPhone 15 Pro",
            "帮我搜索苹果手机"
        ]
        
        for message in test_messages:
            print(f"👤 用户: {message}")
            response = await agent.process_request(message)
            print("🤖 Assistant:", response)
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(test_qwen3_agent()) 