import {
	faBolt,
	faCog,
	faCommentAlt,
	faHistory,
	faMicrophone,
	faPaperPlane,
	// faUser,
	faPlus,
	faTimes,
	faWallet,
	faSignature,
	faPen,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEffect, useRef, useState } from "react";

// RainbowKit 相关导入
import "@rainbow-me/rainbowkit/styles.css";

// 添加自定义样式
import "./ai-response.css";

// Stagewise dev-tool integration (development only)
declare const process: any; // Suppress TypeScript errors for process

if (typeof process !== 'undefined' && process.env?.NODE_ENV === 'development') {
  // Initialize stagewise toolbar asynchronously to avoid blocking the main app
  const initStagewise = async () => {
    try {
      // Dynamic import to handle optional dependency
      const stagewiseModule = await eval('import("@stagewise/toolbar")') as any;
      const { initToolbar } = stagewiseModule;
      
      const stagewiseConfig = {
        plugins: []
      };
      
      // Ensure toolbar container exists
      let toolbarContainer = document.getElementById('stagewise-toolbar-container');
      if (!toolbarContainer) {
        toolbarContainer = document.createElement('div');
        toolbarContainer.id = 'stagewise-toolbar-container';
        toolbarContainer.style.zIndex = '999999';
        document.body.appendChild(toolbarContainer);
      }
      
      initToolbar(stagewiseConfig);
      console.log('✅ Stagewise toolbar initialized');
    } catch (error) {
      console.warn('🔧 Stagewise toolbar not available (install with: npm install @stagewise/toolbar --save-dev)');
    }
  };
  
  // Initialize after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initStagewise);
  } else {
    initStagewise();
  }
}

import {
	ConnectButton,
	getDefaultConfig,
	RainbowKitProvider,
} from "@rainbow-me/rainbowkit";
import {
	WagmiProvider,
	useAccount,
	useSignMessage,
	useBalance,
	useSendTransaction,
} from "wagmi";
import { mainnet, polygon, optimism, arbitrum, base } from "wagmi/chains";
import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { http } from "wagmi";
import { parseEther } from "viem";
import type { Chain } from "wagmi/chains";

// 定义 IoTeX 测试网络
const iotexTestnet: Chain = {
  id: 4690,
  name: "IoTeX Testnet",
  nativeCurrency: {
    name: "IoTeX",
    symbol: "IOTX",
    decimals: 18,
  },
  rpcUrls: {
    default: {
      http: ["https://babel-api.testnet.iotex.one"],
    },
  },
  blockExplorers: {
    default: {
      name: "IoTeX Testnet Explorer",
      url: "https://testnet.iotexscan.io",
    },
  },
  contracts: {},
  testnet: true,
};


// 配置 RainbowKit
const config = getDefaultConfig({
	appName: "PolyAgent",
	// 从 WalletConnect Cloud 获取项目ID: https://cloud.walletconnect.com/
	// 1. 注册/登录 WalletConnect Cloud
	// 2. 创建一个新项目并输入应用名称和URL
	// 3. 复制生成的项目ID到这里
  // projectId: "d56e1374c9d4380694fc205749b5eec2",
	projectId: atob("ZDU2ZTEzNzRjOWQ0MzgwNjk0ZmMyMDU3NDliNWVlYzI="),
	chains: [mainnet, polygon, optimism, arbitrum, base, iotexTestnet],
	transports: {
		// [mainnet.id]: http("https://eth-mainnet.g.alchemy.com/v2/demo"),
		// [polygon.id]: http("https://polygon-mainnet.g.alchemy.com/v2/demo"),
		// [optimism.id]: http("https://opt-mainnet.g.alchemy.com/v2/demo"),
		// [arbitrum.id]: http("https://arb-mainnet.g.alchemy.com/v2/demo"),
		// [base.id]: http("https://base-mainnet.g.alchemy.com/v2/demo"),
    [iotexTestnet.id]: http("https://babel-api.testnet.iotex.one"),
	},
	ssr: true,
});

const queryClient = new QueryClient();

interface Message {
	text: string;
	sender: "user" | "ai";
	type?: "html" | "text";
}

interface Conversation {
	id: string;
	title: string;
	messages: Message[];
	createdAt: number;
}

// 转账表单数据接口
interface TransferFormData {
	contractAddress: string;
	toAddress: string;
	amount: string;
	decimals: string;
	// 支付宝转代币专用字段
	senderAddress?: string;
	senderPrivateKey?: string;
	spenderPrivateKey?: string;
	rpcUrl?: string;
	chainId?: string;
}

// 添加AI助手类型枚举
type AIAgentType = "monitor" | "trade";

