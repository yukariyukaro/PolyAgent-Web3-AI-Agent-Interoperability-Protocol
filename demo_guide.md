# PolyAgent Web3 Payment Bridge Demo Guide

## 🎯 Demo Overview
This demo showcases a complete cross-payment bridge: **Alipay → Cryptocurrency → PayPal**

**Scenario**: Customer uses familiar Alipay payment → System converts to USDT tokens → Merchant receives PayPal payment → Service delivered

---

## 📋 Demo Steps (Copy & Paste These Exact Messages)

### 🔹 Step 1: Create Order
**Frontend Input**: 
```
I want to purchase a custom story service for $15
```
**Expected Response**: Alipay payment order creation with payment link

---

### 🔹 Step 2: Confirm Payment
**Frontend Input**: 
```
Payment completed successfully
```
**Expected Response**: Payment status confirmation and token preparation

---

### 🔹 Step 3: Token Authorization
**Frontend Input**: 
```
Please authorize and mint tokens to my wallet
```
**Expected Response**: Token authorization process with wallet integration prompt

---

### 🔹 Step 4: Transfer to Merchant
**Frontend Input**: 
```
Transfer 15 USDT to merchant wallet
```
**Expected Response**: Token transfer execution with blockchain confirmation

---

### 🔹 Step 5: PayPal Conversion
**Frontend Input**: 
```
Convert tokens to PayPal payment for merchant
```
**Expected Response**: PayPal payment animation and merchant receipt confirmation

---

### 🔹 Step 6: Service Delivery
**Frontend Input**: 
```
Please provide my custom story about a brave knight
```
**Expected Response**: Custom story delivery with complete transaction summary

---

## 🎬 Demo Features

### ✨ What You'll See:
- **Real Alipay MCP Integration**: Actual payment order creation
- **Blockchain Operations**: Token authorization and transfer on IoTeX testnet
- **PayPal Animation**: Simulated merchant payment receipt
- **Wallet Integration**: Connect and sign transactions with your Web3 wallet
- **Complete Flow**: End-to-end payment bridge demonstration

### 🔧 Technical Components:
- **Multi-Agent Coordination**: Automatic routing between 4 different AI agents
- **Cross-Payment Integration**: Alipay ↔ Crypto ↔ PayPal
- **Real-Time Streaming**: Live progress updates in the chat interface
- **Responsive UI**: Beautiful Material Design with smooth animations

---

## 🚀 Quick Start

1. **Connect Wallet**: Use the "Connect Wallet" button in the top-right
2. **Switch to Payment Bridge**: Click "Payment Bridge" in the header  
3. **Follow Steps**: Copy and paste each message exactly as shown above
4. **Watch the Magic**: See how traditional and crypto payments seamlessly connect

---

## 💡 Technical Details

### Backend Agent Routing:
- **Step 1-2**: Alipay MCP Agent
- **Step 3-4**: IoTeX Blockchain Agent  
- **Step 5**: PayPal MCP Agent
- **Step 6**: Story Generation Agent

### Frontend Features:
- **Streaming Responses**: Real-time AI agent communication
- **Wallet Integration**: RainbowKit for Web3 connectivity
- **Payment Animations**: Custom CSS animations for PayPal receipt
- **Responsive Design**: Mobile-friendly Material UI

### Smart Routing Logic:
The system automatically detects keywords in your input and routes to the appropriate agent:
- `purchase, buy, order, service, $` → Alipay Agent
- `payment completed, success` → Payment Status Agent  
- `authorize, mint tokens` → Token Authorization
- `transfer, merchant wallet` → Blockchain Transfer
- `convert, paypal` → PayPal Conversion
- `story, knight, provide` → Service Delivery

---

## 🎯 Expected Timeline
**Total Demo Duration**: ~3-5 minutes
- Each step takes 10-30 seconds
- Real blockchain operations take 30-60 seconds
- PayPal simulation is instant

---

## 🛠️ Troubleshooting

**If a step doesn't work**:
1. Make sure you copied the exact text
2. Wait for the previous step to complete fully
3. Check that your wallet is connected (for token steps)
4. Refresh the page and restart if needed

**Network Requirements**:
- Backend: Alipay MCP server running
- Blockchain: IoTeX testnet connection
- Frontend: Modern browser with Web3 support

---

## 🎉 Success Indicators

You'll know the demo is working when you see:
- ✅ Alipay payment link generated
- ✅ Payment status confirmed
- ✅ Token authorization successful
- ✅ Blockchain transaction confirmed
- ✅ PayPal animation appears
- ✅ Custom story delivered
- ✅ Complete transaction summary

---

**Ready to start? Connect your wallet and begin with Step 1!** 🚀 