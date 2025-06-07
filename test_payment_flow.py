#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

def test_payment_flow():
    """测试完整的支付流程"""
    
    print("🧪 测试支付流程和自动确认功能")
    print("="*60)
    
    # API endpoint
    url = "http://localhost:5000/market-trade"
    
    # 第一步：创建订单
    print("📝 第一步：创建支付订单")
    message1 = "I want to purchase a custom story service for $15"
    
    try:
        response1 = requests.post(url, json={"message": message1}, timeout=30)
        
        if response1.status_code == 200:
            content1 = response1.text
            print("✅ 订单创建成功")
            
            # 检查关键元素
            checks1 = [
                ("包含支付按钮", "alipay-payment-button" in content1 or "Pay with Alipay" in content1),
                ("包含自动确认提示", "automatically confirm" in content1 or "10 seconds" in content1),
                ("包含订单信息", "ORDER2025" in content1 and "$15" in content1),
                ("包含点击事件", "handleAlipayPayment" in content1)
            ]
            
            for check_name, passed in checks1:
                status = "✅" if passed else "❌"
                print(f"  {status} {check_name}")
                
            print("\n" + "-"*50)
            print("🔍 支付按钮HTML检查:")
            
            # 查找支付按钮相关内容
            lines = content1.split('\n')
            for i, line in enumerate(lines):
                if 'alipay-payment-button' in line or 'Pay with Alipay' in line:
                    print(f"第{i+1}行: {line.strip()}")
                    
            print("\n" + "-"*50)
            print("📋 自动确认说明:")
            print("• 点击支付按钮后，系统会打开支付页面")
            print("• 10秒后AI会自动发送支付成功的消息")
            print("• 无需用户手动确认支付状态")
            
            # 模拟第二步 - 支付成功（这会在实际中由前端自动触发）
            print(f"\n⏰ 模拟10秒后的自动支付确认...")
            time.sleep(2)  # 实际测试中缩短等待时间
            
            print("🔄 第二步：自动支付确认")
            message2 = "Payment completed successfully"
            
            response2 = requests.post(url, json={"message": message2}, timeout=30)
            
            if response2.status_code == 200:
                content2 = response2.text
                print("✅ 支付确认成功")
                
                # 检查支付确认响应
                checks2 = [
                    ("包含支付状态", "Payment" in content2 and "SUCCESS" in content2),
                    ("包含下一步提示", "Next Step" in content2 or "authorize" in content2),
                    ("包含步骤指示器", "2/6" in content2 or "Step 2" in content2)
                ]
                
                for check_name, passed in checks2:
                    status = "✅" if passed else "❌"
                    print(f"  {status} {check_name}")
                    
            else:
                print(f"❌ 支付确认失败: {response2.status_code}")
                
        else:
            print(f"❌ 订单创建失败: {response1.status_code}")
            print(response1.text)
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

    print("\n🏁 支付流程测试完成")

if __name__ == "__main__":
    print("🚀 开始测试支付流程")
    print("请确保服务器已启动: python app.py")
    print()
    
    test_payment_flow() 