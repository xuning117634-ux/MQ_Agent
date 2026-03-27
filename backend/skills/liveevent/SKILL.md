---
name: LiveEvent 事件管理
description: 在 LiveEvent 服务中创建、检索和管理事件资源。当用户需要创建消息事件、Topic 或查询已有事件时使用。
dependencies: httpx>=0.24.0
---

# LiveEvent 事件管理

## 概述
LiveEvent 是消息事件网格管理服务，支持创建、查询和管理事件资源。
底层支持 MQS 和 KAFKA 两种协议，两者在创建时所需的默认参数（region、endpoint 等）有所不同。

## Tools

### create_live_event
在 LiveEvent 服务中创建一个新的事件。

**Script:** scripts/create_event.py

**Parameters:**
- protocol (string, required): 协议类型，必须是 "MQS" 或 "KAFKA" 之一
- resource_name (string, optional): 事件资源的名称，如果不提供则系统自动生成 T_{timestamp} 格式

### search_live_event
检索 LiveEvent 服务中的事件，支持按协议类型和关键字搜索。

**Script:** scripts/search_event.py

**Parameters:**
- broker_type (string, required): 协议类型，必须是 "MQS" 或 "KAFKA" 之一
- keyword (string, optional): 搜索关键字，用于匹配事件名称。不提供则返回该协议下所有事件

## Constraints
- protocol/broker_type 参数仅支持 MQS 和 KAFKA 两种值
- 鉴权信息通过环境变量配置：HW_ID、HW_APPKEY
- resource_name 如不提供，脚本内部自动生成 T_{毫秒时间戳} 格式

## 使用场景
- 用户说"创建一个消息事件"
- 用户说"建一个 MQS 的 Topic"
- 用户说"创建 KAFKA 通道"
- 用户说"帮我新建一个事件资源"
- 用户说"查一下 MQS 的事件"
- 用户说"搜索名称包含 test 的事件"
- 用户说"有哪些 KAFKA 事件"
