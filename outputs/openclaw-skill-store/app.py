# app.py — OpenClaw Skill Store Flask 应用
from flask import Flask, render_template, request, redirect, url_for
from models import get_db, init_db

app = Flask(__name__)

# 应用启动时初始化数据库
with app.app_context():
    init_db()


@app.route('/')
def index():
    db = get_db()
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()

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
    stats = {
        'total': db.execute("SELECT COUNT(*) FROM skills").fetchone()[0],
        'categories': db.execute("SELECT COUNT(DISTINCT category) FROM skills WHERE category != ''").fetchone()[0],
    }
    categories = [row['category'] for row in db.execute(
        "SELECT DISTINCT category FROM skills WHERE category != '' ORDER BY category"
    ).fetchall()]
    return render_template(
        'index.html',
        skills=skills,
        query=query,
        category=category,
        stats=stats,
        categories=categories
    )


@app.route('/skills')
def skill_list():
    return redirect(url_for('index'))


@app.route('/skills/<int:skill_id>')
def skill_detail(skill_id):
    db = get_db()
    skill = db.execute("SELECT * FROM skills WHERE id = ?", (skill_id,)).fetchone()
    if skill is None:
        return render_template('404.html'), 404
    # 增加下载计数
    db.execute("UPDATE skills SET downloads = downloads + 1 WHERE id = ?", (skill_id,))
    db.commit()
    return render_template('skill_detail.html', skill=skill)


@app.route('/skills/submit', methods=['GET', 'POST'])
def skill_submit():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not name or not description:
            return render_template('submit.html', error='名称和描述为必填项',
                                   name=name, description=description,
                                   category=request.form.get('category', '').strip(),
                                   author=request.form.get('author', '').strip(),
                                   install_cmd=request.form.get('install_cmd', '').strip(),
                                   homepage=request.form.get('homepage', '').strip(),
                                   emoji=request.form.get('emoji', '🔧').strip())

        db = get_db()
        db.execute("""
            INSERT INTO skills (name, description, category, author, install_cmd, homepage, emoji)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name, description,
            request.form.get('category', '其他').strip(),
            request.form.get('author', '').strip(),
            request.form.get('install_cmd', '').strip(),
            request.form.get('homepage', '').strip(),
            request.form.get('emoji', '🔧').strip()
        ))
        db.commit()
        skill_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        return redirect(url_for('skill_detail', skill_id=skill_id))

    return render_template('submit.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=False)
