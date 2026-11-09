from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.core.ui import page
from app.projects.p6_sedesk import service

router = APIRouter(prefix="/p6", tags=["P6 — Service Desk"])


class TicketRequest(BaseModel):
    subject: str = ""
    body: str = ""


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def view(request: Request):
    return page(request, "p6/sedesk.html", {"page_id": "p6", "active": "P6", "page_title": "Service Desk", "model": service.overview()})


@router.get("/api/tickets")
def api_tickets() -> dict:
    return service.overview()


@router.post("/api/route")
def api_route(payload: TicketRequest) -> dict:
    return service.route(payload.subject, payload.body)
