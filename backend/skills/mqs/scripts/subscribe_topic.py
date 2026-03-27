#!/usr/bin/env python3
"""
MQS 订阅 Topic 独立脚本。
协议：stdin 接收 JSON 参数，stdout 输出 JSON 结果。
用法：echo '{"topic_name":"T_test_001"}' | python subscribe_topic.py
"""
import json
import os
import sys

try:
    import httpx
except ImportError:
    print(json.dumps({"error": "httpx not installed. Run: pip install httpx"}))
    sys.exit(1)

API_URL = "https://apigw-beta.huawei.com/api/beta/mqs/subscriptions"
ENTERPRISE_ID = "11111111111111111111111111111111"
APP_ID = "com.huawei.pass.roma.event"
DEFAULT_REGION = "EDC_GREEN"


def _build_headers() -> dict:
    return {
        "X-HW-ID": os.getenv("HW_ID", APP_ID),
        "X-HW-APPKEY": os.getenv("HW_APPKEY", "test"),
        "Content-Type": "application/json",
    }


def subscribe_topic(topic_name: str, remarks: str = None) -> dict:
    if not topic_name:
        return {"success": False, "error": "topic_name is required"}

    payload = {
        "id": 0,
        "operator": "agent",
        "appId": APP_ID,
        "remarks": remarks or "",
        "enabled": True,
        "topicName": topic_name,
        "authType": "S",
        "regions": [DEFAULT_REGION],
        "enterprise": ENTERPRISE_ID,
        "relationEnterprise": ENTERPRISE_ID,
        "dcMode": "S",
    }

    headers = _build_headers()

    try:
        response = httpx.post(API_URL, json=payload, headers=headers, timeout=10.0)
        response.raise_for_status()
        result = response.json()
    except httpx.HTTPError as exc:
        return {"success": False, "error": f"HTTP error: {str(exc)}"}
    except Exception as exc:
        return {"success": False, "error": f"Error: {str(exc)}"}

    if result.get("code") == 0:
        data = result.get("data", {})
        return {
            "success": True,
            "msg": "MQS Topic 订阅成功",
            "topicName": data.get("topicName", topic_name),
            "id": data.get("id"),
            "regions": data.get("regions"),
        }

    return {"success": False, "error": result.get("msg", "Unknown error"), "code": result.get("code")}


def main():
    input_data = json.loads(sys.stdin.read())
    result = subscribe_topic(
        topic_name=input_data.get("topic_name", ""),
        remarks=input_data.get("remarks"),
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
