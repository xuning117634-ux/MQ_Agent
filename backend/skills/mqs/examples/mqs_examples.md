# MQS 消息队列 - 输入输出示例

## 示例 1：创建 Topic

**用户输入：** "帮我创建一个 MQS Topic，名称叫 T_order_event"

**脚本输入（stdin JSON）：**
```json
{"topic_name": "T_order_event", "description": "订单事件"}
```

**脚本输出（stdout JSON）：**
```json
{
  "success": true,
  "msg": "MQS Topic 创建成功",
  "topicName": "T_order_event",
  "id": 126357
}
```

## 示例 2：发布 Topic

**用户输入：** "把 T_order_event 发布一下"

**脚本输入（stdin JSON）：**
```json
{"topic_name": "T_order_event"}
```

**脚本输出（stdout JSON）：**
```json
{
  "success": true,
  "msg": "MQS Topic 发布成功",
  "topicName": "T_order_event",
  "id": 248900,
  "regions": ["EDC_GREEN"]
}
```

## 示例 3：订阅 Topic

**用户输入：** "订阅 T_order_event"

**脚本输入（stdin JSON）：**
```json
{"topic_name": "T_order_event", "remarks": "消费订单消息"}
```

**脚本输出（stdout JSON）：**
```json
{
  "success": true,
  "msg": "MQS Topic 订阅成功",
  "topicName": "T_order_event",
  "id": 248901,
  "regions": ["EDC_GREEN"]
}
```

## 示例 4：完整流程

**用户输入：** "帮我创建一个 MQS Topic 并发布和订阅"

Agent 将依次调用：
1. `create_mqs_topic` → 创建 Topic
2. `publish_mqs_topic` → 发布 Topic
3. `subscribe_mqs_topic` → 订阅 Topic
