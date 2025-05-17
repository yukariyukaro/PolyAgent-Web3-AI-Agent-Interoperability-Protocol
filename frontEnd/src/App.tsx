import { useState, useEffect, useRef } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  // faUser,
  faPlus,
  faCommentAlt,
  faBolt,
  faHistory,
  faCog,
  faMicrophone,
  faPaperPlane,
} from "@fortawesome/free-solid-svg-icons";

// RainbowKit 相关导入
import "@rainbow-me/rainbowkit/styles.css";
import {
  getDefaultConfig,
  RainbowKitProvider,
  ConnectButton,
} from "@rainbow-me/rainbowkit";
import { WagmiProvider } from "wagmi";
import { mainnet, polygon, optimism, arbitrum, base } from "wagmi/chains";
import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { http } from "wagmi";

// 配置 RainbowKit
const config = getDefaultConfig({
  appName: "PolyAgent",
  // 从 WalletConnect Cloud 获取项目ID: https://cloud.walletconnect.com/
  // 1. 注册/登录 WalletConnect Cloud
  // 2. 创建一个新项目并输入应用名称和URL
  // 3. 复制生成的项目ID到这里
  projectId: "YOUR_PROJECT_ID",
  chains: [mainnet, polygon, optimism, arbitrum, base],
  transports: {
    [mainnet.id]: http("https://eth-mainnet.g.alchemy.com/v2/demo"),
    [polygon.id]: http("https://polygon-mainnet.g.alchemy.com/v2/demo"),
    [optimism.id]: http("https://opt-mainnet.g.alchemy.com/v2/demo"),
    [arbitrum.id]: http("https://arb-mainnet.g.alchemy.com/v2/demo"),
    [base.id]: http("https://base-mainnet.g.alchemy.com/v2/demo"),
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

  // 从本地存储加载对话
  useEffect(() => {
    const storedConversations = localStorage.getItem("nova-ai-conversations");
    if (storedConversations) {
      setConversations(JSON.parse(storedConversations));
    }

    const currentId = localStorage.getItem("nova-ai-current-conversation");
    if (currentId) {
      setCurrentConversationId(currentId);
      const currentConversation = JSON.parse(storedConversations || "[]").find(
        (conv: Conversation) => conv.id === currentId
      );
      if (currentConversation) {
        setMessages(currentConversation.messages);
      }
    }
  }, []);

  // 保存对话到本地存储
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem(
        "nova-ai-conversations",
        JSON.stringify(conversations)
      );
    }

    if (currentConversationId) {
      localStorage.setItem(
        "nova-ai-current-conversation",
        currentConversationId
      );

      // 更新当前对话的消息
      const updatedConversations = conversations.map((conv) =>
        conv.id === currentConversationId ? { ...conv, messages } : conv
      );

      setConversations(updatedConversations);
      localStorage.setItem(
        "nova-ai-conversations",
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
  };

  // 选择对话
  const selectConversation = (id: string) => {
    const conversation = conversations.find((conv) => conv.id === id);
    if (conversation) {
      setCurrentConversationId(id);
      setMessages(conversation.messages);
    }
  };

  // 响应消息
  const respondToMessage = (message: string) => {
    setIsTyping(true);
    console.log(message, "message---");

    // setTimeout(() => {
    //   setIsTyping(false);
    //   let response = "";
    //
    //   if (
    //     message.toLowerCase().includes("hello") ||
    //     message.toLowerCase().includes("hi") ||
    //     message.toLowerCase().includes("你好")
    //   ) {
    //     response = `<p>你好！很高兴与你交流。我是Nova.AI，一个设计用来提供帮助和回答问题的AI助手。你可以问我几乎任何问题，我会尽力提供有用的信息。有什么我能帮到你的吗？</p>`;
    //   } else if (
    //     message.toLowerCase().includes("功能") ||
    //     message.toLowerCase().includes("能做什么")
    //   ) {
    //     response = `
    //       <p>作为Nova.AI，我能够帮你完成很多任务：</p>
    //       <ul class="list-disc pl-5 space-y-2 my-3">
    //           <li>回答一般知识问题</li>
    //           <li>提供创意写作和内容建议</li>
    //           <li>解释复杂概念</li>
    //           <li>帮助编程和代码相关问题</li>
    //           <li>提供信息总结和分析</li>
    //           <li>协助学习和研究</li>
    //       </ul>
    //       <p>有什么具体需要我帮忙的吗？</p>
    //     `;
    //   } else if (
    //     message.toLowerCase().includes("未来") ||
    //     message.toLowerCase().includes("ai发展")
    //   ) {
    //     response = `
    //       <p>AI的未来发展可能会朝着这些方向前进：</p>
    //       <p class="mb-2">🔹 <span class="text-neon-cyan font-medium">多模态融合</span> - AI系统将同时理解和生成文本、图像、声音、视频等多种形式的内容</p>
    //       <p class="mb-2">🔹 <span class="text-neon-cyan font-medium">自主学习能力增强</span> - AI将能从更少的数据中学习，更接近人类的学习方式</p>
    //       <p class="mb-2">🔹 <span class="text-neon-cyan font-medium">与现实世界更深度融合</span> - 通过机器人技术和IoT设备，AI将能更直接地与物理世界交互</p>
    //       <p class="mb-2">🔹 <span class="text-neon-cyan font-medium">提高解释性和透明度</span> - 未来的AI系统将更容易解释其决策过程</p>
    //       <p class="mb-2">🔹 <span class="text-neon-cyan font-medium">伦理AI设计</span> - 重点将放在构建公平、无偏见、尊重隐私的AI系统上</p>
    //       <p>你对AI的哪个发展方向最感兴趣？</p>
    //     `;
    //   } else {
    //     response = `
    //       <p>感谢你的提问。这是一个很有趣的话题！</p>
    //       <p class="my-2">根据我对"${message}"的理解，这涉及到几个关键点：</p>
    //       <div class="p-3 my-3 bg-night-purple/10 border-l-2 border-night-purple rounded-r-md">
    //           <p class="text-sm">每个复杂问题都有其独特的背景和前提条件需要考虑。如果你能提供更多具体信息，我可以给出更有针对性的回答。</p>
    //       </div>
    //       <p>我们可以从不同角度来探讨这个问题。你希望我从哪个方面深入分析呢？</p>
    //     `;
    //   }

    //   const aiResponse: Message = {
    //     text: response,
    //     sender: "ai",
    //     type: "html",
    //   };
    //   setMessages((prev) => [...prev, aiResponse]);

    //   // 如果还没有对话，创建一个新对话
    //   if (!currentConversationId) {
    //     createNewConversation();
    //   }
    // }, 2000);
  };

  // 发送消息
  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      const newMessage = { text: inputMessage, sender: "user" as const };
      setMessages((prev) => [...prev, newMessage]);
      setInputMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "48px";
      }
      const messageTitle =
        inputMessage.length > 20
          ? `${inputMessage.substring(0, 20)}...`
          : inputMessage;
      // 如果还没有对话，创建一个新对话
      if (!currentConversationId) {
        const newId = `conv-${Date.now()}`;
        // const messageTitle =
        //   inputMessage.length > 20
        //     ? `${inputMessage.substring(0, 20)}...`
        //     : inputMessage;

        const newConversation: Conversation = {
          id: newId,
          title: messageTitle,
          messages: [newMessage],
          createdAt: Date.now(),
        };

        setConversations((prev) => [newConversation, ...prev]);
        setCurrentConversationId(newId);
      }

      conversations.map((conv) => {
        if (conv.id === currentConversationId) {
          conv.title = messageTitle;
        }
      });
      respondToMessage(inputMessage);
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
          <div className="min-h-screen text-text-primary relative noise-bg">
            {/* 粒子背景 */}
            <div className="particles" id="particles"></div>

            {/* 头部 */}
            <header className="sticky top-0 z-50 backdrop-blur-xl bg-bg-dark/80 border-b border-night-purple/20">
              <div className="container mx-auto px-4 py-3 flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 relative">
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

                <div className="flex items-center space-x-4">
                  {/* <button 
                    onClick={createNewConversation}
                    className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-md bg-deep-black border border-night-purple/30 hover:border-night-purple/70 transition-all">
                    <FontAwesomeIcon
                      icon={faPlus}
                      className="text-xs text-neon-cyan"
                    />
                    <span className="text-sm">新对话</span>
                  </button> */}

                  {/* RainbowKit 钱包连接按钮 */}
                  <div className="wallet-connect-btn">
                    {/* <ConnectButton label="Connect Wallet" /> */}
                    <ConnectButton label="Connect  Wallet" />
                  </div>

                  {/* <button className="w-8 h-8 rounded-full bg-deep-black border border-night-purple/30 flex items-center justify-center">
                    <FontAwesomeIcon
                      icon={faUser}
                      className="text-xs text-text-secondary"
                    />
                  </button> */}
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
                    Recent conversations
                  </h3>

                  {conversations.length > 0 ? (
                    conversations.map((conv) => (
                      <button
                        key={conv.id}
                        onClick={() => selectConversation(conv.id)}
                        className={`w-full text-left px-3 py-2 rounded-md hover:bg-white/5 transition-all flex items-center space-x-3 group ${
                          currentConversationId === conv.id ? "bg-white/5" : ""
                        }`}
                      >
                        <FontAwesomeIcon
                          icon={faCommentAlt}
                          className={`text-xs ${
                            currentConversationId === conv.id
                              ? "text-neon-cyan"
                              : "text-text-secondary"
                          }`}
                        />
                        <span className="text-sm truncate">{conv.title}</span>
                      </button>
                    ))
                  ) : (
                    <div className="text-text-secondary text-sm px-3 py-2">
                      No conversation records available at the moment
                    </div>
                  )}
                </div>

                <div className="space-y-1">
                  <h3 className="text-text-secondary text-xs uppercase tracking-wider mb-2 px-2">
                    workspace
                  </h3>

                  <button className="w-full text-left px-3 py-2 rounded-md hover:bg-white/5 transition-all flex items-center space-x-3">
                    <FontAwesomeIcon
                      icon={faBolt}
                      className="text-text-secondary text-xs"
                    />
                    <span className="text-sm truncate">My Collection</span>
                  </button>

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
                  </button>
                </div>
              </aside>

              {/* 主要内容 */}
              <main className="flex-1 flex flex-col relative">
                {/* 聊天容器 */}
                <div
                  className="flex-1 overflow-y-auto px-4 py-6 space-y-6"
                  ref={chatContainerRef}
                >
                  {/* 示例消息 */}
                  {messages.length === 0 && (
                    <div className="max-w-3xl mx-auto">
                      {/* 用户消息 */}
                      {/* <div className="user-message mb-6 rounded-tr-lg rounded-b-lg bg-deep-black/50 backdrop-blur-sm p-4 ml-8">
                        <p>
                          你能解释一下人工智能中的神经网络是如何工作的吗？请用简单易懂的方式解释。
                        </p>
                      </div> */}

                      {/* AI消息 */}
                      {/* <div className="ai-message mb-6 rounded-tl-lg rounded-b-lg bg-gradient-to-br from-deep-black/90 to-bg-dark/90 backdrop-blur-sm p-4 mr-8">
                        <div className="flex items-center mb-2">
                          <div className="w-8 h-8 relative mr-4">
                            <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/40 to-night-purple/40 rounded-full opacity-70"></div>
                            <div className="absolute inset-0.5 bg-deep-black rounded-full flex items-center justify-center">
                              <span className="text-neon-cyan text-xs font-bold">
                                N
                              </span>
                            </div>
                          </div>
                          <p className="text-sm text-text-secondary">Nova.AI</p>
                        </div>

                        <div className="space-y-3">
                          <p>
                            想象一下神经网络就像是一个由很多层组成的信息处理系统，类似于我们的大脑：
                          </p>

                          <ol className="list-decimal pl-5 space-y-2">
                            <li>
                              <span className="text-neon-cyan">输入层</span>
                              ：接收初始数据，就像我们的感官接收外部信息
                            </li>
                            <li>
                              <span className="text-neon-cyan">隐藏层</span>
                              ：在中间处理信息，提取复杂特征
                            </li>
                            <li>
                              <span className="text-neon-cyan">输出层</span>
                              ：产生最终结果，比如分类或预测
                            </li>
                          </ol>

                          <p>
                            每层由多个"神经元"组成，它们相互连接。每个连接有一个"权重"，决定了信息传递的强度。当数据通过网络时，每个神经元会：
                          </p>

                          <ul className="list-disc pl-5 space-y-2">
                            <li>接收来自前一层的输入</li>
                            <li>根据权重计算加权和</li>
                            <li>通过"激活函数"转换信号</li>
                            <li>将结果传给下一层</li>
                          </ul>

                          <p>
                            训练过程中，网络通过"反向传播"算法调整权重，减小预测结果与实际结果的差异。随着反复训练，网络逐渐学会识别模式和做出准确预测。
                          </p>

                          <p>
                            这就像一个孩子学习区分猫和狗 -
                            一开始会犯错，但通过不断反馈和调整，最终能够准确辨别。
                          </p>
                        </div>
                      </div> */}
                    </div>
                  )}

                  {/* 历史消息 */}
                  {messages.map((msg, index) => (
                    <div key={index} className="max-w-3xl mx-auto">
                      {msg.sender === "user" ? (
                        <div className="user-message mb-6 rounded-tr-lg rounded-b-lg bg-deep-black/50 backdrop-blur-sm p-4 ml-8">
                          <div className="flex items-center mb-2">
                            {/* <div className="w-8 h-8 rounded-full bg-night-purple/20 border border-night-purple/30 flex items-center justify-center -ml-12 mr-4">
                              <FontAwesomeIcon
                                icon={faUser}
                                className="text-xs text-text-secondary"
                              />
                            </div> */}
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
                        <div className="flex items-center mb-2">
                          <div className="w-8 h-8 relative mr-4">
                            <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/40 to-night-purple/40 rounded-full opacity-70 animate-pulse"></div>
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
                <div className="border-t border-night-purple/20 bg-deep-black/50 backdrop-blur-md p-4">
                  <div className="max-w-3xl mx-auto relative">
                    <div className="relative gradient-border">
                      <div className="flex items-center bg-deep-black rounded-md overflow-hidden input-active">
                        <textarea
                          ref={textareaRef}
                          rows={1}
                          placeholder="问点什么..."
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
          </div>
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
}

export default App;
