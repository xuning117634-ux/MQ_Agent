import os
import json
import logging
import uuid
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from backend.agent.engine import AgentEngine

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="消息Agent")
agent = AgentEngine()

# ---- 会话持久化 ----
DATA_DIR = Path(__file__).parent / "data"
SESSIONS_FILE = DATA_DIR / "sessions.json"
DATA_DIR.mkdir(exist_ok=True)

_sessions = {}


def load_sessions_from_file():
    global _sessions
    if SESSIONS_FILE.exists():
        try:
            with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
                _sessions = json.load(f)
            logger.info(f"Loaded {len(_sessions)} sessions from file")
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            _sessions = {}
    else:
        _sessions = {}


def save_sessions_to_file():
    try:
        with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(_sessions, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save sessions: {e}")


# 启动时加载
load_sessions_from_file()


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": os.getenv("LLM_MODEL", "unknown")}


@app.post("/api/auth/login")
async def login(request: Request):
    """预留登录接口 - 暂时返回 mock token"""
    data = await request.json()
    username = data.get("username", "")

    if not username:
        return {"error": "Username required"}, 400

    token = f"mock_token_{uuid.uuid4().hex[:16]}"
    return {
        "token": token,
        "username": username,
        "message": "Login successful (demo mode)"
    }


@app.get("/api/sessions")
async def get_sessions():
    """获取所有会话（不含 messages，减少传输量）"""
    sessions_list = []
    for s in _sessions.values():
        sessions_list.append({
            "id": s["id"],
            "name": s["name"],
            "createdAt": s["createdAt"],
            "messageCount": len(s.get("messages", []))
        })
    # 按创建时间倒序
    sessions_list.sort(key=lambda x: x["createdAt"], reverse=True)
    return {"sessions": sessions_list}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """获取单个会话（含 messages）"""
    if session_id in _sessions:
        return _sessions[session_id]
    return {"error": "Session not found"}


@app.post("/api/sessions")
async def create_session(request: Request):
    """创建新会话"""
    data = await request.json()
    session_name = data.get("name", "新对话")

    session_id = str(uuid.uuid4())
    session = {
        "id": session_id,
        "name": session_name,
        "createdAt": datetime.now().isoformat(),
        "messages": []
    }

    _sessions[session_id] = session
    save_sessions_to_file()

    return {"id": session_id, "name": session_name}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    if session_id in _sessions:
        del _sessions[session_id]
        save_sessions_to_file()
        return {"message": "Session deleted"}
    return {"error": "Session not found"}


@app.post("/api/chat")
async def chat(request: Request):
    """SSE 流式对话接口"""
    data = await request.json()
    user_message = data.get("message", "")
    session_id = data.get("session_id", None)

    if not user_message.strip():
        return {"error": "Empty message"}

    logger.info(f"Chat request: {user_message}")

    # 保存用户消息 + 自动更新标题
    title_updated = False
    new_title = None
    if session_id and session_id in _sessions:
        session = _sessions[session_id]
        session["messages"].append({"role": "user", "content": user_message})

        # 如果是第一条用户消息，用内容摘要作为标题
        user_msgs = [m for m in session["messages"] if m["role"] == "user"]
        if len(user_msgs) == 1:
            summary = user_message.strip()[:15]
            if len(user_message.strip()) > 15:
                summary += "..."
            session["name"] = summary
            title_updated = True
            new_title = summary

        save_sessions_to_file()

    async def event_generator():
        assistant_content = ""
        try:
            async for event in agent.chat(user_message):
                if 'data: ' in event:
                    try:
                        event_data = json.loads(event.split('data: ')[1].split('\n')[0])
                        if event_data.get('type') == 'text':
                            assistant_content += event_data.get('content', '')
                    except:
                        pass
                yield event
        except Exception as e:
            logger.error(f"Chat error: {e}")
            yield f'data: {json.dumps({"type": "error", "message": str(e)})}\n\n'
        finally:
            # 保存 assistant 消息
            if session_id and session_id in _sessions and assistant_content:
                _sessions[session_id]["messages"].append({
                    "role": "assistant",
                    "content": assistant_content
                })
                save_sessions_to_file()

            # 通知前端标题更新
            if title_updated and new_title:
                yield f'data: {json.dumps({"type": "session_update", "session_id": session_id, "name": new_title})}\n\n'

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# 挂载前端静态文件（必须在最后，否则会拦截 /api 路由）
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="frontend")
