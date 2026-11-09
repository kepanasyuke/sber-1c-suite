"""P1. Метрики хостов кластера, статистика сеансов и обнаружение аномалий."""

from __future__ import annotations

from app.core import db
from app.core.ai import anomaly, narrative

TITLES = {"cpu": "CPU, %", "ram": "Память, %", "resp": "Отклик, мс"}
ORDER = ("cpu", "ram", "resp")


def hosts():
    return db.fetch_all("select code, name, role, dbms, cores from hosts order by code")


def _series(host_code, metric):
    return db.fetch_all("select ts, value from metrics where host_code = %s and metric = %s order by ts", (host_code, metric))


def _collect(host_code):
    return {metric: _series(host_code, metric) for metric in ORDER}


def labels(rows):
    return [row["ts"].strftime("%H:%M") for row in rows]


def mean(rows):
    return round(sum(row["value"] for row in rows) / len(rows), 1) if rows else 0.0


def peak(rows):
    return round(max((row["value"] for row in rows), default=0.0), 1)


def _kpis(data):
    return {metric: {"avg": mean(rows), "peak": peak(rows)} for metric, rows in data.items()}


def _anomalies(data):
    return [{"metric": metric, "label": TITLES[metric], "at": rows[item["index"]]["ts"].strftime("%H:%M"), **item} for metric, rows in data.items() for item in anomaly.detect([row["value"] for row in rows])]


def load_index(data, found):
    return min(100.0, round(mean(data["cpu"]) * 1.1 + len(found) * 6 + mean(data["resp"]) / 20, 1))


def summary(host_code, data, found):
    details = ", ".join(f"{item['label']} в {item['at']} ({item['z']}σ)" for item in found[:4])
    return narrative.sentence([
        f"Хост {host_code}: средняя загрузка CPU {mean(data['cpu'])} %, память {mean(data['ram'])} %, отклик {mean(data['resp'])} мс",
        f"пиковый отклик {peak(data['resp'])} мс",
        f"аномалий за смену: {len(found)}" + (f" — {details}" if details else ""),
        f"вывод: {'требуется вмешательство дежурного' if found else 'отклонений не обнаружено'}",
    ])


def _top_sessions(host_code):
    rows = db.fetch_all("select login, app, started_at, duration_min, calls from sessions where host_code = %s order by calls desc limit 6", (host_code,))
    return [{**row, "started_at": row["started_at"].strftime("%d.%m %H:%M")} for row in rows]


def _overview(host_code, data):
    found = _anomalies(data)
    return {
        "host": host_code,
        "labels": labels(data["cpu"]),
        "series": [{"label": TITLES[metric], "points": [row["value"] for row in rows]} for metric, rows in data.items()],
        "kpis": _kpis(data),
        "anomalies": found,
        "load_index": load_index(data, found),
        "summary": summary(host_code, data, found),
        "sessions": _top_sessions(host_code),
    }


def overview(host_code):
    return _overview(host_code, _collect(host_code))


def default_host():
    items = hosts()
    return items[0]["code"] if items else ""
