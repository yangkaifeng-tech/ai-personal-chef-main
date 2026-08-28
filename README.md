> **学习说明：本项目仿照黑马程序员的 AI 私厨项目进行学习与实践，仅用于个人学习和技术交流。**

# 网约车管理系统 + AI 管家学习 Demo

一个基于 FastAPI + PostgreSQL + Vue3 + Element Plus 的后台管理系统学习项目，同时保留原有 AI 私厨管家能力。

后端使用 FastAPI 提供 RESTful API，业务数据默认存储在 PostgreSQL。AI 管家通过 LangChain / LangGraph 组织模型、联网搜索与会话记忆，checkpoint 默认存储 PostgreSQL，也可以通过配置切换到 SQLite。前端位于 `frontend/`，使用 Vue3、TypeScript、Element Plus、Pinia、Vue Router 实现传统后台系统。

> 本仓库是个人学习成果，并非黑马程序员官方项目，与黑马程序员不存在商业或官方隶属关系。

## 功能特性

- **真实登录**：默认管理员账号 `admin / admin123`，登录后使用 Bearer Token 访问后端接口。
- **权限管理**：支持人员、角色、菜单、按钮权限 CRUD；用户对应角色，角色对应菜单和按钮。
- **网约车管理**：支持司机管理、车辆管理 CRUD；调度管理保留占位页面。
- **后台前端**：Vue3 + Element Plus 实现左侧菜单、顶部栏、动态菜单、按钮级权限。
- **多模态食材输入**：支持选择、拖拽和粘贴食材图片，也支持纯文字描述。
- **智能菜谱推荐**：结合食材、人数、时间和口味生成候选菜谱。
- **联网搜索**：通过 Tavily 搜索参考菜谱信息。
- **流式对话**：模型生成内容会实时显示，无需等待完整回复。
- **会话记忆**：业务会话和消息保存在业务数据库；LangGraph checkpoint 可配置为 PostgreSQL 或 SQLite。
- **菜谱富文本**：支持标题、列表、表格、引用、代码和图片预览。
- **图片预览**：识别 Markdown 图片、参考图片链接和直接图片 URL。
- **友好的等待体验**：显示生成阶段、等待秒数，并支持停止和重新生成。
- **长内容阅读优化**：用户阅读上方内容时不会被强制拉到底部，可一键回到最新消息。
- **实用交互**：支持复制菜谱、草稿恢复、输入字数提示和新会话二次确认。
- **响应式布局**：兼容桌面端和移动端，并适配键盘操作及减少动画偏好。

## 页面使用流程

1. 上传食材照片，或在输入框中描述已有食材。
2. 可补充用餐人数、烹饪时间、忌口和期望口味。
3. AI 识别需求并调用联网搜索工具查找菜谱。
4. 页面以流式方式展示食材分析、推荐排名、制作步骤和营养建议。
5. 用户可复制菜谱、查看参考图片，或继续追问调整方案。

## 技术栈

| 分类 | 技术 |
| --- | --- |
| 后端 | Python 3.13、FastAPI、Uvicorn |
| AI 编排 | LangChain、LangGraph、LangGraph PostgreSQL/SQLite Checkpointer |
| 模型接口 | OpenAI 兼容接口（示例使用阿里云百炼模型） |
| 联网搜索 | Tavily Search |
| 图片存储 | 阿里云 OSS 预签名上传 |
| 数据存储 | PostgreSQL 默认，SQLite 可用于本地 checkpoint |
| 前端 | Vue3、TypeScript、Element Plus、Pinia、Vue Router、Axios |
| 依赖管理 | uv |

## 工作流程

```mermaid
flowchart LR
    A[用户输入文字或图片] --> B[Web 前端]
    B -->|图片| C[获取 OSS 预签名地址]
    C --> D[上传图片到 OSS]
    B -->|文字与图片 URL| E[FastAPI 对话接口]
    D --> E
    E --> F[LangGraph Agent]
    F --> G[多模态大模型]
    F --> H[Tavily 联网搜索]
    F --> I[SQLite 会话记忆]
    G --> J[流式菜谱回复]
    H --> J
    J --> B
```

## 项目结构

