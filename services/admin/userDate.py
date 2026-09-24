import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import db, web  # noqa: E402

from flask import render_template, request, jsonify
from mysql.connector import Error
from werkzeug.security import generate_password_hash
import math
from datetime import datetime

app = web.create_flask_app(__name__)

def get_total_users(search=None):
    """用户总数；search 为纯数字时按 ID 查，否则按用户名模糊查。"""
    if search and search.isdigit():
        query, params = "SELECT COUNT(*) FROM users WHERE id = %s", (int(search),)
    elif search:
        query, params = "SELECT COUNT(*) FROM users WHERE username LIKE %s", (f"%{search}%",)
    else:
        query, params = "SELECT COUNT(*) FROM users", ()

    try:
        with db.db_cursor("mysql", dictionary=False) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()[0]
    except Error:
        app.logger.exception("获取用户总数失败")
        return 0

def get_paginated_users(page=1, per_page=10, search=None):
    """分页查询用户；search 为纯数字时按 ID 查，否则按用户名模糊查。"""
    offset = (page - 1) * per_page
    if search and search.isdigit():
        query = """
            SELECT id, username, email, created_at
            FROM users
            WHERE id = %s
            ORDER BY id DESC
            LIMIT %s OFFSET %s
        """
        params = (int(search), per_page, offset)
    elif search:
        query = """
            SELECT id, username, email, created_at
            FROM users
            WHERE username LIKE %s
            ORDER BY id DESC
            LIMIT %s OFFSET %s
        """
        params = (f"%{search}%", per_page, offset)
    else:
        query = """
            SELECT id, username, email, created_at
            FROM users
            ORDER BY id DESC
            LIMIT %s OFFSET %s
        """
        params = (per_page, offset)

    try:
        with db.db_cursor("mysql") as cursor:
            cursor.execute(query, params)
            users = cursor.fetchall()
    except Error:
        app.logger.exception("获取分页用户失败")
        return []

    # 格式化日期
    for user in users:
        if isinstance(user['created_at'], datetime):
            user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    return users

def username_exists(username, exclude_id=None):
    """用户名是否已被占用；``exclude_id`` 用于更新时排除自身。"""
    if exclude_id:
        query, params = "SELECT 1 FROM users WHERE username = %s AND id != %s", (username, exclude_id)
    else:
        query, params = "SELECT 1 FROM users WHERE username = %s", (username,)

    try:
        with db.db_cursor("mysql") as cursor:
            cursor.execute(query, params)
            return cursor.fetchone() is not None
    except Error:
        app.logger.exception("检查用户名是否存在失败")
        return False

def email_exists(email, exclude_id=None):
    """邮箱是否已被注册；``exclude_id`` 用于更新时排除自身。"""
    if exclude_id:
        query, params = "SELECT 1 FROM users WHERE email = %s AND id != %s", (email, exclude_id)
    else:
        query, params = "SELECT 1 FROM users WHERE email = %s", (email,)

    try:
        with db.db_cursor("mysql") as cursor:
            cursor.execute(query, params)
            return cursor.fetchone() is not None
    except Error:
        app.logger.exception("检查邮箱是否存在失败")
        return False

def add_user(username, email, password):
    if username_exists(username):
        return False, "用户名已存在，请选择其他用户名。"
    if email_exists(email):
        return False, "邮箱已被注册，请使用其他邮箱。"

    hashed_password = generate_password_hash(password)
    query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    try:
        with db.db_cursor("mysql", commit=True, dictionary=False) as cursor:
            cursor.execute(query, (username, email, hashed_password))
        return True, "用户添加成功！"
    except Error:
        app.logger.exception("添加用户失败")
        return False, "添加用户时出错，请稍后重试"

def get_user(user_id):
    query = "SELECT id, username, email, created_at FROM users WHERE id = %s"
    try:
        with db.db_cursor("mysql") as cursor:
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
    except Error:
        app.logger.exception("获取用户信息失败")
        return None

    if user and isinstance(user['created_at'], datetime):
        user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    return user

