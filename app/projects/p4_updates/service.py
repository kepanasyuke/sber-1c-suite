"""P4. Обновления типовых конфигураций: версии, состав объектов, diff и чек-лист."""

from __future__ import annotations

from app.core import db
from app.core.ai import narrative

KIND_WEIGHTS = {"Роль": 0.3, "Документ": 0.25, "Регистр": 0.3, "Справочник": 0.15, "Отчёт": 0.1}

CHECKLIST = (
    "Сделать резервную копию информационной базы и проверить восстановление на тестовом контуре.",
    "Проверить, что расширения и внешние отчёты не перекрывают изменённые объекты.",
    "Обновить типовую конфигурацию в монопольном режиме, затем обновить расширения.",
    "Выполнить обновление конфигурации базы данных с проверкой структуры.",
    "Прогнать регламентные задания и обмены, сверить контрольные отчёты за период.",
)


def configs():
    return db.fetch_all("select config_name, count(*) as versions from conf_versions group by config_name order by config_name")


def versions(config_name):
    return db.fetch_all("select id, version, released_at, objects_total, extended from conf_versions where config_name = %s order by released_at", (config_name,))


def _version_id(config_name, version):
    return db.scalar("select id from conf_versions where config_name = %s and version = %s", (config_name, version))


def _objects(version_id):
    return {row["name"]: row for row in db.fetch_all("select kind, name, checksum from conf_objects where version_id = %s", (version_id,))}


def _objects_of(config_name, version):
    return _objects(_version_id(config_name, version))


def diff_objects(old, new):
    return {
        "added": [new[name] for name in new.keys() - old.keys()],
        "removed": [old[name] for name in old.keys() - new.keys()],
        "changed": [new[name] for name in new.keys() & old.keys() if new[name]["checksum"] != old[name]["checksum"]],
    }


def risk_of(changes):
    weight = sum(KIND_WEIGHTS.get(item["kind"], 0.1) for group in changes.values() for item in group)
    return min(1.0, round(weight, 2))


def checklist(changes, risk):
    extra = ["Согласовать окно обновления с пользователями: риск высокий, нужен откат по плану."] if risk >= 0.7 else []
    return [*CHECKLIST, *extra]


def summary(config_name, old_version, new_version, changes, risk):
    return narrative.sentence([
        f"{config_name}: переход {old_version} → {new_version}",
        f"новых объектов {len(changes['added'])}, удалённых {len(changes['removed'])}, изменённых {len(changes['changed'])}",
        f"оценка риска {risk} ({narrative.risk_word(risk)})",
        "обновление затрагивает роли — проверьте права доступа" if any(item["kind"] == "Роль" for group in changes.values() for item in group) else "изменений ролей нет",
    ])


def _report(config_name, old_version, new_version, changes):
    risk = risk_of(changes)
    return {
        "config": config_name,
        "old": old_version,
        "new": new_version,
        "changes": changes,
        "risk": risk,
        "level": narrative.risk_word(risk),
        "checklist": checklist(changes, risk),
        "summary": summary(config_name, old_version, new_version, changes, risk),
    }


def _compare(config_name, old_version, new_version):
    return _report(config_name, old_version, new_version, diff_objects(_objects_of(config_name, old_version), _objects_of(config_name, new_version)))


def compare(config_name, old_version, new_version):
    return _compare(config_name, old_version, new_version)


def default_config():
    items = configs()
    return items[0]["config_name"] if items else ""


def _overview(items):
    first = items[0]["config_name"] if items else ""
    return {"configs": items, "current": first, "versions": versions(first) if first else []}


def overview():
    return _overview(configs())


def default_pair(config_name):
    rows = versions(config_name)
    return (rows[-2]["version"], rows[-1]["version"]) if len(rows) > 1 else (rows[0]["version"], rows[0]["version"]) if rows else ("", "")
