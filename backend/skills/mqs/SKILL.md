---
name: MQS 消息队列管理
description: 管理 MQS 消息队列的 Topic，包括创建 Topic、发布和订阅。当用户需要创建 MQS Topic、发布 Topic 或订阅 Topic 时使用。
dependencies: httpx>=0.24.0
---

# MQS 消息队列管理

## 概述
MQS 是消息队列服务，支持创建 Topic、发布 Topic（使 Topic 可被发现）、订阅 Topic（消费者接入）。
三个操作通常按顺序进行：创建 → 发布 → 订阅。

## Tools

### create_mqs_topic
创建一个新的 MQS Topic。

**Script:** scripts/create_topic.py

**Parameters:**
- topic_name (string, required): Topic 名称，建议以 T_ 开头
- description (string, optional): Topic 描述信息
- alias_name (string, optional): Topic 别名

### publish_mqs_topic
将已创建的 MQS Topic 发布到指定区域，使其可被其他服务发现和订阅。

**Script:** scripts/publish_topic.py

**Parameters:**
- topic_name (string, required): 要发布的 Topic 名称，必须是已创建的 Topic

### subscribe_mqs_topic
订阅一个已发布的 MQS Topic，建立消费关系。

**Script:** scripts/subscribe_topic.py

**Parameters:**
- topic_name (string, required): 要订阅的 Topic 名称，必须是已发布的 Topic
- remarks (string, optional): 订阅备注说明

## Constraints
- 鉴权信息通过环境变量配置：HW_ID、HW_APPKEY
- 操作顺序：创建 Topic → 发布 Topic → 订阅 Topic
- 发布和订阅前，Topic 必须已存在

## 使用场景
- 用户说"创建一个 MQS Topic"
- 用户说"帮我建一个消息队列主题"
- 用户说"发布这个 Topic"
- 用户说"订阅 T_test_topic"
- 用户说"创建并发布一个 MQS 主题"
