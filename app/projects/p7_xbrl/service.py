"""P7. XBRL/XML отчётность: разбор фактов, обязательные показатели, арифметика и периоды."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date

from app.core import db
from app.core.ai import narrative

REQUIRED = ("АктивыВсего", "Обязательства", "Капитал", "Выручка")
TOLERANCE = 0.01


def reports():
    return db.fetch_all("select id, period, entity, form_code, file_name, loaded_at from xbrl_reports order by id")


def report(report_id):
    return db.fetch_one("select id, period, entity, form_code, file_name, xml_text from xbrl_reports where id = %s", (report_id,))


def _local(tag):
    return tag.split("}")[-1]


def _facts(root):
    return {_local(node.tag): (node.text or "").strip() for node in root.iter() if node.get("contextRef") is not None}


def _tag_text(root, name):
    return next((node.text for node in root.iter() if _local(node.tag) == name), None)


def _period(root):
    return {"start": _tag_text(root, "startDate"), "end": _tag_text(root, "endDate")}


_NUMBER = re.compile(r"^-?\d+(?:\.\d+)?$")


def _parse_number(value):
    return float(value) if _NUMBER.match(value) else None


def number(value):
    return _parse_number(str(value).replace(" ", "").replace(",", ".")) if value else None


def _finding(level, title, detail):
    return {"level": level, "title": title, "detail": detail}


def _check_required(facts):
    missing = [item for item in REQUIRED if item not in facts]
    return [_finding("risk", "Нет обязательных показателей", f"Отсутствуют: {', '.join(missing)}.")] if missing else []


def _extract(facts, keys):
    return [number(facts.get(key)) for key in keys]


def _balance_issue(assets, liabilities, capital):
    balanced = all(item is not None for item in (assets, liabilities, capital)) and abs(assets - liabilities - capital) <= max(1.0, abs(assets) * TOLERANCE)
    return [] if balanced else [_finding("risk", "Не сходится баланс", f"Активы {assets}, обязательства {liabilities}, капитал {capital}: разница {round((assets or 0) - (liabilities or 0) - (capital or 0), 2)}.")]


def _check_balance(facts):
    return _balance_issue(*_extract(facts, ("АктивыВсего", "Обязательства", "Капитал")))


def _check_negative(facts):
    negative = [key for key in ("Выручка", "ЧистаяПрибыль") if (number(facts.get(key)) or 0) < 0]
    return [_finding("warn", "Отрицательный показатель", f"Значение меньше нуля: {', '.join(negative)}.")] if negative else []


def _iso(value):
    return bool(value) and len(value) == 10 and value[4] == "-" and value[7] == "-"


def _span(start, end):
    return (date.fromisoformat(end) - date.fromisoformat(start)).days if _iso(start) and _iso(end) else None


def _days(period):
    return _span(period["start"], period["end"])


def _check_period(period):
    length = _days(period)
    return [] if length is None else [_finding("risk", "Некорректный период", "Дата окончания раньше даты начала.")] if length < 0 else [_finding("warn", "Длинный период", f"Период охватывает {length} дней — проверьте, это отчёт за год или за квартал.")] if length > 400 else []


def _check_units(root):
    count = sum(1 for node in root.iter() if node.get("contextRef") is not None and not node.get("unitRef"))
    return [_finding("warn", "Факты без единицы измерения", f"У {count} фактов нет unitRef.")] if count else []


def _status(issues):
    return "требует исправления" if any(item["level"] == "risk" for item in issues) else "принят"


def _summary(facts, issues, period):
    return narrative.sentence([
        f"Период {period['start']} — {period['end']}",
        f"показателей найдено: {len(facts)}",
        f"активы {facts.get('АктивыВсего', '—')}, капитал {facts.get('Капитал', '—')}",
        f"замечаний: {len(issues)}" + (" — " + "; ".join(item["title"].lower() for item in issues) if issues else ""),
        _status(issues),
    ])


def _report(facts, period, issues):
    return {"facts": facts, "period": period, "issues": issues, "status": _status(issues), "summary": _summary(facts, issues, period)}


def _checks(facts, root, period):
    return [*_check_required(facts), *_check_balance(facts), *_check_negative(facts), *_check_period(period), *_check_units(root)]


def _inspect(root):
    facts = _facts(root)
    return _inspect_period(root, facts, _period(root))


def _inspect_period(root, facts, period):
    return _report(facts, period, _checks(facts, root, period))


def validate(xml_text):
    return _inspect(ET.fromstring(xml_text))


def validate_report(report_id):
    return validate(report(report_id)["xml_text"])


def overview():
    return {"reports": reports()}
