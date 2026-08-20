# pyvue 项目规则 (Project Rules)

> 本规则基于项目实际代码与技术栈自动梳理，所有版本号均来自项目真实配置文件，修改代码时务必遵循。
> 规则文件路径：`.trae/rules/project_rules.md`

---

## 一、项目概述

- **项目名称**：pyvue（智能柜 IntelligentCabinet 系统）
- **项目类型**：前后端分离单体应用（Django 后端 + Vue 前端打包集成）
- **集成方式**：前端 `npm run build` 后将 `dist` 复制到后端 `Templates/dist/`，由 Django TemplateView 承载 `index.html`，静态资源走 Django `STATICFILES_DIRS`。
- **业务域**：用户/角色/菜单权限（RBAC）、智能柜体/柜格管理、柜格状态流转与记录。

---

## 二、技术栈与精确版本

> 所有版本号来源于 `package.json`、`pyvue/settings.py`、`.idea/misc.xml`、`__pycache__/*.cpython-37.pyc`。

### 后端 (Backend)

| 组件 | 版本 | 来源 |
| --- | --- | --- |
| Python | **3.7** | `.idea/misc.xml`（`Python 3.7 (mecheck)`），pyc 为 cpython-37 |
| Django | **2.1.7** | `pyvue/settings.py` 头部注释 `using Django 2.1.7` |
| Django REST Framework | 已安装（djangorestframework） | `INSTALLED_APPS` + `REST_FRAMEWORK` 配置 |
| djangorestframework-simplejwt | 已安装 | `SIMPLE_JWT` 配置 + `RefreshToken` 使用 |
| django-filter (django_filters) | 已安装 | `INSTALLED_APPS` + 视图使用 `DjangoFilterBackend` |
| django-cors-headers (corsheaders) | 已安装 | `INSTALLED_APPS` + `CorsMiddleware` |
| aliyunsdkcore | 已安装 | `backend01/views.py` 阿里云短信 `AcsClient` |
| 数据库 | **MySQL** | `DATABASES` 配置 `django.db.backends.mysql` |

### 数据库 (Database)

| 项 | 值 |
| --- | --- |
| 引擎 | MySQL（`django.db.backends.mysql`） |
| 库名 | `pyvue` |
| 主机 | `127.0.0.1:3306` |
| 驱动 | mysqlclient / PyMySQL（须与 Python 3.7 兼容） |
| 时区 | `TIME_ZONE='UTC'`，`USE_TZ=False`（本地时间存储） |
| 备注 | 项目根目录存在 `db.sqlite3` 但已被注释，**当前以 MySQL 为准** |

### 前端 (Frontend)

| 组件 | 版本 | 来源 |
| --- | --- | --- |
| Vue | **2.5.2** (`^2.5.2`) | `package.json` dependencies，使用 Options API（`new Vue({})`） |
| vue-router | **3.6.5** (`^3.6.5`)，`mode: 'history'` | `package.json` + `router/router.js` |
| vuex | **3.6.2** (`^3.6.2`) | `package.json` + `store/index.js` |
| vuex-persistedstate | **4.1.0** | `package.json` |
| element-ui | **2.15.14** (`^2.15.14`) | `package.json` + `main.js` 全量引入 |
| axios | **0.20.0** (`^0.20.0`) | `package.json` + `utils/request.js` |
| js-cookie | **3.0.5** | `package.json`（用于 CSRF token 读取） |
| core-js | **3.30.2** | `package.json` + `main.js` `import 'core-js/stable'` |
| 构建工具 | **webpack 3.6.0** (`^3.6.0`) | `package.json` devDependencies（注意：非 webpack 4/5） |
| @vue/cli-service | 5.0.9（仅辅助，实际构建以 webpack 3 配置为主） | `package.json` + `build/` 目录 |
| Node 要求 | `>= 6.0.0`，npm `>= 3.0.0` | `package.json` engines |

> ⚠️ **重要**：本项目前端是 **Vue 2**（非 Vue 3、非 React），组件写法使用 **Options API**，禁止使用 Composition API / `<script setup>` / Vue 3 语法。element-ui 是 **Element UI for Vue 2**（非 Element Plus）。

---

## 三、目录结构约定

