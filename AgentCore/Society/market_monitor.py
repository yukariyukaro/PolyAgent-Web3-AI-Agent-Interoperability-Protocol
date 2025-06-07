from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.societies.workforce import Workforce
from camel.tasks import Task

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from AgentCore.Tools.coingecko_toolkit import CoinGeckoToolkit
from AgentCore.Tools.chaingpt_toolkit import ChainGPTToolkit
from AgentCore.Tools.humanloop_toolkit import HumanToolkit

from camel.types import (
    ModelPlatformType,
    ModelType,
    OpenAIBackendRole,
    RoleType,
    TaskType,
)

class MarketMonitorAgent:
    def __init__(self, model):
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.MODELSCOPE,
            model_type='Qwen/Qwen2.5-72B-Instruct',
            model_config_dict={'temperature': 0.2},
            api_key='9d3aed4d-eca1-4e0c-9805-cb923ccbbf21',
        )
        
        # 初始化 agent
        self.coin_price_agent = ChatAgent(
            system_message="你是一个加密货币历史价格助手，帮助用户获取指定加密货币在某一特定日期的历史价格数据，并作一个简单的分析。",
            model=self.model,
            token_limit=32768,
            tools=[*CoinGeckoToolkit().get_tools()],
            output_language="zh"
        )

        self.coin_news_agent = ChatAgent(
            system_message="你是一个加密货币新闻助手，帮助用户获取指定加密货币相关的新闻数据。并做一个简单分析。",
            model=self.model,
            token_limit=32768,
            tools=[*ChainGPTToolkit().get_tools()],
            output_language="en"
        )

        # 初始化 workforce
        self.workforce = Workforce(
            description="这是一个由两个智能体组成的协作系统，用来实时获取加密货币的市场信息。由价格信息代理和新闻信息代理组成，分别负责历史价格查询与相关新闻提取与分析。系统整合两类关键数据，为用户提供更全面的市场洞察，可作为交易策略制定、行情监测和市场研究的基础组件",
            new_worker_agent_kwargs={'model': self.model},
            coordinator_agent_kwargs={'model': self.model},
            task_agent_kwargs={'model': self.model}
        )

        # 添加 agent 到 workforce
        self.workforce.add_single_agent_worker(
            "负责搜索加密货币价格",
            worker=self.coin_price_agent
        ).add_single_agent_worker(
            "负责获取加密货币数据新闻",
            worker=self.coin_news_agent
        )

    def run(self, user_question: str) -> str:
        # 创建并处理任务
        task = Task(
            content=user_question,
            id="task-crypto-info"
        )
        task = self.workforce.process_task(task)
        return task.result

def main():
    user_question = ["现在人民币兑 USDT 汇率是多少",
                    "我想知道USDT 的最新价格",
                    "我想知道USDT 的市场新闻消息",
    ]
    result = run_crypto_insight_agent(user_question[2])
    print(result)

if __name__ == "__main__":
    main()

"""
question[0] answer:

Worker node 918da0 (负责搜索加密货币价格) get task task-crypto-info.0: 由<918da0>负责搜索当前人民币兑USDT的汇率。
======
Reply from Worker node 918da0 (负责搜索加密货币价格):

当前人民币兑USDT（Tether）的汇率会因不同平台和市场情况而略有波动。截至最近数据，人民币兑USDT的汇率大致在7.2至7.3之间，建议在主流加密货币交易平台（如币安、火币等）查询最新汇率以获得最准确信息。
======当前人民币兑USDT（Tether）的汇率大致在7.2至7.3之间。请注意，实际汇率会因不同平台和市场实时行情略有波动，建议在主流加密货币交易平台（如币安、火币等）查询最新数据以获得最准确信息。

"""

"""
question[2] answer:

orker node 046946 (负责获取加密货币数据新闻) get task task-crypto-info.0: 046946: 获取关于USDT的最新市场新闻和消息。
======
Reply from Worker node 046946 (负责获取加密货币数据新闻):

以下是USDT（Tether）最新市场新闻及简要分析：

1. BlockDAG项目已超过1.93亿美元预售并推出推荐返现计划，用户通过推荐获得USDT奖励，显示USDT作为奖励及流动性媒介的重要地位。（2025-02-10）
2. MEXC交易所推进Aptos生态，用户可质押USDT获得APT代币奖励，同时对USDT合约免手续费，凸显USDT在主流合约产品中的核心作用。（2025-01-24）
5. BingX交易所经黑客攻击后优先恢复USDT等主流币种提币，强调USDT在交易和资产安全中的基础货币角色。（2024-09-21）
6. Rho Markets因黑客攻击损失760万美元，涉及USDT和USDC流动池。平台承诺加强安全措施并尽快退还用户资产，再次显示USDT在链上借贷和DeFi中的广泛应用与风险 敞口。（2024-07-20）

简要分析：
USDT作为全球使用最广泛的稳定币，在DeFi、交易所生态及创新项目中均有突出表现。其强大的流动性、定价稳定性及认可度使其成为黑客攻击和安全事件中首选的目标资产，同时也是行业奖励机制和流动性管理的核心。本轮新闻动态凸显USDT在数字货币市场基础设施中的不可替代地位，建议关注其合规监管进展及DeFi平台的风控能力。

如需详细新闻原文或更多数据可随时咨询。
======USDT（Tether）近期市场新闻要点如下：

1. USDT在多项创新项目、如BlockDAG等平台中被用作奖励和流动性媒介，受到了广泛的使用；
2. 多家主流交易所（如MEXC、BingX）围绕USDT开展产品创新，包括质押、合约免手续费等，体现其核心货币地位；
3. DeFi平台如Aave也将USDT作为合成资产锚定及储备的重要部分，突出其在去中心化金融体系内的主导作用；
4. USDT市占率维持在稳定币市场约2/3，拥有极强的话语权，但也因监管、安全及黑客事件反复成为焦点；
5. 黑客事件（如Rho Markets和BingX）显示USDT广泛用于链上生态，也暴露其在安全风险中的高影响力。

综合来看，USDT作为全球最大的稳定币，兼具流动性、定价基准和行业认可三大优势。当前其在DeFi、交易所和数字资产管理领域不可替代，但同时需要高度关注安全防护和合规监管等领域的最新政策和新闻动态。如需获取具体新闻原文或更详细行情分析，可随时提出。

"""