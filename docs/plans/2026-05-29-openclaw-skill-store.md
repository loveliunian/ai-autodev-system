# OpenClaw Skill 线上商店 — 实施计划

> **面向 Hermes：** 使用 autodev-pipeline 技能按任务逐项实施。

**目标：** 构建一个 Flask Web 应用，提供 OpenClaw Skill 的浏览、搜索、详情查看和提交功能。

**架构：** Flask + SQLite + Jinja2 模板，原生 CSS 无前端构建。遵循 MVC 模式：模型层（models.py）、视图层（templates/）、控制器层（app.py 路由）。

**技术栈：**
- Python 3.11 + Flask 3.x
- SQLite 数据库（单文件，零配置）
- Jinja2 模板引擎（Flask 内置）
- 原生 HTML/CSS（暗色主题，参考现代设计）
- pytest 测试框架

**目标目录：** `/Users/huymac/projects/ai-autodev-system/outputs/openclaw-skill-store/`

---

## 项目结构

```
openclaw-skill-store/
├── app.py                  # Flask 应用入口 + 路由
├── models.py               # SQLite 数据模型 + 初始化
├── seed_data.py            # 种子数据脚本（预置 Skill）
├── templates/
│   ├── base.html           # 基础布局（导航栏、页脚）
│   ├── index.html          # 首页（技能列表 + 统计）
│   ├── skill_detail.html   # 技能详情页
│   └── submit.html         # 提交表单
├── static/
│   └── style.css           # 暗色主题样式
├── tests/
│   ├── test_app.py         # 路由测试
│   └── test_models.py      # 模型测试
├── requirements.txt        # 依赖
└── README.md               # 使用说明
```

---

### Task 1: 创建项目骨架

**目标：** 创建项目目录结构和最小 Flask 应用

**文件：**
- 创建：`app.py`（最小 Flask 应用）
- 创建：`requirements.txt`
- 创建：`tests/test_app.py`（第一个测试）

**步骤：**

**Step 1: 写失败测试**

```python
# tests/test_app.py
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_page_returns_200(client):
    """首页应返回 200"""
    response = client.get('/')
    assert response.status_code == 200


def test_home_page_contains_title(client):
    """首页应包含 OpenClaw 标题"""
    response = client.get('/')
    assert 'OpenClaw' in response.data.decode('utf-8')
```

**Step 2: 确认测试失败**

```bash
cd outputs/openclaw-skill-store
python -m pytest tests/test_app.py -v
# 预期：FAIL — ModuleNotFoundError: No module named 'app'
```

**Step 3: 写最小实现**

```python
# app.py
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
```

**Step 4: 确认测试通过**

```bash
python -m pytest tests/test_app.py -v
# 预期：PASS（需要先创建模板文件）
```

**Step 5: 提交**

```bash
git add -A && git commit -m "feat: 创建项目骨架和最小 Flask 应用"
```

---

### Task 2: 创建基础 HTML 模板

**目标：** 创建 base.html 布局和 index.html 首页

**文件：**
- 创建：`templates/base.html`
- 创建：`templates/index.html`
- 创建：`static/style.css`

**步骤：**

**Step 1: 写失败测试**

```python
# 追加到 tests/test_app.py
def test_home_page_has_navigation(client):
    """首页应包含导航栏"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    assert 'nav' in html.lower() or 'header' in html.lower()


def test_home_page_has_search(client):
    """首页应包含搜索框"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    assert 'search' in html.lower() or '搜索' in html
```

**Step 2: 确认测试失败**

