# MQS API 参考

## 认证方式
所有接口使用相同的认证头：
- `X-HW-ID`: 通过环境变量 `HW_ID` 配置
- `X-HW-APPKEY`: 通过环境变量 `HW_APPKEY` 配置

## 1. 创建 Topic
- **URL**: `https://apigw-beta.huawei.com/api/beta/mqs/topics`
- **Method**: `POST`
- **成功标识**: `code == 0`

## 2. 发布 Topic
- **URL**: `https://apigw-beta.huawei.com/api/beta/mqs/publications`
- **Method**: `POST`
- **成功标识**: `code == 0`

## 3. 订阅 Topic
- **URL**: `https://apigw-beta.huawei.com/api/beta/mqs/subscriptions`
- **Method**: `POST`
- **成功标识**: `code == 0`

## 公共参数
- `enterprise`: `11111111111111111111111111111111`
- `appId`: `com.huawei.pass.roma.event`
- `regions`: `["EDC_GREEN"]`
