# 消息Agent (Message Agent) - 产品需求文档

## 1. 产品定位
“消息Agent”是对存量产品“消息联接”的 AI 化升级。它是一个基于 Web 聊天界面的智能助手，通过自然语言理解用户的意图，并将其转化为对底层子服务（MQS、LiveEvent、LiveFlow）的 API 调用。

## 2. 核心子服务与 AI 化能力范围
本期 Agent 需要将以下基础功能“Skills 化（技能化）”：

### 2.1 MQS (消息队列服务)
- **核心能力**：通过对话创建 Topic、发布消息到 Topic、订阅 Topic。
- **业务场景**：“帮我建一个名为 order-events 的消息主题，并往里面发一条测试消息。”

### 2.2 LiveEvent (事件网格服务)
- **核心能力**：创建 Event（事件）、检索指定的 Event。
- **业务场景**：“查询一下今天早上关于 user-login 的所有异常事件。”

### 2.3 LiveFlow (流程编排服务)
- **核心能力**：[待补充] 
- **业务场景**：[待补充]

## 3. 产品交互形态
- **前端 Web Chat**：类似 ChatGPT 的纯净聊天界面。包含历史会话区和输入框。
- **Agent 状态反馈**：当 Agent 决定调用某个子服务的 API 时（例如正在创建 Topic），界面上需要有 loading 或“正在调用 MQS 服务...”的中间状态提示。
- **容错机制**：如果用户提供的信息不足以调用 API（比如缺了 Topic 名称），Agent 不能直接报错，必须在聊天中反问用户补充参数。

## 4. API 对接约束
- 后端 API 均为传统的 RESTful API。
- API 的详细文档（Markdown格式）存放在 `docs/api/` 目录下。Agent 需要动态解析用户的意图，生成符合 API 格式的 JSON 参数发起请求。