**Step 3: 实现模板**

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}OpenClaw Skill 商店{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <header>
        <nav>
            <a href="/" class="logo">🦞 OpenClaw Skill 商店</a>
            <a href="/skills/submit">提交 Skill</a>
        </nav>
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
    <footer>
        <p>OpenClaw Skill 商店 — 社区驱动的技能市场</p>
    </footer>
</body>
</html>
```

```html
<!-- templates/index.html -->
{% extends "base.html" %}
{% block title %}OpenClaw Skill 商店{% endblock %}
{% block content %}
<section class="hero">
    <h1>探索 OpenClaw Skills</h1>
    <form action="/skills" method="get" class="search-bar">
        <input type="text" name="q" placeholder="搜索 Skill..." value="{{ query or '' }}">
        <button type="submit">搜索</button>
    </form>
</section>
<section class="skill-list">
    <h2>全部 Skills</h2>
    {% if skills %}
        <div class="skills-grid">
            {% for skill in skills %}
            <a href="/skills/{{ skill.id }}" class="skill-card">
                <span class="emoji">{{ skill.emoji or '🔧' }}</span>
                <h3>{{ skill.name }}</h3>
                <p>{{ skill.description[:80] }}{% if skill.description|length > 80 %}...{% endif %}</p>
                <span class="category">{{ skill.category }}</span>
            </a>
            {% endfor %}
        </div>
    {% else %}
        <p>暂无 Skill，<a href="/skills/submit">提交第一个</a>。</p>
    {% endif %}
</section>
{% endblock %}
```

```css
/* static/style.css */
:root {
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --text-muted: #8b949e;
    --accent: #58a6ff;
    --accent-hover: #79c0ff;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; display: flex; flex-direction: column; }
header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 1rem 2rem; }
nav { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
.logo { color: var(--text); text-decoration: none; font-weight: 700; font-size: 1.25rem; }
nav a { color: var(--accent); text-decoration: none; }
main { flex: 1; max-width: 1200px; margin: 2rem auto; padding: 0 2rem; width: 100%; }
footer { background: var(--surface); border-top: 1px solid var(--border); padding: 1rem 2rem; text-align: center; color: var(--text-muted); font-size: 0.875rem; }
.hero { text-align: center; padding: 3rem 0; }
.hero h1 { font-size: 2.5rem; margin-bottom: 1.5rem; }
.search-bar { display: flex; gap: 0.5rem; max-width: 500px; margin: 0 auto; }
.search-bar input { flex: 1; padding: 0.75rem 1rem; background: var(--surface); border: 1px solid var(--border); border-radius: 6px; color: var(--text); font-size: 1rem; }
.search-bar button { padding: 0.75rem 1.5rem; background: var(--accent); border: none; border-radius: 6px; color: white; cursor: pointer; font-size: 1rem; }
.search-bar button:hover { background: var(--accent-hover); }
.skills-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; margin-top: 1.5rem; }
.skill-card { display: block; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; text-decoration: none; color: var(--text); transition: border-color 0.2s; }
.skill-card:hover { border-color: var(--accent); }
.emoji { font-size: 2rem; display: block; margin-bottom: 0.75rem; }
.skill-card h3 { margin-bottom: 0.5rem; font-size: 1.1rem; }
.skill-card p { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.75rem; }
.category { display: inline-block; background: var(--bg); padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; color: var(--text-muted); }
```

**Step 4: 确认测试通过**

**Step 5: 提交**

---

### Task 3: 创建数据模型和种子数据

**目标：** 创建 SQLite 数据模型，预置 8 个 Skill 种子数据

**文件：**
- 创建：`models.py`
- 创建：`seed_data.py`

**步骤：**

**Step 1: 写失败测试**

```python
# tests/test_models.py
import pytest
import sqlite3
from models import get_db, init_db, Skill


@pytest.fixture
def db():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    init_db(conn)
    yield conn
    conn.close()


def test_init_db_creates_skills_table(db):
    """init_db 应创建 skills 表"""
    cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='skills'")
    assert cursor.fetchone() is not None


def test_skills_table_has_correct_columns(db):
    """skills 表应有正确的列"""
    cursor = db.execute("PRAGMA table_info(skills)")
    columns = {row['name'] for row in cursor.fetchall()}
    expected = {'id', 'name', 'description', 'category', 'author',
                'install_cmd', 'homepage', 'emoji', 'downloads', 'created_at'}
    assert expected.issubset(columns)


def test_add_and_get_skill(db):
    """应能添加和获取 Skill"""
    db.execute("""
        INSERT INTO skills (name, description, category, author, install_cmd, emoji)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('test-skill', 'A test skill', 'dev', 'tester', 'pip install test-skill', '🧪'))
    db.commit()

    row = db.execute("SELECT * FROM skills WHERE name = ?", ('test-skill',)).fetchone()
    assert row['name'] == 'test-skill'
    assert row['category'] == 'dev'
```

**Step 2: 确认测试失败**

**Step 3: 实现 models.py**

```python
# models.py
import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), 'skills.db')


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn=None):
    if conn is None:
        conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT DEFAULT 'other',
            author TEXT DEFAULT '',
            install_cmd TEXT DEFAULT '',
            homepage TEXT DEFAULT '',
            emoji TEXT DEFAULT '🔧',
            downloads INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
```

**Step 4: 实现 seed_data.py**

```python
# seed_data.py
from models import get_db, init_db

SEED_SKILLS = [
    {'name': 'blogwatcher', 'description': '通过 CLI 监控博客和 RSS/Atom 订阅源更新', 'category': '效率', 'author': 'Hyaxia', 'install_cmd': 'go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest', 'homepage': 'https://github.com/Hyaxia/blogwatcher', 'emoji': '📰'},
    {'name': '1password', 'description': '在 OpenClaw 中安全访问和管理 1Password 凭据', 'category': '安全', 'author': '1Password', 'install_cmd': 'op plugin add openclaw', 'homepage': 'https://1password.com', 'emoji': '🔐'},
    {'name': 'discord', 'description': '通过 OpenClaw 发送和管理 Discord 消息', 'category': '社交', 'author': 'OpenClaw Community', 'install_cmd': 'pip install discord.py', 'homepage': 'https://discord.com', 'emoji': '💬'},
    {'name': 'canvas', 'description': '在 OpenClaw 中生成和编辑 Canvas 图形', 'category': '创作', 'author': 'OpenClaw', 'install_cmd': 'npm install @openclaw/canvas', 'homepage': 'https://openclaw.ai', 'emoji': '🎨'},
    {'name': 'coding-agent', 'description': 'AI 编程助手，支持代码生成、审查和重构', 'category': '开发', 'author': 'OpenClaw', 'install_cmd': 'npm install @openclaw/coding-agent', 'homepage': 'https://openclaw.ai', 'emoji': '💻'},
    {'name': 'diagram-maker', 'description': '根据自然语言描述生成架构图和流程图', 'category': '开发', 'author': 'OpenClaw', 'install_cmd': 'npm install @openclaw/diagram-maker', 'homepage': 'https://openclaw.ai', 'emoji': '📊'},
    {'name': 'apple-notes', 'description': '读取、创建和管理 Apple Notes 笔记', 'category': '效率', 'author': 'macOS User', 'install_cmd': 'brew install apple-notes-cli', 'homepage': 'https://github.com/apple-notes-cli', 'emoji': '📝'},
    {'name': 'gemini', 'description': '接入 Google Gemini 模型进行对话和推理', 'category': 'AI', 'author': 'Google', 'install_cmd': 'pip install google-generativeai', 'homepage': 'https://ai.google.dev', 'emoji': '🤖'},
]


def seed():
    conn = get_db()
    init_db(conn)
    for skill in SEED_SKILLS:
        conn.execute("""
            INSERT OR IGNORE INTO skills (name, description, category, author, install_cmd, homepage, emoji)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (skill['name'], skill['description'], skill['category'],
              skill['author'], skill['install_cmd'], skill['homepage'], skill['emoji']))
    conn.commit()
    print(f"已插入 {len(SEED_SKILLS)} 个 Skill")
    conn.close()


if __name__ == '__main__':
    seed()
```

**Step 5: 提交**

---

### Task 4: 实现首页路由（列表 + 搜索 + 统计）

**目标：** 实现 Flask 路由：首页展示 Skill 列表、搜索功能、统计信息

**文件：**
- 修改：`app.py`

**步骤：**

**Step 1: 写失败测试**

```python
# 追加到 tests/test_app.py
def test_index_shows_skills(client):
    """首页应显示 Skill 卡片"""
    from models import get_db, init_db
    db = get_db()
    init_db(db)
    db.execute("INSERT INTO skills (name, description, category, emoji) VALUES (?, ?, ?, ?)",
               ('test-skill', 'A test', 'dev', '🧪'))
    db.commit()

    response = client.get('/')
    html = response.data.decode('utf-8')
    assert 'test-skill' in html


def test_search_skills(client):
    """搜索应过滤 Skill"""
    from models import get_db, init_db
    db = get_db()
    init_db(db)
    db.execute("INSERT INTO skills (name, description, category, emoji) VALUES (?, ?, ?, ?)",
               ('unique-skill', 'very unique', 'dev', '🔍'))
    db.commit()

    response = client.get('/skills?q=unique')
    html = response.data.decode('utf-8')
    assert 'unique-skill' in html
```

**Step 2: 实现路由**

```python
# app.py 完整版
from flask import Flask, render_template, request
from models import get_db, init_db

app = Flask(__name__)


@app.route('/')
def index():
    db = get_db()
    init_db(db)
    skills = db.execute(
        "SELECT * FROM skills ORDER BY downloads DESC, created_at DESC LIMIT 20"
    ).fetchall()
    stats = {
        'total': db.execute("SELECT COUNT(*) FROM skills").fetchone()[0],
        'categories': db.execute(
            "SELECT COUNT(DISTINCT category) FROM skills"
        ).fetchone()[0],
    }
    return render_template('index.html', skills=skills, stats=stats, query='')


@app.route('/skills')
def skill_list():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    db = get_db()
    init_db(db)

    sql = "SELECT * FROM skills WHERE 1=1"
    params = []
    if query:
        sql += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f'%{query}%', f'%{query}%'])
    if category:
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY downloads DESC, created_at DESC"

    skills = db.execute(sql, params).fetchall()
    return render_template('index.html', skills=skills, query=query, stats=None)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5050)
