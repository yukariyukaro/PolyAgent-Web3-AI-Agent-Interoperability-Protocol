#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动支付流程测试脚本
验证用户手动输入确认的支付流程
"""

import requests
import time
import json

def test_manual_payment_flow():
    """测试手动支付流程"""
    base_url = "http://localhost:5000"
    
    print("🧪 开始测试手动支付流程...")
    print("=" * 60)
    
    # 步骤1: 用户请求购买服务
    print("\n📱 步骤1: 用户请求购买服务")
    step1_message = "I want to purchase your premium service for $15"
    
    try:
        response = requests.post(f"{base_url}/market-trade", 
                               json={"message": step1_message})
        if response.status_code == 200:
            print("✅ 订单创建成功")
            print("📄 AI响应内容:")
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
            print("\n💡 用户应该:")
            print("   1. 点击支付宝支付按钮")
            print("   2. 在支付宝中完成支付")
            print("   3. 手动输入 'Payment completed successfully' 继续")
        else:
            print(f"❌ 步骤1失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 步骤1异常: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("⏸️  流程暂停 - 等待用户手动确认...")
    print("请按照以下步骤操作:")
    print("1. 在浏览器中访问 http://localhost:3000")
    print("2. 切换到 'Payment Bridge' 助手")
    print("3. 在聊天框中输入: Payment completed successfully")
    print("4. 然后按回车键继续后续流程")
    
    input("\n按回车键继续测试剩余步骤...")
    
    # 步骤2: 模拟用户手动确认支付成功
    print("\n✅ 步骤2: 用户手动确认支付成功")
    step2_message = "Payment completed successfully"
    
    try:
        response = requests.post(f"{base_url}/market-trade", 
                               json={"message": step2_message})
        if response.status_code == 200:
            print("✅ 支付确认成功")
            print("📄 AI响应内容:")
            print(response.text[:300] + "..." if len(response.text) > 300 else response.text)
        else:
            print(f"❌ 步骤2失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 步骤2异常: {e}")
    
    # 步骤3: 代币授权
    print("\n🔐 步骤3: 代币授权")
    step3_message = "authorize tokens for trading contract"
    
    try:
        response = requests.post(f"{base_url}/market-trade", 
                               json={"message": step3_message})
        if response.status_code == 200:
            print("✅ 代币授权成功")
        else:
            print(f"❌ 步骤3失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 步骤3异常: {e}")
    
    # 步骤4: 代币转账
    print("\n💸 步骤4: 代币转账")
    step4_message = "transfer tokens to merchant wallet"
    
    try:
        response = requests.post(f"{base_url}/market-trade", 
                               json={"message": step4_message})
        if response.status_code == 200:
            print("✅ 代币转账成功")
        else:
            print(f"❌ 步骤4失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 步骤4异常: {e}")
    
    # 步骤5: PayPal转换
    print("\n💰 步骤5: PayPal转换")
    step5_message = "convert tokens to paypal payment"
    
    try:
        response = requests.post(f"{base_url}/market-trade", 
                               json={"message": step5_message})
        if response.status_code == 200:
            print("✅ PayPal转换成功")
        else:
            print(f"❌ 步骤5失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 步骤5异常: {e}")
    
    # 步骤6: 服务交付
    print("\n📁 步骤6: 服务交付")
    step6_message = "deliver premium service"
    
    try:
        response = requests.post(f"{base_url}/market-trade", 
                               json={"message": step6_message})
        if response.status_code == 200:
            print("✅ 服务交付成功")
            print("📄 下载链接应包含在响应中:")
            print(response.text[:400] + "..." if len(response.text) > 400 else response.text)
        else:
            print(f"❌ 步骤6失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 步骤6异常: {e}")
    
    print("\n🎉 手动支付流程测试完成!")
    print("=" * 60)
    
    return True

def check_server_status():
    """检查服务器状态"""
    try:
        response = requests.get("http://localhost:5000/")
        if response.status_code == 200:
            print("✅ 后端服务器运行正常")
            return True
        else:
            print(f"❌ 后端服务器状态异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接后端服务器: {e}")
        print("请确保运行 'python app.py' 启动后端服务器")
        return False

def main():
    """主函数"""
    print("🧪 PolyAgent 手动支付流程测试")
    print("=" * 60)
    
    # 检查服务器状态
    if not check_server_status():
        return
    
    print("\n🎯 测试说明:")
    print("本测试验证手动确认的支付流程:")
    print("1. 用户请求购买服务")
    print("2. 创建支付宝订单（需要手动确认）")
    print("3. 后续步骤可以手动逐步进行")
    print("4. 最终获得文件下载链接")
    
    input("\n按回车键开始测试...")
    
    # 运行测试
    test_manual_payment_flow()

if __name__ == "__main__":
    main() 