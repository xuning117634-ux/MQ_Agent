# LiveEvent 检索事件 API 参考

## API 基础信息
- **接口地址**: `https://apigw-beta.huawei.com/api/public/event/searchByEs`
- **请求方法**: `POST`
- **认证头**:
  - `X-HW-ID`: 通过环境变量 `HW_ID` 配置
  - `X-HW-APPKEY`: 通过环境变量 `HW_APPKEY` 配置

## 请求体
```json
{
  "enterpriseId": "11111111111111111111111111111111",
  "brokerType": "MQS",
  "keyword": "T_test_mqs_0309_1"
}
```

## 返回值
成功时 `status == "0000"`，`list` 数组包含匹配的事件列表，`total` 为匹配总数。
