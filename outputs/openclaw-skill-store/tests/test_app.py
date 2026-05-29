# tests/test_app.py — Flask 应用初始测试
import pytest
from app import app


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


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
