# LiveEvent 创建事件 - 输入输出示例

## 示例 1：创建 MQS 协议事件（指定名称）

**用户输入：** "帮我创建一个 MQS 协议的事件，名称叫 my_test_topic"

**脚本输入（stdin JSON）：**
```json
{"protocol": "MQS", "resource_name": "my_test_topic"}
```

**脚本输出（stdout JSON）：**
```json
{
  "success": true,
  "msg": "新增/编辑事件成功",
  "resourceName": "my_test_topic",
  "protocol": "MQS"
}
```

## 示例 2：创建 KAFKA 协议事件（自动生成名称）

**用户输入：** "创建一个 KAFKA 事件"

**脚本输入（stdin JSON）：**
```json
{"protocol": "KAFKA"}
```

**脚本输出（stdout JSON）：**
```json
{
  "success": true,
  "msg": "新增/编辑事件成功",
  "resourceName": "T_1710000000000",
  "protocol": "KAFKA"
}
```

## 示例 3：参数错误

**脚本输入（stdin JSON）：**
```json
{"protocol": "MQTT"}
```

**脚本输出（stdout JSON）：**
```json
{
  "success": false,
  "error": "Invalid protocol: MQTT. Must be 'MQS' or 'KAFKA'"
}
```
