import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import config, db, web  # noqa: E402

import logging
import os
from flask import jsonify, redirect, render_template, request, send_from_directory, session, url_for
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash

app = web.create_flask_app(__name__)

logging.basicConfig(level=logging.INFO)


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/administrator')
def administrator():
    return render_template('administrator.html')


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

    try:
        with db.db_cursor('mysql', commit=True) as cursor:
            cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({'success': False, 'message': '用户名已存在，请选择其他用户名。'})

            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                (username, generate_password_hash(password), email),
            )
    except Error:  # noqa: BLE001
        app.logger.exception('注册失败')
        return jsonify({'success': False, 'message': '服务端错误，请稍后重试'}), 500

    return jsonify({'success': True, 'message': '注册成功！'})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    try:
        with db.db_cursor('mysql') as cursor:
            cursor.execute("SELECT username, password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
    except Error:  # noqa: BLE001
        app.logger.exception('登录失败')
        return jsonify({'success': False, 'message': '服务端错误，请稍后重试'}), 500

    if user and check_password_hash(user['password'], password):
        session['logged_in'] = True
        session['username'] = user['username']
        return jsonify({'success': True, 'message': '登录成功！'})
    return jsonify({'success': False, 'message': '用户名或密码错误，请检查后重试。'})


@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    # 返回 static/dist 目录下的 index.html 文件
    return send_from_directory(str(config_path_dist()), 'index.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('home'))


def config_path_dist() -> Path:
    """SPA 构建产物目录：<本服务目录>/static/dist。"""
    return config.path_from(__file__, 'static', 'dist')


if __name__ == '__main__':
    # 登录服务需要对容器 / 局域网可见，默认仍只监听本机，按需用 SERVICE_HOST 覆盖
    web.run_flask(app, int(os.getenv('LOGIN_PORT', '5000')))
