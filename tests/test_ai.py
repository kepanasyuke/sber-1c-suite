"""Юнит-тесты офлайн-моделей: TF-IDF, классификатор, BM25, аномалии, ИНН."""

from app.core.ai import anomaly, bm25, classify, narrative, text
from app.projects.p8_edo.service import inn_valid


def test_tokenize_drops_stop_words():
    assert "и" not in text.tokenize("склад и номенклатура")


def test_cosine_of_equal_vectors_is_one():
    vec = text.vector(text.tokenize("резервное копирование базы"), {})
    assert round(text.cosine(vec, vec), 6) == 1.0


def test_cosine_of_disjoint_vectors_is_zero():
    assert text.cosine({"склад": 1.0}, {"отпуск": 1.0}) == 0.0


def test_classifier_predicts_invoice():
    model = classify.train([("счёт", "счёт на оплату сумма ндс поставщик"), ("акт", "акт оказанных услуг работы подписан")])
    assert classify.predict(model, "счёт на оплату с ндс")["label"] == "счёт"


def test_classifier_confidence_in_range():
    model = classify.train([("счёт", "счёт на оплату сумма ндс"), ("акт", "акт услуг работы")])
    assert 0.0 <= classify.predict(model, "акт работ")["confidence"] <= 1.0


def test_bm25_prefers_relevant_article():
    docs = [text.tokenize("резервное копирование базы восстановление дампа"), text.tokenize("пароль пользователя доступ учётная запись")]
    assert bm25.rank(text.tokenize("восстановление базы"), docs)[0][1] == 0


def test_anomaly_detects_single_spike():
    assert [item["index"] for item in anomaly.detect([10, 11, 9, 10, 60, 12])] == [4]


def test_anomaly_ignores_flat_series():
    assert anomaly.detect([10, 10, 10, 10]) == []


def test_inn_checksum_accepts_valid():
    assert inn_valid("7707083893")


def test_inn_checksum_rejects_broken():
    assert not inn_valid("7707083894")


def test_inn_checksum_handles_twelve_digits():
    assert inn_valid("500100732259")


def test_plural_forms():
    assert [narrative.plural(n, "файл", "файла", "файлов") for n in (1, 3, 11, 21)] == ["файл", "файла", "файлов", "файл"]


def test_risk_word_thresholds():
    assert [narrative.risk_word(score) for score in (0.1, 0.5, 0.9)] == ["низкий", "средний", "высокий"]
