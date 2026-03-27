#!/usr/bin/env python3
"""
LiveEvent 检索事件独立脚本。
协议：stdin 接收 JSON 参数，stdout 输出 JSON 结果。
用法：echo '{"broker_type":"MQS","keyword":"test"}' | python search_event.py
"""
import json
import os
import sys

try:
    import httpx
except ImportError:
    print(json.dumps({"error": "httpx not installed. Run: pip install httpx"}))
    sys.exit(1)

API_URL = "https://apigw-beta.huawei.com/api/public/event/searchByEs"
ENTERPRISE_ID = "11111111111111111111111111111111"
SUPPORTED_BROKER_TYPES = {"MQS", "KAFKA"}


def _build_headers() -> dict:
    return {
        "X-HW-ID": os.getenv("HW_ID", "com.huawei.pass.roma.event"),
        "X-HW-APPKEY": os.getenv("HW_APPKEY", "test"),
        "Content-Type": "application/json",
    }


def search_event(broker_type: str, keyword: str = None) -> dict:
    if broker_type not in SUPPORTED_BROKER_TYPES:
        return {"success": False, "error": f"Invalid broker_type: {broker_type}. Must be 'MQS' or 'KAFKA'"}

    payload = {
        "enterpriseId": ENTERPRISE_ID,
        "brokerType": broker_type,
    }
    if keyword:
        payload["keyword"] = keyword

    headers = _build_headers()

    try:
        response = httpx.post(API_URL, json=payload, headers=headers, timeout=10.0)
        response.raise_for_status()
        result = response.json()
    except httpx.HTTPError as exc:
        return {"success": False, "error": f"HTTP error: {str(exc)}"}
    except Exception as exc:
        return {"success": False, "error": f"Error: {str(exc)}"}

    if result.get("status") == "0000":
        events = result.get("list", [])
        summary = []
        for evt in events:
            summary.append({
                "eventName": evt.get("eventName"),
                "brokerResource": evt.get("brokerResource"),
                "brokerType": evt.get("brokerType"),
                "createdBy": evt.get("createdBy"),
                "endpoint": evt.get("endpoint"),
                "status": evt.get("status"),
                "subscribeNum": evt.get("subscribeNum"),
            })
        return {
            "success": True,
            "total": result.get("total", 0),
            "events": summary,
        }

    return {"success": False, "error": result.get("message", "Unknown error")}


def main():
    input_data = json.loads(sys.stdin.read())
    result = search_event(
        broker_type=input_data.get("broker_type", ""),
        keyword=input_data.get("keyword"),
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
