import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from backend.agent.engine import AgentEngine

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="消息Agent")
agent = AgentEngine()

DATA_DIR = Path(__file__).parent / "data"
SESSIONS_FILE = DATA_DIR / "sessions.json"
DATA_DIR.mkdir(exist_ok=True)

_sessions = {}


def _session_exists(session_id: str) -> bool:
    return session_id in _sessions


def _get_session(session_id: str) -> dict | None:
    return _sessions.get(session_id)


def _load_json_file(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def _save_json_file(file_path: Path, payload: dict) -> None:
    with open(file_path, "w", encoding="utf-8") as file_handle:
        json.dump(payload, file_handle, ensure_ascii=False, indent=2)


def load_sessions_from_file():
    global _sessions

    if not SESSIONS_FILE.exists():
        _sessions = {}
        return

    try:
        _sessions = _load_json_file(SESSIONS_FILE)
        logger.info("Loaded %s sessions from file", len(_sessions))
    except Exception as exc:
        logger.error("Failed to load sessions: %s", exc)
        _sessions = {}


def save_sessions_to_file():
    try:
        _save_json_file(SESSIONS_FILE, _sessions)
    except Exception as exc:
        logger.error("Failed to save sessions: %s", exc)


def _build_session_summary(session: dict) -> dict:
    return {
        "id": session["id"],
        "name": session["name"],
        "createdAt": session["createdAt"],
        "messageCount": len(session.get("messages", [])),
    }


def _get_sorted_sessions() -> list[dict]:
    sessions = [_build_session_summary(session) for session in _sessions.values()]
    sessions.sort(key=lambda item: item["createdAt"], reverse=True)
    return sessions


def _build_new_session(session_name: str) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "name": session_name,
        "createdAt": datetime.now().isoformat(),
        "messages": [],
    }


def _append_user_message(session: dict, user_message: str) -> None:
    session["messages"].append({"role": "user", "content": user_message})


def _append_assistant_message(session_id: str, assistant_content: str) -> None:
    if not assistant_content or not _session_exists(session_id):
        return

    _sessions[session_id]["messages"].append({
        "role": "assistant",
        "content": assistant_content,
    })
    save_sessions_to_file()


def _build_session_title(message: str) -> str:
    stripped_message = message.strip()
    title = stripped_message[:15]
    if len(stripped_message) > 15:
        title += "..."
    return title


def _is_first_user_message(session: dict) -> bool:
    user_messages = [message for message in session["messages"] if message["role"] == "user"]
    return len(user_messages) == 1


def _persist_user_message(session_id: str | None, user_message: str) -> tuple[bool, str | None]:
    if not session_id or not _session_exists(session_id):
        return False, None

    session = _get_session(session_id)
    _append_user_message(session, user_message)

    if not _is_first_user_message(session):
        save_sessions_to_file()
        return False, None

    new_title = _build_session_title(user_message)
    session["name"] = new_title
    save_sessions_to_file()
    return True, new_title


def _extract_event_text(event: str) -> str:
    if "data: " not in event:
        return ""

    try:
        event_data = json.loads(event.split("data: ")[1].split("\n")[0])
    except Exception:
        return ""

    if event_data.get("type") != "text":
        return ""
    return event_data.get("content", "")


def _build_error_event(message: str) -> str:
    return f'data: {json.dumps({"type": "error", "message": message})}\n\n'


def _build_session_update_event(session_id: str, session_name: str) -> str:
    payload = {"type": "session_update", "session_id": session_id, "name": session_name}
    return f"data: {json.dumps(payload)}\n\n"


load_sessions_from_file()


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": os.getenv("LLM_MODEL", "unknown")}


@app.post("/api/auth/login")
async def login(request: Request):
    data = await request.json()
    username = data.get("username", "")

    if not username:
        return {"error": "Username required"}, 400

    token = f"mock_token_{uuid.uuid4().hex[:16]}"
    return {
        "token": token,
        "username": username,
        "message": "Login successful (demo mode)",
    }


@app.get("/api/sessions")
async def get_sessions():
    return {"sessions": _get_sorted_sessions()}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    session = _get_session(session_id)
    if session:
        return session
    return {"error": "Session not found"}


@app.post("/api/sessions")
async def create_session(request: Request):
    data = await request.json()
    session_name = data.get("name", "新对话")

    session = _build_new_session(session_name)
    _sessions[session["id"]] = session
    save_sessions_to_file()

    return {"id": session["id"], "name": session_name}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    if not _session_exists(session_id):
        return {"error": "Session not found"}

    del _sessions[session_id]
    save_sessions_to_file()
    return {"message": "Session deleted"}


@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    session_id = data.get("session_id")

    if not user_message.strip():
        return {"error": "Empty message"}

    logger.info("Chat request: %s", user_message)
    title_updated, new_title = _persist_user_message(session_id, user_message)

    async def event_generator():
        assistant_content = ""
        try:
            async for event in agent.chat(user_message):
                assistant_content += _extract_event_text(event)
                yield event
        except Exception as exc:
            logger.error("Chat error: %s", exc)
            yield _build_error_event(str(exc))
        finally:
            if session_id:
                _append_assistant_message(session_id, assistant_content)
            if title_updated and new_title:
                yield _build_session_update_event(session_id, new_title)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="frontend")
