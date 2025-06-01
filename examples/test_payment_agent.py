from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.toolkits import HumanToolkit
from eth_account import Account

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from AgentCore.Tools.iotextoken_toolkit import IotexTokenToolkit
from camel.toolkits import HumanToolkit

from camel.types import (
    ModelPlatformType,
    ModelType,
    OpenAIBackendRole,
    RoleType,
)

polyagent_token_contract = "0xD3286E20Ff71438D9f6969828F7218af4A375e2f" 
sender_private_key = "e4ad52fbc8c6fe3f4069af70363b24ca4453dbf472d92f83a8adf38e8010991f"
sender_address = Account.from_key('0x' + sender_private_key).address

estnet_rpc = "https://babel-api.testnet.iotex.io"
ERC20_ABI = [
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

# model = ModelFactory.create(
#     model_platform=ModelPlatformType.OPENAI,
#     model_type=ModelType.GPT_4_1,
#     url="https://api.openai.com/v1/",
# )

model = ModelFactory.create(
    model_platform=ModelPlatformType.MODELSCOPE,
    model_type='Qwen/Qwen2.5-72B-Instruct',
    url="https://api-inference.modelscope.cn/v1/",
)

iotex_agent = ChatAgent(
    system_message="""
    你是一个 IoTeX 测试网的区块链助手，具备以下能力：
    - 查询账户 IOTX 或 ERC20 余额
    - 发起 IOTX 或 ERC20 的 transfer、approve、transferFrom 操作

    交互规则：
    - 若用户未提供必要信息（如 from/to 地址、代币类型、数量、合约地址、私钥等），请主动提问获取。
    - 如果用户仅表述操作意图，请引导其补充关键信息：
    - 对于 IOTX：from 地址或私钥、to 地址、金额
    - 对于 ERC20：额外需要合约地址，approve/transferFrom 还需要 spender 或 sender 信息
    - 所有交互仅限 IoTeX 测试网
    - 私钥信息需提醒用户注意安全，不建议明文传播
    """,
    model=model,
    token_limit=32768,
    tools=[*IotexTokenToolkit(estnet_rpc, ERC20_ABI).get_tools(),
           *HumanToolkit().get_tools()],
    output_language="zh"
)

response = iotex_agent.step("帮我查询一下ERC20代币的余额。")
print(response.info['tool_calls'][0].result)
print("----------------------------------------------")
print(response.msgs[0].content)
print("----------------------------------------------")
print(response)