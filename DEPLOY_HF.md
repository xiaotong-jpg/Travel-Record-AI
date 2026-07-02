# Hugging Face Spaces Docker 部署

这个项目已经可以用 Hugging Face Spaces 的 Docker SDK 部署成一个公网链接。容器会先构建 `frontend`，再由 FastAPI 在同一个 `7860` 端口同时提供前端页面、`/api` 接口和 `/uploads` 静态资源。

## 1. 创建 Space

1. 打开 https://huggingface.co/new-space
2. Space SDK 选择 `Docker`
3. Visibility 可以先选 `Public`，方便评委直接访问
4. 创建后，把本仓库代码推到 Hugging Face Space 仓库

也可以在 Hugging Face 网页里选择从 GitHub 导入，但要确认根目录存在：

- `Dockerfile`
- `README.md` 顶部包含 `sdk: docker` 和 `app_port: 7860`

## 2. 配置环境变量

在 Space 页面进入 `Settings -> Variables and secrets`，添加 Secrets：

```text
VIVO_APP_KEY=你的 vivo AppKey
VIVO_API_BASE=https://api-ai.vivo.com.cn/v1
VIVO_MODEL=Doubao-Seed-2.0-mini
VIVO_IMAGE_MODEL=Doubao-Seedream-4.5
VIVO_MOCK_WHEN_NO_KEY=false
```

`DATABASE_URL` 不填也可以，Docker 默认使用：

```text
sqlite:////data/travel_memory.db
```

免费 Space 的本地文件存储可能会随着重启丢失；比赛演示如果需要长期保留数据，建议之后再接云数据库或开 Hugging Face persistent storage。

## 3. 本地验证 Docker

本地有 Docker 时，可以先运行：

```bash
docker build -t travel-record-ai .
docker run --rm -p 7860:7860 --env-file backend/.env travel-record-ai
```

然后访问：

```text
http://127.0.0.1:7860
```

## 4. 评委访问

Space 构建成功后，评委访问 Hugging Face 给出的 `https://你的用户名-你的space名.hf.space` 链接即可，不需要配置前端、后端或本地环境。

## 参考

- Hugging Face Docker Spaces: https://huggingface.co/docs/hub/en/spaces-sdks-docker
- Hugging Face Spaces Overview: https://huggingface.co/docs/hub/en/spaces-overview