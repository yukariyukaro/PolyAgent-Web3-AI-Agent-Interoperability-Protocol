# MCP 服务器配置指南

本文档说明如何在 Cursor、Claude Desktop 等客户端中配置 MCP (Model Context Protocol) 服务器。

## 支持的 MCP 服务器

### 1. Playwright MCP Server (微软官方)
**功能**: 浏览器自动化、网页截图、页面内容提取、元素交互

**配置**:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

**可选配置参数**:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--headless",
        "--browser=chrome"
      ]
    }
  }
}
```

### 2. 支付宝 MCP Server (项目内置)
**功能**: 支付宝支付订单创建、查询、沙箱环境测试

**配置**:
```json
{
  "mcpServers": {
    "alipay": {
      "command": "node",
      "args": ["./AgentCore/Mcp/alipay_server.js"],
      "cwd": "你的项目路径"
    }
  }
}
```

## 在不同客户端中配置

### Cursor IDE
1. 打开 Cursor 设置
2. 导航到 `MCP` 部分  
3. 点击 `Add new MCP Server`
4. 输入服务器名称和配置

或者直接编辑配置文件：
- **Windows**: `%USERPROFILE%\.cursor\mcp.json`
- **macOS**: `~/.cursor/mcp.json`
- **Linux**: `~/.cursor/mcp.json`

### Claude Desktop
编辑配置文件：
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

### VS Code (with GitHub Copilot)
```bash
# 安装 Playwright MCP
code --add-mcp '{"name":"playwright","command":"npx","args":["@playwright/mcp@latest"]}'
```

## 完整配置示例

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--headless"],
      "env": {
        "NODE_ENV": "production"
      }
    },
    "alipay": {
      "command": "node", 
      "args": ["./AgentCore/Mcp/alipay_server.js"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

## 故障排除

### 1. Smithery 安装失败
如果遇到 Smithery 相关错误，建议使用直接的 npx 方式：
```json
{
  "command": "npx",
  "args": ["@playwright/mcp@latest"]
}
```

### 2. 权限问题
确保有足够权限运行 npx 命令和访问项目目录。

### 3. 网络问题
如果下载失败，可以先手动安装：
```bash
npm install -g @playwright/mcp
```

然后使用本地路径：
```json
{
  "command": "playwright-mcp",
  "args": []
}
```

## 验证配置

配置完成后，重启客户端，在对话中尝试：
- "请帮我打开 https://www.google.com 并截图"
- "请帮我创建一个支付宝测试订单"

如果配置正确，应该能看到相应的工具调用。 
 