from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core.ui import page
from app.projects.p3_access import service

router = APIRouter(prefix="/p3", tags=["P3 — права доступа"])


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def view(request: Request):
    return page(request, "p3/access.html", {"page_id": "p3", "active": "P3", "page_title": "Аудит прав доступа", "model": service.overview()})


@router.get("/api/risk")
def api_risk() -> dict:
    return service.overview()


@router.post("/api/recount")
def api_recount() -> dict:
    return service.overview()
