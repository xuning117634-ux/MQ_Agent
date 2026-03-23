import httpx

from backend.skills.liveevent.scripts import create_event as create_event_module


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_create_event_success_with_generated_name(monkeypatch):
    def fake_post(url, json, headers, timeout):
        assert json["edaInfos"][0]["servers"]["protocol"] == "MQS"
        assert json["edaInfos"][0]["resource"]["resourceName"] == "T_123000"
        return DummyResponse(
            {
                "code": 200,
                "msg": "ok",
                "data": {
                    "edaInfos": [
                        {"resource": {"resourceName": json["edaInfos"][0]["resource"]["resourceName"]}}
                    ]
                },
            }
        )

    monkeypatch.setattr(create_event_module.time, "time", lambda: 123)
    monkeypatch.setattr(create_event_module.httpx, "post", fake_post)

    result = create_event_module.create_event("MQS")

    assert result["success"] is True
    assert result["resourceName"] == "T_123000"
    assert result["protocol"] == "MQS"


def test_create_event_invalid_protocol():
    result = create_event_module.create_event("BAD")

    assert result["success"] is False
    assert "Invalid protocol" in result["error"]


def test_create_event_http_error(monkeypatch):
    def fake_post(url, json, headers, timeout):
        raise httpx.HTTPError("boom")

    monkeypatch.setattr(create_event_module.httpx, "post", fake_post)

    result = create_event_module.create_event("KAFKA", resource_name="demo")

    assert result["success"] is False
    assert "HTTP error" in result["error"]
