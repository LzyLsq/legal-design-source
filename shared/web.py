"""Web 框架脚手架：统一 Flask / FastAPI 应用的通用装配逻辑。

把散落在 15 个 Flask 服务里的重复代码收敛到一处：

* ``secret_key`` 注入
* CORS 白名单（替代写死的 ``origins: "*"``）
* 启动参数（host / port / debug 全部走环境变量）
"""

from __future__ import annotations

from typing import Iterable, Optional

from .config import cors_origins, flask_debug, secret_key, setting

__all__ = ["create_flask_app", "run_flask", "configure_fastapi"]


def create_flask_app(import_name: str, *, cors: bool = True, **flask_kwargs):
    """创建一个标准化的 Flask 应用。

    :param import_name: 传 ``__name__``，Flask 据此定位 templates / static。
    :param cors: 是否启用 CORS 白名单。
    """
    from flask import Flask
    from flask_cors import CORS

    app = Flask(import_name, **flask_kwargs)
    app.secret_key = secret_key()
    if cors:
        CORS(app, resources={r"/*": {"origins": cors_origins()}})
    return app


def run_flask(app, default_port: int, *, host: Optional[str] = None) -> None:
    """启动 Flask 服务；端口取 ``SERVICE_PORT``，缺省用 ``default_port``。"""
    app.run(
        host=host or setting("SERVICE_HOST", "127.0.0.1"),
        port=int(setting("SERVICE_PORT", str(default_port))),
        debug=flask_debug(),
    )


def configure_fastapi(app, *, origins: Optional[Iterable[str]] = None) -> None:
    """给 FastAPI 应用挂上 CORS 白名单中间件。"""
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(origins) if origins else cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
