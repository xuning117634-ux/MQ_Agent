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
│ ├── skills/ # 技能系统目录（遵循 Anthropic Skills 规范）
│ │ ├── registry.py # 通用技能引擎（自动扫描、解析、执行）
│ │ └── liveevent/ # 每个技能是一个独立文件夹
│ │ ├── SKILL.md # 技能契约（YAML frontmatter + Markdown 指令）
│ │ ├── scripts/ # 独立可执行脚本（stdin/stdout JSON）
│ │ ├── references/ # 补充文档（按需加载）
│ │ └── examples/ # 输入输出示例
│ └── static/ # 存放 React build 后的静态文件
├── frontend/ # React 前端代码
│ ├── src/
│ │ ├── components/ # Chat UI 组件
│ │ ├── hooks/ # 状态管理（如 useChat）
│ │ └── services/ # 调用后端 FastAPI 接口
├── docs/
│ ├── api/ # 存放散落的传统 API markdown 文档
│ ├── SKILLS_SPEC.md # Skills 架构规范文档
│ └── PRD.md / ARCHITECTURE.md / PROGRESS.md

## 3. Skills 引擎架构（核心设计）
采用 Anthropic 官方 Skills 规范，基于”工具调用（Tool Calling）”模式编排 API。详见 `docs/SKILLS_SPEC.md`。
- **SKILL.md 驱动**：每个技能以 SKILL.md 为唯一契约，YAML frontmatter 声明元数据，Markdown body 定义工具 schema 和使用指令。
- **三级渐进式披露**：Level 1 frontmatter 始终加载 → Level 2 body 按需加载 → Level 3 scripts/references 执行时加载。
- **自动发现注册**：registry.py 启动时扫描所有含 SKILL.md 的子文件夹，自动解析并生成 OpenAI Tool Calling schema。
- **独立脚本执行**：scripts/ 中的脚本通过 subprocess 执行（stdin JSON → stdout JSON），不依赖父项目代码，支持跨项目复用。
- **即插即用**：新增技能只需添加一个文件夹到 skills/ 目录，无需修改任何其他代码。

## 4. 开发红线（AI 请严格遵守）
- **严禁过度设计**：不要一次性生成整个后端的代码，必须按照 `PROGRESS.md` 的步骤小步快跑。
- **日志优先**：后端调用大模型 API 和传统后端 API 时，必须输出清晰的 Log，方便 Tech Lead 调试。
- **CLI 工具授权**：你已经被授权使用 jq、curl 和 tree 命令，请在日常 Debug 和文件分析中积极使用它们。