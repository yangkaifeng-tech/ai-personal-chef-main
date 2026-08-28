# Implementation Plan

- [x] 1. 补齐后端依赖和配置
  - 新增认证、密码哈希、JWT、PostgreSQL 所需依赖。
  - 扩展配置项：JWT secret、过期时间、默认管理员、数据库连接。
  - 更新 `.env.example` 和 README。
  - _Requirement: 认证, 数据需求_

- [x] 2. 扩展 SQLAlchemy 数据模型
  - 扩展 `users` 表，增加 `username`、`password_hash`、`status`。
  - 新增 `roles`、`menus`、`buttons`、`user_roles`、`role_menus`、`role_buttons`。
  - 新增 `drivers`、`vehicles`。
  - 保留现有 `conversations`、`messages` 给 AI 管家使用。
  - _Requirement: 权限, 权限管理, 网约车管理, 数据需求_

- [x] 3. 实现初始化种子数据
  - 初始化默认管理员账号 `admin / admin123`。
  - 初始化超级管理员、运营管理员、普通客服角色。
  - 初始化网约车管理、AI管家、权限管理菜单。
  - 初始化司机、车辆、权限相关按钮权限。
  - 给超级管理员分配全部菜单和按钮。
  - _Requirement: 初始菜单, 初始角色, 验收标准_

- [x] 4. 实现认证与权限基础设施
  - 实现密码哈希与密码校验。
  - 实现 JWT 创建和解析。
  - 实现 `get_current_user` FastAPI dependency。
  - 实现 `require_permission(code)` 后端按钮权限校验。
  - _Requirement: 认证, 权限_

- [x] 5. 实现认证 API
  - `POST /api/v1/auth/login`
  - `GET /api/v1/auth/me`
  - `GET /api/v1/auth/menus`
  - 登录返回 token、用户信息、菜单树和按钮权限 code。
  - _Requirement: 认证, 权限_

- [x] 6. 实现权限管理服务和 API
  - 实现人员 CRUD。
  - 实现角色 CRUD。
  - 实现菜单 CRUD。
  - 实现按钮 CRUD。
  - 实现用户分配角色。
  - 实现角色分配菜单和按钮。
  - 对权限管理写操作增加 `permission:*` 权限校验。
  - _Requirement: 权限管理_

- [x] 7. 实现司机管理后端
  - 新增司机列表、详情、新增、编辑、删除接口。
  - 支持按姓名、手机号、状态查询。
  - 对新增、编辑、删除接口增加按钮权限校验。
  - _Requirement: 网约车管理_

- [x] 8. 实现车辆管理后端
  - 新增车辆列表、详情、新增、编辑、删除接口。
  - 支持按车牌号、状态、司机查询。
  - 支持车辆关联司机。
  - 对新增、编辑、删除接口增加按钮权限校验。
  - _Requirement: 网约车管理_

- [x] 9. 调整 AI 管家后端鉴权
  - 让 AI 管家接口使用当前登录用户。
  - 保持现有多用户 conversation 和 message 存储。
  - 保持 LangGraph checkpoint PostgreSQL/SQLite 配置切换。
  - _Requirement: AI 管家, 数据需求_

- [x] 10. 创建 Vue 3 后台项目
  - 在 `frontend/` 初始化 Vite + Vue 3 + TypeScript。
  - 安装 Element Plus、Vue Router、Pinia、Axios、Element Plus icons。
  - 配置 Vite proxy 指向 FastAPI。
  - 配置 typecheck 和 build scripts。
  - _Requirement: 前端 Vue3 + Element Plus_

- [x] 11. 实现前端基础框架
  - 实现登录页。
  - 实现后台主布局：侧栏、顶部栏、内容区。
  - 实现 Axios token 拦截器。
  - 实现 Pinia auth store。
  - 实现路由守卫。
  - 实现动态菜单渲染。
  - 实现 `v-permission` 按钮权限指令。
  - _Requirement: 认证, 权限_

- [x] 12. 实现网约车管理前端页面
  - 实现司机管理列表、搜索、分页、新增、编辑、删除。
  - 实现车辆管理列表、搜索、分页、新增、编辑、删除。
  - 实现调度管理占位页。
  - 所有新增、编辑、删除按钮使用 `v-permission` 控制。
  - _Requirement: 网约车管理_

- [x] 13. 实现权限管理前端页面
  - 实现人员管理 CRUD 和角色分配。
  - 实现角色管理 CRUD 和菜单/按钮授权。
  - 实现菜单管理 CRUD。
  - 实现按钮管理 CRUD。
  - _Requirement: 权限管理_

- [x] 14. 迁移 AI 管家页面到 Vue
  - 将当前静态私厨页面迁移为 `ChefHousekeeper.vue`。
  - 接入登录用户身份。
  - 接入 SSE 流式响应。
  - 保留图片上传、Markdown 展示、历史会话、清空会话。
  - 放入菜单 `AI管家 / 私厨管家`。
  - _Requirement: AI 管家_

- [x] 15. 后端验证
  - 运行 Python 编译检查。
  - 使用 PostgreSQL 启动 FastAPI。
  - 验证默认数据初始化。
  - 验证登录、菜单权限、按钮权限。
  - 验证司机 CRUD、车辆 CRUD。
  - 验证无 token 返回 401，无权限返回 403。
  - _Requirement: 验收标准_

- [x] 16. 前端验证
  - 运行 `npm run typecheck`。
  - 运行 `npm run build`。
  - 启动 Vite 开发服务。
  - 浏览器验证登录、动态菜单、按钮权限、司机 CRUD、车辆 CRUD、AI 管家流式对话。
  - _Requirement: 验收标准_
