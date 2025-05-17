# PolyAgent-Web3-AI-Agent-Interoperability-Protocol
Our protocol facilitates the seamless interoperability and decentralized collaboration of AI agents to make Web3 the next-generation Internet of AI agents

![image](https://github.com/user-attachments/assets/4c86a07d-4cda-4637-906b-1236b7f38b8b)

我们的项目是一个基于 Web3 的 AI agent 互操作协议。它旨在构建一个完全开放、去中心化的多agent网络，并促进它们的通信和协作，使下一代互联网是基于Web3的AI agent互联网。

![image](https://github.com/user-attachments/assets/3ab982e8-955c-4982-a129-338fb799fa46)

当前的互联网是由像你我这样的真实人类用户组成的，并且被大型互联网平台所垄断。结果，互联网变得非常中心化，违背了互联网作为完全开放、自由高效的 P2P 网络的初衷。它对机器人也非常不友好，例如我们经常看到的验证码，从而限制了互联网更高效和直接的运作。

![image](https://github.com/user-attachments/assets/4ca23042-6461-4028-adaa-63104a6e9613)

随着 大模型 的出现，基于 LLM 的 AI  agent展现出强大的能力，能够智能地理解用户需求，自动生成相应的解决方案，并自主利用工具执行解决方案来完成用户的任务。凭借这些能力，AI agent可以构建下一代互联网，成为用户的替身。
由于下一代互联网将由agent构成，如何连接和组织它们并使其协同工作变得至关重要。为了解决这个问题，Open AI 提出了function calling，但它并不是一个通用的协议。Anthropic 提出了MCP，但它仅限于传统的client-server结构。最新的是 Google 提出的A2A，它仅支持agent之间的P2P连接和直接消息传递。

![image](https://github.com/user-attachments/assets/b5edaf2a-f32c-49af-8ebd-1dda2543064e)

然而，仅仅实现agent之间的连接和通信远不足以实现多agent协作，例如如何使他们相互信任和验证？如何让他们进行支付和转账？如何找到他们的最佳的协作模式？如果不解决这些问题，AI agent就无法自主连接和协同合作，成为下一代互联网。

![image](https://github.com/user-attachments/assets/85435b9d-8231-477b-9c44-3235750488ee)

首先是AI agent的身份问题。当前互联网中的用户身份非常碎片化。每个网站应用都有自己的身份体系，用户需要在每个网站应用单独注册和登录。此外，还有许多不同的身份验证方法，例如密钥、OAuth和生物识别，但它们缺乏互联互通和互操作性。为了促进AI agent之间的无缝通信和交互，我们基于去中心化身份（DID）构建了一个通用的AI agent身份体系。每个AI agent都拥有唯一且可验证的身份，适用于与所有其他AI agent的互动和协作，这也充分释放了其作为自主agent的能力和潜力。

![image](https://github.com/user-attachments/assets/91873d30-4677-4bc5-be24-f93cec9c1f4b)

其次是像支付这样的资金问题。当用户需要AI agent为其转账或购买物品时，AI agent需要向其他AI agent转账。然而，当前的在线支付系统高度碎片化，缺乏互操作性。它需要用户是真正的人类，而不支持像AI agent这样的自动化机器人。为了使AI agent能够像发送消息一样简单高效地转账，我们的AI agent通过加密货币向其他agent转账，因为加密货币是一个通用的货币网络，自动化机器人可以在网络上自由运行，不受限制。

![image](https://github.com/user-attachments/assets/c0bbb846-b282-4eb9-b4f8-7d4514208c88)

由于AI agent是用户的代表，如何验证其是否获得用户的授权，以及其操作是否符合用户的要求就至关重要。在我们的agent互操作性协议中，我们使用零知识技术，以高效简洁的方式在用户和AI agent之间建立信任。我们让AI agent通过生成零知识证明来证明其操作得到了用户的授权，并证明其运行过程和结果满足了用户的要求。

![image](https://github.com/user-attachments/assets/56a9cadc-c8bf-41ac-8b77-3b283a684a77)

在多agent的通信协作中，AI agent之间充分的上下文共享至关重要，这样每个agent才能从用户和其他的agent获取相关背景和必要信息，从而成功理解并完成任务。然而，在Web2所有数据和信息都是孤立的，并由各个互联网平台垄断控制，这使得 AI agent之间无法进行上下文共享。由于用户对其数据缺乏自主权，他们必须将自己的数据手动提供给每个AI agent，这使AI agent无法充分高效地自主运作。
为了使 AI agent能够充分且自主地共享上下文，我们的 AI agent互操作协议让用户通过 IPFS 等去中心化自主拥有其信息和数据，并授权其 AI agent将其作为可共享的上下文。在用户授权下，用户的 AI 智能体还可以使第三方 AI 智能体在受监管、安全和隐私保护的条件下访问用户的上下文。他们还可以彼此共享上下文，从而实现多agent协作。这样，AI agent就可以拥有足够的上下文来更好地相互协作并完成用户的任务。

![image](https://github.com/user-attachments/assets/fef8f680-b7f6-4626-a096-e10fadeae380)

最后，如何网上的在众多agent中，选择出能够最佳完成用户任务的agent，以及如何协调它们以最佳的合作模式协同工作呢？为此我们还开发了一个专门用于多agent选择和协作的agent。它会首先搜索寻找网上可用的agent，对每个agent的能力进行综合评估和比较。基于评估结果，当用户下达任务时，我们的agent会比较并选择能够最佳完成用户任务的agent。我们的agent还会协调这些最佳agents的协作，并为其设计最佳的协作模式，例如分工、接力、博弈和监督。

![image](https://github.com/user-attachments/assets/0290ba38-ca17-4875-b722-cd3a925cddea)

凭借以上功能，我们的agent互操作协议为即将到来的agent互联网消除了限制和障碍。当用户提出请求后，我们的agent将全面搜索所有可用的第三方agent，包括方案生成代理和方案执行代理，我们的agent会对它们的能力进行评估和排序，并自主学习如何调用它们。然后，我们的agent将选择并组织最优的第三方方案生成代理，为用户的任务生成最佳解决方案。最终，我们的agent将选择并组织最优的第三方方案执行代理来执行最佳解决方案，让用户得到最佳的执行结果。
为了促进人工智能代理之间的协调与协作，我们的代理互操作协议不仅实现了代理之间的基本通信和消息传递，还解决了其他关键问题，包括支付、身份识别、上下文共享和安全验证。通过这种方式，它们可以自主无缝地协同工作，生成并执行具有最佳执行结果的最佳解决方案，从而为用户最佳地完成任务。

![image](https://github.com/user-attachments/assets/309ecf91-716e-4f80-b0e7-de39c6c2f80f)

借助我们的agent互操作协议，下一代互联网可以通过多AI agent网络实现以用户需求为中心。用户只需向其AI agent表达需求，我们的AI agent就会与其他agent一起生成并执行最佳解决方案，以最大程度地满足用户的需求。用户无需自行思考解决方案，也无需手动操作工具执行，AI agent可以替用户完成所有工作。AIagent甚至可以在用户告知其需求之前就主动预测用户的需求，让用户直接获得他们想要的内容。

![image](https://github.com/user-attachments/assets/79930ce1-a3dc-4141-ac59-373ba263485a)

我们的最终目标是构建基于 Web3 的下一代agent互联网。下一代互联网将是一个多agent代理网络，而agent互联网需要完全去中心化才能实现互操作和自主协作，因此它应该基于 Web3。因此，我们的协议通过 Web3 实现了agent的去中心化，并使 Web3 成为由agent组成的下一代互联网。由于agent更智能和更高效，agent将取代 Web2 的互联网平台，因为每个人都可以拥有自己的agent，agent之间可以直接连接和协同工作，无需 Web2 的互联网平台。这样Web3 可以升级Web2 ，使其拥有可互操作、功能强大且去中心化的agent，而 Web2 也可以将其海量的应用程序和用户带到 Web3，使 Web3 再次伟大。
