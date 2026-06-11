# AI 旅行记忆助手 MVP

手机端风格的 AI 旅行日志应用。前端使用 Vue3 + Vite + Vant UI，后端使用 FastAPI，数据保存到 MySQL，vivo 大模型 AppKey 只放在后端 `.env`。

## 项目结构

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── travel.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   └── travel.py
│   │   ├── schemas/
│   │   │   └── travel.py
│   │   ├── services/
│   │   │   └── vivo_ai.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.vue
│       ├── main.js
│       ├── router/
│       │   └── index.js
│       ├── services/
│       │   └── api.js
│       ├── styles/
│       │   └── main.css
│       └── views/
│           ├── Generate.vue
│           ├── Home.vue
│           ├── Memory.vue
│           ├── Mine.vue
│           └── TravelDetail.vue
├── .env.example
├── docker-compose.yml
└── schema.sql
```

## 启动 MySQL

```bash
docker compose up -d mysql
```

或手动创建数据库后执行：

```bash
mysql -u root -p < schema.sql
```

## 启动后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

把 `.env` 里的 `VIVO_APP_KEY` 替换成真实 AppKey。没有 AppKey 时，默认会使用本地模拟结果，方便先跑通 MVP。

如果本机暂时没有 MySQL，可以把 `backend/.env` 中的数据库配置改成：

```env
DATABASE_URL=sqlite:///./travel_memory.db
```

这只用于本地前后端联调；需要使用 MySQL 时改回 `.env.example` 中的 `mysql+pymysql://...` 配置即可。

## 启动前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 Vite 输出的地址，通常是 `http://localhost:5173`。页面按移动端宽度设计，后续可接 Capacitor 打包。

前端默认通过 Vite proxy 把 `/api` 转发到 `http://127.0.0.1:8000`，不会使用前端 mock 数据。生产部署或 Capacitor 打包时，可以在 `frontend/.env` 中设置：

```env
VITE_API_BASE_URL=http://你的后端地址/api
```

## 后端接口

- `POST /api/travel/generate` 生成旅行日志并保存
- `GET /api/travel/list` 获取历史记录
- `GET /api/travel/{id}` 获取详情
- `POST /api/travel/year-summary` 生成年度旅行总结
- `POST /api/chat/message` AI 旅行搭子单轮聊天，返回追问和已提取旅行信息
- `POST /api/chat/generate-travel-log` 根据聊天会话和上传图片生成手账日志
- `POST /api/recommend/nearby` 根据当前位置、偏好和 POI 生成下一站推荐
- `GET /health` 健康检查

## 本次升级

- 新增 `ChatGenerate`：聊天式 AI 旅行搭子，不再要求用户一次性填写完整表单。
- 新增图片上传：聊天生成时支持 1-9 张旅行照片，保存到 `backend/uploads` 并在手账详情页展示。
- 新增 `Recommend`：当前位置智能推荐，支持浏览器定位、手动地点、偏好标签和已去过地点。
- 新增 `TravelHandAccount`：旅行日志详情改为手账长页，包含照片胶片、便签、标签、时间轴和长图导出。
- 新增 vivo 封装：`vivo_chat_client.py` 和 `vivo_geo_client.py`，API 失败最多重试 2 次。
- 新增数据库迁移：`migrations/001_chat_recommend_upgrade.sql`。

## 测试数据

聊天生成日志：

```text
我去了杭州西湖
傍晚沿着湖边散步，风吹过荷叶，远处的灯慢慢亮起来
和朋友一起去的
心情很松弛
把晚风收进口袋
手账风
```

上传图片生成手账：

```text
在 AI 旅行搭子页面上传 1-9 张 jpg/png/webp 图片，然后点击“生成手账”。
成功后会跳转到旅行手账详情页，照片会以胶片拼贴形式展示。
```

北京什刹海附近推荐：

```json
{
  "city": "北京",
  "current_place": "什刹海",
  "preferences": ["文化古迹", "小众安静"],
  "visited_places": ["鼓楼"]
}
```

## 注意

- 前端不会保存或传递 vivo AppKey。
- CORS 已在 FastAPI 中配置，默认允许 `http://localhost:5173`。
- 第一版未实现图片识别、真实地图定位、短视频生成和 APK 打包，只保留主流程。
