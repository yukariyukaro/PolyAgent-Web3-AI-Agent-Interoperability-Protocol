#!/usr/bin/env python3
"""
PolyAgent API Server 启动脚本
"""

import os
import sys
import subprocess
from config import get_config

def check_dependencies():
    """检查依赖项"""
    required_packages = [
        'flask',
        'flask-cors', 
        'camel-ai',
        'web3',
        'eth-account',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_environment():
    """检查环境变量"""
    config = get_config()
    
    print("🔧 环境配置检查:")
    print(f"   - OpenAI API Key: {'✅ 已配置' if config.OPENAI_API_KEY else '❌ 未配置'}")
    print(f"   - IoTeX RPC: ✅ {config.IOTEX_TESTNET_RPC}")
    print(f"   - 服务端口: ✅ {config.FLASK_PORT}")
    
    if not config.OPENAI_API_KEY:
        print("\n⚠️  请设置 OPENAI_API_KEY 环境变量:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("   或在 .env 文件中配置")
    
    return config.validate_config()

def start_server():
    """启动服务器"""
    print("🚀 启动 PolyAgent API Server...")
    
    # 设置环境变量
    os.environ.setdefault('FLASK_ENV', 'development')
    
    # 启动应用
    try:
        from app import app, config
        print(f"   服务地址: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
        app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    print("=" * 60)
    print("🤖 PolyAgent Web3 AI Agent API Server")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    print()
    
    # 检查环境
    if not check_environment():
        print("\n⚠️  配置不完整，但服务仍可启动（部分功能可能不可用）")
    
    print()
    
    # 启动服务
    start_server()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 