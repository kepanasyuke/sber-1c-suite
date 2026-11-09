"""Тонкий слой доступа к PostgreSQL: свой пул соединений, без ORM."""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from app.core.config import settings

_LOCK = threading.Lock()
_FREE: list[psycopg.Connection] = []
_READERS = {"all": lambda cur: cur.fetchall(), "one": lambda cur: cur.fetchone()}


def _connect() -> psycopg.Connection:
    return psycopg.connect(settings.dsn, row_factory=dict_row, autocommit=True)


def _acquire() -> psycopg.Connection:
    with _LOCK:
        return _FREE.pop() if _FREE else _connect()


def _release(conn: psycopg.Connection) -> None:
    with _LOCK:
        _FREE.append(conn) if not conn.closed else None


@contextmanager
def connection() -> Iterator[psycopg.Connection]:
    conn = _acquire()
    try:
        yield conn
    finally:
        _release(conn)


def _reader(mode: str):
    return _READERS[mode]


def _run(sql: str, params: tuple, mode: str):
    with connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return _reader(mode)(cur) if cur.description else []


def fetch_all(sql: str, params: tuple = ()) -> list[dict]:
    return _run(sql, params, "all")


def fetch_one(sql: str, params: tuple = ()) -> dict | None:
    return _run(sql, params, "one")


def execute(sql: str, params: tuple = ()) -> list[dict]:
    return _run(sql, params, "all")


def scalar(sql: str, params: tuple = ()):
    row = fetch_one(sql, params)
    return next(iter(row.values())) if row else None


def is_up() -> bool:
    return bool(scalar("select 1 as ok") == 1)
