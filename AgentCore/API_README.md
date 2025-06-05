# PolyAgent API 接口文档

## 概述

PolyAgent Web3 AI Agent 提供了三个主要的API接口，支持不同类型的AI助手功能。

## API 端点

### 1. Market Trade Agent (`/market-trade`)

**功能**: IoTeX 测试网专用的区块链交易助手

**请求方式**: `POST`

**请求格式**:
```json
{
  "message": "用户输入的文本"
}
```

**支持的功能**:
- 查询账户 IOTX 主币余额
- 查询 ERC20 代币余额  
- 查询 ERC20 授权额度（allowance）
- 查询 ERC20 代币合约信息
- 执行 ERC20 代币授权（approve）
- 执行 ERC20 代币转账（transferFrom）

**示例请求**:
```bash
curl -X POST http://localhost:5000/market-trade \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我查询一下ERC20代币的余额"}'
```

**内置参数**:
- PolyAgent Token 合约地址: `0xD3286E20Ff71438D9f6969828F7218af4A375e2f`
- 发送者地址: `0xE4949a0339320cE9ec93c9d0836c260F23DFE8Ca`
- 授权者地址: `0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE`
- 默认精度: 18
- 默认金额: 2

### 2. Market Monitor Agent (`/market-monitor`)

**功能**: 加密货币市场监控和分析助手

**请求方式**: `POST`

**请求格式**:
```json
{
  "message": "用户输入的文本"
}
```

**支持的功能**:
- 查询加密货币历史价格
- 获取加密货币相关新闻
- 市场趋势分析
- 价格数据分析

**示例请求**:
```bash
curl -X POST http://localhost:5000/market-monitor \
  -H "Content-Type: application/json" \
  -d '{"message": "我想了解比特币的最新价格"}'
```

### 3. 原始接口 (`/polyPost`)

**功能**: 原有的综合策略制定助手（保持向后兼容）

**请求方式**: `POST`

**请求格式**:
```json
{
  "message": "用户输入的文本"
}
```

### 4. 状态检查 (`/agents/status`)

**功能**: 检查所有Agent的运行状态

**请求方式**: `GET`

**响应格式**:
```json
{
  "market_trade": "正常",
  "market_monitor": "正常"
}
```

## 响应格式

所有接口都返回**流式响应**（Server-Sent Events），Content-Type为 `text/plain`。

响应会实时流式传输Agent的处理结果，包括：
- 工具调用过程
- 中间处理步骤
- 最终结果

## 使用示例

### Python 客户端示例

```python
import requests

def call_market_trade(message):
    response = requests.post(
        "http://localhost:5000/market-trade",
        json={"message": message},
        stream=True
    )
    
    for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
        if chunk:
            print(chunk, end='')

# 使用示例
call_market_trade("查询我的IOTX余额")
```

### JavaScript 客户端示例

```javascript
async function callMarketMonitor(message) {
    const response = await fetch('/market-monitor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        console.log(chunk);
    }
}

// 使用示例
callMarketMonitor("USDT的市场新闻");
```

## 测试

运行测试脚本验证API功能：

```bash
# 启动服务
cd AgentCore
python app.py

# 在另一个终端运行测试
python test_api.py
```

## 错误处理

如果Agent执行过程中出现错误，会在流式响应中包含错误信息：
- `Market Trade Agent 错误: [具体错误信息]`
- `Market Monitor Agent 错误: [具体错误信息]`

## 注意事项

1. **安全性**: Market Trade Agent涉及私钥操作，请确保在安全环境中使用
2. **网络**: 依赖IoTeX测试网和外部API，需要稳定的网络连接
3. **限制**: 仅限测试网使用，不可用于主网交易
4. **API密钥**: 需要配置OpenAI API密钥和相关第三方服务密钥 