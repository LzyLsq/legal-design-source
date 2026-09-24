"""数据库连接与事务上下文。

把散落在 8 个服务里、重复 30 多遍的

    conn = connect()
    cursor = conn.cursor(dictionary=True)
    ... cursor.execute(...)
    conn.commit()
    cursor.close()
    conn.close()

收敛成一行::

    with db.db_cursor("mysql", commit=True) as cursor:
        cursor.execute(...)

收益：

* **连接和游标一定被关闭**，即使 ``cursor.execute`` 抛异常；
* 连接本身失败时不会再走进 ``finally`` 里的 ``cursor.close()``，
  也就不会再用 ``UnboundLocalError`` 覆盖真正的数据库错误
  （原代码在 ``login.py`` / ``administrator.py`` / ``userDate.py``
  里都有这个隐患）；
* ``mysql-connector`` 用 ``cursor(dictionary=True)``、
  ``PyMySQL`` 用 ``cursor(DictCursor)``，驱动差异在这里统一消化。
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from .config import db_config

__all__ = ["connect", "db_connection", "db_cursor"]


def connect(driver: str = "mysql"):
    """按驱动名创建数据库连接。

    :param driver: ``"mysql"`` 用 mysql-connector-python，
        ``"pymysql"`` 用 PyMySQL（并附带 DictCursor）。
    """
    if driver == "pymysql":
        import pymysql

        return pymysql.connect(**db_config("pymysql"))
    import mysql.connector

    return mysql.connector.connect(**db_config("mysql"))


@contextmanager
def db_connection(driver: str = "mysql"):
    """只管理连接生命周期，游标由调用方自行创建。"""
    conn = connect(driver)
    try:
        yield conn
    finally:
        _close(conn)


@contextmanager
def db_cursor(driver: str = "mysql", *, commit: bool = False, dictionary: bool = True) -> Iterator[Any]:
    """打开连接 + 游标，退出时先关游标、再按需提交、最后关连接。

    :param driver: 数据库驱动，见 :func:`connect`。
    :param commit: 正常退出时是否提交事务。
    :param dictionary: 是否返回字典行（``row['col']`` 而不是 ``row[0]``）。
    """
    conn = connect(driver)
    try:
        cursor = _make_cursor(conn, driver, dictionary)
        try:
            yield cursor
        finally:
            _close(cursor)
        if commit:
            conn.commit()
    finally:
        _close(conn)


def _make_cursor(conn, driver: str, dictionary: bool):
    """不同驱动的「字典游标」创建方式不一样，在这里统一。"""
    if not dictionary:
        return conn.cursor()
    if driver == "pymysql":
        import pymysql

        return conn.cursor(pymysql.cursors.DictCursor)
    return conn.cursor(dictionary=True)


def _close(obj: Any) -> None:
    """关闭资源；关闭失败不能掩盖调用方真正的异常。"""
    if obj is None:
        return
    try:
        obj.close()
    except Exception:  # noqa: BLE001
        pass
