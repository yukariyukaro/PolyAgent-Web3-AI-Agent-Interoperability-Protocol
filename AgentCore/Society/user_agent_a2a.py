import os
import sys
import json
import asyncio
import logging
import aiohttp
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass

# --- A2A 和 CAMEL 库导入 ---
from python_a2a import A2AServer, run_server, AgentCard, AgentSkill, TaskStatus, TaskState, A2AClient
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# --- 确保项目路径正确 ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- 日志配置 ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AmazonA2AAgent")


# ==============================================================================
#  数据类与枚举
# ==============================================================================
@dataclass
class AmazonProduct:
    asin: str
    title: str
    price: float
    currency: str
    merchant_id: str
    delivery_speed: int # 模拟一个发货速度评分
    rating: float
    prime_eligible: bool
    url: str

class PurchaseStrategy(Enum):
    CHEAPEST = "cheapest"
    FASTEST = "fastest"
    BEST_RATED = "best_rated"
    PRIME = "prime"


# ==============================================================================
#  业务逻辑层: AmazonServiceManager
#  这个类包含了所有亚马逊购物的业务逻辑。
# ==============================================================================
class AmazonServiceManager:
    """
    管理所有与亚马逊购物相关的业务逻辑，包括模型初始化、意图理解、商品搜索和支付。
    """
    def __init__(self):
        """初始化模型和配置"""
        print("🧠 [AmazonServer] Initializing the core AI model...")
        # 改用与Alipay Agent相同的模型工厂
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.DEEPSEEK,
            model_type=ModelType.DEEPSEEK_REASONER,
            # 建议将API密钥放在环境变量或配置文件中
            api_key="",
            url="https://api.chatanywhere.tech/v1/",
        )
        print("✅ [AmazonServer] AI model is ready.")

        # 不在初始化时创建session，而是在每次需要时创建
        self.session = None
        self.amazon_search_api = "https://amazon-backend.replit.app/api/v1/search"

    async def _get_session(self):
        """获取或创建aiohttp会话，确保在当前事件循环中创建"""
        # 每次都创建新的会话，避免跨事件循环问题
        return aiohttp.ClientSession()

    async def close(self):
        """关闭 aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

        # 不在初始化时创建session，而是在每次需要时创建
        self.session = None
        self.amazon_search_api = "https://amazon-backend.replit.app/api/v1/search"

    async def _get_session(self):
        """获取或创建aiohttp会话，确保在当前事件循环中创建"""
        # 每次都创建新的会话，避免跨事件循环问题
        return aiohttp.ClientSession()

    async def close(self):
        """关闭 aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def understand_intent(self, user_input: str) -> Dict:
        """使用大模型解析用户的购物意图"""
        system_prompt = f"""
        You are a shopping intent parser. Your task is to analyze the user's request and extract key information into a structured JSON object.

        The JSON object MUST contain these fields:
        - "product_description": A detailed description of the product the user wants.
        - "quantity": The number of items to buy. Default is 1.
        - "max_price": The maximum acceptable price as a float. If not specified, use null.
        - "min_rating": The minimum acceptable product rating. Default is 4.0.
        - "delivery_urgency": The user's delivery preference. Must be one of: "low", "medium", "high".
        - "preferred_payment_methods": A list (array) of payment methods the user can use, such as ["alipay", "visa", "usdc"]. If the user does not state any preference, use an empty list.

        User's request: "{user_input}"

        Respond ONLY with the JSON object, and nothing else.
        """
        try:
            # 使用与Alipay Agent相同的ChatAgent
            intent_agent = ChatAgent(system_message=system_prompt, model=self.model)
            response = await intent_agent.astep(user_input)
            content = response.msgs[0].content

            # 从模型返回的文本中提取JSON
            start = content.find('{')
            end = content.rfind('}') + 1
            if start == -1 or end == 0:
                raise ValueError("LLM did not return a valid JSON object.")
            
            parsed_json = json.loads(content[start:end])
            logger.info(f"✅ Intent parsed successfully: {parsed_json}")
            return parsed_json

        except Exception as e:
            logger.error(f"❌ Intent understanding failed: {str(e)}. Falling back to default.")
            return {
                "product_description": user_input,
                "quantity": 1,
                "max_price": None,
                "min_rating": 4.0,
                "delivery_urgency": "low",
                "preferred_payment_methods": []
            }

    def set_strategy_from_intent(self, intent: Dict) -> PurchaseStrategy:
        """根据解析出的意图，设定本次购买的策略"""
        urgency = intent.get("delivery_urgency", "low")
        if urgency == "high":
            strategy = PurchaseStrategy.FASTEST
        elif intent.get("min_rating", 4.0) >= 4.5:
            strategy = PurchaseStrategy.BEST_RATED
        elif intent.get("max_price") and float(intent["max_price"]) < 100:
            strategy = PurchaseStrategy.CHEAPEST
        else:
            strategy = PurchaseStrategy.PRIME
        logger.info(f"⚙️ Purchase strategy set to: {strategy.value}")
        return strategy

    async def search_amazon_products(self, intent: Dict, strategy: PurchaseStrategy) -> List[AmazonProduct]:
        """调用亚马逊API搜索商品，并根据策略排序"""
        logger.info(f"🔍 Searching Amazon for: {intent['product_description']}")
        try:
            # 为每次搜索创建新的会话
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.amazon_search_api,
                    params={"q": intent["product_description"], "domain": "amazon.com"},
                    timeout=15
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    products = []
                    
                    # 添加调试信息
                    logger.info(f"✅ API 返回数据: {len(data)} 条记录")
                    
                    for item in data[:10]:  # 只处理前10个结果
                        try:
                            # 添加更多调试信息
                            logger.info(f"处理商品: {item.get('title', '无标题')[:30]}...")
                            
                            # 安全地获取价格和评分
                            price_str = str(item.get("price", "0")).replace("$", "").replace(",", "").strip()
                            price = float(price_str) if price_str and price_str != "None" else 0.0
                            rating = float(item.get("rating", 4.0)) if item.get("rating") else 4.0
                            
                            if intent.get("max_price") and price > intent["max_price"]:
                                continue
                            if rating < intent.get("min_rating", 4.0):
                                continue
                            
                            products.append(AmazonProduct(
                                asin=item.get("asin", "UNKNOWN"),
                                title=item.get("title", "No Title"),
                                price=price,
                                currency="USD",
                                merchant_id="Amazon",
                                delivery_speed=5 if item.get("brand", "").lower() in ["apple", "sony"] else 4 if item.get("is_prime") else 2,
                                rating=rating,
                                prime_eligible=item.get("is_prime", True),
                                url=f"https://www.amazon.com/dp/{item.get('asin', '')}"
                            ))
                        except (ValueError, TypeError) as e:
                            logger.error(f"处理商品时出错: {e}")
                            continue  # 跳过无法解析价格或评分的商品
                    
                    # 根据策略排序
                    if strategy == PurchaseStrategy.CHEAPEST:
                        products.sort(key=lambda x: x.price)
                    elif strategy == PurchaseStrategy.FASTEST:
                        products.sort(key=lambda x: -x.delivery_speed)
                    elif strategy == PurchaseStrategy.BEST_RATED:
                        products.sort(key=lambda x: -x.rating)
                    else:  # PRIME
                        products.sort(key=lambda x: (not x.prime_eligible, -x.rating))
                    
                    logger.info(f"✅ Found {len(products)} suitable products.")
                    return products
                    
        except Exception as e:
            logger.error(f"❌ Amazon search failed: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            # 返回空列表而不是抛出异常
            return []

    async def _mock_payment(self, amount: float, merchant_id: str) -> Dict:
        """模拟支付流程"""
        logger.info(f"💰 Initiating MOCK payment of ${amount} to {merchant_id}")
        await asyncio.sleep(1) # 模拟网络延迟
        return {"status": "success", "transaction_id": "mock-tx-123456"}

    async def autonomous_purchase(self, user_input: str) -> Dict:
        """
        完整的自主购买流程。这是A2A Agent的核心执行函数。
        它会解析意图，搜索，并根据策略自动选择最优商品进行购买。
        """
        try:
            # 1. 理解意图
            intent = await self.understand_intent(user_input)

            # 2. 设定策略
            strategy = self.set_strategy_from_intent(intent)

            # 3. 搜索商品
            products = await self.search_amazon_products(intent, strategy)
            if not products:
                return {
                    "status": "error", 
                    "message": "未能找到任何符合您要求的商品。",
                    "response": "很抱歉，我无法找到符合您要求的商品。请尝试使用不同的关键词或放宽搜索条件。"
                }

            # 4. 选出最优商品
            best_product = products[0]
            solution = {
                "status": "solution",
                "asin": best_product.asin,
                "title": best_product.title,
                "unit_price": best_product.price,
                "quantity": intent.get("quantity", 1),
                "total_amount": best_product.price * intent.get("quantity", 1),
                "currency": "USD",
                "product_url": best_product.url,
                "strategy": strategy.value,
            }
            
            # 5. 调用 Alipay A2A Agent 发起支付
            logger.info("📞 Calling Alipay A2A Agent to create payment...")
            try:
                # 使用A2A客户端连接支付宝Agent
                ALIPAY_AGENT_URL = "http://0.0.0.0:5005"
                logger.info(f"🔗 Connecting to Alipay A2A Agent at {ALIPAY_AGENT_URL}")
                print(f"🔗 正在连接支付宝 A2A Agent: {ALIPAY_AGENT_URL}")

                # 构造支付请求的文本
                payment_request_text = f"请为商品 '{solution['title']}' 创建一个总价为 {solution['total_amount']:.2f} USD 的支付订单。"
                logger.info(f"📤 Sending payment request: {payment_request_text}")
                print(f"📤 发送支付请求: {payment_request_text}")

                # 使用A2AClient发送请求
                alipay_client = A2AClient(ALIPAY_AGENT_URL)
                payment_response = alipay_client.ask(payment_request_text)

                print(f"📥 收到支付宝 Agent 响应: {payment_response}")
                logger.info("✅ Successfully received payment info from Alipay Agent.")

                # 将支付信息附加到最终结果中
                solution['payment_info'] = payment_response
                solution['status'] = 'payment_initiated'
                solution['response'] = f"✅ 已为您找到最适合的商品：{solution['title']}，价格：${solution['total_amount']:.2f}。\n\n**支付信息**：\n{payment_response}"
                
            except Exception as e:
                logger.error(f"❌ Failed to call Alipay Agent: {e}")
                import traceback
                error_details = traceback.format_exc()
                logger.error(f"详细错误: {error_details}")
                print(f"❌ 连接支付宝 Agent 失败: {e}")
                print(f"详细错误: {error_details}")
                
                # 尝试使用不同的端点
                try:
                    print("🔄 尝试使用备用端点...")
                    response = requests.post(
                        f"{ALIPAY_AGENT_URL}/a2a/tasks/send",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )
                    response.raise_for_status()
                    result = response.json()
                    print(f"✅ 备用端点成功: {result}")
                    
                    # 从响应中提取文本内容
                    payment_response_html = ""
                    if "artifacts" in result and len(result["artifacts"]) > 0:
                        parts = result["artifacts"][0].get("parts", [])
                        if parts and len(parts) > 0:
                            text_part = next((p for p in parts if p.get("type") == "text"), None)
                            if text_part:
                                payment_response_html = text_part.get("text", "")
                    
                    if payment_response_html:
                        solution['payment_info'] = payment_response_html
                        solution['status'] = 'payment_initiated'
                        solution['response'] = f"✅ 已为您找到最适合的商品：{solution['title']}，价格：${solution['total_amount']:.2f}。\n\n**支付信息**：\n{payment_response_html}"
                        return solution
                except Exception as backup_error:
                    print(f"❌ 备用端点也失败: {backup_error}")
                
                solution['payment_info'] = f"Error: Could not connect to Alipay Agent. {str(e)}"
                solution['status'] = 'payment_failed'
                solution['response'] = f"✅ 已为您找到最适合的商品：{solution['title']}，价格：${solution['total_amount']:.2f}。\n\n但无法连接到支付宝服务，请稍后重试。错误：{str(e)}"
            
            return solution
            
        except Exception as e:
            logger.error(f"❌ Autonomous purchase failed: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            
            return {
                "status": "error",
                "message": f"处理您的请求时出错: {str(e)}",
                "response": f"很抱歉，处理您的请求时出现了技术问题：{str(e)}。请稍后重试。"
            }

# ==============================================================================
#  A2A 服务器的实现
# ==============================================================================
class AmazonA2AServer(A2AServer, AmazonServiceManager):
    """
    最终的A2A服务器，整合了网络服务和亚马逊购物业务逻辑。
    """
    def __init__(self, agent_card: AgentCard):
        A2AServer.__init__(self, agent_card=agent_card)
        AmazonServiceManager.__init__(self)
        print("✅ [AmazonA2AServer] Server fully initialized and ready.")

    def handle_task(self, task):
        f"""A2A服务器的核心处理函数。"""
        text = task.message.get("content", {}).get("text", "")
        print(f"📩 [AmazonA2AServer] Received task: '{text}'")

        if not text:
            response_text = "错误: 收到了一个空的请求。"
            task.status = TaskStatus(state=TaskState.FAILED)
        else:
            try:
                # 使用nest_asyncio允许在已有事件循环中运行新的事件循环
                import nest_asyncio
                nest_asyncio.apply()
                
                # 使用asyncio.run运行异步函数，它会创建新的事件循环
                import asyncio
                result = asyncio.run(self.autonomous_purchase(text))
                
                # 使用 result 中的 response 字段或构建响应
                if "response" in result:
                    response_text = result["response"]
                else:
                    # 格式化输出
                    if result.get('status') == 'solution' or result.get('status') == 'payment_initiated':
                        response_text = (
                            f"✅ **方案已生成**\n\n"
                            f"**商品详情:**\n"
                            f"- **名称**: {result.get('title', '未知商品')}\n"
                            f"- **总价**: ${result.get('total_amount', 0):.2f} {result.get('currency', 'USD')}\n"
                        )
                        
                        if result.get('product_url'):
                            response_text += f"- **链接**: {result.get('product_url')}\n\n"
                        
                        if result.get('payment_info'):
                            response_text += f"**支付信息:**\n{result.get('payment_info')}"
                    else:
                        # 安全地获取错误消息
                        error_msg = result.get('message', '未知错误')
                        response_text = f"❌ **操作失败**\n\n原因: {error_msg}"

                task.status = TaskStatus(state=TaskState.COMPLETED)
                print("💬 [AmazonA2AServer] Processing complete.")

            except Exception as e:
                import traceback
                print(f"❌ [AmazonA2AServer] Critical error during task handling: {e}")
                traceback.print_exc()
                response_text = f"服务器内部错误: {e}"
                task.status = TaskStatus(state=TaskState.FAILED)

        task.artifacts = [{"parts": [{"type": "text", "text": str(response_text)}]}]
        return task

def main():
    """主函数，用于配置和启动A2A服务器"""
    port = int(os.environ.get("AMAZON_A2A_PORT", 5011))
    
    agent_card = AgentCard(
        name="Amazon Autonomous Purchase A2A Agent",
        description="An A2A agent that autonomously understands shopping requests, "
                    "searches Amazon, and purchases the best product based on a smart strategy.",
        url=f"http://localhost:{port}",
        skills=[
            AgentSkill(name="autonomous_purchase", description="Handle the entire purchase flow from a single user request.")
        ]
    )
    
    server = AmazonA2AServer(agent_card)
    
    print("\n" + "="*60)
    print("🚀 Starting Amazon Autonomous Purchase A2A Server...")
    print(f"👂 Listening on http://localhost:{port}")
    print("="*60 + "\n")
    
    run_server(server, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()






