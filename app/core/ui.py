"""Шаблоны Jinja2 и фильтры оформления."""

from __future__ import annotations

from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.catalog import MODULES, NAV

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = BASE_DIR / "templates"


def spaces(value):
    return f"{int(value):,}".replace(",", " ") if value is not None else "—"


def decimal(value):
    return f"{float(value):,.2f}".replace(",", " ").replace(".", ",") if value is not None else "—"


def dt(value):
    return value.strftime("%d.%m %H:%M") if value else "—"


def short_date(value):
    return value.strftime("%d.%m.%Y") if value else "—"


templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.filters.update({"spaces": spaces, "decimal": decimal, "dt": dt, "date": short_date})
templates.env.globals.update({"modules": MODULES, "nav": NAV})


def page(request, template, context):
    return templates.TemplateResponse(request, template, context)