```text
study_raw/
├─ README.md
├─ pyproject.toml              # Python 项目配置与依赖
├─ uv.lock                     # uv 锁定文件
├─ langgraph.json              # LangGraph 配置
├─ .env.example                # 环境变量模板
└─ src/
├─ frontend/                    # Vue3 + Element Plus 后台前端
└─ src/
   └─ app/
      ├─ main.py               # FastAPI 应用入口
      ├─ agents/
      │  └─ personal_chief.py  # AI 私厨 Agent、搜索与会话记忆
      ├─ api/v1/
      │  ├─ auth.py            # 登录、当前用户、菜单权限
      │  ├─ chat.py            # AI 管家对话、历史记录与清空会话接口
      │  ├─ drivers.py         # 司机管理 RESTful API
      │  ├─ vehicles.py        # 车辆管理 RESTful API
      │  ├─ permissions.py     # 人员、角色、菜单、按钮权限管理
      │  └─ oss.py             # OSS 预签名上传接口
      ├─ models/
      │  └─ schemas.py         # Pydantic 请求模型
      ├─ common/
      │  └─ logger.py          # 日志配置
      ├─ db/                   # SQLAlchemy 模型、会话和初始化种子数据
      └─ static/
         ├─ index.html         # 前端页面结构
         ├─ app.css            # 页面视觉和响应式样式
         └─ app.js             # 对话、上传与交互逻辑
```

## 本地运行

## GitHub Actions 自动部署

推送到 `feature-demo` 分支后，GitHub Actions 会通过 SSH 部署到阿里云服务器：拉取代码、同步 Python 依赖、构建 Vue 前端、重启 `ride-ops-api` 并执行健康检查。

首次配置只需在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 添加以下 Secrets：

| Secret | 值 |
| --- | --- |
| `DEPLOY_HOST` | 服务器公网 IP，例如 `8.130.209.205` |
| `DEPLOY_USER` | `root`（或配置了免密 sudo 的专用部署用户） |
| `DEPLOY_SSH_PRIVATE_KEY` | 用于登录服务器的私钥完整内容 |

服务器还需要将相应公钥写入该用户的 `~/.ssh/authorized_keys`。部署配置见 `.github/workflows/deploy.yml`；也可从 Actions 页面手动运行 **Deploy to Alibaba Cloud**。

### 1. 前置条件

