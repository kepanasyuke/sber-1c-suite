"""Робастное обнаружение аномалий: медиана и MAD, устойчивые к выбросам."""

from __future__ import annotations

from statistics import median


def mad(values):
    center = median(values)
    return median([abs(value - center) for value in values]) or 1e-9


def _scale(values):
    return mad(values) * 1.4826


def robust_z(values):
    center = median(values)
    return [(value - center) / _scale(values) for value in values]


def detect(values, threshold=3.5):
    scores = robust_z(values)
    return [{"index": index, "value": value, "z": round(z, 2), "direction": "выше нормы" if z > 0 else "ниже нормы"} for index, (value, z) in enumerate(zip(values, scores, strict=True)) if abs(z) >= threshold]


def _spread(ordered):
    return {"min": ordered[0], "max": ordered[-1], "median": median(ordered), "p95": ordered[max(0, int(len(ordered) * 0.95) - 1)]}


def summarize(values):
    return _spread(sorted(values)) if values else {"min": 0.0, "max": 0.0, "median": 0.0, "p95": 0.0}
