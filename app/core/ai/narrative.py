"""Порождение текста без внешних моделей: правила, склонения, короткие сводки."""

from __future__ import annotations

TEEN_TAILS = (12, 13, 14)


def plural(number, one, few, many):
    tail = abs(number) % 100
    return one if tail % 10 == 1 and tail not in (11,) else few if tail % 10 in (2, 3, 4) and tail not in TEEN_TAILS else many


def bullets(items):
    return "\n".join(f"· {item}" for item in items) if items else "· данных нет"


def sentence(parts):
    return " ".join(f"{part.strip().rstrip('.')}." for part in parts if part)


def risk_word(score):
    return "низкий" if score < 0.35 else "средний" if score < 0.7 else "высокий"


def percent(part, whole):
    return round(100 * part / whole, 1) if whole else 0.0
