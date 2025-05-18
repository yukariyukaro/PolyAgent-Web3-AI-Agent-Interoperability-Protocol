from datetime import time

from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
# from camel.messages import BaseMessage
from camel.societies.workforce import Workforce
from camel.tasks import Task
# from camel.toolkits import FunctionTool

from Tools.coingecko_toolkit import CoinGeckoToolkit
from Tools.chaingpt_toolkit import ChainGPTToolkit
# from Tools.yamlwriter_toolkit import YamlWriterToolkit

import io
import contextlib
import threading
import queue
import sys


def get_crypto_agent_data(uq):

    model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI,
        model_type=ModelType.GPT_4_1,
        url="https://api.openai.com/v1/",
        api_key=""
    )

    workforce = Workforce(description="制定加密货币交易策略组", new_worker_agent_kwargs={'model': model},
                          coordinator_agent_kwargs={'model': model}, task_agent_kwargs={'model': model})

    coin_price_agent = ChatAgent(
        system_message="你是一个加密货币历史价格助手，帮助用户获取指定加密货币在某一特定日期的历史价格数据，并作一个简单的分析。",
        model=model,
        token_limit=32768,
        tools=[*CoinGeckoToolkit().get_tools()],
        output_language="zh"
    )

    coin_news_agent = ChatAgent(
        system_message="你是一个加密货币新闻助手，帮助用户获取指定加密货币相关的新闻数据。并做一个简单分析。",
        model=model,
        token_limit=32768,
        tools=[*ChainGPTToolkit().get_tools()],
        output_language="zh"
    )

    strategy_generator_agent = ChatAgent(
        system_message="""\"\"
    你是一个加密货币交易策略生成助手，能够根据实时的价格和新闻数据，为指定的加密货币生成适用于 Hummingbot 的交易策略 YAML 配置文件。

    Hummingbot 是一个开源的高频交易机器人，支持多种交易策略，包括纯市场做市（Pure Market Making）策略。以下是一个基于纯市场做市策略的 YAML 配置文件示例，其中id行不需要改动：

    ```yaml
    id: BvVzz5BtsZHywoYsPGtVtTbe2GvZK9tCiNGKfEZ2oJ5x
    controller_name: pmm_simple
    controller_type: market_making
    total_amount_quote: '100'
    manual_kill_switch: false
    candles_config: []
    connector_name: binance_perpetual
    trading_pair: ETH-USDT
    buy_spreads:
    - 10000.0
    - 20000.0
    sell_spreads:
    - 10000.0
    - 20000.0
    buy_amounts_pct:
    - '50.0'
    - '50.0'
    sell_amounts_pct:
    - '50.0'
    - '50.0'
    executor_refresh_time: 60
    cooldown_time: 60
    leverage: 1
    position_mode: HEDGE
    stop_loss: '0.01'
    take_profit: '0.02'
    time_limit: 2700
    take_profit_order_type: 2
    trailing_stop:
      activation_price: '0.013'
      trailing_delta: '0.003'
    ```

    """,
        model=model,
        token_limit=32768,
        tools=[*ChainGPTToolkit().get_tools()],
        output_language="zh"
    )

    workforce.add_single_agent_worker(
        "负责搜索加密货币价格",
        worker=coin_price_agent
    ).add_single_agent_worker(
        "负责获取加密货币数据新闻",
        worker=coin_news_agent
    ).add_single_agent_worker(
        "负责制定交易策略",
        worker=strategy_generator_agent
    )

    content = """
    根据用户的问题，制定相关的交易策略。要严格按照如下步骤：

    1. 分析用户想要投资的加密货币以及日期。
    2. 获取加密货币的历史或当前价格。
    3. 获取与该加密货币相关的新闻数据。
    4. 基于上述信息制定一份可执行的交易策略。
    5. 将最终制定的交易策略写入一个以当前日期命名的 YAML 文件中。
    6. 提示用户确认策略内容，并回复是否去执行

    用户的问题是：{{user_question}}
    """

    user_question = "今天是5月18日，我想投资bitcoin。"
    if uq:
        user_question = uq

    task = Task(
        content=content.replace("{{user_question}}", user_question),
        id="0",  # id可以是任何标记字符串
    )

    q = queue.Queue()

    def worker():
        sys_stdout = sys.stdout
        sys.stdout = StreamToQueue(q)
        try:
            workforce.process_task(task)
        finally:
            # sys.stdout = sys_stdout
            q.put(None)  # 结束标志

    threading.Thread(target=worker, daemon=True).start()

    while True:
        msg = q.get()
        if msg is None:
            break
        yield msg


class StreamToQueue:
    def __init__(self, q):
        self.q = q
    def write(self, msg):
        if msg:
            self.q.put(msg)
    def flush(self):
        pass