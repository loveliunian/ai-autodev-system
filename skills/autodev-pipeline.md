---
name: autodev-pipeline
description: "AI 自主开发流水线：需求→计划→并行开发→审查→部署，全程对话驱动"
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [autonomous-dev, pipeline, orchestration, multi-agent, deployment]
    related_skills:
      - writing-plans
      - subagent-driven-development
      - test-driven-development
      - requesting-code-review
      - systematic-debugging
---

# AI 自主开发流水线（AutoDev Pipeline）

## 概述

对话驱动的端到端开发流水线。用户描述需求，系统自动完成：需求分析 → 方案设计 → 任务拆分 → 并行开发（子 Agent）→ 代码审查 → 测试 → 部署。

**核心原则：** 全程自动化，但保留 3 个人机确认节点。所有文档和注释使用中文。

## 触发条件

用户说类似以下内容时加载此技能：
- "用自主开发系统开发 XXX"
- "自动开发一个 XXX"
- "搭建 XXX 项目"
- "用 AI 开发流水线实现 XXX"

## 工作流

### 阶段 1：需求分析与方案设计

#### 1.1 需求澄清
与用户对话确认需求理解。使用 `clarify` 工具解决模糊点。

#### 1.2 生成实施计划
加载 `writing-plans` 技能，按以下步骤操作：

1. 探索目标代码库（如有）— `search_files` / `read_file`
2. 设计技术方案（架构、技术栈、文件组织）
3. 生成中文实施计划
4. 保存到目标项目的 `docs/plans/YYYY-MM-DD-feature-name.md`

计划文档 MUST 包含以下结构：
```markdown
# [特性名称] 实施计划

> **面向 Hermes：** 使用 autodev-pipeline 技能按任务逐项实施。

**目标：** [一句话描述]

**架构：** [2-3 句技术方案]

**技术栈：** [关键库/框架]

---

### Task 1: [任务名]
**目标：** ...
**文件：** ...
**步骤：** ...
```

#### 1.3 用户确认节点 #1
展示计划摘要，使用 `clarify` 询问："方案是否可行？"

---

### 阶段 2：并行开发（核心）

加载 `subagent-driven-development` 技能，按计划逐任务执行。

#### 对每个 Task：

**Step 1：派发实现子 Agent**
```
delegate_task(
    goal="实现 Task N: [任务名称]",
    context="""
    [完整的 Task 描述、文件路径、目标代码]

    遵循 TDD：
    1. 先写失败测试
    2. 运行测试确认失败
    3. 写最小实现
    4. 运行测试确认通过
    5. 运行全量测试确认无回归
    6. 提交：git add ... && git commit -m "feat: ..."

    项目上下文：
    - 工作目录：[绝对路径]
    - 测试命令：[pytest 命令]
    - 提交规范：[commit message 格式]
    """,
    toolsets=['terminal', 'file']
)
```

**Step 2：Spec 合规审查**
```
delegate_task(
    goal="审查 Task N 实现是否符合计划规格",
    context="""
    原始规格：
    [Task 原文]

    检查：
    - [ ] 所有规格要求都已实现？
    - [ ] 文件路径符合规格？
    - [ ] 没有超出范围的内容？

    输出：PASS 或 FAIL + 具体差距列表
    """,
    toolsets=['file']
)
```

**Step 3：代码质量审查**
```
delegate_task(
    goal="审查 Task N 代码质量",
    context="""
    审查文件：
    [文件列表]

    检查：
    - [ ] 代码规范
    - [ ] 错误处理
    - [ ] 测试覆盖
    - [ ] 无明显 bug

    输出：APPROVED 或 REQUEST_CHANGES + 具体问题
    """,
    toolsets=['file']
)
```

**Step 4：主 Agent 验证（关键！）**
子 Agent 的自我报告不可靠 — 声称已完成的操作（git commit、数据库写入、文件创建）可能未实际执行。审查通过后，主 Agent 必须亲自验证：

```bash
# 检查文件是否真实存在
ls -la [关键文件路径]

# 检查 git 提交是否真实存在（不仅仅是子 Agent 声称）
cd <项目目录> && git log --oneline -3

# 重新运行测试确认通过
cd <项目目录> && <pytest命令>
```

验证通过后才标记 task 完成。如果发现子 Agent 声称但未执行的操作（如 git commit 缺失），主 Agent 直接补上。

> 📖 详见 `references/subagent-verification-pattern.md`

---

### 阶段 3：集成测试与审查

所有任务完成后，加载 `requesting-code-review` 技能：

1. 运行全量测试：`pytest tests/ -v`
2. 安全扫描（检查 git diff）
3. 最终审查子 Agent

---

### 阶段 4：Docker 化

所有项目在部署前必须 Docker 化，生成以下文件：

#### 4.1 生成 Docker 文件

```dockerfile
# Dockerfile — 多阶段可选，Python 3.11-slim 基础镜像
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python seed_data.py  # 如有种子数据
EXPOSE <端口>
CMD ["python", "app.py"]
```

```yaml
# docker-compose.yml
services:
  app:
    build: .
    container_name: <项目名>
    restart: always
    ports:
      - "<端口>:<端口>"
    environment:
      - FLASK_ENV=production
      - DATABASE=/app/data/skills.db
    volumes:
      - app-data:/app/data

volumes:
  app-data:
```

