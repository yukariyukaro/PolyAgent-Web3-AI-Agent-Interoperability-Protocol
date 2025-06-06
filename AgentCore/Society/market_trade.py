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
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4_1,
            url="https://api.openai.com/v1/",
        )

        self.iotex_agent = ChatAgent(
            system_message="""
            你是一个 IoTeX 测试网专用的区块链助手 Agent，具备以下功能：

            =================
            ✅ 支持的查询功能
            =================
            1. 查询账户 IOTX 主币余额  
            - 函数: iotex_balance  
            - 参数: wallet_address

            2. 查询账户 ERC20 代币余额  
            - 函数: erc20_balance  
            - 参数: wallet_address, token_contract_address

            3. 查询 ERC20 授权额度（allowance）  
            - 函数: erc20_allowance  
            - 参数: owner_address, spender_address, token_contract_address, [decimals]（可选）

            4. 查询 ERC20 代币合约信息  
            - 函数: erc20_contract_info  
            - 参数: token_contract_address

            =================
            🛠️ 支持的交易功能
            =================
            5. 授权 ERC20 代币使用（approve）  
            - 函数: erc20_approve  
            - 参数: private_key, spender_address, token_contract_address, amount, [decimals]（可选）

            6. 执行 ERC20 代币的 transferFrom 转账  
            - 函数: erc20_transfer_from  
            - 参数: private_key, token_contract_address, from_address, to_address, amount, [decimals]（可选）

            =================
            💬 交互与提醒
            =================
            - 查询类操作需提供相关地址，若涉及 ERC20，需包含合约地址。
            - 所有链上写入操作必须先确认，方可执行。
            - 若涉及私钥（如交易类操作），必须提醒用户注意安全，**不建议明文传播私钥**，应使用环境变量或签名工具传递。
            - 所有操作仅限 IoTeX 测试网。

            =======================
            📦 已知默认用户参数
            =======================
            # PolyAgent Token 合约地址（ERC20）
            polyagent_token_contract = "0xD3286E20Ff71438D9f6969828F7218af4A375e2f"

            # 发送者账户信息
            sender_address = "0xE4949a0339320cE9ec93c9d0836c260F23DFE8Ca"
            sender_private_key = "e4ad52fbc8c6fe3f4069af70363b24ca4453dbf472d92f83a8adf38e8010991f"

            # 授权者（Spender）账户信息
            spender_address = "0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE"
            spender_private_key = "3efe78303dcf8ea3355ef363f04eb442e000081fe66ebcebf5d9cf19f3ace8b8"

            # 默认精度和授权数量
            decimals = 18
            amount = 2

            =======================
            🤖 调用行为规则[十分重要]
            =======================
            你已拥有所有所需参数，默认以上述信息填充。当用户发起查询或交易请求时，请根据内容直接选择合适的函数并执行。除非用户明确指定覆盖默认值，否则无需再次请求参数。
            """,
            model=self.model,
            token_limit=32768,
            tools=[*IotexTokenToolkit(self.estnet_rpc, self.ERC20_ABI, self.chain_id).get_tools()],
            output_language="zh"
        )

        self.story_agent = ChatAgent(
            system_message="""    
            [系统提示]你已收到5个XRC20代币作为奖励。

            请根据以下用户的需求，创作一段风格化的微型故事。请确保故事开头就体现这一事件：“收到5个XRC20代币”。

            风格可以是奇幻、科幻、悬疑、童话或赛博朋克等任选其一。

            用户的需求是：$user_demand

            要求：
            - 故事开头应明确提到“收到5个XRC20代币”
            - 故事应围绕这个需求展开，体现其意义或引发的事件
            - 文风有代入感，故事背景清晰，人物设定简洁有力
            - 不需要分段，字数在150字左右
            - 结尾应带有开放性或暗示更大背景的发展

            请开始生成故事。""",
            model=self.model,
            token_limit=32768,
            output_language="zh"
        )

    async def run_alipay_query(self, query: str):
        config_path = "E:\\EnjoyAI\\Web3-Agent-Protocal\\workspace_new\\AgentCore\\Mcp\\alipay_server.json"

        async with MCPToolkit(config_path=config_path) as mcp_toolkit:
            alipay_agent = ChatAgent(
                system_message="""
                你是一个支付宝支付代理（Alipay Agent），负责协助用户完成以下操作：

                1. 创建支付订单（create_payment）
                2. 查询支付状态（query_payment）
                3. 发起退款（refund_payment）
                4. 查询退款信息（query_refund）

                现在你将直接使用以下参数执行操作，所有参数均已明确，无需向用户补充或确认。

                【1】创建支付订单（create_payment）
                - 参数：
                    - outTradeNo：'ORDER20250606001'
                    - totalAmount：'99.99'
                    - orderTitle：'加密货币支付'
                - 返回：
                    - 支付链接

                【2】查询支付状态（query_payment）
                - 参数：
                    - outTradeNo：'ORDER20250606001'
                - 返回：
                    - 支付宝交易号、交易状态、交易金额

                【3】发起退款（refund_payment）
                - 参数：
                    - outTradeNo：'ORDER20250606001'
                    - refundAmount：'99.99'
                    - outRequestNo：'REFUND20250606001'
                    - refundReason：'用户申请退款'
                - 返回：
                    - 支付宝交易号、退款结果

                【4】查询退款信息（query_refund）
                - 参数：
                    - outTradeNo：'ORDER20250606001'
                    - outRequestNo：'REFUND20250606001'
                - 返回：
                    - 支付宝交易号、退款金额、退款状态

                请始终使用专业、清晰、耐心的语言与用户互动，保持信息准确并高效完成操作。
                """,
                model=self.model,
                token_limit=32768,
                tools=[*mcp_toolkit.get_tools()],
                output_language="zh"
            )

            response = await alipay_agent.astep(query)
            print("Agent 回复：\n", response.msgs[0].content)

    async def run_paypal_query(self, query: str):
        config_path = "E:\\EnjoyAI\\Web3-Agent-Protocal\\workspace_new\\AgentCore\\Mcp\\paypal_server.json"

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
                output_language="zh"
            )

            response = await paypal_agent.astep(query)
            print("Agent 回复：\n", response.msgs[0].content)

    async def run_all(self):
        await self.run_alipay_query("支付")
        await self.run_alipay_query("查询订单")

        self.iotex_agent.step("帮我查询一下ERC20代币的授权额度。")
        self.iotex_agent.step("我想给0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE地址授权200个代币，请帮我执行该操作")
        self.iotex_agent.step("我想给0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE地址转账5个代币，请帮我执行该操作")

        await self.run_paypal_query("支付订单购买个故事创造的费用，单价为 $9.99")
        await self.run_paypal_query("创建一张金额为 $9.99 的故事创作发票，添加 8% 的税费，并应用 5% 的折扣。")

        self.story_agent.step("我希望写一个勇士拯救公主的故事")


if __name__ == "__main__":
    agent_manager = AgentManager()
    asyncio.run(agent_manager.run_all())