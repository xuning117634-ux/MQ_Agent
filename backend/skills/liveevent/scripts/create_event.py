#!/usr/bin/env python3
"""
LiveEvent 创建事件独立脚本。
协议：stdin 接收 JSON 参数，stdout 输出 JSON 结果。
用法：echo '{"protocol":"MQS"}' | python create_event.py
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

MQS_RESOURCE_DEFAULTS = {
    "operationType": 0,
    "enterprise": "11111111111111111111111111111111",
    "appId": "com.huawei.pass.roma.event",
    "regionCode": "EDC_GREEN",
    "regionName": "东莞",
    "instanceId": "",
    "instanceName": "",
    "cloudVendor": "HuaweiCloud",
    "endpoint": "nkgtsv20112ctx.huawei.com:9776;nkgtsv20113ctx.huawei.com:9776",
    "createdBy": "agent",
    "eventType": 2,
    "accountId": "test_it",
}

KAFKA_RESOURCE_DEFAULTS = {
    "operationType": 0,
    "enterprise": "11111111111111111111111111111111",
    "appId": "com.huawei.pass.roma.event",
    "regionCode": "cn-west-hcd-4",
    "regionName": "华西-贵阳二零二-华为云(鲲鹏专属)",
    "instanceId": "8045624d-e131-4872-b2e2-62373d9b33cb",
    "instanceName": "agentAateway_dev",
    "cloudVendor": "HuaweiCloud",
    "endpoint": "7.180.154.189:9093,7.180.152.77:9093,7.180.153.15:9093",
    "createdBy": "agent",
    "eventType": 2,
    "accountId": "test_it",
}

API_URL = "https://apigw-beta.huawei.com/api/event/api/beta/manage/managingEventInfoByEda"
SUPPORTED_PROTOCOLS = {"MQS", "KAFKA"}


def _is_valid_protocol(protocol: str) -> bool:
    return protocol in SUPPORTED_PROTOCOLS


def _build_invalid_protocol_result(protocol: str) -> dict:
    return {"success": False, "error": f"Invalid protocol: {protocol}. Must be 'MQS' or 'KAFKA'"}


def _resolve_resource_name(resource_name: str | None) -> str:
    if resource_name:
        return resource_name
    return f"T_{int(time.time() * 1000)}"


def _get_resource_defaults(protocol: str) -> dict:
    if protocol == "MQS":
        return MQS_RESOURCE_DEFAULTS.copy()
    return KAFKA_RESOURCE_DEFAULTS.copy()


def _build_payload(protocol: str, resource_name: str) -> dict:
    resource_defaults = _get_resource_defaults(protocol)
    resource_defaults["resourceName"] = resource_name
    return {
        "eventOperationType": 0,
        "edaInfos": [{"servers": {"protocol": protocol}, "resource": resource_defaults}],
    }


def _build_headers() -> dict:
    return {
        "X-HW-ID": os.getenv("HW_ID", "com.huawei.pass.roma.event"),
        "X-HW-APPKEY": os.getenv("HW_APPKEY", "test"),
        "Content-Type": "application/json",
    }


def _extract_resource_name(result: dict, fallback_name: str) -> str:
    eda_infos = result.get("data", {}).get("edaInfos", [])
    if not eda_infos:
        return fallback_name
    return eda_infos[0].get("resource", {}).get("resourceName", fallback_name)


def _build_success_result(result: dict, resource_name: str, protocol: str) -> dict:
    return {
        "success": True,
        "msg": result.get("msg", "事件创建成功"),
        "resourceName": _extract_resource_name(result, resource_name),
        "protocol": protocol,
    }


def _build_failure_result(result: dict) -> dict:
    return {
        "success": False,
        "error": result.get("msg", "Unknown error"),
        "code": result.get("code"),
    }


def _send_create_event_request(payload: dict, headers: dict) -> dict:
    response = httpx.post(API_URL, json=payload, headers=headers, timeout=10.0)
    response.raise_for_status()
    return response.json()


def create_event(protocol: str, resource_name: str = None) -> dict:
    if not _is_valid_protocol(protocol):
        return _build_invalid_protocol_result(protocol)

    resolved_resource_name = _resolve_resource_name(resource_name)
    payload = _build_payload(protocol, resolved_resource_name)
    headers = _build_headers()

    try:
        result = _send_create_event_request(payload, headers)
    except httpx.HTTPError as exc:
        return {"success": False, "error": f"HTTP error: {str(exc)}"}
    except Exception as exc:
        return {"success": False, "error": f"Error: {str(exc)}"}

    if result.get("code") == 200:
        return _build_success_result(result, resolved_resource_name, protocol)
    return _build_failure_result(result)


def main():
    input_data = json.loads(sys.stdin.read())
    result = create_event(
        protocol=input_data.get("protocol", ""),
        resource_name=input_data.get("resource_name"),
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
