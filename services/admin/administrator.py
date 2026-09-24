import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import db, web  # noqa: E402

import logging
import os
from flask import request, jsonify, render_template, redirect, url_for, session
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash

app = web.create_flask_app(__name__)

logging.basicConfig(level=logging.INFO)

#: 登录成功后管理端门户地址，可通过 MANAGER_URL 覆盖
_MANAGER_URL = os.getenv('MANAGER_URL', 'http://127.0.0.1:8003')

# 初始化数据库，创建管理员表并插入默认管理员用户
def init_db():
    """确保 administrator 表存在，并写入默认管理员（口令见 .env 的 ADMIN_DEFAULT_PASSWORD）。"""
    create_table = """
        CREATE TABLE IF NOT EXISTS administrator (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """
    default_username = os.getenv("ADMIN_DEFAULT_USERNAME", "admin")
    default_password = os.getenv("ADMIN_DEFAULT_PASSWORD")

    try:
        with db.db_cursor("mysql", commit=True, dictionary=False) as cursor:
            cursor.execute(create_table)
            cursor.execute("SELECT 1 FROM administrator WHERE username = %s", (default_username,))
            if not cursor.fetchone():
                if not default_password:
                    raise RuntimeError("首次创建管理员前请设置 ADMIN_DEFAULT_PASSWORD")
                cursor.execute(
                    "INSERT INTO administrator (username, password) VALUES (%s, %s)",
                    (default_username, generate_password_hash(default_password)),
                )
    except Error:
        app.logger.exception("管理员表初始化失败")
        return
    app.logger.info("管理员表初始化完成（%s）", default_username)

@app.route('/')
def home():
    return render_template('administrator.html')

@app.route('/administrator1')
def administrator1_page():
    return render_template('administrator1.html')

@app.route('/administrator1', methods=['POST'])
def update_administrator():
    data = request.get_json()
    current_password = data.get('current_password')  # 可选：如果需要验证当前密码
    new_password = data.get('new_password')
    confirm_new_password = data.get('confirm_new_password')

    if not new_password or not confirm_new_password:
        return jsonify({'success': False, 'message': '所有字段均为必填项！'})

    if new_password != confirm_new_password:
        return jsonify({'success': False, 'message': '两次输入的新密码不一致！'})

    current_username = session.get('username')  # 从会话中获取当前用户名
    if not current_username:
        return jsonify({'success': False, 'message': '未登录或会话过期！'})

    try:
        with db.db_cursor("mysql", commit=True) as cursor:
            # 可选：验证当前密码
            if current_password:
                cursor.execute("SELECT * FROM administrator WHERE username = %s", (current_username,))
                administrator = cursor.fetchone()
                if not administrator or not check_password_hash(administrator['password'], current_password):
                    return jsonify({'success': False, 'message': '当前密码错误！'})

            # 更新密码
            cursor.execute(
                "UPDATE administrator SET password = %s WHERE username = %s",
                (generate_password_hash(new_password), current_username),
            )

        return jsonify({'success': True, 'message': '密码更新成功！请重新登录。'})
    except Error:  # noqa: BLE001
        app.logger.exception('修改管理员密码失败')
        return jsonify({'success': False, 'message': '服务端错误，请稍后重试'}), 500


@app.route('/administrator', methods=['POST'])
def login_administrator():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        with db.db_cursor("mysql") as cursor:
            cursor.execute("SELECT * FROM administrator WHERE username = %s", (username,))
            administrator = cursor.fetchone()

        # 检查用户名和密码
        if administrator and check_password_hash(administrator['password'], password):
            session['logged_in'] = True
            session['username'] = administrator['username']

            # 登录成功后跳转到管理端门户
            return jsonify({'success': True, 'message': '登录成功！', 'redirect_url': _MANAGER_URL})
        return jsonify({'success': False, 'message': '账户或密码错误，请检查后重试。'})
    except Error:  # noqa: BLE001
        app.logger.exception('管理员登录失败')
        return jsonify({'success': False, 'message': '服务端错误，请稍后重试'}), 500



@app.route('/get_admin_info', methods=['GET'])
def get_admin_info():
    current_username = session.get('username')  # 从会话中获取当前管理员的用户名
    if not current_username:
        return jsonify({'success': False, 'message': '未登录或会话过期！'})

    try:
        with db.db_cursor("mysql") as cursor:
            cursor.execute("SELECT username FROM administrator WHERE username = %s", (current_username,))
            admin_info = cursor.fetchone()

        if not admin_info:
            return jsonify({'success': False, 'message': '管理员信息不存在！'})

        return jsonify({'success': True, 'data': admin_info})
    except Error:  # noqa: BLE001
        app.logger.exception('获取管理员信息失败')
        return jsonify({'success': False, 'message': '服务端错误，请稍后重试'}), 500


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    init_db()  # 初始化数据库
    web.run_flask(app, 5011)