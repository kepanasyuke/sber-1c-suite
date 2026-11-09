from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core.ui import page
from app.projects.p4_updates import service

router = APIRouter(prefix="/p4", tags=["P4 — обновления"])


def _pair_state(target, old, new):
    pair = service.default_pair(target)
    return {"config": target, "versions": service.versions(target), "result": service.compare(target, old or pair[0], new or pair[1])}


def _state(config, old, new):
    target = config or service.default_config()
    return _pair_state(target, old, new)


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def view(request: Request, config: str = "", old: str = "", new: str = ""):
    return page(request, "p4/updates.html", {"page_id": "p4", "active": "P4", "page_title": "Обновления конфигураций", "model": service.overview(), **_state(config, old, new)})


@router.get("/api/configs")
def api_configs() -> dict:
    return service.overview()


@router.get("/api/versions")
def api_versions(config: str) -> list:
    return service.versions(config)


@router.get("/api/diff")
def api_diff(config: str, old: str, new: str) -> dict:
    return service.compare(config, old, new)
