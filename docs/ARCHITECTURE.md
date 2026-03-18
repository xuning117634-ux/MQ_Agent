# 消息Agent - 系统架构与开发规范

## 1. 技术栈选型
- **后端**：Python 3.10+、FastAPI（提供 API 服务并托管前端静态文件）
- **前端**：React 18 + Vite + Tailwind CSS（构建 SPA 单页应用）
- **Agent 引擎**：纯 Python 实现 + 原生 OpenAI SDK（利用大模型的 Function Calling/Tool Calling 能力，禁止使用 LangChain）。

## 2. 目录结构规范
项目采用前后端分离但单体部署的 Monorepo 结构，严格遵守以下目录：
├── backend/ # Python 后端代码
│ ├── main.py # FastAPI 入口
│ ├── agent/ # 核心 Agent 引擎（处理对话与大模型交互）
│ ├── skills/ # 技能系统目录
│ │ ├── static/ # 静态注册的技能（如 mqs.py, liveevent.py）
│ │ ├── dynamic/ # 动态加载的插件技能
│ │ └── registry.py # 技能注册表引擎
│ └── static/ # 存放 React build 后的静态文件
├── frontend/ # React 前端代码
│ ├── src/
│ │ ├── components/ # Chat UI 组件
│ │ ├── hooks/ # 状态管理（如 useChat）
│ │ └── services/ # 调用后端 FastAPI 接口
├── docs/
│ ├── api/ # 存放散落的传统 API markdown 文档
│ └── PRD.md / ARCHITECTURE.md / PROGRESS.md

## 3. Skills 引擎架构（核心设计）
采用“工具调用（Tool Calling）”模式编排 API。
- **Schema 动态协商**：无需手动编写复杂的静态 Pydantic/JSON Schema，通过提供清晰的 Skill 函数签名（Docstring 和 Type Hint），让大模型自主推导并生成调用所需的数据契约。
- **静态与动态共存**：
  - `skills/static/` 中的技能在服务启动时硬编码注册（针对核心、高频 API）。
  - 支持在 `skills/dynamic/` 下动态加载 JSON/YAML+Python 脚本的插件式技能扩展。

## 4. 开发红线（AI 请严格遵守）
- **严禁过度设计**：不要一次性生成整个后端的代码，必须按照 `PROGRESS.md` 的步骤小步快跑。
- **日志优先**：后端调用大模型 API 和传统后端 API 时，必须输出清晰的 Log，方便 Tech Lead 调试。