# AI 自主开发系统 + OpenClaw Skill 线上商店 — 总体架构设计

> **面向 Hermes：** 本文档定义两套系统的完整架构，后续按此设计分阶段实现。

**目标：** 构建一套对话驱动的 AI 自主开发流水线，并以 OpenClaw Skill 线上商店为案例验证其能力。

**架构理念：** 分层解耦 — 开发系统是"工厂"，Skill 商店是"产品"。工厂先搭建好，再生产产品。

---

## 一、系统总览

```
┌──────────────────────────────────────────────────────┐
│                   用户（对话交互）                       │
└──────────────────────┬───────────────────────────────┘
                       │ 需求描述
                       ▼
┌──────────────────────────────────────────────────────┐
│            AI 自主开发系统 (AutoDev Pipeline)           │
│                                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐ │
│  │需求分析 │→│方案设计  │→│任务拆分  │→│并行开发 │ │
│  │(理解需求)│ │(技术方案)│ │(bite-size)│ │(子Agent)│ │
│  └─────────┘  └─────────┘  └─────────┘  └────┬───┘ │
│                                              │      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐      │      │
│  │部署上线 │←│集成测试  │←│代码审查  │←─────┘      │
│  │(deploy) │  │(pytest)  │  │(review)  │             │
│  └─────────┘  └─────────┘  └─────────┘             │
│                                                      │
│  核心机制：                                            │
│  - Hermes skills 编排（writing-plans / subagent-      │
│    driven-development / requesting-code-review）      │
│  - delegate_task 子 Agent 并行开发                     │
│  - 用户可在任意阶段介入确认                              │
│  - 全中文文档输出                                      │
└──────────────────────┬───────────────────────────────┘
                       │ 产出
                       ▼
┌──────────────────────────────────────────────────────┐
│            OpenClaw Skill 线上商店 (Web App)            │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐ │
│  │技能浏览   │  │技能搜索   │  │技能详情（安装指南）  │ │
│  │(browse)  │  │(search)  │  │(detail)            │ │
│  └──────────┘  └──────────┘  └────────────────────┘ │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐ │
│  │技能提交   │  │分类筛选   │  │统计面板             │ │
│  │(submit)  │  │(filter)  │  │(stats)             │ │
│  └──────────┘  └──────────┘  └────────────────────┘ │
│                                                      │
│  技术栈：Flask + SQLite + Jinja2 + 原生 CSS            │
└──────────────────────────────────────────────────────┘
```

---

## 二、AI 自主开发系统 — 详细设计

### 2.1 工作流（Pipeline）

```
用户输入需求
    │
    ▼
[阶段1: 需求分析] ─── 与用户对话确认需求理解，生成需求文档
    │
    ▼
[阶段2: 方案设计] ─── 加载 writing-plans，探索技术方案，生成实施计划（中文）
    │                        ↓ 用户确认
    ▼
[阶段3: 任务拆分] ─── 按 TDD 原则拆分为 bite-size tasks（2-5分钟/任务）
    │                        ↓ 保存到 docs/plans/
    ▼
[阶段4: 并行开发] ─── 加载 subagent-driven-development
    │                  ↓ 每个 task → delegate_task 子 Agent
    │                  ↓ 每 task 完成后：spec 审查 → quality 审查
    │                  ↓ 通过后 commit
    ▼
[阶段5: 集成测试] ─── loading requesting-code-review
    │                  ↓ 安全扫描 + 测试回归 + 自动修复
    ▼
[阶段6: 部署上线] ─── 生成部署脚本，运行部署
    │                  ↓ 用户确认部署目标
    ▼
完成交付
```

### 2.2 关键技术实现

| 环节 | Hermes 机制 | 说明 |
|------|-------------|------|
| 需求分析 | clarify + session_search | 多轮对话确认需求，参考历史上下文 |
| 方案设计 | writing-plans skill | 生成完整中文实施计划 |
| 任务拆分 | writing-plans skill | Bite-size tasks（2-5分钟粒度） |
| 并行开发 | delegate_task | 每次最多 3 个子 Agent 并行 |
| 代码审查 | requesting-code-review | 两阶段：spec 合规 + 代码质量 |
| 测试回归 | pytest | PYTHONPATH=src 运行全量测试 |
| 版本管理 | git | 每次 commit 对应一个 task |
| 部署 | terminal(background) | 启动服务，验证健康检查 |