```ignore
# .dockerignore
__pycache__/
.pytest_cache/
*.pyc
*.db
.git/
```

#### 4.2 提交 Docker 文件
```bash
git add Dockerfile docker-compose.yml .dockerignore
git commit -m "feat: 添加 Docker 部署配置"
```

---

### 阶段 5：云服务器部署

#### 5.1 用户确认节点 #3
使用 `clarify` 收集部署信息：

```
部署目标：
- 云平台：阿里云 / 腾讯云 / AWS / 其他
- ECS IP：[公网 IP]
- SSH 用户：[root / ubuntu]
- SSH 认证：[密码 / 密钥路径]
- 端口：[应用端口]
```

#### 5.2 检查服务器环境
```bash
sshpass -p '<密码>' ssh -o StrictHostKeyChecking=no <用户>@<IP> \
  "cat /etc/os-release | head -3 && docker --version && docker compose version"
```

如果缺少 Docker：
```bash
curl -fsSL https://get.docker.com | sh
```

#### 5.3 上传项目文件
```bash
sshpass -p '<密码>' ssh -o StrictHostKeyChecking=no <用户>@<IP> \
  "mkdir -p /opt/<项目名>"
sshpass -p '<密码>' scp -o StrictHostKeyChecking=no -r \
  {Dockerfile,docker-compose.yml,.dockerignore,requirements.txt,*.py,static,templates} \
  <用户>@<IP>:/opt/<项目名>/
```

#### 5.4 构建并启动
```bash
sshpass -p '<密码>' ssh -o StrictHostKeyChecking=no <用户>@<IP> \
  "cd /opt/<项目名> && docker compose up -d --build"
```

> 📖 部署常见问题见 `references/cloud-deployment-pitfalls.md`（超时、镜像加速、安全组等）

#### 5.5 配置防火墙
```bash
# 检查阿里云安全组是否开放端口（需在阿里云控制台操作）
# ECS 本地防火墙（如有 ufw）：
sshpass -p '<密码>' ssh <用户>@<IP> \
  "ufw allow <端口>/tcp 2>/dev/null; ufw reload 2>/dev/null || true"
```

#### 5.6 验证部署
```bash
curl -s -o /dev/null -w "%{http_code}" http://<IP>:<端口>/
# 预期: 200
```

---

### 阶段 6：最终交付

#### 6.1 推送 GitHub
```bash
cd <项目目录>
gh repo create <项目名> --source . --public --push
```

#### 6.2 输出部署摘要
```
部署完成:
  项目地址: http://<IP>:<端口>
  GitHub:   https://github.com/<用户>/<项目名>
  技术栈:   [技术栈]
  测试:     N/N 通过
```

---

## 人机交互节点（仅 3 处）

| 节点 | 时机 | 说明 |
|------|------|------|
| 确认 #1 | 方案设计完成后 | 技术方案是否可行？ |
| 确认 #2 | 开发完成后 | 功能是否满足需求？ |
| 确认 #3 | 部署前 | 收集云服务器连接信息（IP/用户/密码） |

## 流水线全貌（6 阶段）

```
阶段 1: 需求分析 → 方案设计     ✅ 确认 #1
阶段 2: 并行开发（子Agent+TDD）  🤖 全自动
阶段 3: 集成测试与审查           🤖 全自动
阶段 4: Docker 化               🤖 全自动
阶段 5: 云服务器部署             ✅ 确认 #3（收集 SSH 信息）
阶段 6: 最终交付（GitHub + 摘要） 🤖 全自动
```

其他所有环节全自动执行。

---

## 注意事项

- **子 Agent 报告不可靠：** 子 Agent 声称完成的操作（git commit、文件写入、数据库操作）可能未实际执行。每 task 完成后必须由主 Agent 亲自验证 `git log`、文件存在性和测试结果。发现偏差立即补上，不要依赖子 Agent 的自述。
- 子 Agent 没有上下文记忆，必须提供完整的 task 描述和项目背景
- 同一时刻修改同一文件的 task 不能并行（避免冲突）
- 无冲突的 task 可以并行派发（如 Task A 写模板、Task B 写模型）以加速
- 审查失败时修复后必须重新审查
- 所有文档和注释用中文
- 每次 commit 对应一个 task
- 最终交付物包括源码 + 测试 + 部署脚本 + 文档

---

## 示例对话

```
用户："在 /Users/huymac/projects/hello-api/ 开发一个返回 Hello World 的 Flask API"

→ [阶段 1] 需求分析，生成计划
→ [确认 #1] "方案：Flask + JSON 响应，路由 /api/hello，是否可行？"
→ [阶段 2] 派发子 Agent 开发 → Spec 审查 → Quality 审查 → 主 Agent 验证
→ [阶段 3] 集成测试：pytest 全量通过
→ [确认 #2] "功能验收完成。需要部署吗？"
→ [阶段 4] 生成 Dockerfile + docker-compose.yml + .dockerignore
→ [确认 #3] "请提供云服务器 SSH 信息：IP / 用户 / 密码"
→ [阶段 5] sshpass 上传 → docker compose up -d --build → 防火墙配置
→ [阶段 6] 推送到 GitHub → 输出部署摘要
→ "完成！hello-api 运行在 http://47.95.208.205:5050"
```
