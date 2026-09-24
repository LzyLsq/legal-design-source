"""LawDesign 公共库。

集中存放各服务共用的配置加载、路径解析、安全校验与 Web 框架脚手架，
避免 20+ 个服务各自复制一份 ``db_config`` / ``secret_key`` / CORS 配置。

用法示例::

    from shared import config, web

    app = web.create_flask_app(__name__)     # 自动注入 SECRET_KEY + CORS 白名单
    laws_dir = config.path_from(__file__, "laws")

    with db.db_cursor("mysql", commit=True) as cursor:   # 连接/游标自动关闭
        cursor.execute("SELECT 1")

    app = feedback.create_feedback_app(__name__, "feedback")  # 可选：通用反馈表单
"""

from . import config  # noqa: F401
from . import db  # noqa: F401
from . import web  # noqa: F401
from .config import (  # noqa: F401
    REPO_ROOT,
    cors_origins,
    db_config,
    connect_mysql,
    connect_pymysql,
    flask_debug,
    load_env,
    path_from,
    safe_path,
    secret_key,
    setting,
)

__all__ = [
    "REPO_ROOT",
    "config",
    "db",
    "web",
    "setting",
    "load_env",
    "db_config",
    "connect_mysql",
    "connect_pymysql",
    "secret_key",
    "cors_origins",
    "flask_debug",
    "path_from",
    "safe_path",
]
