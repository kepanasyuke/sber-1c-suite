"""P8. Документооборот: классификация документов, реквизиты, контроль ИНН, поиск дублей."""

from __future__ import annotations

import re

from app.core import db
from app.core.ai import classify, narrative, text

TRAIN = [
    ("счёт", "Счёт на оплату № 2145, сумма 148000 руб, НДС 20%, поставщик, оплатить в течение 5 дней"),
    ("счёт", "Счёт на оплату лицензий 1С, сумма, в том числе НДС, покупатель, реквизиты для оплаты"),
    ("счёт", "Счёт на оплату ремонта оборудования, счёт действителен 10 дней, оплата по реквизитам"),
    ("акт", "Акт оказанных услуг по договору, стоимость работ, НДС не облагается, подписан сторонами"),
    ("акт", "Акт сверки взаимных расчётов, сальдо на конец периода, задолженность контрагента"),
    ("акт", "Акт выполненных работ, объём работ, претензий нет, подписи сторон"),
    ("договор", "Договор поставки оборудования, предмет договора, сроки поставки, штрафные санкции"),
    ("договор", "Договор оказания услуг, стороны заключили договор, приложения, реквизиты сторон"),
    ("договор", "Договор аренды помещения, срок аренды, арендная плата, обеспечительный платёж"),
    ("накладная", "Товарная накладная, грузоотправитель, грузополучатель, товар, количество, сумма"),
    ("накладная", "Транспортная накладная, перевозчик, груз, вес, сопроводительные документы"),
    ("накладная", "Расходная накладная на отпуск товара со склада, единицы измерения, цена"),
    ("записка", "Служебная записка, согласование скидки, руководитель отдела просит рассмотреть"),
    ("записка", "Заявка на закупку канцелярии, обоснование необходимости, подпись начальника"),
]

MODEL = classify.train(TRAIN)

_INN = re.compile(r"ИНН\s*(\d{10}|\d{12})")
_AMOUNT = re.compile(r"([\d\s]{4,})[,.](\d{2})\s*руб")
_PARTY = re.compile(r"(?:Поставщик|Исполнитель|Грузоотправитель|Грузополучатель|Получатель|Покупатель):?\s*(ООО|ПАО|АО|ЗАО|ИП)\s*«([^»]+)»")
_W10 = (2, 4, 10, 3, 5, 9, 4, 6, 8)
_W11 = (7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
_W12 = (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8)


def _control(digits, weights):
    return sum(int(digit) * weight for digit, weight in zip(digits, weights, strict=True)) % 11 % 10


def inn_valid(value):
    digits = re.sub(r"\D", "", value or "")
    return _control(digits[:9], _W10) == int(digits[9]) if len(digits) == 10 else (_control(digits[:10], _W11) == int(digits[10]) and _control(digits[:11], _W12) == int(digits[11])) if len(digits) == 12 else False


def _amount(body):
    found = _AMOUNT.search(body or "")
    return round(float(f"{found.group(1).replace(' ', '')}.{found.group(2)}"), 2) if found else None


def _build(inn, party, amount):
    return {
        "inn": inn.group(1) if inn else "",
        "inn_valid": inn_valid(inn.group(1) if inn else ""),
        "counterparty": f"{party.group(1)} «{party.group(2)}»" if party else "",
        "amount": amount,
    }


def requisites(body):
    return _build(_INN.search(body or ""), _PARTY.search(body or ""), _amount(body))


def documents():
    return db.fetch_all("select id, file_name, body, received_at, doc_type, counterparty, inn, amount from documents order by id")


def _classify(row):
    verdict = classify.predict(MODEL, f"{row['file_name']} {row['body']}")
    return {**row, "predicted": verdict["label"], "confidence": verdict["confidence"], "requisites": requisites(row["body"])}


def _duplicates(rows):
    vectors, _ = text.tfidf([text.tokenize(row["body"]) for row in rows])
    return [{"a": rows[left]["file_name"], "b": rows[right]["file_name"], "score": round(text.cosine(vectors[left], vectors[right]), 3)} for left in range(len(rows)) for right in range(left + 1, len(rows)) if text.cosine(vectors[left], vectors[right]) >= 0.55]


def _counts(rows):
    return {label: sum(1 for row in rows if row["predicted"] == label) for label in sorted({row["predicted"] for row in rows})}


def _summary(rows, duplicates):
    bad = [row for row in rows if row["requisites"]["inn"] and not row["requisites"]["inn_valid"]]
    return narrative.sentence([
        f"Обработано документов: {len(rows)}",
        f"распознано типов: {len(_counts(rows))}",
        f"найдено дублей: {len(duplicates)}" if duplicates else "дублей не найдено",
        f"документов с недостоверным ИНН: {len(bad)}" + (f" — {', '.join(row['file_name'] for row in bad)}" if bad else ""),
    ])


def _pack(rows):
    return [_classify(row) for row in rows], _duplicates(rows)


def _overview(rows):
    classified, duplicates = _pack(rows)
    return {
        "documents": classified,
        "duplicates": duplicates,
        "counts": _counts(classified),
        "kpis": {
            "total": len(classified),
            "bad_inn": sum(1 for row in classified if row["requisites"]["inn"] and not row["requisites"]["inn_valid"]),
            "duplicates": len(duplicates),
            "average": round(sum(row["confidence"] for row in classified) / max(1, len(classified)), 3),
        },
        "summary": _summary(classified, duplicates),
    }


def overview():
    return _overview(documents())
