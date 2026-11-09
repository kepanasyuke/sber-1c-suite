"""P5. Разбор SQL-запроса и плана: индексные ловушки, оценка, рекомендации."""

from __future__ import annotations

import re

from app.core import db
from app.core.ai import narrative

PENALTIES = {"high": 22, "warn": 12, "info": 4}
PREFIXES = {"high": "Высокий", "warn": "Средний", "info": "Замечание"}
FUNCTIONS = ("to_char(", "convert(", "year(", "month(", "datepart(", "cast(", "substring(")
_FROM = re.compile(r"\bfrom\s+([a-zA-Zа-яА-ЯёЁ_][\w.]*)", re.I)
_WHERE = re.compile(r"\bwhere\b(.+?)(?=\bgroup\b|\border\b|\blimit\b|\breturning\b|$)", re.I | re.S)
_COLUMN = re.compile(r"([a-zA-Zа-яА-ЯёЁ_][\w.]*)\s*(?:=|>=|<=|>|<|\bbetween\b|\bin\b|\blike\b)", re.I)
_ROWS = re.compile(r"Estimated rows:\s*(\d+).*?Actual rows:\s*(\d+)", re.I | re.S)


def samples():
    return db.fetch_all("select id, dbms, title, query_text, plan_text, duration_ms from sql_samples order by id")


def _finding(level, title, detail, advice):
    return {"level": level, "label": PREFIXES[level], "title": title, "detail": detail, "advice": advice}


def _rule_select_star(query, plan, duration):
    return [_finding("warn", "SELECT *", "Выбираются все столбцы таблицы, включая тяжёлые текстовые поля.", "Перечислите только нужные столбцы, чтобы уменьшить чтение и сетевой трафик.")] if re.search(r"select\s+(\w+\.)?\*", query, re.I) else []


def _rule_leading_like(query, plan, duration):
    return [_finding("high", "LIKE с ведущим шаблоном", "Условие LIKE '%…%' не даёт использовать обычный индекс по столбцу.", "Перейдите на поиск по префиксу, полнотекстовый индекс или отдельную таблицу поиска.")] if re.search(r"like\s+'%", query, re.I) else []


def _rule_function_predicate(query, plan, duration):
    used = [item for item in FUNCTIONS if item in query.lower()]
    return [_finding("high", f"Функция в условии: {used[0].rstrip('(')}()", "Функция над столбцом в WHERE или JOIN отключает индекс по этому столбцу.", "Приведите условие к сравнению с диапазоном дат или создайте функциональный индекс по выражению.")] if used else []


def _rule_no_where(query, plan, duration):
    return [_finding("warn", "Запрос без фильтра", "Отсутствует WHERE: читается вся таблица.", "Добавьте отбор по периоду или подразделению, иначе рост данных ухудшит план.")] if query and "where" not in query.lower() else []


def _rule_seq_scan(query, plan, duration):
    hits = [line.strip() for line in plan.splitlines() if re.search(r"Seq Scan|Clustered Index Scan", line, re.I)]
    return [_finding("high", "Последовательное чтение в плане", f"План содержит полное чтение: {hits[0][:120]}", "Проверьте индекс по столбцам фильтра и обновите статистику таблицы.")] if hits else []


def _rule_order_without_limit(query, plan, duration):
    source = query.lower()
    return [_finding("info", "Сортировка без ограничения", "ORDER BY без LIMIT/TOP сортирует весь результирующий набор.", "Ограничьте выборку LIMIT или TOP, если интерфейсу нужна первая страница.")] if "order by" in source and not re.search(r"\blimit\b|\btop\b", source) else []


def _rule_in_subquery(query, plan, duration):
    return [_finding("info", "Подзапрос в IN", "Подзапрос внутри IN может выполняться отдельно для каждой строки.", "Перепишите через JOIN или EXISTS и проверьте план после правки.")] if re.search(r"\bin\s*\(\s*select", query, re.I) else []


def _rule_comma_join(query, plan, duration):
    return [_finding("warn", "Неявное соединение", "Таблицы перечислены через запятую, условие соединения спрятано в WHERE.", "Используйте явный JOIN: читаемее и проще для оптимизатора.")] if re.search(r"from\s+[\w.]+\s+\w+\s*,", query, re.I) else []


def _rule_slow(query, plan, duration):
    return [_finding("high", "Долгое выполнение", f"Замер: {duration} мс, цель — до 1000 мс для интерактивного отчёта.", "Снимите актуальный план через EXPLAIN ANALYZE и проверьте блокировки на момент замера.")] if duration and duration > 1000 else []


def _ratio(plan):
    found = _ROWS.search(plan)
    return round(int(found.group(2)) / max(int(found.group(1)), 1), 1) if found else 1.0


def _rule_row_estimate(query, plan, duration):
    ratio = _ratio(plan)
    return [_finding("warn", "Оценка строк расходится с фактом", f"Оценка отличается от факта в {ratio} раза.", "Обновите статистику (ANALYZE) и проверьте коррелированность столбцов.")] if ratio > 5 else []


RULES = (
    _rule_select_star,
    _rule_leading_like,
    _rule_function_predicate,
    _rule_no_where,
    _rule_seq_scan,
    _rule_order_without_limit,
    _rule_in_subquery,
    _rule_comma_join,
    _rule_slow,
    _rule_row_estimate,
)


def findings(query, plan, duration):
    return [item for rule in RULES for item in rule(query, plan, duration)]


def score_of(items):
    return max(0, 100 - sum(PENALTIES[item["level"]] for item in items))


def _table(query):
    found = _FROM.search(query or "")
    return found.group(1) if found else ""


def _columns(query):
    block = _WHERE.search(query or "")
    return list(dict.fromkeys(match.group(1) for match in _COLUMN.finditer(block.group(1)))) if block else []


def _hint(table, columns):
    return {"table": table, "columns": columns, "ddl": f"create index on {table} ({', '.join(columns)});" if table and columns else ""}


def index_hint(query):
    return _hint(_table(query), _columns(query))


def summary(items, score, hint):
    top = [f"{item['label']}: {item['title'].lower()}" for item in items[:3]]
    return narrative.sentence([
        f"Оценка запроса {score} из 100",
        f"замечаний: {len(items)}" + (f" — {'; '.join(top)}" if top else ""),
        f"проверка индекса: {hint['ddl']}" if hint["ddl"] else "индекс по условиям фильтра не требуется",
        "запрос пригоден для интерактивной работы" if score >= 80 else "перед выкаткой нужна оптимизация",
    ])


def _report(dbms, duration, items, hint):
    return {"dbms": dbms, "duration": duration, "findings": items, "score": score_of(items), "index": hint, "summary": summary(items, score_of(items), hint)}


def _analyze(query, plan, dbms, duration):
    items = findings(query, plan, duration)
    return _report(dbms, duration, items, index_hint(query))


def analyze(query, plan="", dbms="PostgreSQL", duration=0):
    return _analyze(query or "", plan or "", dbms, duration)
