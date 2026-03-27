#!/usr/bin/env python3
"""
MQS 创建 Topic 独立脚本。
协议：stdin 接收 JSON 参数，stdout 输出 JSON 结果。
用法：echo '{"topic_name":"T_test_001"}' | python create_topic.py
"""
import json
import os
import sys
import time

try:
    import httpx
except ImportError:
    print(json.dumps({"error": "httpx not installed. Run: pip install httpx"}))
    sys.exit(1)

API_URL = "https://apigw-beta.huawei.com/api/beta/mqs/topics"
ENTERPRISE_ID = "11111111111111111111111111111111"
APP_ID = "com.huawei.pass.roma.event"


def _build_headers() -> dict:
    return {
        "X-HW-ID": os.getenv("HW_ID", APP_ID),
        "X-HW-APPKEY": os.getenv("HW_APPKEY", "test"),
        "Content-Type": "application/json",
    }


def create_topic(topic_name: str = None, description: str = None, alias_name: str = None) -> dict:
    if not topic_name:
        topic_name = f"T_{int(time.time() * 1000)}"

    payload = {
        "enterprise": ENTERPRISE_ID,
        "appId": APP_ID,
        "topicName": topic_name,
        "description": description or "",
        "aliasName": alias_name or topic_name,
        "isShowMsgBody": 1,
        "routerEnable": True,
        "logEnable": False,
        "status": True,
        "type": "D",
        "physicsEnterprise": ENTERPRISE_ID,
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
            "msg": "MQS Topic 创建成功",
            "topicName": data.get("topicName", topic_name),
            "id": data.get("id"),
            "description": data.get("description"),
        }

    return {"success": False, "error": result.get("msg", "Unknown error"), "code": result.get("code")}


def main():
    input_data = json.loads(sys.stdin.read())
    result = create_topic(
        topic_name=input_data.get("topic_name"),
        description=input_data.get("description"),
        alias_name=input_data.get("alias_name"),
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
