import importlib
import json
import sys
import tempfile
import types
from pathlib import Path

from fastapi.testclient import TestClient


class FakeAgentEngine:
    def __init__(self):
        self.events = []

    async def chat(self, user_message: str):
        for event in self.events:
            yield event


def load_main_module(monkeypatch, tmp_path: Path):
    fake_engine_module = types.ModuleType("backend.agent.engine")
    fake_engine_module.AgentEngine = FakeAgentEngine
    monkeypatch.setitem(sys.modules, "backend.agent.engine", fake_engine_module)
    sys.modules.pop("backend.main", None)

    module = importlib.import_module("backend.main")
    module.DATA_DIR = tmp_path
    module.SESSIONS_FILE = tmp_path / "sessions.json"
    module._sessions = {}
    return module


def make_local_tmp_dir() -> Path:
    base_dir = Path(".test_tmp_runtime").resolve()
    base_dir.mkdir(exist_ok=True)
    return Path(tempfile.mkdtemp(dir=str(base_dir))).resolve()


def test_health_endpoint(monkeypatch):
    tmp_path = make_local_tmp_dir()
    module = load_main_module(monkeypatch, tmp_path)
    monkeypatch.setenv("LLM_MODEL", "test-model")
    client = TestClient(module.app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model": "test-model"}


def test_login_and_session_endpoints(monkeypatch):
    tmp_path = make_local_tmp_dir()
    module = load_main_module(monkeypatch, tmp_path)
    client = TestClient(module.app)

    login_response = client.post("/api/auth/login", json={"username": "alice"})
    assert login_response.status_code == 200
    assert login_response.json()["username"] == "alice"

    create_response = client.post("/api/sessions", json={"name": "demo"})
    assert create_response.status_code == 200
    session_id = create_response.json()["id"]
    assert create_response.json()["name"] == "demo"

    list_response = client.get("/api/sessions")
    assert list_response.status_code == 200
    assert list_response.json()["sessions"][0]["id"] == session_id

    detail_response = client.get(f"/api/sessions/{session_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["name"] == "demo"

    delete_response = client.delete(f"/api/sessions/{session_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Session deleted"


def test_chat_endpoint_updates_session(monkeypatch):
    tmp_path = make_local_tmp_dir()
    module = load_main_module(monkeypatch, tmp_path)
    client = TestClient(module.app)

    create_response = client.post("/api/sessions", json={"name": "temp"})
    session_id = create_response.json()["id"]

    module.agent.events = [
        f'data: {json.dumps({"type": "text", "content": "hello "})}\n\n',
        f'data: {json.dumps({"type": "text", "content": "world"})}\n\n',
        f'data: {json.dumps({"type": "done"})}\n\n',
    ]

    response = client.post(
        "/api/chat",
        json={"message": "this is my first message", "session_id": session_id},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert '"type": "session_update"' in response.text

    session = module._sessions[session_id]
    assert session["name"].startswith("this is my fir")
    assert session["messages"][0]["role"] == "user"
    assert session["messages"][1]["role"] == "assistant"
    assert session["messages"][1]["content"] == "hello world"
