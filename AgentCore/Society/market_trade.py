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
        import os
        # 使用相对路径来定位 MCP 配置文件
        config_path = os.path.join(os.path.dirname(__file__), "..", "Mcp", "alipay_server.json")
        config_path = os.path.abspath(config_path)
        
        # 移除调试信息，避免在用户界面显示配置路径
        # print(f"📁 支付宝配置文件路径: {config_path}")
        # print(f"📝 用户查询: {query}")
        
        if not os.path.exists(config_path):
            error_msg = f"❌ 支付系统配置错误：找不到配置文件 {config_path}"
            print(error_msg)
            return f"""❌ 支付系统配置错误

<div style="
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 1rem 0;
    color: #E6E6ED;
">
    <strong>配置文件缺失</strong><br>
    找不到支付宝MCP配置文件：<br>
    <code style="color: #9CA3AF; font-family: monospace;">{config_path}</code><br><br>
    请检查项目配置或联系系统管理员。
</div>"""

        try:
        async with MCPToolkit(config_path=config_path) as mcp_toolkit:
                print("✅ MCP 工具包连接成功")
                
                tools = mcp_toolkit.get_tools()
                print(f"🛠️ 可用工具数量: {len(tools)}")
                
                if len(tools) == 0:
                    return f"""⚠️ 支付系统工具不可用

<div style="
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05));
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 1rem 0;
    color: #E6E6ED;
">
    <strong>工具包连接成功但无可用工具</strong><br>
    MCP工具包已连接，但没有检测到支付宝相关的工具函数。<br>
    请检查支付宝MCP服务器配置和环境变量设置。
</div>"""
                
            alipay_agent = ChatAgent(
                system_message="""
                你是一个支付宝支付代理（Alipay Agent），负责协助用户完成以下操作：

                1. 创建支付订单（create_payment）
                2. 查询支付状态（query_payment）
                3. 发起退款（refund_payment）
                4. 查询退款信息（query_refund）

                现在你将直接使用以下参数执行操作，所有参数均已明确，无需向用户补充或确认。

                【1】创建支付订单（create_payment）
                    - 当用户说"支付"、"创建支付"、"付款"时，直接调用create_payment函数
                - 参数：
                    - outTradeNo：'ORDER20250606001'
                    - totalAmount：'99.99'
                    - orderTitle：'加密货币支付'
                - 返回：
                    - 支付链接

                【2】查询支付状态（query_payment）
                    - 当用户说"查询订单"、"查询状态"时，直接调用query_payment函数
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
                    tools=tools,
                output_language="zh"
            )

                print("🤖 支付宝代理创建成功，正在处理查询...")
            response = await alipay_agent.astep(query)
                
            if response and response.msgs:
                result = response.msgs[0].content
                    print(f"✅ 收到支付宝响应: {result[:100]}...")
                return result
                else:
                    print("❌ 未收到有效响应")
                    return f"""❌ 支付宝服务无响应

<div style="
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 1rem 0;
    color: #E6E6ED;
">
    <strong>服务响应异常</strong><br>
    支付宝代理已创建但未返回有效响应。<br>
    这可能是由于网络问题或服务配置错误导致的。<br><br>
    请稍后重试或联系技术支持。
</div>"""
                    
        except Exception as e:
            error_str = str(e)
            print(f"❌ MCP 连接或处理失败: {e}")
            
            # 根据错误类型提供详细的错误信息
            if "AP_APP_ID" in error_str:
                return f"""❌ 支付宝环境变量配置错误

<div style="
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 1rem 0;
    color: #E6E6ED;
">
    <strong>缺少必需的环境变量</strong><br>
    错误详情：缺少 AP_APP_ID 环境变量<br><br>
    
    <strong>解决方案：</strong><br>
    1. 检查 AgentCore/Mcp/alipay_server.json 配置文件<br>
    2. 确保已设置正确的支付宝应用ID (AP_APP_ID)<br>
    3. 确保已设置应用私钥 (AP_APP_KEY)<br>
    4. 确保已设置支付宝公钥 (AP_PUB_KEY)<br><br>
    
    <details style="margin-top: 1rem;">
        <summary style="color: #9CA3AF; cursor: pointer;">🔧 技术错误详情</summary>
        <div style="margin-top: 0.5rem; padding: 0.75rem; background: rgba(75, 85, 99, 0.1); border-radius: 0.5rem; font-size: 0.75rem; color: #9CA3AF; font-family: monospace;">
            {error_str}
        </div>
    </details>
</div>"""
            
            elif "AP_APP_KEY" in error_str:
                return f"""❌ 支付宝应用私钥配置错误

<div style="
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 1rem 0;
    color: #E6E6ED;
">
    <strong>应用私钥配置缺失</strong><br>
    错误详情：缺少或无效的 AP_APP_KEY 环境变量<br><br>
    
    请检查支付宝应用私钥配置是否正确。<br><br>
    
    <details style="margin-top: 1rem;">
        <summary style="color: #9CA3AF; cursor: pointer;">🔧 技术错误详情</summary>
        <div style="margin-top: 0.5rem; padding: 0.75rem; background: rgba(75, 85, 99, 0.1); border-radius: 0.5rem; font-size: 0.75rem; color: #9CA3AF; font-family: monospace;">
            {error_str}
        </div>
    </details>
</div>"""
            
            elif "AP_PUB_KEY" in error_str:
                return f"""❌ 支付宝公钥配置错误

<div style="
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 1rem 0;
    color: #E6E6ED;
">
    <strong>支付宝公钥配置缺失</strong><br>
    错误详情：缺少或无效的 AP_PUB_KEY 环境变量<br><br>
    
    请检查支付宝公钥配置是否正确。<br><br>
    
    <details style="margin-top: 1rem;">
        <summary style="color: #9CA3AF; cursor: pointer;">🔧 技术错误详情</summary>
        <div style="margin-top: 0.5rem; padding: 0.75rem; background: rgba(75, 85, 99, 0.1); border-radius: 0.5rem; font-size: 0.75rem; color: #9CA3AF; font-family: monospace;">
            {error_str}
        </div>
    </details>
</div>"""
            
            elif "timeout" in error_str.lower() or "network" in error_str.lower():
                return f"""❌ 网络连接错误

<div style="
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 1rem 0;
    color: #E6E6ED;
">
    <strong>网络连接超时或失败</strong><br>
    无法连接到支付宝MCP服务器。<br><br>
    
    <strong>可能的原因：</strong><br>
    • 网络连接不稳定<br>
    • MCP服务器未启动<br>
    • 防火墙阻止了连接<br><br>
    
    请检查网络连接后重试。<br><br>
    
    <details style="margin-top: 1rem;">
        <summary style="color: #9CA3AF; cursor: pointer;">🔧 技术错误详情</summary>
        <div style="margin-top: 0.5rem; padding: 0.75rem; background: rgba(75, 85, 99, 0.1); border-radius: 0.5rem; font-size: 0.75rem; color: #9CA3AF; font-family: monospace;">
            {error_str}
        </div>
    </details>
</div>"""
            
            else:
                return f"""❌ 支付系统服务错误

<div style="
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 1rem 0;
    color: #E6E6ED;
">
    <strong>支付系统暂时不可用</strong><br>
    支付宝MCP服务在处理请求时发生了未知错误。<br><br>
    
    请稍后重试，如果问题持续存在，请联系技术支持。<br><br>
    
    <details style="margin-top: 1rem;">
        <summary style="color: #9CA3AF; cursor: pointer;">🔧 技术错误详情</summary>
        <div style="margin-top: 0.5rem; padding: 0.75rem; background: rgba(75, 85, 99, 0.1); border-radius: 0.5rem; font-size: 0.75rem; color: #9CA3AF; font-family: monospace;">
            {error_str}
        </div>
    </details>
</div>"""

    async def handle_payment_confirmation(self):
        """处理支付确认，模拟支付成功后查询订单状态"""
        import asyncio
        
        # 等待10秒模拟支付处理时间
        print("💳 正在处理支付...")
        await asyncio.sleep(10)
        
        # 模拟支付成功，返回查询结果
        return """✅ Payment Successful!

<div class="payment-info-card" style="
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.08));
    border: 1px solid rgba(16, 185, 129, 0.4);
    border-radius: 16px;
    padding: 24px;
    margin: 24px 0;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.15);
