import os
import json
import time
import httpx
from backend.skills.registry import register_skill

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


@register_skill
def create_live_event(protocol: str, resource_name: str = None) -> dict:
    """
    在 LiveEvent 服务中创建一个新的事件。

    Args:
        protocol: 协议类型，必须是 "MQS" 或 "KAFKA" 之一。
        resource_name: 事件资源的名称。如果不提供则系统将自动生成。

    Returns:
        包含创建结果的字典，包括 msg 和最终生效的 resourceName。
    """
    # 验证 protocol
    if protocol not in ["MQS", "KAFKA"]:
        return {"error": f"Invalid protocol: {protocol}. Must be 'MQS' or 'KAFKA'"}

    # 自动生成 resource_name
    if not resource_name:
        timestamp = int(time.time() * 1000)
        resource_name = f"T_{timestamp}"

    # 选择对应的默认字典
    if protocol == "MQS":
        resource_defaults = MQS_RESOURCE_DEFAULTS.copy()
    else:
        resource_defaults = KAFKA_RESOURCE_DEFAULTS.copy()

    # 设置 resourceName
    resource_defaults["resourceName"] = resource_name

    # 构造请求体
    payload = {
        "eventOperationType": 0,
        "edaInfos": [
            {
                "servers": {
                    "protocol": protocol
                },
                "resource": resource_defaults
            }
        ]
    }

    # 读取鉴权信息
    hw_id = os.getenv("HW_ID", "com.huawei.pass.roma.event")
    hw_appkey = os.getenv("HW_APPKEY", "test")

    headers = {
        "X-HW-ID": hw_id,
        "X-HW-APPKEY": hw_appkey,
        "Content-Type": "application/json"
    }

    # 调用 LiveEvent API
    api_url = "https://apigw-beta.huawei.com/api/event/api/beta/manage/managingEventInfoByEda"

    try:
        response = httpx.post(api_url, json=payload, headers=headers, timeout=10.0)
        response.raise_for_status()

        result = response.json()

        # 检查返回值
        if result.get("code") == 200:
            # 提取最终生效的 resourceName
            final_resource_name = resource_name
            if "data" in result and "edaInfos" in result["data"]:
                if result["data"]["edaInfos"]:
                    final_resource_name = result["data"]["edaInfos"][0].get("resource", {}).get("resourceName", resource_name)

            return {
                "success": True,
                "msg": result.get("msg", "事件创建成功"),
                "resourceName": final_resource_name,
                "protocol": protocol
            }
        else:
            return {
                "success": False,
                "error": result.get("msg", "Unknown error"),
                "code": result.get("code")
            }

    except httpx.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }
