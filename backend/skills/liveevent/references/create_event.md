# LiveEvent 服务 API 文档：创建/编辑事件

## 1. 业务说明
此接口用于在 LiveEvent（事件网格）中创建或编辑一个事件（Event）。
由于底层架构差异，目前支持两种底层协议（Protocol）：`MQS` 和 `KAFKA`。两者在创建时所需的默认参数（如 region、endpoint 等）有所不同。

**对于 Agent 技能化（Skill）的开发要求：**
大模型只需要从用户的自然语言中提取 2 个参数：
1. `protocol` (必填)：协议类型，枚举值为 "MQS" 或 "KAFKA"。
2. `resource_name` (选填)：事件资源的名称。如果用户没有提供，脚本内部自动生成一个以 `T_` 开头加上当前时间戳的默认名称。

## 2. API 基础信息
- **接口地址 (URL)**: `https://apigw-beta.huawei.com/api/event/api/beta/manage/managingEventInfoByEda`
- **请求方法 (Method)**: `POST`
- **必填请求头 (Headers)**:
  - `X-HW-ID`: 通过环境变量 `HW_ID` 配置
  - `X-HW-APPKEY`: 通过环境变量 `HW_APPKEY` 配置
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
                "// 根据 protocol 的不同，填入不同的默认值字典"
            }
        }
    ]
}
```

### 3.1 当 protocol == "MQS" 时的 resource 默认值
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
    "accountId": "test_it"
}
```

### 3.2 当 protocol == "KAFKA" 时的 resource 默认值
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
    "accountId": "test_it"
}
```

## 4. 返回值处理
期望的成功返回值为 HTTP 200，`code == 200` 时提取 `msg` 和最终生效的 `resourceName`。

```json
{
    "code": 200,
    "msg": "新增/编辑事件成功",
    "data": {
        "eventOperationType": 0,
        "edaInfos":[
            {
                "servers": { "protocol": "MQS" },
                "resource": { "resourceName": "T_test_mqs_0309_2" }
            }
        ]
    }
}
```