```

**Step 3: 确认测试通过**

**Step 4: 提交**

---

### Task 5: 实现技能详情页

**目标：** 创建 `/skills/<id>` 路由和详情模板

**文件：**
- 修改：`app.py`
- 创建：`templates/skill_detail.html`

**Step 1: 写失败测试**

```python
def test_skill_detail_page(client):
    """技能详情页应显示技能信息"""
    from models import get_db, init_db
    db = get_db()
    init_db(db)
    cursor = db.execute(
        "INSERT INTO skills (name, description, category, install_cmd, emoji) VALUES (?, ?, ?, ?, ?)",
        ('detail-skill', 'A skill for detail view', 'dev', 'pip install detail-skill', '🔬'))
    db.commit()
    skill_id = cursor.lastrowid

    response = client.get(f'/skills/{skill_id}')
    html = response.data.decode('utf-8')
    assert response.status_code == 200
    assert 'detail-skill' in html
    assert 'pip install detail-skill' in html


def test_skill_not_found_returns_404(client):
    """不存在的技能应返回 404"""
    response = client.get('/skills/99999')
    assert response.status_code == 404
```

**Step 2: 实现**

```python
# 追加到 app.py
@app.route('/skills/<int:skill_id>')
def skill_detail(skill_id):
    db = get_db()
    init_db(db)
    skill = db.execute("SELECT * FROM skills WHERE id = ?", (skill_id,)).fetchone()
    if skill is None:
        return "Skill not found", 404
    return render_template('skill_detail.html', skill=skill)