### 2.3 交付物

```
/Users/huymac/projects/ai-autodev-system/
├── docs/
│   ├── plans/                          # 系统自身实施计划
│   │   └── 2026-05-29-autodev-system.md
│   └── architecture.md                 # 本文档
├── skills/
│   └── autodev-pipeline/               # [核心] Hermes Skill：自主开发流水线
│       └── SKILL.md                    # 编排指令（需求→计划→开发→部署）
└── outputs/                            # 由自主开发系统产出的项目目录
    └── openclaw-skill-store/           # Skill 商店 Web 应用
```

### 2.4 人机交互点

每次以下节点暂停，等待用户确认：
1. 需求文档生成后 — "需求理解是否正确？"
2. 实施计划生成后 — "技术方案是否可行？"
3. 部署目标选择 — "部署到哪里？"

---

## 三、OpenClaw Skill 线上商店 — 需求定义

### 3.1 业务场景

OpenClaw 是一个开源个人 AI 助手框架，拥有 150,000+ 用户和 10,000+ Skill 分享。但目前缺乏一个集中的 Skill 商店来浏览、搜索和安装技能。

本商店提供：
- 技能目录浏览（Web 端）
- 关键词搜索
- 分类筛选
- 技能详情页（含安装命令）
- 技能提交入口

### 3.2 功能列表

| 功能 | 优先级 | 说明 |
|------|--------|------|
| 技能列表 | P0 | 首页展示所有 Skill，分页加载 |
| 技能搜索 | P0 | 按名称/描述关键字搜索 |
| 分类筛选 | P1 | 按 category 筛选（开发/效率/娱乐等） |
| 技能详情 | P0 | 显示名称、描述、安装命令、元数据 |
| 技能提交 | P1 | 表单提交新 Skill（名称/描述/安装命令） |
| 统计面板 | P2 | 首页显示 Skill 总数、分类分布 |

### 3.3 技术选型

| 层 | 技术 | 原因 |
|----|------|------|
| 后端 | Python Flask | 轻量、与 Hermes 生态一致 |
| 数据库 | SQLite | 零配置、单文件 |
| 模板 | Jinja2 | Flask 内置 |
| 前端 | 原生 HTML/CSS | 无需构建工具，开箱即用 |
| 测试 | pytest | 与现有技能一致 |

### 3.4 数据模型

```
Skill:
  id          INTEGER PRIMARY KEY
  name        TEXT NOT NULL        # 技能名称（如 "blogwatcher"）
  description TEXT NOT NULL        # 技能描述
  category    TEXT                 # 分类（dev/productivity/entertainment...）
  author      TEXT                 # 作者
  install_cmd TEXT                 # 安装命令
  homepage    TEXT                 # 项目主页
  emoji       TEXT                 # 图标 emoji
  downloads   INTEGER DEFAULT 0    # 下载量
  created_at  TIMESTAMP
```

### 3.5 路由设计

```
GET  /                    首页（技能列表 + 统计）
GET  /skills              技能列表（含搜索/筛选）
GET  /skills/<id>         技能详情
GET  /skills/submit       提交新技能（表单）
POST /skills/submit       提交新技能（处理）
GET  /api/skills          技能列表 API（JSON，供前端搜索）
```

---

## 四、实施路径

### Phase 1: 搭建 AI 自主开发系统
- 创建 `autodev-pipeline` Hermes Skill
- 验证流水线各环节

### Phase 2: 用自主开发系统构建 Skill 商店
- 对话驱动：
  > "在 outputs/openclaw-skill-store/ 下开发一个 Flask Web 应用..."
- 自主完成：计划 → 开发 → 测试 → 部署

### Phase 3: 部署上线
- 本地运行 Flask
- 可选：ngrok 公网暴露

---

## 五、验收标准

- [ ] 用户可通过对话触发完整开发流水线
- [ ] 流水线自动生成中文需求文档和实施计划
- [ ] 子 Agent 并行开发，每个 task 通过双审
- [ ] Skill 商店可运行：浏览、搜索、详情、提交
- [ ] 全部测试通过
- [ ] Git 提交记录完整
