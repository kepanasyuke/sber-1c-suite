"""P3. Аудит прав доступа: роли, права, поиск избыточных и опасных назначений."""

from __future__ import annotations

from app.core import db
from app.core.ai import narrative

IT_WORDS = ("программист", "администратор", "аналитик", "поддержк", "учётные системы")
DUTY = {"accountant": ("Бухгалтерия",), "hr": ("Кадры",), "manager": ("Продажи",), "warehouse": ("Логистика",)}


def users():
    return db.fetch_all("""
        select u.id, u.login, u.full_name, u.position, u.department, u.is_active, u.fired_at,
               coalesce(array_agg(distinct r.code) filter (where r.code is not null), '{}') as roles
        from users u
        left join user_roles ur on ur.user_id = u.id
        left join roles r on r.id = ur.role_id
        group by u.id
        order by u.login
    """)


def rights():
    return db.fetch_all("""
        select r.code as role, r.title, x.object_kind, x.object_name, x.access_level
        from rights x
        join roles r on r.id = x.role_id
        order by r.code, x.object_kind, x.object_name
    """)


def _rights_map(rows):
    return {role: [row for row in rows if row["role"] == role] for role in {row["role"] for row in rows}}


def _profile(user, rights_map):
    return [item for role in user["roles"] for item in rights_map.get(role, [])]


def _is_it(user):
    return any(word in (user["position"] or "").lower() or word in (user["department"] or "").lower() for word in IT_WORDS)


def _rule_fired(user):
    return [] if user["is_active"] else [{"code": "R1", "weight": 0.95, "text": "Уволенный сотрудник сохраняет учётную запись и роли"}]


def _rule_admin(user):
    return [{"code": "R2", "weight": 0.8, "text": f"Полные права администратора у сотрудника не из ИТ: {user['position']}"}] if "admin" in user["roles"] and not _is_it(user) else []


def _rule_admin_extra(user):
    return [{"code": "R3", "weight": 0.45, "text": "Администратор совмещает полный доступ с дополнительными ролями"}] if "admin" in user["roles"] and len(user["roles"]) > 1 else []


def _rule_mismatch(user):
    return [{"code": "R4", "weight": 0.4, "text": f"Роль {role} не соответствует подразделению «{user['department']}»"} for role in user["roles"] if role in DUTY and user["department"] not in DUTY[role]]


def _rule_conducting(profile):
    count = sum(1 for item in profile if "проведение" in item["access_level"])
    return [{"code": "R5", "weight": 0.3, "text": f"Право проведения документов у {count} объектов — проверьте необходимость"}] if count > 2 else []


def _rule_wildcard(profile):
    count = sum(1 for item in profile if item["object_name"] == "*")
    return [{"code": "R6", "weight": 0.25, "text": f"Права на все объекты (шаблон «*») в {count} правилах доступа"}] if count > 1 else []


def _issues(user, profile):
    return [_rule_fired(user), _rule_admin(user), _rule_admin_extra(user), _rule_mismatch(user), _rule_conducting(profile), _rule_wildcard(profile)]


def _score(found):
    return min(1.0, round(sum(item["weight"] for item in found), 2))


def _entry(user, found):
    return {"login": user["login"], "full_name": user["full_name"], "department": user["department"], "position": user["position"], "roles": user["roles"], "active": user["is_active"], "score": _score(found), "level": narrative.risk_word(_score(found)), "issues": found}


def _evaluate(user, rights_map):
    found = [item for group in _issues(user, _profile(user, rights_map)) for item in group]
    return _entry(user, found)


def _matrix(rows):
    return [{"role": role, "title": rows[0]["title"] if rows else role, "rules": len(rows), "wildcards": sum(1 for item in rows if item["object_name"] == "*")} for role, rows in sorted(_rights_map(rows).items())]


def _summarize(risky, total):
    high = [item for item in risky if item["score"] >= 0.7]
    return narrative.sentence([
        f"Проанализировано учётных записей: {total}",
        f"с высоким риском: {len(high)}",
        f"средний балл риска {(sum(item['score'] for item in risky) / len(risky)):.2f}" if risky else "рисков не обнаружено",
        f"первый приоритет: {high[0]['full_name']} — {high[0]['issues'][0]['text'].lower()}" if high else "плановых действий не требуется",
    ])


def _ranked(people, rights_map):
    return sorted([_evaluate(user, rights_map) for user in people], key=lambda item: item["score"], reverse=True)


def _assemble(people, rights_rows, risky):
    return {
        "users": people,
        "rights": rights_rows,
        "matrix": _matrix(rights_rows),
        "risky": risky,
        "kpis": {
            "total": len(people),
            "high": sum(1 for item in risky if item["score"] >= 0.7),
            "fired": sum(1 for item in people if not item["is_active"]),
            "admins": sum(1 for item in people if "admin" in item["roles"]),
            "rules": len(rights_rows),
        },
        "summary": _summarize(risky, len(people)),
    }


def _overview(people, rights_rows):
    return _assemble(people, rights_rows, _ranked(people, _rights_map(rights_rows)))


def overview():
    return _overview(users(), rights())