def update_user(user_id, new_username, new_email, new_password=None):
    if username_exists(new_username, user_id):
        return False, "用户名已存在，请选择其他用户名。"
    if email_exists(new_email, user_id):
        return False, "邮箱已被注册，请使用其他邮箱。"

    if new_password:
        query = "UPDATE users SET username = %s, email = %s, password = %s WHERE id = %s"
        params = (new_username, new_email, generate_password_hash(new_password), user_id)
    else:
        query = "UPDATE users SET username = %s, email = %s WHERE id = %s"
        params = (new_username, new_email, user_id)

    try:
        with db.db_cursor("mysql", commit=True, dictionary=False) as cursor:
            cursor.execute(query, params)
        return True, "用户信息已更新。"
    except Error:
        app.logger.exception("更新用户失败")
        return False, "更新用户时出错，请稍后重试"

def delete_user(user_id):
    query = "DELETE FROM users WHERE id = %s"
    try:
        with db.db_cursor("mysql", commit=True, dictionary=False) as cursor:
            cursor.execute(query, (user_id,))
        return True, "用户已删除。"
    except Error:
        app.logger.exception("删除用户失败")
        return False, "删除用户时出错，请稍后重试"

@app.route('/')
@app.route('/users/<int:page>')
def index(page=1):
    search = request.args.get('search', '').strip()
    per_page = 10
    total_users = get_total_users(search)
    total_pages = max(math.ceil(total_users / per_page), 1)

    # 确保page在有效范围内
    page = max(1, min(page, total_pages))

    users = get_paginated_users(page, per_page, search)
    return render_template('userDate.html',
                           users=users,
                           page=page,
                           total_pages=total_pages,
                           search=search)

@app.route('/api/users', methods=['POST'])
def user_api():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': '无效的请求数据'}), 400

    operation = data.get('operation')
    if not operation:
        return jsonify({'status': 'error', 'message': '缺少操作类型'}), 400

    try:
        if operation == 'add':
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()

            if not all([username, email, password]):
                return jsonify({'status': 'error', 'message': '请填写所有必填项'}), 400

            success, message = add_user(username, email, password)
            return jsonify({'status': 'success' if success else 'error', 'message': message})

        elif operation == 'query':
            user_id = data.get('user_id')
            if not user_id:
                return jsonify({'status': 'error', 'message': '缺少用户ID'}), 400

            user = get_user(user_id)
            if user:
                return jsonify({'status': 'success', 'user': user})
            return jsonify({'status': 'error', 'message': f"未找到ID为{user_id}的用户"}), 404

        elif operation == 'update':
            user_id = data.get('user_id')
            new_username = data.get('new_username', '').strip()
            new_email = data.get('new_email', '').strip()
            new_password = data.get('new_password', '').strip() or None

            if not all([user_id, new_username, new_email]):
                return jsonify({'status': 'error', 'message': '请填写所有必填项'}), 400

            success, message = update_user(user_id, new_username, new_email, new_password)
            return jsonify({'status': 'success' if success else 'error', 'message': message})

        elif operation == 'delete':
            user_id = data.get('user_id')
            if not user_id:
                return jsonify({'status': 'error', 'message': '缺少用户ID'}), 400

            success, message = delete_user(user_id)
            return jsonify({'status': 'success' if success else 'error', 'message': message})

        elif operation == 'get_user':
            user_id = data.get('user_id')
            if not user_id:
                return jsonify({'status': 'error', 'message': '缺少用户ID'}), 400

            user = get_user(user_id)
            if user:
                return jsonify({'status': 'success', 'user': user})
            return jsonify({'status': 'error', 'message': f"未找到ID为{user_id}的用户"}), 404

        else:
            return jsonify({'status': 'error', 'message': '无效的操作类型'}), 400

    except Exception:  # noqa: BLE001
        app.logger.exception("用户管理 API 处理异常")
        return jsonify({'status': 'error', 'message': '服务器内部错误'}), 500

if __name__ == '__main__':
    web.run_flask(app, 5009)