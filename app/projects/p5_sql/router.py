from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.core.ui import page
from app.projects.p5_sql import service

router = APIRouter(prefix="/p5", tags=["P5 — SQL-аналитик"])


class AnalyzeRequest(BaseModel):
    dbms: str = "PostgreSQL"
    query: str = ""
    plan: str = ""
    duration_ms: int = 0


def _pick(items, sample):
    return next((item for item in items if item["id"] == sample), items[0] if items else None)


def _chosen_state(items, chosen):
    return {"samples": items, "chosen": chosen, "result": service.analyze(chosen["query_text"], chosen["plan_text"], chosen["dbms"], chosen["duration_ms"]) if chosen else None}


def _state(sample):
    items = service.samples()
    return _chosen_state(items, _pick(items, sample))


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def view(request: Request, sample: int = 1):
    return page(request, "p5/sql.html", {"page_id": "p5", "active": "P5", "page_title": "SQL-аналитик", **_state(sample)})


@router.get("/api/samples")
def api_samples() -> list:
    return service.samples()


@router.post("/api/analyze")
def api_analyze(payload: AnalyzeRequest) -> dict:
    return service.analyze(payload.query, payload.plan, payload.dbms, payload.duration_ms)
