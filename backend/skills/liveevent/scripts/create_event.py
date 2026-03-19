#!/usr/bin/env python3
"""
LiveEvent 创建事件 - 独立可执行脚本
协议：stdin 接收 JSON 参数，stdout 输出 JSON 结果
用法：echo '{"protocol":"MQS"}' | python create_event.py
"""
import sys
import json
import os
import time

try:
    import httpx
except ImportError:
    print(json.dumps({"error": "httpx not installed. Run: pip install httpx"}))
    sys.exit(1)

# 硬编码的默认 payload 字典
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
    "accountId": "test_it"
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
    "accountId": "test_it"
}

API_URL = "https://apigw-beta.huawei.com/api/event/api/beta/manage/managingEventInfoByEda"


def create_event(protocol: str, resource_name: str = None) -> dict:
    if protocol not in ["MQS", "KAFKA"]:
        return {"success": False, "error": f"Invalid protocol: {protocol}. Must be 'MQS' or 'KAFKA'"}

    if not resource_name:
        resource_name = f"T_{int(time.time() * 1000)}"

    resource_defaults = (MQS_RESOURCE_DEFAULTS if protocol == "MQS" else KAFKA_RESOURCE_DEFAULTS).copy()
    resource_defaults["resourceName"] = resource_name

    payload = {
        "eventOperationType": 0,
        "edaInfos": [{"servers": {"protocol": protocol}, "resource": resource_defaults}]
    }

    hw_id = os.getenv("HW_ID", "com.huawei.pass.roma.event")
    hw_appkey = os.getenv("HW_APPKEY", "test")
    headers = {"X-HW-ID": hw_id, "X-HW-APPKEY": hw_appkey, "Content-Type": "application/json"}

    try:
        response = httpx.post(API_URL, json=payload, headers=headers, timeout=10.0)
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 200:
            final_name = resource_name
            if "data" in result and "edaInfos" in result["data"]:
                if result["data"]["edaInfos"]:
                    final_name = result["data"]["edaInfos"][0].get("resource", {}).get("resourceName", resource_name)
            return {"success": True, "msg": result.get("msg", "事件创建成功"), "resourceName": final_name, "protocol": protocol}
        else:
            return {"success": False, "error": result.get("msg", "Unknown error"), "code": result.get("code")}
    except httpx.HTTPError as e:
        return {"success": False, "error": f"HTTP error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}"}


def main():
    input_data = json.loads(sys.stdin.read())
    result = create_event(
        protocol=input_data.get("protocol", ""),
        resource_name=input_data.get("resource_name")
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