```

```html
<!-- templates/skill_detail.html -->
{% extends "base.html" %}
{% block title %}{{ skill.name }} - OpenClaw Skill 商店{% endblock %}
{% block content %}
<article class="skill-detail">
    <a href="/" class="back-link">← 返回列表</a>
    <div class="detail-header">
        <span class="emoji-large">{{ skill.emoji or '🔧' }}</span>
        <div>
            <h1>{{ skill.name }}</h1>
            <p class="author">作者：{{ skill.author or '未知' }}</p>
        </div>
    </div>
    <p class="description">{{ skill.description }}</p>
    <div class="meta">
        <span>分类：{{ skill.category or '未分类' }}</span>
        <span>下载量：{{ skill.downloads }}</span>
    </div>
    {% if skill.install_cmd %}
    <div class="install-section">
        <h2>安装</h2>
        <pre><code>{{ skill.install_cmd }}</code></pre>
    </div>
    {% endif %}
    {% if skill.homepage %}
    <p><a href="{{ skill.homepage }}" target="_blank">访问项目主页 →</a></p>
    {% endif %}
</article>
{% endblock %}
```

**Step 3-5: 测试 + 提交**

---

### Task 6: 实现技能提交功能

**目标：** 创建 `/skills/submit` 表单和处理路由

**文件：**
- 修改：`app.py`
- 创建：`templates/submit.html`

**Step 1: 写失败测试**

**Step 2-5: 实现 + 测试 + 提交**

---

### Task 7: 集成验证和 README

**目标：** 运行全量测试、撰写 README、最终审查

**文件：**
- 修改：`README.md`
- 运行：`python seed_data.py`

---

### Task 8: 部署配置

**目标：** 创建生产部署脚本

**文件：**
- 创建：`run.sh`
- 修改：`requirements.txt`