```
pyvue/
├── pyvue/                    # Django 项目配置（settings/urls/wsgi）
├── backend01/                # 主后端 app：用户/角色/菜单/权限(RBAC)、认证
│   ├── models.py             #   UserInfo(AbstractBaseUser)/Menu/Permission/Role/Books/Imgs
│   ├── serializer.py         #   DRF Serializer
│   ├── views.py              #   APIView / ViewSet
│   ├── backends.py           #   自定义认证后端 CustomUserBackend
│   ├── urls.py               #   /api/ 路由
│   └── management/commands/  #   自定义命令（如 initdata）
├── IntelligentCabinet/       # 智能柜业务 app：Cabinet/CabinetGrid/GridRecord
│   ├── models.py
│   ├── views.py
│   └── urls.py               #   /IntelligentCabinet/ 路由
├── middleware/               # 自定义中间件
│   └── UserIP.py             #   LogMiddle：记录请求日志/IP
├── Templates/dist/           # 前端打包产物（生产环境由 Django 托管）
├── frontend01/               # Vue 前端源码
│   ├── src/
│   │   ├── api/              #   按业务拆分的请求函数（user.js / cabinet.js）
│   │   ├── layout/           #   布局组件（含菜单顶部/左侧切换）
│   │   ├── router/router.js  #   路由（静态 + 动态 addDynamicRoutes）
│   │   ├── store/            #   Vuex（index.js + modules/）
│   │   ├── utils/request.js  #   axios 实例与拦截器
│   │   ├── views/            #   页面级 .vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── build/                #   webpack 配置
│   ├── config/               #   dev/prod 环境配置
│   └── vue.config.js         #   devServer + 代理
├── logs/                     # 日志（按天滚动 all/error/info）
├── manage.py
└── .trae/rules/              # 本规则目录
```

---

## 四、后端开发规则 (Django)

### 4.1 模型 (Models)

- 自定义用户模型：`AUTH_USER_MODEL = 'backend01.UserInfo'`，继承 `AbstractBaseUser`，登录字段为 `account`。**禁止**改用 `auth.User` 或 `AbstractUser` 以免迁移冲突。
- 用户管理器须继承 `BaseUserManager`，实现 `create_user` / `create_superuser` / `get_by_natural_key`。
- 字段 `verbose_name` 统一使用**中文**（如 `verbose_name="柜体名称"`），`Meta` 中 `verbose_name` / `verbose_name_plural` 必填。
- `Meta.ordering` 显式声明排序；涉及唯一约束用 `unique_together`（如 `('cabinet','position')`）。
- 外键必须显式 `on_delete`（项目统一 `on_delete=models.CASCADE`），关联反查用 `related_name`。
- `DateTimeField`：创建时间用 `auto_now_add=True`，更新时间用 `auto_now=True`。
- 状态枚举用 `choices`（`STATUS_CHOICES = ((0,'空闲'),(1,'使用中')...)`），展示用 `get_<field>_display()`。

### 4.2 序列化器 (Serializers)

- `ModelSerializer` 优先；需保留**原始字段名**时用 `fields` 显式枚举（项目存在大写字段如 `Menu_title`、`CNname`、`Tel`、`Photo`，不要强行改名以保持前后端契约一致）。
- 动态/派生字段用 `SerializerMethodField`（参考 `menu_tree` 实现）。
- 密码字段必须 `extra_kwargs = {'password': {'write_only': True}}`。

### 4.3 视图 (Views)

- 认证类视图继承 `APIView` 或 `viewsets.ModelViewSet` / `GenericViewSet`。
- 登录/注册/重置密码等获取 token 的视图：`authentication_classes = []`、`permission_classes = []`。
- 受保护视图默认 `IsAuthenticated`（已由 `REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES']` 全局配置）。
- DRF 全局配置（位于 `settings.py`）：
  - 认证：`SessionAuthentication` + `JWTAuthentication`
  - 权限：`IsAuthenticated`
- 返回统一用 `Response(data, status=status.HTTP_xxx)`。

### 4.4 路由 (URLs)

- 顶层 `pyvue/urls.py`：`/admin/`、`/api/`(include backend01)、`/IntelligentCabinet/`(include cabinet)，最后 `re_path(r'^.*$', ...index.html)` 兜底给前端 history 路由。
- 子 app 路由：
  - `backend01/urls.py`：`/api/login/`、`/api/register/`、`/api/userinfo/` …，ViewSet 用 `DefaultRouter` 注册。
  - `IntelligentCabinet/urls.py`：`cabinets/`、`cabinets/<int:pk>/`、`grids/<int:pk>/update/`、`grids/<int:pk>/reserve/` 等。
