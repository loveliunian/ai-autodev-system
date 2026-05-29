# app.py — OpenClaw Skill Store 最小 Flask 应用
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    """首页路由"""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
