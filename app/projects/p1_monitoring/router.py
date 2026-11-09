from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core.ui import page
from app.projects.p1_monitoring import service

router = APIRouter(prefix="/p1", tags=["P1 — мониторинг"])


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def view(request: Request, host: str = ""):
    host_list = service.hosts()
    return page(request, "p1/monitoring.html", {"page_id": "p1", "active": "P1", "page_title": "Мониторинг серверов 1С", "hosts": host_list, "current": host or service.default_host(), "model": service.overview(host or service.default_host())})


@router.get("/api/overview")
def api_overview(host: str = "") -> dict:
    return service.overview(host or service.default_host())
