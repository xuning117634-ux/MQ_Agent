# LiveEvent 服务 API 文档：创建/编辑事件

## 1. 业务说明
此接口用于在 LiveEvent（事件网格）中创建或编辑一个事件（Event）。
由于底层架构差异，目前支持两种底层协议（Protocol）：`MQS` 和 `KAFKA`。两者在创建时所需的默认参数（如 region、endpoint 等）有所不同。

**对于 Agent 技能化（Skill）的开发要求：**
大模型只需要从用户的自然语言中提取 2 个参数：
1. `protocol` (必填)：协议类型，枚举值为 "MQS" 或 "KAFKA"。
2. `resource_name` (选填)：事件资源的名称。如果用户没有提供，Python 技能内部必须使用代码自动生成一个以 `T_` 开头加上当前时间戳的默认名称。

## 2. API 基础信息
- **接口地址 (URL)**: `https://apigw-beta.huawei.com/api/event/api/beta/manage/managingEventInfoByEda`
- **请求方法 (Method)**: `POST`
- **必填请求头 (Headers)**:
  - `X-HW-ID`: `com.huawei.pass.roma.event`
  - `X-HW-APPKEY`: `test`
  - `Content-Type`: `application/json`

## 3. 请求体构造规则 (Payload)

请求体的最外层结构固定为：
```json
{
    "eventOperationType": 0,
    "edaInfos":[
        {
            "servers": {
                "protocol": "<动态填入 MQS 或 KAFKA>"
            },
            "resource": {
                // ... 根据 protocol 的不同，填入不同的默认值字典
            }
        }
    ]
}
```

### 3.1 当 protocol == "MQS" 时的 `resource` 默认值
```json
{
    "operationType": 0,
    "resourceName": "<动态填入或自动生成的名称>",
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
    "accountId" : "test_it"
}
```

### 3.2 当 protocol == "KAFKA" 时的 `resource` 默认值
```json
{
    "operationType": 0,
    "resourceName": "<动态填入或自动生成的名称>",
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
    "accountId" : "test_it"
}
```

## 4. 返回值处理
期望的成功返回值为 HTTP 200，并包含以下格式。如果 `code == 200`，请在 Agent 的技能返回值中提取 `msg` 和最终生效的 `resourceName` 告知大模型。

```json
{
    "code": 200,
    "msg": "新增/编辑事件成功",
    "data": {
        "eventOperationType": 0,
        "edaInfos":[
            {
                "servers": { "protocol": "MQS" },
                "resource": {
                    "resourceName": "T_test_mqs_0309_2"
                }
            }
        ]
    }
}
```

## 5. 开发建议 (给 Claude Code 的提示)
在编写 `backend/skills/static/liveevent.py` 中的 `create_live_event` 技能时：
1. **不要**要求大模型传入 `enterprise`, `regionCode` 等冗长参数，请将这两个不同 protocol 的默认字典作为硬编码常量写在 Python 函数内部。
2. 在组装 payload 之前，判断 `resource_name` 是否为空。如果为空，使用 Python 的 `time` 或 `datetime` 模块生成形如 `T_{timestamp}` 的字符串。
3. Python 函数签名严格按照如下格式编写：
```python
def create_live_event(protocol: str, resource_name: str = None) -> dict:
    """
    在 LiveEvent 服务中创建一个新的事件。
    
    Args:
        protocol: 协议类型，必须是 "MQS" 或 "KAFKA" 之一。
        resource_name: 事件资源的名称。如果不提供则系统将自动生成。
    """
    # ...业务逻辑...
```