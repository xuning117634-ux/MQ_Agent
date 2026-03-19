# 消息Agent - 部署文档

## 1. 本地开发部署

### 1.1 环境要求
- Python 3.10+
- Node.js 22+
- npm 9+

### 1.2 后端启动

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量（复制并填写真实值）
cp .env.example .env

# 4. 启动后端（端口 8002）
uvicorn backend.main:app --host 0.0.0.0 --port 8002 --reload
```

### 1.3 前端启动（开发模式）

```bash
cd frontend
npm install
npm run dev
# Vite 默认启动在 http://localhost:5173，已配置 /api 代理到 8002
```

### 1.4 前端构建 & 单端口部署（本地生产模式）

```bash
# 构建前端
cd frontend
npm run build

# 拷贝构建产物到后端静态目录
# Linux/macOS:
cp -r dist/* ../backend/static/
# Windows PowerShell:
Copy-Item -Path dist\* -Destination ..\backend\static\ -Recurse -Force

# 启动后端（同时托管前端，需先激活 venv）
cd ..
source venv/bin/activate   
# Windows: 
venv\Scripts\activate
uvicorn backend.main:app --host 0.0.0.0 --port 8002
```

访问 `http://localhost:8002` 即可使用完整应用。

### 1.5 环境变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `LLM_BASE_URL` | 大模型 API 地址（OpenAI 兼容协议） | `https://coding.dashscope.aliyuncs.com/v1` |
| `LLM_API_KEY` | 大模型 API Key | `sk-xxx` |
| `LLM_MODEL` | 模型名称 | `qwen3.5-plus` |
| `HW_ID` | LiveEvent 服务 HW_ID | `com.huawei.pass.roma.event` |
| `HW_APPKEY` | LiveEvent 服务 AppKey | `your_appkey` |

---

## 2. Docker 容器化

### 2.1 Dockerfile（多阶段构建）

在项目根目录创建 `Dockerfile`：

```dockerfile
# ---- Stage 1: 构建前端 ----
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --registry=https://registry.npmmirror.com
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Python 运行时 ----
FROM python:3.10-slim
WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 拷贝后端代码
COPY backend/ ./backend/

# 拷贝前端构建产物到后端静态目录
COPY --from=frontend-build /app/frontend/dist/ ./backend/static/

EXPOSE 8002

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

### 2.2 .dockerignore

在项目根目录创建 `.dockerignore`：

```
venv/
__pycache__/
*.pyc
.env
.idea/
.vscode/
.claude/
node_modules/
frontend/dist/
backend/data/
backend/static/
backend/__pycache__/
.git/
```

### 2.3 本地构建 & 运行

```bash
# 构建镜像
docker build -t message-agent:latest .

# 运行容器
docker run -d \
  --name message-agent \
  -p 8002:8002 \
  -e LLM_BASE_URL=https://coding.dashscope.aliyuncs.com/v1 \
  -e LLM_API_KEY=your_api_key \
  -e LLM_MODEL=qwen3.5-plus \
  -e HW_ID=com.huawei.pass.roma.event \
  -e HW_APPKEY=your_appkey \
  message-agent:latest
```

---

## 3. Kubernetes 部署

### 3.1 命名空间

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: message-agent
```

### 3.2 Secret（敏感配置）

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: message-agent-secret
  namespace: message-agent
type: Opaque
stringData:
  LLM_API_KEY: "your_api_key_here"
  HW_APPKEY: "your_appkey_here"
```

### 3.3 ConfigMap（非敏感配置）

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: message-agent-config
  namespace: message-agent
data:
  LLM_BASE_URL: "https://coding.dashscope.aliyuncs.com/v1"
  LLM_MODEL: "qwen3.5-plus"
  HW_ID: "com.huawei.pass.roma.event"
```

### 3.4 Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: message-agent
  namespace: message-agent
  labels:
    app: message-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: message-agent
  template:
    metadata:
      labels:
        app: message-agent
    spec:
      containers:
        - name: message-agent
          image: your-registry.com/message-agent:latest
          ports:
            - containerPort: 8002
          envFrom:
            - configMapRef:
                name: message-agent-config
            - secretRef:
                name: message-agent-secret
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /api/health
              port: 8002
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /api/health
              port: 8002
            initialDelaySeconds: 5
            periodSeconds: 10
```

### 3.5 Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: message-agent
  namespace: message-agent
spec:
  selector:
    app: message-agent
  ports:
    - port: 80
      targetPort: 8002
      protocol: TCP
  type: ClusterIP
```

### 3.6 Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: message-agent
  namespace: message-agent
  annotations:
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
    # SSE 流式响应需要关闭缓冲
    nginx.ingress.kubernetes.io/proxy-buffering: "off"
spec:
  ingressClassName: nginx
  rules:
    - host: message-agent.your-domain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: message-agent
                port:
                  number: 80
```

### 3.7 一键部署

```bash
# 推送镜像到仓库
docker tag message-agent:latest your-registry.com/message-agent:latest
docker push your-registry.com/message-agent:latest

# 部署到 K8S
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# 检查状态
kubectl get pods -n message-agent
kubectl logs -f deployment/message-agent -n message-agent
```

---

## 4. 注意事项

- SSE 流式响应：Ingress/网关层必须关闭 proxy buffering，否则流式输出会被缓冲导致前端无法实时接收。
- 会话存储：当前使用本地 JSON 文件存储会话数据（`backend/data/sessions.json`），K8S 多副本部署时会话不共享。生产环境建议接入 Redis 或数据库。
- 镜像仓库：`your-registry.com` 需替换为实际的容器镜像仓库地址。
- 域名：`message-agent.your-domain.com` 需替换为实际域名并配置 DNS 解析。
