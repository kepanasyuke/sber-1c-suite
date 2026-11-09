"""Центроидный классификатор текста на TF-IDF: обучение на разметке, ранжирование классов."""

from __future__ import annotations

from dataclasses import dataclass
from functools import reduce

from app.core.ai.text import cosine, merge_all, tfidf, tokenize_stemmed, vector


def features(value):
    return tokenize_stemmed(value)


@dataclass(frozen=True)
class CentroidModel:
    idf: dict
    centroids: dict
    samples: int


def _labels(samples):
    return sorted({label for label, _ in samples})


def _centroids(samples, vectors):
    return {label: merge_all([vec for (sample_label, _), vec in zip(samples, vectors, strict=True) if sample_label == label]) for label in _labels(samples)}


def train(samples):
    vectors, idf_map = tfidf([features(text) for _, text in samples])
    return CentroidModel(idf=idf_map, centroids=_centroids(samples, vectors), samples=len(samples))


def ranking(model, text):
    probe = vector(features(text), model.idf)
    return sorted(((round(cosine(probe, centroid), 4), label) for label, centroid in model.centroids.items()), reverse=True)


def predict(model, text):
    ranked = ranking(model, text)
    return {"label": ranked[0][1], "confidence": ranked[0][0], "ranking": ranked} if ranked else {"label": None, "confidence": 0.0, "ranking": []}


@dataclass(frozen=True)
class KnnModel:
    idf: dict
    vectors: list
    labels: list
    k: int


def train_knn(samples, k=3):
    vectors, idf_map = tfidf([features(text) for _, text in samples])
    return KnnModel(idf=idf_map, vectors=vectors, labels=[label for label, _ in samples], k=k)


def _tally(totals, neighbour):
    score, label = neighbour
    return {**totals, label: totals.get(label, 0.0) + score}


def _votes(neighbours):
    return reduce(_tally, neighbours, {})


def _normalize(totals):
    limit = sum(totals.values()) or 1e-9
    return sorted(((round(share / limit, 4), label) for label, share in totals.items()), reverse=True)


def _neighbours(model, probe):
    scored = sorted(((round(cosine(probe, vec), 4), label) for vec, label in zip(model.vectors, model.labels, strict=True)), reverse=True)
    return _normalize(_votes(scored[: model.k]))


def ranking_knn(model, text):
    return _neighbours(model, vector(features(text), model.idf))


def predict_knn(model, text):
    ranked = ranking_knn(model, text)
    return {"label": ranked[0][1], "confidence": ranked[0][0], "ranking": ranked} if ranked else {"label": None, "confidence": 0.0, "ranking": []}
