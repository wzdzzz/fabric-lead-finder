# 管理后台设计文档

## 概述

为 fabric-lead-finder 项目添加 Web 管理后台，便于随时爬取不同地区的服装厂商数据，并将数据持久化到数据库中，支持数据标记和修改。

## 技术栈

- **后端**: FastAPI + SQLAlchemy + SQLite + JWT
- **前端**: React + TypeScript + Ant Design + Vite
- **数据库**: SQLite（存放在 `data/leads.db`）

## 项目结构

```
fabric-lead-finder/
├── config.py                # 现有配置（保留）
├── scraper_map.py           # 现有爬虫（保留）
├── exporter.py              # 现有导出（保留）
├── main.py                  # 现有 CLI 入口（保留）
├── server/                  # 后端
│   ├── app.py               # FastAPI 应用入口
│   ├── auth.py              # JWT 登录认证
│   ├── database.py          # SQLAlchemy + SQLite 配置
│   ├── models.py            # 数据库模型
│   ├── schemas.py           # Pydantic 请求/响应模型
│   ├── routers/
│   │   ├── auth.py          # 登录接口
│   │   ├── tasks.py         # 爬取任务接口
│   │   ├── leads.py         # 客户数据 CRUD 接口
│   │   └── export.py        # 导出接口
│   └── services/
│       ├── scraper.py       # 封装现有爬虫为后台任务
│       └── export.py        # 封装现有导出逻辑
├── web/                     # 前端
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx
│       ├── api/             # API 请求封装
│       ├── pages/
│       │   ├── Login.tsx
│       │   ├── Dashboard.tsx
│       │   ├── Leads.tsx
│       │   └── History.tsx
│       └── components/
├── data/
│   └── leads.db             # SQLite 数据库文件
└── output/                  # 现有导出目录（保留）
```

## 数据库模型

### leads 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| name | TEXT UNIQUE | 公司名称（去重键） |
| phone | TEXT | 联系电话 |
| city | TEXT | 所在城市 |
| district | TEXT | 区县 |
| address | TEXT | 详细地址 |
| region | TEXT | 省市区组合 |
| industry | TEXT | 行业分类 |
| location | TEXT | 经纬度 |
| source | TEXT | 数据来源 |
| search_keyword | TEXT | 搜索关键词 |
| search_region | TEXT | 搜索地区 |
| status | TEXT | 跟进状态：未联系/已联系/有意向/无意向/已成交/无效 |
| tags | TEXT | 标签，JSON 数组存储 |
| notes | TEXT | 备注 |
| created_at | DATETIME | 入库时间 |
| updated_at | DATETIME | 最后更新时间 |

### scrape_tasks 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| keywords | TEXT | JSON 数组 |
| regions | TEXT | JSON 数组 |
| status | TEXT | pending/running/completed/failed |
| total_found | INTEGER | 找到总数 |
| new_added | INTEGER | 新增数 |
| started_at | DATETIME | 开始时间 |
| finished_at | DATETIME | 结束时间 |
| error_msg | TEXT | 错误信息 |

## API 接口

### 认证
- POST `/api/auth/login` — 登录，返回 JWT token

### 爬取任务
- POST `/api/tasks` — 创建爬取任务
- GET `/api/tasks` — 任务列表
- GET `/api/tasks/{id}` — 任务详情 + 进度

### 客户数据
- GET `/api/leads` — 客户列表（分页、搜索、筛选）
- PUT `/api/leads/{id}` — 修改客户信息
- PUT `/api/leads/batch` — 批量修改
- GET `/api/leads/tags` — 获取所有标签
- GET `/api/leads/stats` — 统计概览

### 导出
- POST `/api/export` — 导出 Excel

### 配置
- GET `/api/config/keywords` — 可用关键词
- GET `/api/config/regions` — 可用地区

## 前端页面

1. **登录页** — 账号密码表单，token 存 localStorage
2. **Dashboard** — 统计卡片 + 发起爬取 + 任务进度
3. **Leads 列表** — 数据表格，支持搜索/筛选/编辑状态/打标签/批量操作/导出
4. **History** — 爬取任务历史

## 认证方案

单用户固定账号，配置文件中设置用户名密码，JWT token 认证，所有 API（除 login）需要 token。

## 部署方式

单机部署：
- 后端：`uvicorn server.app:app`
- 前端：`vite build` 生成静态文件，由 FastAPI 托管
- 生产模式下前后端合并为一个服务
