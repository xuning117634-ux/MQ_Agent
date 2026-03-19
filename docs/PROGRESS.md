# 消息Agent - 开发进度控制表

## 🟢 Epic 1: 项目脚手架搭建与连通性测试 (✅ Done)
- [x] 1.1 初始化 Python FastAPI 项目环境 (`backend/`)。
- [x] 1.2 初始化 React + Vite 前端项目 (`frontend/`)。
- [x] 1.3 配置 FastAPI 挂载前端静态文件目录，实现前后端在同一端口下的连通。

## 🟢 Epic 2: Agent 核心引擎与 Skills 注册机制开发 (✅ Done)
- [x] 2.1 编写 `backend/skills/registry.py`，实现一个基于装饰器的简单静态 Skill 注册中心。
- [x] 2.2 开发基础 Agent 对话引擎（封装大模型 API，注入注册表中的 Skills Schema，支持 SSE 流式输出）。
- [x] 2.3 开发一个 `POST /api/chat` 接口供前端调用（SSE 响应）。

## 🟢 Epic 3: LiveEvent 服务技能化 (✅ Done)
- [x] 3.1 阅读 `docs/api/liveevent/create_event.md`。
- [x] 3.2 实现 `create_live_event` 技能并注册。
- [x] 3.3 端到端验证：通过对话触发技能调用，验证 API 请求与返回。
- [x] 3.4 Skills 架构重构：按 Anthropic 官方规范重构为文件夹式技能包（SKILL.md + scripts/ + references/ + examples/），registry.py 改为自动扫描 + subprocess 执行。

## ⚪ Epic 4: MQS 服务技能化 (Todo)
- [ ] 4.1 阅读 MQS API 文档（按需创建 `docs/api/mqs/` 目录）。
- [ ] 4.2 在 `backend/skills/mqs/` 下按 Skills 规范创建技能包（SKILL.md + scripts/）。
- [ ] 4.3 通过端到端验证大模型能否正确路由到 MQS 技能并生成正确参数。

## ⚪ Epic 5: LiveFlow 服务技能化 (Pending - 待规划)
- [ ] 待需求明确后补充。

## ⚪ Epic 6: 前端 Web Chat UI 完善 (Todo)
- [ ] 6.1 开发流式打字机效果的对话组件。
- [ ] 6.2 增加 Tool Calling 过程中的中间状态 UI（如"🛠️ 正在创建 LiveEvent..."）。