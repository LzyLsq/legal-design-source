"""通用「意见反馈」服务工厂。

``services/litigation/feedback.py`` 和 ``services/agreement/feedback.py``
原本是两份逐行相同的代码（只差表名和端口），任一侧改 bug 都要改两遍。
这里合并成一份实现，两个入口各自 3 行：:

    app = feedback.create_feedback_app(__name__, "feedback_b")
"""

from . import db, web

__all__ = ["create_feedback_app"]

#: 允许写入的表名白名单，防止把外部字符串拼进 SQL
_ALLOWED_TABLES = frozenset({"feedback", "feedback_b"})


def create_feedback_app(import_name: str, table: str, *, template: str = "feedback_form.html"):
    """创建一个把表单写入 ``table`` 表的反馈服务。

    :param import_name: 传 ``__name__``，Flask 据此定位 templates / static。
    :param table: 目标表名，必须在 :data:`_ALLOWED_TABLES` 白名单内。
    :param template: 使用的模板文件名。
    """
    if table not in _ALLOWED_TABLES:
        raise ValueError(f"不允许的反馈表名: {table!r}（可选: {sorted(_ALLOWED_TABLES)}）")

    from flask import render_template, request

    app = web.create_flask_app(import_name)

    @app.route("/")
    def index():
        return render_template(template)

    @app.route("/submit_feedback", methods=["POST"])
    def submit_feedback():
        template_name = request.form.get("template_name", "").strip()
        submitter = request.form.get("submitter", "").strip()
        content = request.form.get("content", "").strip()

        if not template_name or not content:
            return render_template(template, success=False, error="所需模板和反馈内容不能为空"), 400

        query = f"INSERT INTO {table} (template_name, content, submitter) VALUES (%s, %s, %s)"
        with db.db_cursor("pymysql", commit=True, dictionary=False) as cursor:
            cursor.execute(query, (template_name, content, submitter))
        return render_template(template, success=True)

    return app
