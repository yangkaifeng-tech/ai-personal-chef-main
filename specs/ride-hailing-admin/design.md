# 网约车后台与 AI 管家技术设计

## Design Specification

1. Purpose Statement: 本系统面向网约车运营后台用户，核心任务是高频管理司机、车辆、权限和 AI 管家能力。界面需要服务日常运营，优先保证信息密度、权限清晰、表格操作高效和状态可扫描。
2. Aesthetic Direction: Industrial/utilitarian。
3. Color Palette: `#0f172a` 深色侧栏，`#f8fafc` 页面底色，`#2563eb` 主操作蓝，`#16a34a` 成功/启用，`#dc2626` 删除/禁用。
4. Typography: 使用 `Aptos`、`PingFang SC`、`Microsoft YaHei`，以中文后台可读性优先。
5. Layout Strategy: 传统后台布局，左侧固定菜单、顶部用户栏、内容区表格和表单；不做营销式首屏。核心列表使用紧凑工具栏 + 表格 + 分页，AI 管家使用后台内容区内的双栏对话布局。

## 架构

项目采用前后端分离：

```text
frontend/                  Vue 3 + Vite + TypeScript + Element Plus
src/app/                   FastAPI 后端
PostgreSQL                 业务数据 + LangGraph checkpoint
SQLite                     可选 checkpoint fallback
```

前端开发时通过 Vite proxy 调用 FastAPI。生产时可单独部署前端，也可以将 `frontend/dist` 挂载到 FastAPI 静态目录。

## 后端模块

新增后端模块：

```text
src/app/auth/
  security.py              密码哈希、JWT 创建和解析
  dependencies.py          current_user、权限校验依赖

src/app/api/v1/
  auth.py                  登录、当前用户、菜单权限
  drivers.py               司机 CRUD
  vehicles.py              车辆 CRUD
  permissions.py           用户、角色、菜单、按钮 CRUD 和授权

src/app/db/
  models.py                业务表 SQLAlchemy model
  session.py               engine/session/init_db
  seed.py                  初始化管理员、角色、菜单、按钮

src/app/services/
  permission_service.py    RBAC 查询和授权逻辑
  driver_service.py        司机业务逻辑
  vehicle_service.py       车辆业务逻辑
```

现有 `chat.py` 和 Agent 模块继续保留，AI 管家页面复用当前 `/api/v1/chat/stream` 和 conversation 接口。

## 数据模型

已有/扩展表：

```text
users
  id
  username
  password_hash
  name
  status
  created_at

roles
  id
  name
  code
  description
  created_at

menus
  id
  parent_id
  name
  path
  component
  icon
  sort
  visible
  permission_code

buttons
  id
  menu_id
  name
  code
  description

user_roles
  user_id
  role_id

role_menus
  role_id
  menu_id

role_buttons
  role_id
  button_id

drivers
  id
  name
  phone
  id_card
  license_no
  status
  rating
  hired_at
  created_at
  updated_at

vehicles
  id
  plate_no
  brand
  model
  color
  status
  seat_count
  driver_id
  registered_at
  created_at
  updated_at
```

AI 会话继续使用：

```text
conversations
messages
```

LangGraph checkpoint 表由 `langgraph-checkpoint-postgres` 自动创建，和业务表放在同一个 PostgreSQL 数据库。

## 权限模型

采用 RBAC：

```text
User -> UserRole -> Role -> RoleMenu -> Menu
User -> UserRole -> Role -> RoleButton -> Button
```

菜单权限控制前端路由和左侧菜单。按钮权限控制页面内按钮显示，也控制后端写操作。

后端接口写操作必须校验按钮 code，例如：

```text
driver:create
driver:update
driver:delete
vehicle:create
vehicle:update
vehicle:delete
permission:user:create
permission:role:update
```

## 认证

使用账号密码登录：

```text
POST /api/v1/auth/login
```

