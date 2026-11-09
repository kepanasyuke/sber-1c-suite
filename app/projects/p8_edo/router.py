from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core.ui import page
from app.projects.p8_edo import service

router = APIRouter(prefix="/p8", tags=["P8 — документооборот"])


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def view(request: Request):
    return page(request, "p8/edo.html", {"page_id": "p8", "active": "P8", "page_title": "Документооборот", "model": service.overview()})


@router.get("/api/documents")
def api_documents() -> dict:
    return service.overview()


@router.post("/api/classify")
def api_classify() -> dict:
    return service.overview()


@router.post("/api/inn")
def api_inn(payload: dict) -> dict:
    return {"inn": payload.get("inn", ""), "valid": service.inn_valid(payload.get("inn", ""))}