- Python 3.13 或更高版本
- [uv](https://docs.astral.sh/uv/)
- 可用的 OpenAI 兼容模型 API
- Tavily API Key
- 阿里云 OSS Bucket 与访问凭据（使用图片上传功能时需要）

### 2. 克隆仓库

```bash
git clone https://github.com/wupa12/ai-personal-chef-learning-demo.git
cd ai-personal-chef-learning-demo
```

### 3. 安装依赖

由于该仓库采用 `src/app` 作为应用包，而不是与项目名同名的可安装包，请跳过安装项目本身：

```bash
uv sync --no-install-project
```

### 4. 配置环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

然后编辑 `.env`，填入自己的 API Key、模型接口和 OSS 配置。请勿把 `.env` 提交到 Git。

### 5. 准备 PostgreSQL

默认连接：

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/personal_chef
POSTGRES_CHECKPOINT_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/personal_chef
CHECKPOINT_BACKEND=postgres
```

如果只是临时本地验证后端结构，可以把业务库临时改成 SQLite：

```bash
DATABASE_URL=sqlite:///./local-dev.db CHECKPOINT_BACKEND=sqlite SQLITE_CHECKPOINT_DB_PATH=./local-checkpoint.db
```

### 6. 启动 FastAPI 后端

建议从项目根目录启动，并显式设置 `PYTHONPATH=src`。

Windows PowerShell：

```powershell
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

macOS / Linux：

```bash
export PYTHONPATH="$(pwd)/src"
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

API 文档：

```text
http://127.0.0.1:8001/docs
```

### 7. 启动 Vue 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问：

```text
http://127.0.0.1:5173
```

Vite 已配置代理，前端请求 `/api/v1/*` 会转发到 `http://127.0.0.1:8001`。

## 环境变量

| 变量 | 是否必需 | 用途 |
| --- | --- | --- |
| `ALIBABA_API_KEY` | 是 | 阿里云百炼/OpenAI 兼容模型密钥 |
| `ALIBABA_API_URL` | 是 | OpenAI 兼容接口基础地址 |
| `TAVILY_API_KEY` | 是 | Tavily 联网搜索密钥 |
| `TAVILY_API_URL` | 否 | Tavily 自定义接口地址 |
| `DATABASE_URL` | 是 | 业务数据库连接，保存用户、会话和消息，默认使用 PostgreSQL |
| `CHECKPOINT_BACKEND` | 否 | Agent checkpoint 存储位置，可选 `postgres` 或 `sqlite`，默认 `postgres` |
| `POSTGRES_CHECKPOINT_DATABASE_URL` | PostgreSQL checkpoint 需要 | LangGraph PostgreSQL checkpoint 连接地址 |
| `SQLITE_CHECKPOINT_DB_PATH` | SQLite checkpoint 需要 | SQLite checkpoint 文件路径 |
| `OSS_ACCESS_KEY_ID` | 图片功能需要 | 阿里云 OSS Access Key ID |
| `OSS_ACCESS_KEY_SECRET` | 图片功能需要 | 阿里云 OSS Access Key Secret |
| `OSS_BUCKET` | 图片功能需要 | OSS Bucket 名称 |
| `OSS_ENDPOINT` | 否 | OSS 公网域名，默认北京区域 |
| `LANGSMITH_API_KEY` | 否 | LangSmith 追踪密钥 |
| `LANGSMITH_TRACING` | 否 | 是否启用 LangSmith 追踪 |
| `LANGSMITH_PROJECT` | 否 | LangSmith 项目名称 |

## API 概览

### 登录

```http
POST /api/v1/auth/login
Content-Type: application/json
```

请求示例：

```json
{
  "username": "admin",
  "password": "admin123"
}
```

登录后前端会把 `access_token` 作为 Bearer Token 发送给需要鉴权的接口。

### 流式生成菜谱

```http
POST /api/v1/chat/stream
Content-Type: application/json
Authorization: Bearer your-token
```

请求示例：

```json
{
  "conversation_id": null,
  "message": "我有两个鸡蛋和一个西红柿，想做一道十分钟内完成的菜",
  "image_url": null
}
```

接口以 SSE 方式返回会话 ID 和流式模型内容。

### 获取会话历史

```http
GET /api/v1/chat/messages?conversation_id=your-conversation-id
```

### 清空会话

```http
DELETE /api/v1/chat/messages?conversation_id=your-conversation-id
```

### 获取用户会话列表

```http
GET /api/v1/conversations
```

### 司机和车辆

```http
GET /api/v1/drivers
POST /api/v1/drivers
PUT /api/v1/drivers/{driver_id}
DELETE /api/v1/drivers/{driver_id}

GET /api/v1/vehicles
POST /api/v1/vehicles
PUT /api/v1/vehicles/{vehicle_id}
DELETE /api/v1/vehicles/{vehicle_id}
```

### 权限管理

```http
GET /api/v1/permissions/users
GET /api/v1/permissions/roles
GET /api/v1/permissions/menus
GET /api/v1/permissions/buttons
```

### 获取 OSS 上传地址

```http
GET /api/v1/oss/presign?filename=example.jpg
```

## 前端交互说明

- 登录页默认填入 `admin / admin123`，可直接登录。
- 左侧菜单由后端角色菜单权限返回。
- 页面中的新增、编辑、删除按钮由按钮权限控制。
- `AI管家 / 私厨管家` 支持图片上传和 SSE 流式响应。

## 数据与安全说明

- `.env` 包含私密凭据，已通过 `.gitignore` 排除。
- 本地 SQLite checkpoint、WAL 文件和缓存文件不会提交到仓库。
- 上传的图片会发送到配置的阿里云 OSS，请勿上传敏感或隐私图片。
- AI 生成的菜谱仅供参考；涉及过敏、慢性疾病、特殊营养或食品安全问题时，应结合专业意见判断。
- 当前项目已实现学习版登录和 RBAC 权限，但仍未包含生产级审计、限流、刷新 token、密码找回等能力。

## 已知限制

- 模型和联网搜索耗时受网络及第三方服务影响。
- 菜品预览要求模型返回直接图片 URL；网页链接无法直接作为图片显示。
- 当前 SQLite 连接与同步 Agent 流程更适合单机学习，不适合高并发部署。
- 前端位于 FastAPI 静态目录中，没有单独的构建和热更新流程。
- `pyproject.toml` 中的项目打包入口仍保留学习过程配置，推荐使用文档中的启动方式。

## 可选改进方向

- 增加模型调用、搜索和图片上传超时。
- 将同步 Agent 流程改为异步或放入线程池。
- 将数据库路径改成不依赖工作目录的绝对路径。
- 增加烹饪步骤模式、计时器、食材勾选和收藏功能。
- 增加结构化模型输出，进一步稳定菜谱卡片和图片展示。
- 公网部署时增加身份验证、限流、日志脱敏和上传校验。

## 学习目的

本项目主要用于练习以下内容：

- FastAPI 接口设计与静态资源托管
- LangChain / LangGraph Agent 开发
- 多模态模型输入与流式输出
- Tavily 工具调用
- SQLite 会话记忆
- OSS 预签名直传
- AI 产品的响应式前端与人机交互设计

欢迎将本仓库作为学习参考，并根据自己的模型、存储方案和交互需求继续扩展。
