"""共享配置：环境变量、数据库连接、路径解析与安全校验。

设计原则
--------
1. **单一事实来源**：所有服务的数据库 / 密钥 / CORS 配置都从这里读取，
   不再在每个 ``*.py`` 里复制一份 ``db_config`` 字典。
2. **不依赖 ``python-dotenv``**：内置极简 ``.env`` 解析，方便直接
   ``python3 services/xxx/xxx.py`` 启动而未先 source ``.env``。
3. **零密钥入库**：真实密钥只允许来自环境变量 / 本地 ``.env``（已被 git 忽略）。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

__all__ = [
    "REPO_ROOT",
    "setting",
    "load_env",
    "db_config",
    "connect_pymysql",
    "connect_mysql",
    "secret_key",
    "cors_origins",
    "flask_debug",
    "path_from",
    "safe_path",
]

# 仓库根目录（本文件位于 <root>/shared/config.py）
REPO_ROOT: Path = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------- #
# 环境变量
# --------------------------------------------------------------------------- #
def _parse_env_file(path: Path) -> Dict[str, str]:
    """极简 .env 解析：忽略注释/空行，支持 ``export K=V`` 与引号包裹。"""
    values: Dict[str, str] = {}
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return values
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export "):].strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def load_env(path: Optional[Path] = None, *, override: bool = False) -> Dict[str, str]:
    """把 ``.env`` 中的键值注入 ``os.environ``（已存在的变量默认不覆盖）。

    返回实际生效的映射，便于调试。
    """
    env_path = Path(path) if path else REPO_ROOT / ".env"
    parsed = _parse_env_file(env_path)
    applied: Dict[str, str] = {}
    for key, value in parsed.items():
        if override or key not in os.environ:
            os.environ[key] = value
            applied[key] = value
    return applied


# 导入即加载一次 .env，保证 `python3 services/auth/login.py` 也能拿到配置
load_env()


def setting(name: str, default: Optional[str] = None, *, required: bool = False) -> Optional[str]:
    """读取环境变量，缺省时给出可读的错误信息。"""
    value = os.getenv(name, default)
    if required and (value is None or value == ""):
        raise RuntimeError(f"缺少必需的环境变量 {name}，请在 .env 或部署环境中配置")
    return value


# --------------------------------------------------------------------------- #
# 数据库
# --------------------------------------------------------------------------- #
def db_config(driver: str = "pymysql") -> Dict[str, Any]:
    """根据环境变量生成数据库连接配置。

    :param driver: ``pymysql`` 返回 PyMySQL 参数；``mysql`` 返回
        mysql-connector-python 参数（键名不同：``db`` -> ``database``）。
    """
    import pymysql

    common: Dict[str, Any] = {
        "host": setting("DB_HOST", "127.0.0.1"),
        "user": setting("DB_USER", "root"),
        "password": setting("DB_PASSWORD", ""),
    }
    if driver == "mysql":
        return {**common, "database": setting("DB_NAME", "flask_login_system")}
    return {
        **common,
        "db": setting("DB_NAME", "flask_login_system"),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
    }


def connect_pymysql():
    """返回一个 PyMySQL 连接（DictCursor）。"""
    import pymysql

    return pymysql.connect(**db_config("pymysql"))


def connect_mysql():
    """返回一个 mysql-connector-python 连接。"""
    import mysql.connector

    return mysql.connector.connect(**db_config("mysql"))


# --------------------------------------------------------------------------- #
# 安全 / 跨域
# --------------------------------------------------------------------------- #
def secret_key() -> str:
    """Flask session 密钥。

    生产环境必须通过 ``SECRET_KEY`` 注入固定值；未设置时回退为随机值
    （进程重启后 session 失效，仅适合本地开发）。
    """
    return setting("SECRET_KEY") or os.urandom(24).hex()


def cors_origins(default: Iterable[str] = ("http://localhost:5173", "http://127.0.0.1:5173")) -> List[str]:
    """CORS 白名单，来源于 ``CORS_ORIGINS``（逗号分隔）。"""
    raw = setting("CORS_ORIGINS")
    if not raw:
        return list(default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def flask_debug() -> bool:
    """是否开启 Flask debug（由 ``FLASK_DEBUG`` 控制，默认关闭）。"""
    return str(setting("FLASK_DEBUG", "false")).lower() in {"1", "true", "yes", "on"}


# --------------------------------------------------------------------------- #
# 路径
# --------------------------------------------------------------------------- #
def path_from(anchor: str, *parts: str) -> Path:
    """以**某个源文件所在目录**为基准解析路径，彻底摆脱 ``../`` 相对路径。

    ``path_from(__file__, "laws")`` 永远指向 ``<该文件所在目录>/laws``，
    无论从哪个工作目录启动服务都不会错。
    """
    return (Path(anchor).resolve().parent / Path(*parts)).resolve()


def safe_path(base: Path, filename: str) -> Optional[Path]:
    """把用户输入的文件名限制在 ``base`` 目录内，防路径穿越。

    任何包含 ``..``、绝对路径或指向 ``base`` 之外的路径都会返回 ``None``。
    """
    if not filename:
        return None
    candidate = (Path(base) / filename).resolve()
    base_resolved = Path(base).resolve()
    if candidate == base_resolved or base_resolved not in candidate.parents:
        return None
    return candidate