">
    <div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #10B981, #34D399, #10B981); background-size: 200% 100%; animation: payment-card-gradient 3s ease infinite;"></div>
    
    <div class="payment-card-header" style="display: flex; align-items: center; margin-bottom: 20px;">
        <div style="
            width: 48px; 
            height: 48px; 
            background: linear-gradient(135deg, #10B981, #34D399); 
            border-radius: 12px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            margin-right: 16px;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        ">
            <span style="font-size: 24px; color: white;">✅</span>
        </div>
        <div>
            <h3 style="color: #10B981; font-size: 20px; font-weight: 700; margin-bottom: 4px;">Payment Successful</h3>
            <p style="color: #A0A0B4; font-size: 14px; margin: 0;">Transaction completed successfully</p>
        </div>
    </div>
    
    <div class="payment-info-item" style="display: flex; justify-content: space-between; align-items: center; padding: 16px 0; border-bottom: 1px solid rgba(16, 185, 129, 0.2);">
        <span class="payment-info-label" style="color: #A0A0B4; font-size: 16px; font-weight: 500;">Order ID</span>
        <span class="payment-info-value" style="color: #10B981; font-weight: 600; font-size: 18px;">ORDER20250606001</span>
    </div>
    
    <div class="payment-info-item" style="display: flex; justify-content: space-between; align-items: center; padding: 16px 0; border-bottom: 1px solid rgba(16, 185, 129, 0.2);">
        <span class="payment-info-label" style="color: #A0A0B4; font-size: 16px; font-weight: 500;">Amount</span>
        <span class="payment-info-value amount" style="color: #10B981; font-weight: 700; font-size: 24px;">¥99.99</span>
    </div>
    
    <div class="payment-info-item" style="display: flex; justify-content: space-between; align-items: center; padding: 16px 0; border-bottom: 1px solid rgba(16, 185, 129, 0.2);">
        <span class="payment-info-label" style="color: #A0A0B4; font-size: 16px; font-weight: 500;">Status</span>
        <span class="payment-info-value status" style="
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            background: rgba(16, 185, 129, 0.15);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        ">Payment Successful</span>
    </div>
    
    <div class="payment-info-item" style="display: flex; justify-content: space-between; align-items: center; padding: 16px 0;">
        <span class="payment-info-label" style="color: #A0A0B4; font-size: 16px; font-weight: 500;">Transaction ID</span>
        <span class="payment-info-value" style="color: #10B981; font-weight: 600; font-size: 18px; font-family: monospace;">2025060622001001950002</span>
    </div>
</div>"""

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


if __name__ == "__main__":
    agent_manager = AgentManager()
    asyncio.run(agent_manager.run_all())
