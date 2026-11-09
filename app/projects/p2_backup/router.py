from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.core.ui import page
from app.projects.p2_backup import service

router = APIRouter(prefix="/p2", tags=["P2 — резервное копирование"])


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def view(request: Request):
    return page(request, "p2/backup.html", {"page_id": "p2", "active": "P2", "page_title": "Резервное копирование", "model": service.overview()})


@router.get("/api/jobs")
def api_jobs() -> dict:
    return service.overview()


@router.post("/api/analyze/{job_id}")
def api_analyze(job_id: int) -> dict:
    try:
        return service.analyze(job_id)
    except (AttributeError, TypeError) as error:
        raise HTTPException(status_code=404, detail=f"Задание {job_id} не найдено") from error
