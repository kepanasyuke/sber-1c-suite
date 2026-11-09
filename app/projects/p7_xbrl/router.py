from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.core.ui import page
from app.projects.p7_xbrl import service

router = APIRouter(prefix="/p7", tags=["P7 — XBRL"])


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def view(request: Request, report: int = 1):
    return page(request, "p7/xbrl.html", {"page_id": "p7", "active": "P7", "page_title": "XBRL-отчётность", "model": service.overview(), "current": report, "result": service.validate_report(report)})


@router.get("/api/reports")
def api_reports() -> dict:
    return service.overview()


@router.post("/api/validate/{report_id}")
def api_validate(report_id: int) -> dict:
    try:
        return service.validate_report(report_id)
    except (TypeError, AttributeError) as error:
        raise HTTPException(status_code=404, detail=f"Отчёт {report_id} не найден") from error