- **URL 末尾统一带斜杠 `/`**（遵循 Django `APPEND_SLASH`）。
- 资源路径用 `<int:pk>` 命名捕获组。

### 4.5 认证与安全

- 双重认证：**JWT (simplejwt)** + **Session**。Access Token 60 分钟，Refresh 7 天。
- 前端请求头：`Authorization: Bearer <access_token>`。
- 非安全方法（POST/PUT/PATCH/DELETE）须携带 **CSRF token**，前端通过 `X-CSRFToken: Cookies.get('csrftoken')` 注入。
- CORS：开发环境 `CORS_ORIGIN_ALLOW_ALL = True`，允许凭证 `CORS_ALLOW_CREDENTIALS = True`。
- Session：`SESSION_SAVE_EVERY_REQUEST=True`，Cookie 12 小时，存储后端 `db`，序列化用 `PickleSerializer`。
- `SECRET_KEY` 等敏感信息当前硬编码在 `settings.py`，**生产环境前必须迁出**（环境变量/外部配置）。

### 4.6 中间件与日志

- 自定义中间件继承 `MiddlewareMixin`，放 `middleware/` 目录（参考 `UserIP.LogMiddle`）。
- 日志统一通过 `logging.getLogger('log')` 或 `logging.getLogger('Django')`，配置见 `settings.LOGGING`，文件按天滚动到 `logs/`（all/error/info），单文件 5MB，备份数 5，编码 utf-8。

### 4.7 迁移

- 改动模型后必须 `python manage.py makemigrations && python manage.py migrate`。
- 自定义用户模型一旦投入生产，**不可**再更换 `AUTH_USER_MODEL`（会导致数据丢失）。

---

## 五、前端开发规则 (Vue 2 + Element UI)

> ⚠️ 本项目为 **Vue 2.5.2 + element-ui 2.15.14 + webpack 3**，**禁止**引入 Vue 3 / Composition API / Element Plus / Vite 等不兼容技术。

### 5.1 组件写法

- 一律使用 **Options API**：`export default { name, data() { return {} }, methods: {}, computed: {}, ... }`。
- 单文件组件 `<template>` / `<script>` / `<style>` 三段式。
- 页面组件放 `src/views/`，布局组件放 `src/layout/`，命名 **PascalCase.vue**（如 `SmartCabinet.vue`、`Login.vue`）。
- UI 组件统一用 element-ui（`el-menu`/`el-submenu`/`el-menu-item`/`el-form`/`el-table`…），已在 `main.js` `Vue.use(ElementUI)` 全量注册。

### 5.2 状态管理 (Vuex 3)

- Store 文件：`src/store/index.js`，按模块拆分放 `src/store/modules/`（如 `cabinet.js`）。
- mutations 命名 **大写下划线**（`SET_TOKEN`、`SET_MENU_TREE`、`TOGGLE_COLLAPSE`、`LOGOUT`）。
- actions 处理异步（`login`、`fetchUserInfo`、`logout`）。
- 需要持久化的状态写入 `localStorage`（如 `token`/`user`/`menuTree`）。

### 5.3 路由 (vue-router 3)

- `mode: 'history'`，`base: process.env.BASE_URL`。
- 静态路由（登录/注册/404 等）放 `router/router.js` 的 `routes` 数组，`hidden: true` 标记不在菜单显示。
- 动态路由通过 `addDynamicRoutes(menuTree)` 在登录后/刷新时根据后端返回的菜单树 `router.addRoute` 注入，叶子组件用 `() => import('@/views/${item.component}.vue')` 懒加载。
- `router.beforeEach` 负责鉴权：无 token / token 过期 → 跳 `/login`；menuTree 为空 → 拉取 `fetchUserInfo` 后动态加路由。
- 路由别名：`@ -> src`（webpack `resolve.alias`）。

### 5.4 请求层 (axios)

- 统一实例：`src/utils/request.js`，`baseURL: 'http://127.0.0.1:8000'`，`withCredentials: true`，`timeout: 5000`。
- 请求拦截器：登录接口外，自动注入 `Authorization: Bearer <token>`。
- 响应拦截器：401 → 清除 `localStorage` 并跳 `/login`；403 → 判断 token 过期并清理重定向。
- 业务请求函数按模块放 `src/api/`（`user.js`、`cabinet.js`），**命名导出**（`export function login(data) {...}`）。
- GET 用 `params`，POST/PUT/PATCH/DELETE 用 `data`；非 GET 方法需带 `X-CSRFToken` 头（`Cookies.get('csrftoken')`）。

