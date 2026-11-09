"""P2. Резервное копирование: состояние заданий, разбор журналов, классификация причин."""

from __future__ import annotations

from datetime import datetime

from app.core import db
from app.core.ai import classify, narrative

TRAINING = [
    ("connect", "FATAL: could not connect to server: Connection refused"),
    ("connect", "ошибка соединения с сервером базы данных, служба не отвечает"),
    ("connect", "connection reset by peer, разрыв соединения при копировании"),
    ("auth", "FATAL: password authentication failed for user postgres"),
    ("auth", "ошибка аутентификации, неверный логин или пароль"),
    ("space", "недостаточно места на диске D, запись файла прервана"),
    ("space", "could not write to file: No space left on device"),
    ("timeout", "timeout expired while waiting for backup stream"),
    ("timeout", "превышено время ожидания потока резервного копирования"),
    ("retention", "срок хранения копии истёк, файл будет удалён"),
    ("retention", "размер копии вырос, политика хранения требует ревизии"),
    ("retention", "копия создана без проверки целостности"),
    ("ok", "резервное копирование завершено, файл создан успешно"),
    ("ok", "полная копия сжата, проверка целостности пройдена"),
]

CAUSES = {
    "connect": {
        "title": "Сервер СУБД недоступен",
        "action": "Проверить службу PostgreSQL/MS SQL, прослушивание порта и сетевую доступность хоста из задания копирования.",
        "priority": "критический",
    },
    "auth": {
        "title": "Ошибка аутентификации",
        "action": "Проверить учётную запись службы резервного копирования и права на каталог назначения.",
        "priority": "высокий",
    },
    "space": {
        "title": "Недостаточно места на диске",
        "action": "Освободить том или перенести каталог копий, пересмотреть срок хранения и сжатие.",
        "priority": "критический",
    },
    "timeout": {
        "title": "Таймаут потока копирования",
        "action": "Проверить блокировки базы, разделить полную копию и журнал, увеличить окно копирования.",
        "priority": "высокий",
    },
    "retention": {
        "title": "Требуется ревизия политики хранения",
        "action": "Пересчитать срок хранения по объёму, включить проверку целостности после каждой копии.",
        "priority": "средний",
    },
    "ok": {
        "title": "Копия создана штатно",
        "action": "Действий не требуется, продолжить наблюдение.",
        "priority": "низкий",
    },
}

MODEL = classify.train(TRAINING)


def jobs():
    return db.fetch_all("select id, base_name, host_code, schedule, retention_days, last_status, last_run, size_mb, rpo_hours from backup_jobs order by id")


def logs(job_id):
    return db.fetch_all("select ts, level, message from backup_logs where job_id = %s order by ts", (job_id,))


def _classify_log(row):
    verdict = classify.predict(MODEL, row["message"])
    return {"ts": row["ts"], "level": row["level"], "message": row["message"], "cause": verdict["label"], "confidence": verdict["confidence"]}


def _severity_counts(rows):
    return {cause: sum(1 for item in rows if item["cause"] == cause and item["level"] != "info") for cause in {row["cause"] for row in rows}}


def _dominant(rows):
    counts = _severity_counts(rows)
    return max(counts, key=counts.get) if counts and max(counts.values()) > 0 else (rows[0]["cause"] if rows else "ok")


def rpo_breach(job, now=None):
    now = now or datetime.now(tz=job["last_run"].tzinfo if job["last_run"] else None)
    return (now - job["last_run"]).total_seconds() / 3600 > job["rpo_hours"] if job["last_run"] else True


def _job(job_id):
    return db.fetch_one("select id, base_name, host_code, schedule, last_status, last_run, size_mb, rpo_hours from backup_jobs where id = %s", (job_id,))


def _pack(job_id):
    rows = [_classify_log(row) for row in logs(job_id)]
    return {"job": _job(job_id), "logs": rows, "cause": _dominant(rows)}


def _summary(pack, detail):
    return narrative.sentence([
        f"База «{pack['job']['base_name']}»: статус {pack['job']['last_status']}, копия {pack['job']['size_mb']} МБ",
        f"разобрано записей журнала: {len(pack['logs'])}",
        f"наиболее вероятная причина — {detail['title'].lower()} (приоритет {detail['priority']})",
        f"рекомендация: {detail['action']}",
        "RPO нарушен" if rpo_breach(pack["job"]) else "RPO соблюдён",
    ])


def _report(pack):
    detail = CAUSES[pack["cause"]]
    return {**pack, "title": detail["title"], "action": detail["action"], "priority": detail["priority"], "breach": rpo_breach(pack["job"]), "summary": _summary(pack, detail)}


def analyze(job_id):
    return _report(_pack(job_id))


def overview():
    rows = jobs()
    return {
        "jobs": rows,
        "kpis": {
            "total": len(rows),
            "ok": sum(1 for row in rows if row["last_status"] == "ok"),
            "fail": sum(1 for row in rows if row["last_status"] == "fail"),
            "size": sum(row["size_mb"] for row in rows),
            "breach": sum(1 for row in rows if rpo_breach(row)),
        },
    }