// 签名功能组件
function WalletSignature() {
  const { address, isConnected, chain } = useAccount();
  const { data: balance } = useBalance({ address });
  const [messageToSign, setMessageToSign] = useState("");
  const [signatureResult, setSignatureResult] = useState("");
  const [recipientAddress, setRecipientAddress] = useState("");
  const [sendAmount, setSendAmount] = useState("");
  const [showSignaturePanel, setShowSignaturePanel] = useState(false);
  const { signMessage, isPending: isSignPending } = useSignMessage({
    mutation: {
      onSuccess: (signature) => {
        setSignatureResult(signature);
        console.log("签名成功:", signature);
      },
      onError: (error) => {
        console.error("签名失败:", error);
        setSignatureResult(`签名失败: ${error.message}`);
      },
    },
  });

  const { sendTransaction, isPending: isSendPending } = useSendTransaction({
    mutation: {
      onSuccess: (hash) => {
        console.log("交易发送成功:", hash);
        alert(`交易发送成功! 哈希: ${hash}`);
      },
      onError: (error) => {
        console.error("交易发送失败:", error);
        alert(`交易发送失败: ${error.message}`);
      },
    },
  });

  const handleSignMessage = () => {
    if (!messageToSign.trim()) {
      alert("Please enter a message to sign");
      return;
    }
    signMessage({ message: messageToSign });
  };

  const handleSendTransaction = () => {
    if (!recipientAddress.trim() || !sendAmount.trim()) {
      alert("Please fill in recipient address and amount");
      return;
    }

    try {
      sendTransaction({
        to: recipientAddress as `0x${string}`,
        value: parseEther(sendAmount),
      });
    } catch (error) {
      console.error("交易参数错误:", error);
      alert("Transaction parameter error, please check address and amount format");
    }
  };

  if (!isConnected) {
    return (
      <div className="wallet-signature-panel p-4 bg-deep-black/50 backdrop-blur-sm rounded-lg border border-night-purple/20">
        <p className="text-text-secondary text-center">
          Please connect your wallet to use signature features
        </p>
      </div>
    );
  }

  return (
    <div className="wallet-signature-panel p-4 bg-deep-black/50 backdrop-blur-sm rounded-lg border border-night-purple/20 space-y-4">
      {/* 钱包信息 */}
      <div className="wallet-info border-b border-night-purple/20 pb-4">
        <h3 className="text-neon-cyan font-bold mb-2 flex items-center">
          <FontAwesomeIcon icon={faSignature} className="mr-2" />
          Wallet Signature Tools
        </h3>
        <div className="text-sm space-y-1">
          {/* <p><span className="text-text-secondary">地址:</span> <span className="text-neon-cyan font-mono">{address}</span></p> */}
          <p>
            <span className="text-text-secondary">Network:</span>{" "}
            <span className="text-neon-cyan">{chain?.name}</span>
          </p>
          <p>
            <span className="text-text-secondary">Balance:</span>{" "}
            <span className="text-neon-cyan">
              {balance
                ? `${parseFloat(balance.formatted).toFixed(4)} ${
                    balance.symbol
                  }`
                : "Loading..."}
            </span>
          </p>
        </div>
      </div>

      {/* 消息签名 */}
      <div className="message-signing">
        <h4 className="text-text-primary font-semibold mb-2 flex items-center">
          <FontAwesomeIcon icon={faPen} className="mr-2 text-xs" />
          Message Signing
        </h4>
        <div className="space-y-2">
          <textarea
            placeholder="Enter message to sign..."
            className="w-full p-2 bg-deep-black border border-night-purple/30 rounded text-text-primary placeholder-text-secondary resize-none"
            rows={2}
            value={messageToSign}
            onChange={(e) => setMessageToSign(e.target.value)}
          />
          <button
            onClick={handleSignMessage}
            disabled={isSignPending}
            className="w-full px-4 py-2 bg-gradient-to-r from-neon-cyan/20 to-night-purple/20 hover:from-neon-cyan/30 hover:to-night-purple/30 border border-neon-cyan/30 text-neon-cyan rounded transition-all disabled:opacity-50"
          >
            {isSignPending ? "Signing..." : "Sign Message"}
          </button>
          {signatureResult && (
            <div className="signature-result p-2 bg-deep-black/80 border border-neon-cyan/20 rounded">
              <p className="text-xs text-text-secondary mb-1">Signature Result:</p>
              <p className="text-xs text-neon-cyan font-mono break-all">
                {signatureResult}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* 发送交易 */}
      <div className="send-transaction">
        <h4 className="text-text-primary font-semibold mb-2">Send Transaction</h4>
        <div className="space-y-2">
                      <input
              type="text"
              placeholder="Recipient Address (0x...)"
              className="w-full p-2 bg-deep-black border border-night-purple/30 rounded text-text-primary placeholder-text-secondary"
              value={recipientAddress}
              onChange={(e) => setRecipientAddress(e.target.value)}
            />
            <input
              type="number"
              placeholder="Amount"
              step="0.001"
              className="w-full p-2 bg-deep-black border border-night-purple/30 rounded text-text-primary placeholder-text-secondary"
              value={sendAmount}
              onChange={(e) => setSendAmount(e.target.value)}
            />
          <button
            onClick={handleSendTransaction}
            disabled={isSendPending}
            className="w-full px-4 py-2 bg-gradient-to-r from-night-purple/20 to-neon-cyan/20 hover:from-night-purple/30 hover:to-neon-cyan/30 border border-night-purple/30 text-text-primary rounded transition-all disabled:opacity-50"
          >
            {isSendPending
              ? "Sending..."
              : `Send ${chain?.nativeCurrency.symbol || "Token"}`}
          </button>
        </div>
      </div>
    </div>
  );
}

function App() {
	const [messages, setMessages] = useState<Message[]>([]);
	const [inputMessage, setInputMessage] = useState("");
	const chatContainerRef = useRef<HTMLDivElement>(null);
	const [isTyping, setIsTyping] = useState(false);
	const textareaRef = useRef<HTMLTextAreaElement>(null);
	const [conversations, setConversations] = useState<Conversation[]>([]);
	const [currentConversationId, setCurrentConversationId] = useState<
		string | null
	>(null);

	const [showLogoOverlay, setShowLogoOverlay] = useState(false);

	// 转账表单相关状态
	const [showTransferForm, setShowTransferForm] = useState(false);
	const [transferFormData, setTransferFormData] = useState<TransferFormData>({
		contractAddress: "0xD3286E20Ff71438D9f6969828F7218af4A375e2f", // 默认PAT合约地址
		toAddress: "",
		amount: "",
		decimals: "18"
	});
	const [isSubmittingTransfer, setIsSubmittingTransfer] = useState(false);

	// 支付宝转代币的默认参数
	const alipayTransferDefaults = {
		testnet_rpc: "https://babel-api.testnet.iotex.io",
		chain_id: 4690,
		polyagent_token_contract: "0xD3286E20Ff71438D9f6969828F7218af4A375e2f",
		sender_address: "0xE4949a0339320cE9ec93c9d0836c260F23DFE8Ca",
		sender_private_key: "e4ad52fbc8c6fe3f4069af70363b24ca4453dbf472d92f83a8adf38e8010991f",
		spender_address: "0xf874871Bc0f99a06b5327F34AceAa80Ae71905DE",
		spender_private_key: "3efe78303dcf8ea3355ef363f04eb442e000081fe66ebcebf5d9cf19f3ace8b8",
		decimals: "18"
	};



	// 添加AI助手选择状态
	const [selectedAgent, setSelectedAgent] = useState<AIAgentType>("monitor");
	const [isAgentSwitching, setIsAgentSwitching] = useState(false);

	// Tooltip状态
	const [showTooltip, setShowTooltip] = useState<{
		show: boolean;
		agent: AIAgentType | null;
		position: { x: number; y: number };
	}>({
		show: false,
		agent: null,
		position: { x: 0, y: 0 }
	});

	// AI助手切换处理函数
	const handleAgentSwitch = async (agentType: AIAgentType) => {
		if (agentType === selectedAgent || isAgentSwitching) return;

		setIsAgentSwitching(true);

		// 模拟切换动画延迟
		await new Promise(resolve => setTimeout(resolve, 300));

		setSelectedAgent(agentType);
		setIsAgentSwitching(false);

		console.log(`AI助手已切换至: ${agentType === 'monitor' ? '加密货币监控' : '支付宝转代币'}`);
	};

	// Tooltip处理函数
	const handleMouseEnter = (agent: AIAgentType, event: React.MouseEvent) => {
		const rect = event.currentTarget.getBoundingClientRect();
		setShowTooltip({
			show: true,
			agent,
			position: {
				x: rect.left + rect.width / 2,
				y: rect.bottom + 8
			}
		});
	};

	const handleMouseLeave = () => {
		setShowTooltip({
			show: false,
			agent: null,
			position: { x: 0, y: 0 }
		});
	};

	// 获取Agent描述信息
	const getAgentDescription = (agent: AIAgentType) => {
		if (agent === "monitor") {
			return {
				title: "🚀 Cryptocurrency Market Assistant",
				description: "Get price data, analyze market trends and develop trading strategies",
				features: [


				]
			};
		} else {
			return {
				title: "💰 Payment Bridge Assistant",
				description: "Assist with token transfers and cross-border payment operations",
				features: [


				]
			};
		}
	};
  const [showSignaturePanel, setShowSignaturePanel] = useState(false);

	// 从本地存储加载对话
	useEffect(() => {
		const storedConversations = localStorage.getItem("poly-ai-conversations");
		if (storedConversations) {
			setConversations(JSON.parse(storedConversations));
		}

		const currentId = localStorage.getItem("poly-ai-current-conversation");
		if (currentId) {
			setCurrentConversationId(currentId);
			const currentConversation = JSON.parse(storedConversations || "[]").find(
				(conv: Conversation) => conv.id === currentId
			);
			
		}
	}, []);

	// 保存对话到本地存储
	useEffect(() => {
		if (conversations.length > 0) {
			localStorage.setItem(
				"poly-ai-conversations",
				JSON.stringify(conversations)
			);
		}

		if (currentConversationId) {
			localStorage.setItem(
				"poly-ai-current-conversation",
				currentConversationId
			);

			// 更新当前对话的消息
			const updatedConversations = conversations.map((conv) =>
				conv.id === currentConversationId ? { ...conv, messages } : conv
			);

			setConversations(updatedConversations);
			localStorage.setItem(
				"poly-ai-conversations",
				JSON.stringify(updatedConversations)
			);
		}
	}, [messages, currentConversationId]);

	// 创建粒子效果
	useEffect(() => {
		const particles = document.getElementById("particles");
		const particleCount = 30;

		if (particles) {
			for (let i = 0; i < particleCount; i++) {
				const particle = document.createElement("div");
				particle.classList.add("particle");

				// 随机位置
				particle.style.left = `${Math.random() * 100}%`;
				particle.style.top = `${Math.random() * 100}%`;

				// 随机大小
				const size = Math.random() * 3 + 1;
				particle.style.width = `${size}px`;
				particle.style.height = `${size}px`;

				// 随机透明度
				particle.style.opacity = `${Math.random() * 0.5 + 0.1}`;

				// 动画
				particle.style.animationName = "float";
				particle.style.animationDuration = `${Math.random() * 10 + 5}s`;
				particle.style.animationDelay = `${Math.random() * 5}s`;

				particles.appendChild(particle);
			}
		}
	}, []);

	// 创建新对话
	const createNewConversation = () => {
		console.log("创建新对话被调用");
		console.trace("调用堆栈");

		const newId = `conv-${Date.now()}`;
		const newConversation: Conversation = {
			id: newId,
			// title: `new Chat ${conversations.length + 1}`,
			title: `new Chat`,
			messages: [],
			createdAt: Date.now(),
		};

		setConversations((prev) => [newConversation, ...prev]);
		setCurrentConversationId(newId);
		setMessages([]);

		console.log("新对话创建完成，ID:", newId);
	};

	// 选择对话
	const selectConversation = (id: string) => {
		const conversation = conversations.find((conv) => conv.id === id);
		if (conversation) {
			setCurrentConversationId(id);
			setMessages(conversation.messages);
		}
	};

	// 删除对话
	const deleteConversation = (conversationId: string, e: React.MouseEvent) => {
		e.stopPropagation(); // 阻止事件冒泡，避免触发选择对话

		// 如果删除的是当前激活的对话
		if (conversationId === currentConversationId) {
			// 找到剩余对话中的第一个作为新的激活对话
			const remainingConversations = conversations.filter(conv => conv.id !== conversationId);

			if (remainingConversations.length > 0) {
				// 选择第一个剩余对话
				const firstRemaining = remainingConversations[0];
				setCurrentConversationId(firstRemaining.id);
				setMessages(firstRemaining.messages);
			} else {
				// 没有剩余对话，创建新对话
				createNewConversation();
			}
		}

		// 从对话列表中移除
		const updatedConversations = conversations.filter(conv => conv.id !== conversationId);
		setConversations(updatedConversations);

		// 更新localStorage
		localStorage.setItem("poly-ai-conversations", JSON.stringify(updatedConversations));

		// 如果删除的是当前对话且没有其他对话，清除当前对话ID
		if (conversationId === currentConversationId && updatedConversations.length === 0) {
			localStorage.removeItem("poly-ai-current-conversation");
		}
	};

	// 响应消息
	const respondToMessage = async (message: string) => {
		setIsTyping(true);
		console.log("发送消息:", message);
		console.log("当前对话ID:", currentConversationId);
		console.log("选中的Agent:", selectedAgent);

		// 如果还没有对话，创建一个新对话
		if (!currentConversationId) {
			console.log("警告：没有当前对话ID，创建新对话");
			createNewConversation();
			// 等待状态更新
			await new Promise(resolve => setTimeout(resolve, 100));
		}

		try {
			// 创建新的AI消息但不填充内容
			const aiResponse: Message = {
				text: "",
				sender: "ai",
				type: "html",
			};
			console.log(messages, "messages---xxx");

			setMessages((prev) => [...prev, aiResponse]);

			// 根据选择的agent类型调用不同的API接口
			let apiEndpoint = "";
			if (selectedAgent === "monitor") {
				apiEndpoint = "http://localhost:5000/market-monitor"; // 加密货币市场助手
				console.log("使用Monitor Agent API");
			} else if (selectedAgent === "trade") {
				apiEndpoint = "http://localhost:5000/market-trade"; // 支付宝转代币助手
				console.log("使用Trade Agent API");
			} else {
				console.error("未知的Agent类型:", selectedAgent);
			}

			console.log("API端点:", apiEndpoint);

			// 使用fetch API和ReadableStream处理流式响应
			try {
				const response = await fetch(apiEndpoint, {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						message: message
					}),
				});

				if (!response.ok) {
					throw new Error(`HTTP error! Status: ${response.status}`);
				}

				if (!response.body) {
					throw new Error("ReadableStream not supported");
				}

				// 获取response的ReadableStream
				const reader = response.body.getReader();
				const decoder = new TextDecoder();
				let streamText = "";

				// 读取流数据
				while (true) {
					const { done, value } = await reader.read();
					if (done) break;

					// 解码二进制数据为文本
					const chunk = decoder.decode(value, { stream: !done });
					streamText += chunk;

					// 更新UI上的消息
					setMessages((prev) => {
						const updatedMessages = [...prev];
						const lastMessage = updatedMessages[updatedMessages.length - 1];

						if (lastMessage && lastMessage.sender === "ai") {
							// 确保HTML内容中的换行符被正确处理
							let formattedText = streamText
								.replace(/\n/g, "<br>") // 将\n替换为HTML的<br>标签
								.replace(/\r/g, ""); // 移除可能存在的\r字符

							// 调试：输出接收到的HTML内容（仅在开发模式下）
							if (process.env.NODE_ENV === 'development') {
								console.log("接收到的AI响应内容:", formattedText);
								
								// 检查是否包含按钮HTML
								if (formattedText.includes('confirm-btn-purple')) {
									console.log("检测到确认按钮HTML");
								}
							}

							lastMessage.text = formattedText;
						}

						return updatedMessages;
					});
				}
			} catch (streamError) {
				console.error("流式响应处理错误:", streamError);
			}

			// 请求完成后，确保设置isTyping为false
			setIsTyping(false);
		} catch (error) {
			console.error("请求错误:", error);
			setIsTyping(false);

			// 显示错误消息
			setMessages((prev) => {
				const updatedMessages = [...prev];
				const lastMessage = updatedMessages[updatedMessages.length - 1];

				if (lastMessage && lastMessage.sender === "ai") {
					lastMessage.text =
						"<p class='text-red-500 whitespace-pre-wrap'>Sorry, an error occurred. Please try again.</p>";
				}

				return updatedMessages;
			});
		}
	};

	// 处理转账表单提交 - 调用市场交易API
	const handleTransferSubmit = async () => {
		if (!transferFormData.toAddress || !transferFormData.amount) {
			alert("Please fill in complete transfer information");
			return;
		}

		setIsSubmittingTransfer(true);

		try {
			// 创建新的AI消息用于显示流式响应
			const aiResponse: Message = {
				text: "",
				sender: "ai",
				type: "html",
			};

			setMessages((prev) => [...prev, aiResponse]);

			// 调用market-trade API接口
			const response = await fetch("http://localhost:5000/market-trade", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					message: `执行转账操作：从 ${transferFormData.senderAddress || '发送方'} 转账 ${transferFormData.amount} PAT 代币到 ${transferFormData.toAddress}`
				}),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}

			if (!response.body) {
				throw new Error("ReadableStream not supported");
			}

			// 获取response的ReadableStream
			const reader = response.body.getReader();
			const decoder = new TextDecoder();
			let streamText = "";

			// 读取流数据
			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				// 解码二进制数据为文本
				const chunk = decoder.decode(value, { stream: !done });
				streamText += chunk;

				// 更新UI上的消息
				setMessages((prev) => {
					const updatedMessages = [...prev];
					const lastMessage = updatedMessages[updatedMessages.length - 1];

					if (lastMessage && lastMessage.sender === "ai") {
						// 确保HTML内容中的换行符被正确处理
						let formattedText = streamText
							.replace(/\n/g, "<br>") // 将\n替换为HTML的<br>标签
							.replace(/\r/g, ""); // 移除可能存在的\r字符

						lastMessage.text = formattedText;
					}

					return updatedMessages;
				});
			}

			// 关闭转账表单
			setShowTransferForm(false);

			// 重置表单
			setTransferFormData({
				contractAddress: "0xD3286E20Ff71438D9f6969828F7218af4A375e2f",
				toAddress: "",
				amount: "",
				decimals: "18"
			});

		} catch (error) {
			console.error("转账提交错误:", error);

			const errorMessage: Message = {
				text: `
					<div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05)); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 0.5rem; padding: 1rem; margin: 1rem 0; display: flex; align-items: center; gap: 1rem;">
						<div style="font-size: 1.5rem; color: #ef4444;">❌</div>
						<div style="color: #E6E6ED; font-weight: 500;">Transfer submission failed, please try again</div>
					</div>
				`,
				sender: "ai",
				type: "html"
			};

			setMessages((prev) => [...prev, errorMessage]);
		} finally {
			setIsSubmittingTransfer(false);
		}
	};

	// 自动填充表单数据的函数
	const autoFillTransferForm = () => {
		setTransferFormData({
			contractAddress: alipayTransferDefaults.polyagent_token_contract,
			toAddress: alipayTransferDefaults.spender_address,
			amount: "2.0", // 默认转账2个代币
			decimals: alipayTransferDefaults.decimals,
			// 支付宝转代币专用参数
			senderAddress: alipayTransferDefaults.sender_address,
			senderPrivateKey: alipayTransferDefaults.sender_private_key,
			spenderPrivateKey: alipayTransferDefaults.spender_private_key,
			rpcUrl: alipayTransferDefaults.testnet_rpc,
			chainId: alipayTransferDefaults.chain_id.toString()
		});
		setShowTransferForm(true);
	};

	// 添加按钮点击状态管理
	const [buttonClickedMap, setButtonClickedMap] = useState<Record<string, boolean>>({});

	// 全局函数，供HTML按钮调用
	useEffect(() => {
		(window as any).showTransferForm = (buttonId?: string) => {
			console.log("确认按钮被点击, buttonId:", buttonId);
			console.log("当前对话ID:", currentConversationId);
			console.log("选中的Agent:", selectedAgent);

			// 生成唯一的按钮ID（如果没有提供）
			const uniqueButtonId = buttonId || `btn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

			// 检查按钮是否已经被点击过
			if (buttonClickedMap[uniqueButtonId]) {
				console.log("按钮已被点击过，忽略重复点击");
				return;
			}

			// 标记按钮为已点击
			setButtonClickedMap(prev => ({
				...prev,
				[uniqueButtonId]: true
			}));

			// 直接向AI发送确认执行的消息，而不是打开表单
			const confirmMessage = "确认执行支付订单";

			// 添加用户确认消息
			const userConfirmMessage: Message = {
				text: confirmMessage,
				sender: "user"
			};
			setMessages((prev) => [...prev, userConfirmMessage]);

			// 发送确认消息到AI
			respondToMessage(confirmMessage);
		};

		return () => {
			delete (window as any).showTransferForm;
		};
	}, [currentConversationId, selectedAgent, setMessages, respondToMessage, buttonClickedMap]);

	// 发送消息
	const handleSendMessage = () => {
		if (inputMessage.trim()) {
			const newMessage = { text: inputMessage, sender: "user" as const };
			setMessages((prev) => [...prev, newMessage]);

			// 保存当前输入的消息内容
			const currentMessage = inputMessage;

			// 清空输入框
			setInputMessage("");

			// 滚动到底部
			setTimeout(() => {
				if (chatContainerRef.current) {
					chatContainerRef.current.scrollTop =
						chatContainerRef.current.scrollHeight;
				}
			}, 100);

			// 发送消息到服务端并处理响应
			respondToMessage(currentMessage);

			// 自动调整输入框高度
			if (textareaRef.current) {
				textareaRef.current.style.height = "auto";
			}
		}
	};

	// 自动调整文本区域高度
	const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		setInputMessage(e.target.value);
		e.target.style.height = "auto";
		e.target.style.height = `${e.target.scrollHeight}px`;
	};

	// 处理键盘事件
	const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			handleSendMessage();
		}
	};

	// 滚动到底部
	useEffect(() => {
		if (chatContainerRef.current) {
			chatContainerRef.current.scrollTop =
				chatContainerRef.current.scrollHeight;
		}
	}, [messages, isTyping]);

	return (
		<WagmiProvider config={config}>
			<QueryClientProvider client={queryClient}>
				<RainbowKitProvider>
					<div className="app-container min-h-screen text-text-primary relative noise-bg">
						{/* 粒子背景 */}
						<div className="particles" id="particles"></div>

						{/* 头部 */}
						<header className="sticky top-0 z-50 backdrop-blur-xl bg-bg-dark/80 border-b border-night-purple/20">
							<div className="container mx-auto px-4 py-3 flex justify-between items-center">
								<div className="flex items-center space-x-2">
									<div
										className="w-8 h-8 relative cursor-pointer hover:scale-110 transition-transform duration-300"
										onClick={() => setShowLogoOverlay(true)}
									>
										<div className="absolute inset-0 bg-gradient-to-br from-neon-cyan to-night-purple rounded-lg opacity-70 animate-pulse-slow"></div>
										<div className="absolute inset-0.5 bg-deep-black rounded-lg flex items-center justify-center">
											<span className="text-neon-cyan font-bold text-xl glow-text">
												P
											</span>
										</div>
									</div>
									<h1 className="text-xl font-bold tracking-tight">
										PolyAgent
										{/* <span className="text-neon-cyan">.AI</span> */}
									</h1>
								</div>

								{/* AI助手切换按钮组 */}
								<div className="flex items-center space-x-1 bg-deep-black/50 backdrop-blur-md border border-night-purple/20 rounded-lg p-1 agent-switch-container">
														<button
						onClick={() => handleAgentSwitch("monitor")}
						onMouseEnter={(e) => handleMouseEnter("monitor", e)}
						onMouseLeave={handleMouseLeave}
						disabled={isAgentSwitching}
						className={`agent-switch-button relative px-4 py-2 rounded-md font-medium text-sm transition-all duration-300 ${selectedAgent === "monitor"
							? "bg-gradient-to-r from-neon-cyan/20 to-night-purple/20 text-neon-cyan border border-neon-cyan/30 shadow-lg agent-switch-active"
							: "text-text-secondary hover:text-text-primary hover:bg-white/5"
							} ${isAgentSwitching ? "opacity-50 cursor-not-allowed agent-switching" : ""}`}
					>
						{isAgentSwitching && selectedAgent === "monitor" && (
							<div className="absolute inset-0 rounded-md bg-gradient-to-r from-neon-cyan/10 to-night-purple/10 animate-pulse"></div>
						)}
						<span className="relative flex items-center space-x-2">
							<span className="agent-switch-icon">📈</span>
							<span className="hidden sm:inline">Crypto Monitor</span>
							<span className="sm:hidden">Monitor</span>
						</span>
					</button>

														<button
						onClick={() => handleAgentSwitch("trade")}
						onMouseEnter={(e) => handleMouseEnter("trade", e)}
						onMouseLeave={handleMouseLeave}
						disabled={isAgentSwitching}
						className={`agent-switch-button relative px-4 py-2 rounded-md font-medium text-sm transition-all duration-300 ${selectedAgent === "trade"
							? "bg-gradient-to-r from-neon-cyan/20 to-night-purple/20 text-neon-cyan border border-neon-cyan/30 shadow-lg agent-switch-active"
							: "text-text-secondary hover:text-text-primary hover:bg-white/5"
							} ${isAgentSwitching ? "opacity-50 cursor-not-allowed agent-switching" : ""}`}
					>
						{isAgentSwitching && selectedAgent === "trade" && (
							<div className="absolute inset-0 rounded-md bg-gradient-to-r from-neon-cyan/10 to-night-purple/10 animate-pulse"></div>
						)}
						<span className="relative flex items-center space-x-2">
							<span className="agent-switch-icon">💰</span>
							<span className="hidden sm:inline">Payment Bridge</span>
							<span className="sm:hidden">Payment</span>
						</span>
					</button>
								</div>

								<div className="flex items-center space-x-4">
									{/* RainbowKit 钱包连接按钮 */}
									<div className="wallet-connect-btn">
										<ConnectButton label="Connect  Wallet" />
									</div>
								</div>
							</div>
						</header>

						<div className="container mx-auto flex flex-col md:flex-row min-h-[calc(100vh-57px)]">
							{/* 侧边栏 */}
							<aside className="md:w-64 bg-deep-black/50 backdrop-blur-md border-r border-night-purple/20 p-4 hidden md:block">
								<button
									onClick={createNewConversation}
									className="w-full px-4 py-2 mb-6 rounded-md bg-gradient-to-r from-neon-cyan/20 to-night-purple/20 hover:from-neon-cyan/30 hover:to-night-purple/30 border border-neon-cyan/30 text-neon-cyan flex items-center justify-center space-x-2 transition-all shine-effect"
								>
									<FontAwesomeIcon icon={faPlus} className="text-xs" />
									<span>New Chat</span>
								</button>
								<div className="space-y-1 mb-6">
									<h3 className="text-text-secondary text-xs uppercase tracking-wider mb-2 px-2">
										Recent Conversations
									</h3>

									{conversations.length > 0 ? (
										conversations.map((conv) => (
											<div
												key={conv.id}
												className={`conversation-item group relative w-full text-left px-3 py-2 rounded-md transition-all flex items-center justify-between ${currentConversationId === conv.id ? "bg-white/5" : ""
													}`}
											>
												{/* 对话内容区域 */}
												<button
													className="flex items-center space-x-3 flex-1 min-w-0"
													onClick={() => {
														selectConversation(conv.id);
													}}
												>
													<FontAwesomeIcon
														icon={faCommentAlt}
														className={`text-xs flex-shrink-0 ${currentConversationId === conv.id
															? "text-neon-cyan"
															: "text-text-secondary"
															}`}
													/>
													<span className="text-sm truncate">{conv.title}</span>
												</button>

												{/* 删除按钮 - 悬浮时显示 */}
												<button
													onClick={(e) => deleteConversation(conv.id, e)}
													className="delete-conversation-btn opacity-0 group-hover:opacity-100 transition-all duration-200 w-6 h-6 rounded-md bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 hover:border-red-500/40 flex items-center justify-center ml-2 flex-shrink-0"
													title="删除对话"
												>
													<FontAwesomeIcon
														icon={faTimes}
														className="delete-conversation-icon text-xs text-red-400 hover:text-red-300"
													/>
												</button>
											</div>
										))
									) : (
																			<div className="text-text-secondary text-sm px-3 py-2">
										No conversations yet
									</div>
									)}
								</div>

								<div className="space-y-1">
									<h3 className="text-text-secondary text-xs uppercase tracking-wider mb-2 px-2">
										Workspace
									</h3>

									{/* <button className="w-full text-left px-3 py-2 rounded-md hover:bg-white/5 transition-all flex items-center space-x-3">
										<FontAwesomeIcon
											icon={faBolt}
											className="text-text-secondary text-xs"
										/>
										<span className="text-sm truncate">My Collection</span>
                  </button> */}

                  <button
                    onClick={() => setShowSignaturePanel(!showSignaturePanel)}
                    className="w-full text-left px-3 py-2 rounded-md hover:bg-white/5 transition-all flex items-center space-x-3"
                  >
                    <FontAwesomeIcon
                      icon={faSignature}
                      className="text-text-secondary text-xs"
                    />
                    <span className="text-sm truncate">Wallet Signature</span>
									</button>
                  {/* 
									<button className="w-full text-left px-3 py-2 rounded-md hover:bg-white/5 transition-all flex items-center space-x-3">
										<FontAwesomeIcon
											icon={faHistory}
											className="text-text-secondary text-xs"
										/>
										<span className="text-sm truncate">historical records</span>
									</button>

									<button className="w-full text-left px-3 py-2 rounded-md hover:bg-white/5 transition-all flex items-center space-x-3">
										<FontAwesomeIcon
											icon={faCog}
											className="text-text-secondary text-xs"
										/>
										<span className="text-sm truncate">set up</span>
									</button> */}
								</div>

                {/* 签名工具面板 */}
                {showSignaturePanel && (
                  <div className="mt-4">
                    <WalletSignature />
                  </div>
                )}
							</aside>

							{/* 主要内容 */}
							<main className="flex-1 flex flex-col relative">
								{/* 聊天容器 */}
								<div
									className="agent-container flex-1 overflow-y-auto px-4 py-6 space-y-6 pb-0"
									ref={chatContainerRef}
								>
									{/* 历史消息 */}
									{messages.map((msg, index) => (
										<div key={index} className="max-w-3xl mx-auto">
											{msg.sender === "user" ? (
												<div className="user-message mb-6 rounded-tr-lg rounded-b-lg bg-deep-black/50 backdrop-blur-sm p-4 ml-8">
													<div className="flex items-center mb-2">
														<p className="text-sm text-text-secondary">user</p>
													</div>
													<p>{msg.text}</p>
												</div>
											) : (
												<div className="ai-message mb-6 rounded-tl-lg rounded-b-lg bg-gradient-to-br from-deep-black/90 to-bg-dark/90 backdrop-blur-sm p-4 mr-8">
													<div className="flex items-center mb-2">
														<div className="w-8 h-8 relative mr-4">
															<div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/40 to-night-purple/40 rounded-full opacity-70"></div>
															<div className="absolute inset-0.5 bg-deep-black rounded-full flex items-center justify-center">
																<span className="text-neon-cyan text-xs font-bold">
																	P
																</span>
															</div>
														</div>
														<p className="text-sm text-text-secondary">
															PolyAgent
														</p>
													</div>
													{msg.type === "html" ? (
														<div
															className="ai-response-content whitespace-pre-wrap"
															dangerouslySetInnerHTML={{ __html: msg.text }}
														></div>
													) : (
														<p>{msg.text}</p>
													)}
												</div>
											)}
										</div>
									))}

									{/* 打字指示器 */}
									{isTyping && (
										<div className="max-w-3xl mx-auto">
											<div className="ai-message mb-6 rounded-tl-lg rounded-b-lg bg-gradient-to-br from-deep-black/90 to-bg-dark/90 backdrop-blur-sm p-4 mr-8">
												<div className="flex space-x-2">
													<span
														className="w-2 h-2 bg-neon-cyan/50 rounded-full animate-bounce"
														style={{ animationDelay: "0ms" }}
													></span>
													<span
														className="w-2 h-2 bg-neon-cyan/50 rounded-full animate-bounce"
														style={{ animationDelay: "300ms" }}
													></span>
													<span
														className="w-2 h-2 bg-neon-cyan/50 rounded-full animate-bounce"
														style={{ animationDelay: "600ms" }}
													></span>
												</div>
											</div>
										</div>
									)}
								</div>


								{/* 输入区域 */}
								<div className="user-input-container border-t border-night-purple/20 bg-deep-black/50 backdrop-blur-md p-4">
									<div className="mx-auto relative">
										<div className="relative gradient-border">
											<div className="flex items-center bg-deep-black rounded-md overflow-hidden input-active">
																				<textarea
									ref={textareaRef}
									rows={1}
									placeholder="Ask me anything about crypto or payments..."
									className="flex-1 resize-none bg-transparent border-none outline-none p-3 pr-12 text-text-primary placeholder-text-secondary/50"
									style={{ height: "48px", maxHeight: "200px" }}
									value={inputMessage}
									onChange={handleTextareaChange}
									onKeyDown={handleKeyDown}
								></textarea>

												<div className="absolute right-2 bottom-2 flex items-center">
													<button className="w-8 h-8 rounded-md text-text-secondary hover:text-neon-cyan flex items-center justify-center transition-colors">
														<FontAwesomeIcon icon={faMicrophone} />
													</button>
													<button
														onClick={handleSendMessage}
														className="w-8 h-8 rounded-md bg-gradient-to-r from-neon-cyan to-night-purple text-deep-black flex items-center justify-center ml-1"
													>
														<FontAwesomeIcon icon={faPaperPlane} />
													</button>
												</div>
											</div>
										</div>
									</div>
								</div>
							</main>
						</div>

						{/* 转账表单悬浮层 */}
						{showTransferForm && (
							<div
								className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md"
								onClick={() => setShowTransferForm(false)}
							>
								<div
									className="relative bg-gradient-to-br from-deep-black/95 to-bg-dark/95 backdrop-blur-xl border border-night-purple/30 rounded-xl p-6 w-full max-w-md mx-4 animate-fade-in"
									onClick={(e) => e.stopPropagation()}
								>
									{/* 表单标题 */}
									<div className="flex items-center justify-between mb-6">
										<div className="flex items-center space-x-3">
											<div className="w-10 h-10 bg-gradient-to-br from-neon-cyan/20 to-night-purple/20 rounded-lg flex items-center justify-center">
												<FontAwesomeIcon icon={faWallet} className="text-neon-cyan" />
											</div>
											<h2 className="text-xl font-bold text-text-primary">Transfer Tokens</h2>
										</div>
										<button
											className="w-8 h-8 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center text-white/70 hover:text-white transition-all"
											onClick={() => setShowTransferForm(false)}
										>
											<FontAwesomeIcon icon={faTimes} />
										</button>
									</div>

									{/* 表单内容 */}
									<div className="space-y-4">
										{/* 合约地址 */}
										<div>
											<label className="block text-sm font-medium text-text-secondary mb-2">
												Contract Address *
											</label>
											<input
												type="text"
												value={transferFormData.contractAddress}
												onChange={(e) => setTransferFormData((prev: TransferFormData) => ({
													...prev,
													contractAddress: e.target.value
												}))}
												className="w-full bg-deep-black/50 border border-night-purple/30 rounded-lg px-4 py-3 text-text-primary placeholder-text-secondary/50 focus:border-neon-cyan/50 focus:outline-none transition-colors"
												placeholder="Enter ERC20 contract address"
											/>
										</div>

										{/* 接收地址 */}
										<div>
											<label className="block text-sm font-medium text-text-secondary mb-2">
												Recipient Address *
											</label>
											<input
												type="text"
												value={transferFormData.toAddress}
												onChange={(e) => setTransferFormData((prev: TransferFormData) => ({
													...prev,
													toAddress: e.target.value
												}))}
												className="w-full bg-deep-black/50 border border-night-purple/30 rounded-lg px-4 py-3 text-text-primary placeholder-text-secondary/50 focus:border-neon-cyan/50 focus:outline-none transition-colors"
												placeholder="Enter recipient wallet address"
											/>
										</div>

										{/* 转账金额 */}
										<div>
											<label className="block text-sm font-medium text-text-secondary mb-2">
												Transfer Amount *
											</label>
											<input
												type="number"
												step="0.000001"
												value={transferFormData.amount}
												onChange={(e) => setTransferFormData((prev: TransferFormData) => ({
													...prev,
													amount: e.target.value
												}))}
												className="w-full bg-deep-black/50 border border-night-purple/30 rounded-lg px-4 py-3 text-text-primary placeholder-text-secondary/50 focus:border-neon-cyan/50 focus:outline-none transition-colors"
												placeholder="Enter transfer amount"
											/>
										</div>

										{/* 代币精度 */}
										<div>
											<label className="block text-sm font-medium text-text-secondary mb-2">
												Token Decimals
											</label>
											<select
												value={transferFormData.decimals}
												onChange={(e) => setTransferFormData((prev: TransferFormData) => ({
													...prev,
													decimals: e.target.value
												}))}
												className="w-full bg-deep-black/50 border border-night-purple/30 rounded-lg px-4 py-3 text-text-primary focus:border-neon-cyan/50 focus:outline-none transition-colors"
											>
												<option value="18">18 (Standard ERC20)</option>
												<option value="6">6 (USDC/USDT)</option>
												<option value="8">8 (WBTC)</option>
												<option value="9">9 (Custom)</option>
											</select>
										</div>
									</div>

									{/* 提交按钮 */}
									<div className="flex space-x-3 mt-6">
										<button
											onClick={() => setShowTransferForm(false)}
											className="flex-1 px-4 py-3 bg-deep-black/50 border border-night-purple/30 rounded-lg text-text-secondary hover:text-text-primary hover:border-night-purple/50 transition-all"
										>
											Cancel
										</button>
										<button
											onClick={handleTransferSubmit}
											disabled={isSubmittingTransfer || !transferFormData.toAddress || !transferFormData.amount}
											className="flex-1 px-4 py-3 bg-gradient-to-r from-neon-cyan to-night-purple text-deep-black font-medium rounded-lg hover:shadow-lg hover:shadow-neon-cyan/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
										>
											{isSubmittingTransfer ? (
												<div className="flex items-center justify-center space-x-2">
													<div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
													<span>Submitting...</span>
												</div>
											) : (
												"Confirm Transfer"
											)}
										</button>
									</div>

									{/* 安全提示 */}
									<div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
										<p className="text-xs text-yellow-400/80">
											⚠️ Please verify transfer details carefully. Blockchain transactions are irreversible.
										</p>
									</div>
								</div>
							</div>
						)}

						{/* Logo 放大覆盖层 */}
						{showLogoOverlay && (
							<div
								className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md"
								onClick={() => setShowLogoOverlay(false)}
							>
								<div
									className="relative animate-fade-in"
									onClick={(e) => e.stopPropagation()}
								>
									{/* 关闭按钮 */}
									<button
										className="absolute -top-10 -right-10 w-8 h-8 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center text-white/70 hover:text-white transition-all"
										onClick={() => setShowLogoOverlay(false)}
									>
										<span className="text-xl">×</span>
									</button>

									{/* 放大的 Logo */}
									<div className="w-80 h-80 relative logo-enlarged">
										<div className="absolute inset-0 bg-gradient-to-br from-neon-cyan to-night-purple rounded-3xl opacity-70 animate-pulse-slow shadow-2xl shadow-neon-cyan/30"></div>
										<div className="absolute inset-2 bg-deep-black rounded-3xl flex items-center justify-center border border-white/10">
											<span className="text-neon-cyan font-bold text-9xl glow-text drop-shadow-2xl">
												P
											</span>
										</div>
									</div>

									{/* Logo 信息 */}
									<div className="mt-6 text-center text-white/90">
										<h2 className="text-2xl font-bold mb-2">PolyAgent</h2>
										<p className="text-sm text-white/70">Web3 AI Agent Interoperability Protocol</p>
										<p className="text-xs text-white/50 mt-2">320x320 pixels - Ready for icon processing</p>
									</div>
								</div>
							</div>
						)}

						{/* Agent Tooltip */}
						{showTooltip.show && showTooltip.agent && (
							<div
								className="fixed z-[60] pointer-events-none transform -translate-x-1/2"
								style={{
									left: `${showTooltip.position.x}px`,
									top: `${showTooltip.position.y}px`,
								}}
							>
								<div className="agent-tooltip animate-fade-in">
									{/* Tooltip 箭头 */}
									<div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
										<div className="w-0 h-0 border-l-[8px] border-l-transparent border-r-[8px] border-r-transparent border-b-[8px] border-b-gray-800"></div>
										<div className="absolute top-1 left-1/2 transform -translate-x-1/2">
											<div className="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-b-[6px] border-b-deep-black"></div>
										</div>
									</div>

									{/* Tooltip 内容 */}
									<div className="bg-gradient-to-br from-deep-black/95 to-bg-dark/95 backdrop-blur-xl border border-night-purple/30 rounded-xl p-4 min-w-[280px] max-w-[320px] shadow-2xl shadow-night-purple/20">
										<div className="space-y-3">
											{/* 标题 */}
											<div className="flex items-center space-x-2">
												<h3 className="text-lg font-bold text-text-primary">
													{getAgentDescription(showTooltip.agent).title}
												</h3>
											</div>

											{/* 描述 */}
											<p className="text-sm text-text-secondary leading-relaxed">
												{getAgentDescription(showTooltip.agent).description}
											</p>

											{/* 功能特性 */}
											<div className="space-y-2">
												{getAgentDescription(showTooltip.agent).features.map((feature, index) => (
													<div key={index} className="flex items-start space-x-2 text-sm">
														<div className="w-1.5 h-1.5 rounded-full bg-neon-cyan mt-2 flex-shrink-0"></div>
														<span className="text-text-secondary leading-relaxed">{feature}</span>
													</div>
												))}
											</div>

											{/* 提示 */}
											<div className="mt-3 pt-3 border-t border-night-purple/20">
												<p className="text-xs text-text-secondary/80 italic">
													Click to switch to this assistant
												</p>
											</div>
										</div>
									</div>
								</div>
							</div>
						)}
					</div>
				</RainbowKitProvider>
			</QueryClientProvider>
		</WagmiProvider>
	);
}

export default App;