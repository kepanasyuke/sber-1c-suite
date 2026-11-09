"""Точка сборки: миграция, наполнение демо-данными, восемь модулей и лендинг."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.catalog import MODULES
from app.core import db, seed
from app.core.config import settings
from app.core.ui import BASE_DIR, page
from app.projects import (
    p1_monitoring,
    p2_backup,
    p3_access,
    p4_updates,
    p5_sql,
    p6_sedesk,
    p7_xbrl,
    p8_edo,
)

ROUTERS = (
    p1_monitoring.router,
    p2_backup.router,
    p3_access.router,
    p4_updates.router,
    p5_sql.router,
    p6_sedesk.router,
    p7_xbrl.router,
    p8_edo.router,
)

TABLES = (
    "hosts",
    "metrics",
    "sessions",
    "backup_jobs",
    "backup_logs",
    "users",
    "roles",
    "user_roles",
    "rights",
    "conf_versions",
    "conf_objects",
    "sql_samples",
    "tickets",
    "kb_articles",
    "xbrl_reports",
    "documents",
)


def _migrate() -> int:
    return len(db.execute((BASE_DIR / "migrations" / "001_init.sql").read_text(encoding="utf-8")))


def _prepare() -> dict:
    _migrate()
    return seed.seed_all()


def _total_rows():
    return sum(db.scalar(f"select count(*) from {table}") or 0 for table in TABLES)


def _mttr():
    return round(float(db.scalar("select coalesce(avg(extract(epoch from (closed_at - created_at)) / 3600), 0) from tickets where closed_at is not null") or 0), 1)


def _exposure():
    return db.scalar("select count(*) from tickets where status = 'open'") or 0


def _stats():
    return {
        "projects": len(MODULES),
        "metrics": db.scalar("select count(*) from metrics") or 0,
        "hosts": db.scalar("select count(*) from hosts") or 0,
        "bases": db.scalar("select count(*) from backup_jobs") or 0,
        "rows": _total_rows(),
        "mttr": _mttr(),
        "open_tickets": _exposure(),
        "routing": p6_sedesk.service.cross_validate()["accuracy"],
    }


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _prepare()
    yield


app = FastAPI(title=settings.title, version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

for module_router in ROUTERS:
    app.include_router(module_router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing(request: Request):
    return page(request, "landing.html", {"page_id": "landing", "stats": _stats()})


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "database": db.is_up(), "llm": settings.llm_enabled, "modules": len(ROUTERS)}


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8010, reload=False)


if __name__ == "__main__":
    main()
