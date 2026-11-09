"""BM25: ранжирование статей базы знаний под текст обращения."""

from __future__ import annotations

import math
from collections import Counter


def _document_counts(docs):
    return Counter(term for doc in docs for term in set(doc))


def _idf_map(total, frequencies, terms):
    return {term: math.log(1 + (total - frequencies[term] + 0.5) / (frequencies[term] + 0.5)) for term in terms}


def _idf(docs, terms):
    return _idf_map(len(docs), _document_counts(docs), terms)


def stats(docs):
    terms = {term for doc in docs for term in doc}
    return {"idf": _idf(docs, terms), "avgdl": (sum(map(len, docs)) / len(docs)) if docs else 1.0}


def _weigh(query, frequencies, length, model, k1, b):
    return sum(model["idf"].get(term, 0.0) * frequencies[term] * (k1 + 1) / (frequencies[term] + k1 * (1 - b + b * length / model["avgdl"])) for term in query)


def score(query, doc, model, k1=1.5, b=0.75):
    return _weigh(query, Counter(doc), len(doc) or 1, model, k1, b)


def rank(query, docs):
    model = stats(docs)
    return sorted(((round(score(query, doc, model), 4), index) for index, doc in enumerate(docs)), reverse=True)
