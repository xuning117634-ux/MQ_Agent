# LiveEvent 检索事件 - 输入输出示例

## 示例 1：按关键字搜索 MQS 事件

**用户输入：** "帮我查一下 MQS 里面有没有 test 相关的事件"

**脚本输入（stdin JSON）：**
```json
{"broker_type": "MQS", "keyword": "test"}
```

**脚本输出（stdout JSON）：**
```json
{
  "success": true,
  "total": 1,
  "events": [
    {
      "eventName": "test_mqs_0309_1",
      "brokerResource": "T_test_mqs_0309_1",
      "brokerType": "MQS",
      "createdBy": "agent",
      "endpoint": "nkgtsv20112ctx.huawei.com:9776;nkgtsv20113ctx.huawei.com:9776",
      "status": true,
      "subscribeNum": 2
    }
  ]
}
```

## 示例 2：查询所有 KAFKA 事件

**用户输入：** "列出所有 KAFKA 事件"

**脚本输入（stdin JSON）：**
```json
{"broker_type": "KAFKA"}
```

## 示例 3：参数错误

**脚本输入（stdin JSON）：**
```json
{"broker_type": "MQTT"}
```

**脚本输出（stdout JSON）：**
```json
{
  "success": false,
  "error": "Invalid broker_type: MQTT. Must be 'MQS' or 'KAFKA'"
}
```
