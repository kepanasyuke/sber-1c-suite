"""Сквозные тесты: страницы, JSON-API и работа модулей на живой базе."""

import pytest
from fastapi.testclient import TestClient

from app.core import db
from app.main import app

PAGES = ("/", "/p1", "/p2", "/p3", "/p4", "/p5", "/p6", "/p7", "/p8")
ENDPOINTS = ("/healthz", "/p1/api/overview", "/p2/api/jobs", "/p3/api/risk", "/p4/api/configs", "/p7/api/reports", "/p8/api/documents")
needs_db = pytest.mark.skipif(not db.is_up(), reason="нужна запущенная PostgreSQL на 127.0.0.1:5433")


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@needs_db
def test_pages_render(client):
    assert [client.get(path).status_code for path in PAGES] == [200] * len(PAGES)


@needs_db
def test_endpoints_answer(client):
    assert [client.get(path).status_code for path in ENDPOINTS] == [200] * len(ENDPOINTS)


@needs_db
def test_monitoring_finds_anomalies(client):
    assert client.get("/p1/api/overview").json()["anomalies"]


@needs_db
def test_backup_analysis_classifies_failure(client):
    assert client.post("/p2/api/analyze/4").json()["cause"] in {"connect", "timeout", "space"}


@needs_db
def test_access_audit_flags_fired_user(client):
    risky = client.get("/p3/api/risk").json()["risky"]
    assert any("R1" in [issue["code"] for issue in item["issues"]] for item in risky)


@needs_db
def test_updates_diff_detects_added_objects(client):
    assert client.get("/p4/api/diff?config=Бухгалтерия предприятия 3.0&old=3.0.141&new=3.0.160").json()["changes"]["added"]


@needs_db
def test_sql_analyzer_scores_and_suggests_index(client):
    result = client.post("/p5/api/analyze", json={"query": "select * from регистр where period >= '2026-01-01' and склад in ('a')", "plan": "Seq Scan on регистр", "duration_ms": 2400}).json()
    assert result["score"] < 100 and result["index"]["ddl"].startswith("create index")


@needs_db
def test_sql_analyzer_marks_bad_query(client):
    result = client.post("/p5/api/analyze", json={"query": "select * from t where lower(name) like '%ivan%'"}).json()
    assert [item["title"] for item in result["findings"]]


@needs_db
def test_sedesk_routes_invoice_ticket(client):
    verdict = client.post("/p6/api/route", json={"subject": "Не печатается счёт на оплату", "body": "ошибка печати, расширение печати не подключается"}).json()
    assert verdict["label"] == "1С: Бухгалтерия" and verdict["articles"]


@needs_db
def test_xbrl_validator_catches_broken_balance(client):
    assert client.post("/p7/api/validate/2").json()["status"] == "требует исправления"


@needs_db
def test_xbrl_validator_accepts_clean_report(client):
    assert client.post("/p7/api/validate/1").json()["status"] == "принят"


@needs_db
def test_edo_classifies_documents(client):
    assert all(row["predicted"] in {"счёт", "акт", "договор", "накладная", "записка"} for row in client.get("/p8/api/documents").json()["documents"])


@needs_db
def test_edo_validates_inn_endpoint(client):
    assert client.post("/p8/api/inn", json={"inn": "7707083894"}).json()["valid"] is False
