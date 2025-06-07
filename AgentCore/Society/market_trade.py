from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from eth_account import Account
from string import Template

import sys
import os
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from AgentCore.Tools.iotextoken_toolkit import IotexTokenToolkit
from camel.toolkits import MCPToolkit
from camel.societies import RolePlaying
from AgentCore.config import config

from camel.types import (
    ModelPlatformType,
    ModelType,
    OpenAIBackendRole,
    RoleType,
    TaskType,
)

class AgentManager:
    def __init__(self):
        self.estnet_rpc = "https://babel-api.testnet.iotex.io"
        self.chain_id = 4690

        self.ERC20_ABI = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_spender", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_from", "type": "address"},
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transferFrom",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [
                    {"name": "_owner", "type": "address"},
                    {"name": "_spender", "type": "address"}
                ],
                "name": "allowance",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]

        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.MODELSCOPE,
            model_type='Qwen/Qwen2.5-72B-Instruct',
            model_config_dict={'temperature': 0.2},
            api_key='9d3aed4d-eca1-4e0c-9805-cb923ccbbf21',
        )

        self.iotex_agent = ChatAgent(
            system_message="""
            You are a professional IoTeX testnet blockchain assistant with the following capabilities:

            =================
            ✅ Query Functions
            =================
            1. Query account IOTX balance  
            - Function: iotex_balance  
            - Parameters: wallet_address

            2. Query account ERC20 token balance  
            - Function: erc20_balance  
            - Parameters: wallet_address, token_contract_address

            3. Query ERC20 allowance  
            - Function: erc20_allowance  
            - Parameters: owner_address, spender_address, token_contract_address, [decimals] (optional)

            4. Query ERC20 contract information  
            - Function: erc20_contract_info  
            - Parameters: token_contract_address

            =================
            🛠️ Transaction Functions
            =================
            5. Approve ERC20 token usage  
            - Function: erc20_approve  
            - Parameters: private_key, spender_address, token_contract_address, amount, [decimals] (optional)

            6. Execute ERC20 transferFrom  
            - Function: erc20_transfer_from  
            - Parameters: private_key, token_contract_address, from_address, to_address, amount, [decimals] (optional)

            =================
            💬 Interaction Guidelines
            =================
            - For query operations, provide relevant addresses and contract addresses for ERC20 tokens
            - All on-chain write operations require confirmation before execution
            - For operations involving private keys, remind users about security - **never share private keys in plaintext**
            - All operations are limited to IoTeX testnet

            =======================
            📦 Default Parameters
            =======================
            # PolyAgent Token Contract (ERC20)
            polyagent_token_contract = "0xD3286E20Ff71438D9f6969828F7218af4A375e2f"

            # Sender Account
            Sender Address: "0xE4949a0339320cE9ec93c9d0836c260F23DFE8Ca"
            Sender Private Key: "e4ad52fbc8c6fe3f4069af70363b24ca4453dbf472d92f83a8adf38e8010991f"

            # Spender Account
            Spender Address: "0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE"
            Spender Private Key: "3efe78303dcf8ea3355ef363f04eb442e000081fe66ebcebf5d9cf19f3ace8b8"

            # Default settings
            decimals = 18
            amount = 2

            =======================
            🤖 Execution Rules [Important]
            =======================
            You have all required parameters. When users request queries or transactions, select and execute the appropriate function directly based on the content. Unless users explicitly specify different values, use the default parameters above without asking for additional input.
            
            Respond in English and provide clear, professional explanations.
            """,
            model=self.model,
            token_limit=32768,
            tools=[*IotexTokenToolkit(self.estnet_rpc, self.ERC20_ABI, self.chain_id).get_tools()],
            output_language="en"
        )

        self.story_agent = ChatAgent(
            system_message="""    
            [System Notice] You have received 5 XRC20 tokens as a reward.

            Please create a stylized micro-story based on the user's request. Ensure the story begins by mentioning this event: "receiving 5 XRC20 tokens".

            Choose from styles like fantasy, sci-fi, mystery, fairy tale, or cyberpunk.

            User request: $user_demand

            Requirements:
            - Story must clearly mention "receiving 5 XRC20 tokens" at the beginning
            - Story should develop around this request, showing its significance or triggered events
            - Immersive writing style with clear background and concise character development
            - No paragraph breaks, around 150 words
            - Ending should be open or hint at larger developments

            Please generate the story in English.""",
            model=self.model,
            token_limit=32768,
            output_language="en"
        )

        # 添加演示流程状态跟踪
        self.demo_step = 0
        self.demo_context = {
            "order_id": "ORDER20250107001",
            "amount_usd": 49.99,
            "amount_tokens": 49.99,
            "merchant_wallet": "0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE",
            "user_wallet": "0xE4949a0339320cE9ec93c9d0836c260F23DFE8Ca",
            "usd_to_rmb_rate": 7.25,  # USD to RMB exchange rate
            "download_link": "https://pan.baidu.com/s/1F4TgbbTrz4LbSifczoDcXg?pwd=6712" # 真实的百度网盘链接
        }

    async def smart_route_request(self, user_input: str):
        """
        Intelligent routing system - Routes user input to appropriate handling processes
        """
        user_input_lower = user_input.lower()
        
        # Course purchase flow detection
        course_keywords = ["purchase", "buy", "course", "want to buy", "learning", "training", "enroll", "python", "web", "ai", "machine learning"]
        if any(keyword in user_input_lower for keyword in course_keywords):
            return await self.handle_step1_create_order(user_input)
        
        # Automated payment confirmation detection
        if "confirm_payment" in user_input_lower:
            return await self.handle_step2_automated_payment(user_input)
        
        # Blockchain query operation detection
        blockchain_keywords = ["balance", "query", "check", "iotex", "token", "blockchain", "wallet", "address"]
        if any(keyword in user_input_lower for keyword in blockchain_keywords):
            return await self.handle_blockchain_query(user_input)
        
        # Token authorization operation detection
        auth_keywords = ["authorize", "approve", "authorization", "allow", "permit", "allowance"]
        if any(keyword in user_input_lower for keyword in auth_keywords):
            return await self.handle_token_authorization(user_input)
        
        # Creative story generation detection
        story_keywords = ["story", "create", "novel", "sci-fi", "fantasy", "cyberpunk", "received", "reward", "xrc20"]
        if any(keyword in user_input_lower for keyword in story_keywords):
            return await self.handle_creative_story(user_input)
        
        # Default: general assistant handling
        return await self.handle_general_query(user_input)

    async def handle_step1_create_order(self, user_input: str):
        """
        第一步：创建支付宝支付订单（前端已处理课程展示和Payment Journey）
        """
        print(f"(Creating Alipay Payment Order) for user: {user_input}")
        
        # 提取课程信息用于订单创建
        course_info = self.extract_course_info(user_input)
        
        # 调用支付宝MCP服务创建订单
        payment_info = await self.run_alipay_query(
            f"Create a payment order for {course_info['price_rmb']:.2f} RMB to purchase {course_info['name']}, with order ID {self.demo_context['order_id']}"
        )
        
        # 只返回支付宝支付按钮
        return payment_info

    def extract_course_info(self, user_input):
        """从用户输入中提取或生成课程信息"""
        # 根据用户输入智能提取课程信息，这里使用示例数据
        if "python" in user_input.lower():
            return {
                "name": "Primary Python Course",
                "platform": "edX",
                "duration": "8 weeks",
                "level": "Beginner to Intermediate",
                "description": "Learn Python programming fundamentals through hands-on exercises and projects. This comprehensive course covers Python syntax, data structures, functions, and object-oriented programming concepts essential for modern development.",
                "price_usd": 49.99,
                "price_rmb": 49.99 * self.demo_context['usd_to_rmb_rate'],
                "url": "https://www.edx.org/learn/python",
                "instructor": "edX Professional Education",
                "certificate": "Verified Certificate Available"
            }
        elif "web" in user_input.lower() or "javascript" in user_input.lower():
            return {
                "name": "Full Stack Web Development Bootcamp",
                "platform": "edX",
                "duration": "12 weeks",
                "level": "Intermediate to Advanced",
                "description": "Learn to build complete web applications using modern technologies like React, Node.js, and MongoDB. Includes deployment and DevOps practices.",
                "price_usd": 89.99,
                "price_rmb": 89.99 * self.demo_context['usd_to_rmb_rate'],
                "url": "https://www.edx.org/learn/web-development",
                "instructor": "edX Professional Education",
                "certificate": "Professional Certificate"
            }
        else:
            # 默认课程
            return {
                "name": "AI & Machine Learning Fundamentals",
                "platform": "edX",
                "duration": "10 weeks",
                "level": "Beginner to Intermediate",
                "description": "Explore the fundamentals of artificial intelligence and machine learning. Learn to build and deploy ML models using Python, TensorFlow, and scikit-learn.",
                "price_usd": 69.99,
                "price_rmb": 69.99 * self.demo_context['usd_to_rmb_rate'],
                "url": "https://www.edx.org/learn/artificial-intelligence",
                "instructor": "edX Professional Education",
                "certificate": "Professional Certificate"
            }

    async def handle_step2_automated_payment(self, user_input: str):
        """
        第二步：自动化支付流程（已迁移到前端处理）
        """
        print(f"(Automated Payment Process - Frontend Handled) for user: {user_input}")
        
        # 前端已完全处理自动化流程，后端无需返回HTML
        return """
<div style="background: rgba(74, 144, 226, 0.1); border: 1px solid rgba(74, 144, 226, 0.3); border-radius: 6px; padding: 12px; margin: 1rem 0; font-size: 0.9em; color: #94A3B8;">
    <strong>✅ Automated payment process started</strong><br>
    The frontend will handle the automated payment flow.
</div>
"""

    async def run_alipay_query(self, query: str):
        import os
                # 使用绝对路径来定位 MCP 配置文件，避免相对路径问题
        config_path = os.path.join(os.path.dirname(__file__), "..", "Mcp", "alipay_server.json")
        config_path = os.path.abspath(config_path)
        
        try:
            async with MCPToolkit(config_path=config_path) as mcp_toolkit:
                alipay_agent = ChatAgent(
                    system_message="""
                    You are an Alipay Agent for a cross-border payment service. Your task is to create a payment order in Chinese Yuan (RMB) for a product priced in US Dollars.

                    **Action: Create Payment Order (`create_payment`)**
                    - When a user wants to pay, call the `create_payment` function.
                    - Use these exact parameters:
                        - `outTradeNo`: 'ORDER20250107001'
                        - `totalAmount`: '362.43'  (This is the RMB equivalent of $49.99 USD)
                        - `orderTitle`: 'PolyAgent edX Course - Primary Python'

                    **Response Format:**
                    - You MUST return an HTML block with a payment link. Use this exact format:
                    
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="[支付链接]" class="alipay-payment-button" target="_blank" onclick="handleAlipayPayment(this)">Confirm Payment with Alipay</a>
                    </div>
                    
                    <div style="background: rgba(74, 144, 226, 0.1); border: 1px solid rgba(74, 144, 226, 0.3); border-radius: 6px; padding: 12px; margin: 1rem 0; font-size: 0.9em; color: #94A3B8;">
                        <strong>💡 Payment Instructions:</strong><br>
                        1. Click the button to open the Alipay payment page.
                    </div>
                    """,
                    model=self.model,
                    token_limit=32768,
                    tools=[*mcp_toolkit.get_tools()],
                    output_language="en"
                )

                response = await alipay_agent.astep(query)
                
                if response and response.msgs:
                    return response.msgs[0].content
                else:
                    return "Unable to get Alipay response"
                    
        except Exception as e:
            error_msg = f"支付宝处理过程中出现错误: {str(e)}"
            print(error_msg)
            return f"""❌ Alipay Processing Error

An error occurred while processing Alipay request: {str(e)}
Please check Alipay MCP server status and try again."""

    async def run_paypal_query(self, query: str):
        import os
        # 使用绝对路径来定位 PayPal MCP 配置文件，避免相对路径问题
        config_path = os.path.join(os.path.dirname(__file__), "..", "Mcp", "paypal_server.json")
        config_path = os.path.abspath(config_path)
        
        try:
            async with MCPToolkit(config_path=config_path) as mcp_toolkit:
                paypal_agent = ChatAgent(
                    system_message="""
                      你是一个经验丰富的 Paypal 交易代理，负责协助用户完成以下操作：

                1. 创建发票（create_invoice）
                2. 查询订单状态（query_order）
                3. 处理退款请求（process_refund）

                请根据用户的具体需求使用合适的工具进行操作，确保金额、税费、折扣等计算准确，语言清晰专业。
                    """,
                    model=self.model,
                    token_limit=32768,
                    tools=[*mcp_toolkit.get_tools()],
                    output_language="en"
                )

                response = await paypal_agent.astep(query)
                
                if response and response.msgs:
                    return response.msgs[0].content
                else:
                    return "Unable to get PayPal response"
                    
        except Exception as e:
            error_msg = f"PayPal处理过程中出现错误: {str(e)}"
            print(error_msg)
            return f"""❌ PayPal Processing Error

An error occurred while processing PayPal request: {str(e)}
Please check PayPal MCP server status and try again."""

    async def run_amap_query(self, query: str):
        config_path = "E:\\EnjoyAI\\Web3-Agent-Protocal\\workspace_new\\AgentCore\\Mcp\\amap_server.json"

        async with MCPToolkit(config_path=config_path) as mcp_toolkit:
            amap_agent = ChatAgent(
                system_message="""
                你是一个高德地图骑行助手，擅长分析用户的出行需求，并基于实时数据、路线安全性、景色美观度和道路类型，为用户推荐最优骑行路线。

                请根据用户的出发地、目的地，以及是否偏好快速到达、风景优美或避开车流等偏好，推荐一条骑行路线。

                你需要：
                1. 指出推荐的路线途经哪些关键路段或地标。
                2. 说明这条路线在时间、距离、风景、安全性等方面的优势。
                3. 简洁明了地解释为何这是当前最优选择。

                请以自然语言中文回答，条理清晰，重点突出。
                """,
                model=self.model,
                token_limit=32768,
                tools=[*mcp_toolkit.get_tools()],
                output_language="en"
            )

            response = await amap_agent.astep(query)
            print("Agent response：\n", response.msgs[0].content)

    async def run_all(self):
        """执行完整的支付流程演示"""
        results = []
        
        # 步骤1: 创建支付订单
        print("📱 步骤1: 创建支付宝支付订单...")
        payment_result = await self.run_alipay_query("支付")
        results.append(f"步骤1 - 支付订单创建:\n{payment_result}")
        
        # 步骤2: 查询支付状态  
        print("\n📊 步骤2: 查询支付状态...")
        query_result = await self.run_alipay_query("查询订单")
        results.append(f"步骤2 - 支付状态查询:\n{query_result}")
        
        # 步骤3: 查询授权额度
        print("\n🔍 步骤3: 查询ERC20代币授权额度...")
        allowance_response = self.iotex_agent.step("帮我查询一下ERC20代币的授权额度。")
        allowance_result = allowance_response.msgs[0].content if allowance_response and allowance_response.msgs else "查询失败"
        results.append(f"步骤3 - 授权额度查询:\n{allowance_result}")
        
        # 步骤4: 执行代币授权
        print("\n🔐 步骤4: 执行代币授权操作...")
        approve_response = self.iotex_agent.step("我想给0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE地址授权200个代币，请帮我执行该操作")
        approve_result = approve_response.msgs[0].content if approve_response and approve_response.msgs else "授权失败"
        results.append(f"步骤4 - 代币授权:\n{approve_result}")
        
        # 步骤5: 执行稳定币转账
        print("\n💸 步骤5: 执行稳定币转账...")
        transfer_response = self.iotex_agent.step("我想给0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE地址转账5个代币，请帮我执行该操作")
        transfer_result = transfer_response.msgs[0].content if transfer_response and transfer_response.msgs else "转账失败"
        results.append(f"步骤5 - 稳定币转账:\n{transfer_result}")
        
        # 步骤6: 提供定制故事服务
        print("\n📖 步骤6: 生成定制故事服务...")
        story_response = self.story_agent.step("我希望写一个勇士拯救公主的故事")
        story_result = story_response.msgs[0].content if story_response and story_response.msgs else "故事生成失败"
        results.append(f"步骤6 - 故事服务交付:\n{story_result}")
        
        return results

    async def handle_blockchain_query(self, user_input: str):
        """Handle blockchain-related queries"""
        response = self.iotex_agent.step(user_input)
        
        return f"""🔗 **IoTeX Blockchain Query Results**

{response.msgs[0].content if response.msgs else "Query failed, please try again later"}

---
*Query completed on IoTeX Testnet*"""

    async def handle_token_authorization(self, user_input: str):
        """Handle token authorization operations"""
        response = self.iotex_agent.step(f"Please execute the following authorization operation: {user_input}")
        
        return f"""🔐 **Token Authorization Operation**

{response.msgs[0].content if response.msgs else "Authorization operation failed"}

⚠️ **Security Reminder**
- Authorization operations involve on-chain transactions, please verify operation security
- Recommend testing operation flow on testnet environment
- Handle private key information carefully in production environment

---
*Operation executed on IoTeX Testnet*"""

    async def handle_creative_story(self, user_input: str):
        """Handle creative story generation"""
        # Use Template to safely format strings
        story_template = Template(self.story_agent.system_message)
        formatted_system_message = story_template.safe_substitute(user_demand=user_input)
        
        # Update system message
        self.story_agent.system_message = formatted_system_message
        
        response = self.story_agent.step("Please create a story based on my requirements")
        
        return f"""📖 **AI Creative Story**

{response.msgs[0].content if response.msgs else "Story generation failed, please try again later"}

---
*Generated by PolyAgent Creative Engine*
*Content is for entertainment purposes only*"""

    async def handle_general_query(self, user_input: str):
        """Handle general queries"""
        return f"""🤖 **General Assistant Response**

Your question: "{user_input}"

I apologize, but I cannot understand your specific requirements at the moment. I am the PolyAgent Payment Bridge Assistant, and I can mainly help you with:

🔹 **Cross-border Payment Process**
   - Course purchase demonstration
   - Alipay to PayPal bridge service

🔹 **Blockchain Operations**  
   - IoTeX testnet balance queries
   - ERC20 token operations
   - Wallet address verification

🔹 **Token Management**
   - Authorization operations (approve)
   - Transfer operations (transfer)
   - Contract interactions

🔹 **Creative Services**
   - Blockchain-themed story creation
   - Sci-fi/cyberpunk style content generation

Please try to describe your needs more specifically, or you can ask questions like:
- "Check my IoTeX wallet balance"
- "Help me authorize tokens"
- "Create a cyberpunk story about receiving tokens"
- "I want to purchase a Python course"

---
*For market information queries, please switch to the "Crypto Monitor" assistant*"""

if __name__ == "__main__":
    agent_manager = AgentManager()
    agent_manager = AgentManager()
    asyncio.run(agent_manager.run_all())