成功后返回：

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {},
  "menus": [],
  "permissions": []
}
```

前端保存 token 到 `localStorage`，Axios 请求自动加：

```text
Authorization: Bearer <token>
```

密码使用 `passlib[bcrypt]` 哈希。JWT 使用 `python-jose`。

## API 设计

认证：

```text
POST /api/v1/auth/login
GET  /api/v1/auth/me
GET  /api/v1/auth/menus
```

司机：

```text
GET    /api/v1/drivers
POST   /api/v1/drivers
GET    /api/v1/drivers/{driver_id}
PUT    /api/v1/drivers/{driver_id}
DELETE /api/v1/drivers/{driver_id}
```

车辆：

```text
GET    /api/v1/vehicles
POST   /api/v1/vehicles
GET    /api/v1/vehicles/{vehicle_id}
PUT    /api/v1/vehicles/{vehicle_id}
DELETE /api/v1/vehicles/{vehicle_id}
```

权限管理：

```text
GET/POST/PUT/DELETE /api/v1/permissions/users
GET/POST/PUT/DELETE /api/v1/permissions/roles
GET/POST/PUT/DELETE /api/v1/permissions/menus
GET/POST/PUT/DELETE /api/v1/permissions/buttons
PUT /api/v1/permissions/users/{user_id}/roles
PUT /api/v1/permissions/roles/{role_id}/menus
PUT /api/v1/permissions/roles/{role_id}/buttons
```

AI 管家：

```text
POST /api/v1/chat/stream
GET  /api/v1/conversations
GET  /api/v1/conversations/{conversation_id}/messages
```

## 前端模块

新增 Vue 项目：

```text
frontend/
  package.json
  vite.config.ts
  tsconfig.json
  src/
    main.ts
    App.vue
    api/
      request.ts
      auth.ts
      drivers.ts
      vehicles.ts
      permissions.ts
      ai.ts
    router/
      index.ts
      dynamicRoutes.ts
    stores/
      auth.ts
      permission.ts
    layouts/
      AdminLayout.vue
    directives/
      permission.ts
    views/
      login/LoginView.vue
      dashboard/DashboardView.vue
      ride/DriverManagement.vue
      ride/VehicleManagement.vue
      ride/DispatchManagement.vue
      ai/ChefHousekeeper.vue
      permissions/UserManagement.vue
      permissions/RoleManagement.vue
      permissions/MenuManagement.vue
      permissions/ButtonManagement.vue
```

前端菜单结构：

```text
网约车管理
  司机管理
  车辆管理
  调度管理
AI管家
  私厨管家
权限管理
  人员管理
  角色管理
  菜单管理
  按钮管理
```

## 前端权限

登录后保存：

```text
token
user
menus
permissions
```

路由守卫逻辑：

```text
未登录 -> /login
已登录访问 /login -> /
访问未授权菜单 -> 403 页面
```

按钮指令：

```vue
<el-button v-permission="'driver:create'">新增司机</el-button>
```

## 初始化数据

系统启动时执行 `seed_default_data()`：

```text
admin / admin123
超级管理员 / super_admin
运营管理员 / operator_admin
普通客服 / support
```

管理员拥有全部菜单和按钮。普通客服只有查看类权限。

## 测试策略

后端：

```text
python -m compileall -q src/app
FastAPI 启动检查
登录接口 smoke
司机 CRUD smoke
车辆 CRUD smoke
权限接口 smoke
```

前端：

```text
npm install
npm run typecheck
npm run build
浏览器验证登录、菜单、按钮权限、司机/车辆 CRUD、AI 管家流式对话
```

## 风险与处理

- PostgreSQL 未启动时，后端无法启动业务接口：需要在 README 中明确建库和环境变量。
- checkpoint 的 PostgreSQL URL 与 SQLAlchemy URL 格式不同：配置中分开 `DATABASE_URL` 和 `POSTGRES_CHECKPOINT_DATABASE_URL`。
- SSE 中包含换行：后端统一 JSON SSE，前端按 event 解析。
- 权限只做前端隐藏不安全：后端写操作也必须校验按钮权限。
