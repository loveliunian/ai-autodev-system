# tests/test_app.py — Flask 应用测试
import pytest
import tempfile
import os


@pytest.fixture
def client(monkeypatch):
    """创建测试客户端，使用临时数据库并预置测试数据"""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    import models
    monkeypatch.setattr(models, 'DATABASE', db_path)
    models.init_db()

    # 预置测试数据
    conn = models.get_db()
    conn.executemany(
        "INSERT INTO skills (name, description, category, author, install_cmd, homepage, emoji) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            ("test-skill", "A test skill for testing", "测试", "Tester", "pip install test", "https://example.com/test", "🧪"),
            ("another-skill", "Another skill description", "开发", "Dev", "pip install another", "https://example.com/another", "💻"),
            ("blog-watcher", "Monitor RSS feeds and blogs", "效率", "OpenClaw", "openclaw install blogwatcher", "https://openclaw.ai/skills/blogwatcher", "📰"),
        ]
    )
    conn.commit()
    conn.close()

    from app import app as flask_app
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

    os.unlink(db_path)


def test_home_page_returns_200(client):
    """首页应返回 200 状态码"""
    response = client.get('/')
    assert response.status_code == 200


def test_home_page_contains_title(client):
    """首页应包含 OpenClaw 品牌名"""
    response = client.get('/')
    assert 'OpenClaw' in response.data.decode('utf-8')


def test_home_page_has_navigation(client):
    """首页应包含导航栏"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    assert ('nav' in html) or ('header' in html) or ('导航' in html)


def test_home_page_has_search(client):
    """首页应包含搜索框"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    assert ('search' in html) or ('搜索' in html)


def test_index_shows_skills(client):
    """首页应展示数据库中的 Skill"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    assert 'test-skill' in html
    assert 'another-skill' in html
    assert 'blog-watcher' in html


def test_search_skills(client):
    """搜索应过滤结果"""
    response = client.get('/?q=test')
    html = response.data.decode('utf-8')
    assert 'test-skill' in html
    assert 'another-skill' not in html
    assert 'blog-watcher' not in html


def test_search_skills_no_results(client):
    """搜索无结果时应显示空状态"""
    response = client.get('/?q=nonexistent')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert '没有找到' in html or '无结果' in html or 'empty' in html.lower()


def test_category_filter(client):
    """分类过滤应只显示对应分类的技能"""
    response = client.get('/?category=开发')
    html = response.data.decode('utf-8')
    assert 'another-skill' in html
    assert 'test-skill' not in html


def test_skill_detail_page(client):
    """详情页返回 200 + 显示技能信息"""
    response = client.get('/skills/1')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'test-skill' in html
    assert 'A test skill for testing' in html
    assert 'Tester' in html


def test_skill_not_found_returns_404(client):
    """不存在的 ID 返回 404"""
    response = client.get('/skills/999')
    assert response.status_code == 404


def test_skills_redirect(client):
    """/skills 应重定向到首页"""
    response = client.get('/skills')
    assert response.status_code in (301, 302)


def test_index_shows_stats(client):
    """首页应显示统计信息"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    # 应有 3 个技能
    assert '3' in html


# ============================================================
# 技能提交功能测试 (Task 6)
# ============================================================

def test_submit_page_returns_200(client):
    """GET /skills/submit 应返回 200"""
    response = client.get('/skills/submit')
    assert response.status_code == 200


def test_submit_page_has_form(client):
    """提交页面应包含表单"""
    response = client.get('/skills/submit')
    html = response.data.decode('utf-8')
    assert '<form' in html
    assert 'name="name"' in html
    assert 'name="description"' in html


def test_submit_creates_skill(client):
    """POST 提交创建 Skill 并重定向到详情页"""
    response = client.post('/skills/submit', data={
        'name': 'new-skill',
        'description': 'A brand new skill',
        'category': '开发',
        'author': 'NewAuthor',
        'install_cmd': 'pip install new',
        'homepage': 'https://example.com/new',
        'emoji': '🆕',
    }, follow_redirects=True)
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'new-skill' in html
    assert 'A brand new skill' in html
    assert 'NewAuthor' in html


def test_submit_empty_name_shows_error(client):
    """空名称提交应返回错误提示"""
    response = client.post('/skills/submit', data={
        'name': '',
        'description': 'Some description',
    })
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert '名称' in html
    assert '<form' in html  # 仍然显示表单