### 5.5 代码风格

- 缩进 **2 空格**，行尾 **LF**，编码 **UTF-8**，文件末尾保留空行（见 `.editorconfig`）。
- 注释使用**中文**。
- JS 函数/变量 **camelCase**；Vue 组件/类 **PascalCase**；常量 **UPPER_SNAKE_CASE**。

### 5.6 构建与运行

- 开发：`cd frontend01 && npm run dev`（端口 8080，devServer 代理 `/api` → `http://localhost:8000`，见 `vue.config.js`）。
- 生产打包：`npm run build`，产物在 `frontend01/dist/`；**复制 `dist` 到 `Templates/dist/`**，由 Django `TEMPLATES.DIRS` 托管。
- `node_modules` 应位于 `frontend01/` 下。

---

## 六、API 契约与前后端对接

1. **URL 前缀**：
   - 用户/认证/RBAC：`/api/...`（backend01）
   - 智能柜业务：`/IntelligentCabinet/...`
   - Django admin：`/admin/`
2. **请求/响应格式**：JSON。DRF 默认 JSONRenderer。
3. **认证头**：`Authorization: Bearer <access_token>`（除登录/注册/验证码等公开接口）。
4. **CSRF**：非 GET 方法前端带 `X-CSRFToken`。
5. **字段命名一致性**：后端 Serializer `fields` 必须与前端使用字段**完全一致**（含大小写，如 `CNname`、`Menu_title`、`Photo`、`Tel` 等大写开头的既有字段，不得擅自改名）。
6. **错误处理**：后端查询异常必须 `try/except`，记录日志并返回合适的 HTTP 状态码（401/403/404/400 等）。

---

## 七、开发环境与命令

| 操作 | 命令 |
| --- | --- |
| 后端启动 | `python manage.py runserver 0.0.0.0:8000`（工作目录：项目根 `pyvue/`） |
| 前端开发 | `cd frontend01 && npm run dev`（端口 8080） |
| 前端打包 | `cd frontend01 && npm run build` |
| 数据库迁移 | `python manage.py makemigrations && python manage.py migrate` |
| 创建超级用户 | `python manage.py createsuperuser`（使用 `account` 字段登录） |
| 初始化数据 | `python manage.py initdata`（backend01 自定义命令） |
| 收集静态文件 | `python manage.py collectstatic`（生产） |

> 前端代理：`vue.config.js` 将 `/api` 代理到 `http://localhost:8000`；静态资源 `/static`、`/public` 不代理。

---

## 八、用户偏好与约束（必须遵守）

> 来源：用户记忆与历史约定。

1. **沟通语言**：中文。
2. **样式修改隔离**：所有样式调整**只允许改 `base.html`**，不得影响子页面。如需改动其他文件可能影响页面显示，须**先征得用户确认**。
3. **故障回滚原则**：当新改动导致页面不可用等严重问题时，优先**回滚到上一个可用版本**，而非在错误状态上反复尝试。
4. **最小改动**：只做被要求的改动，不要顺手重构、补文档、加注释、加类型注解到未改动的代码。
5. **禁止修改既有代码字段名**：见第六节第 5 条，避免前后端契约断裂。

---

## 九、禁止事项

- ❌ 不得把前端升级到 Vue 3 / 引入 Composition API / Element Plus / Vite / webpack 5 等不兼容栈。
- ❌ 不得更换 `AUTH_USER_MODEL` 或改用 `auth.User`。
- ❌ 不得在未确认情况下改动 `settings.py` 中的 `SECRET_KEY`、数据库连接、`INSTALLED_APPS`、`MIDDLEWARE` 等关键配置。
- ❌ 不得擅自重命名后端既有字段（含大写开头的 `CNname`/`Tel`/`Photo`/`Menu_title` 等）。
- ❌ 不得在 `package.json` / `requirements` 未声明的情况下引入新依赖；如确需新增，须先给出安装指令并经用户确认。
- ❌ 不得将 `SECRET_KEY`、数据库密码等敏感信息提交到版本库或硬编码到新文件。
