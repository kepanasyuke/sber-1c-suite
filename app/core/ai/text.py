"""Текстовые примитивы: токенизация, TF-IDF, косинусная близость."""

from __future__ import annotations

import math
import re
from collections import Counter
from functools import reduce

_WORD = re.compile(r"[0-9a-zA-Zа-яА-ЯёЁ]+")
_STOP_TEXT = """и в во не что он на я с со как а то все она так его но да ты к у же вы за бы по только ее мне
    было вот от меня еще нет о из ему теперь когда даже ну вдруг ли если уже или ни быть был него до
    вас нибудь опять уж вам ведь там потом себя ничего ей может они тут где есть надо ней для мы тебя
    их чем была сам чтоб без будто чего раз тоже себе под будет ж тогда кто этот того потому этого
    какой совсем ним здесь этом один почти мой тем чтобы нее сейчас были куда зачем всех никогда можно
    при наконец два об другой хоть после над больше тот через эти нас про всего них какая много разве
    три эту моя впрочем хорошо свою этой перед иногда лучше чуть том нельзя такой им более всегда
    конечно всю между the and for with that this from are was were has have will not you"""

_STOP = frozenset(_STOP_TEXT.split())


def tokenize(text: str) -> list[str]:
    return [word.lower() for word in _WORD.findall(text or "") if len(word) > 2 and word.lower() not in _STOP]


def counts(tokens: list[str]) -> Counter:
    return Counter(tokens)


_SUFFIX_TEXT = """иями ями ами ими еями ой ей ий ый ой ем ом ам ям ах ях ия ие ые ое ую юю ая яя ою ею ут ют
    ат ят ит ет ешь ишь ла ло ли ть ся сь ов ев ив ост ость ест ние ния ний ция ции ций ск ой а я о е у
    ю ы и й ь"""

_SUFFIXES = sorted(set(_SUFFIX_TEXT.split()), key=len, reverse=True)


def _cut(word):
    return next((word[: -len(suffix)] for suffix in _SUFFIXES if word.endswith(suffix) and len(word) - len(suffix) >= 4), word)


def stem(word):
    return _cut(word) if len(word) > 5 else word


def tokenize_stemmed(value: str) -> list[str]:
    return [stem(token) for token in tokenize(value)]


def _document_frequency(docs):
    return Counter(term for doc in docs for term in set(doc))


def _weight(total, frequencies):
    return {term: math.log((total + 1) / (freq + 0.5)) + 1.0 for term, freq in frequencies.items()}


def inverse_document_frequency(docs):
    return _weight(len(docs), _document_frequency(docs))


def vector(tokens, idf_map):
    return {term: freq * idf_map.get(term, 1.0) for term, freq in Counter(tokens).items()}


def tfidf(docs):
    idf_map = inverse_document_frequency(docs)
    return [vector(doc, idf_map) for doc in docs], idf_map


def _dot(left, right):
    return sum(value * right.get(term, 0.0) for term, value in left.items())


def norm(vec):
    return math.sqrt(_dot(vec, vec)) or 1.0


def cosine(left, right):
    return _dot(left, right) / (norm(left) * norm(right))


def _merge(left, right):
    return {term: left.get(term, 0.0) + right.get(term, 0.0) for term in left.keys() | right.keys()}


def merge_all(vectors):
    return reduce(_merge, vectors, {})


def coverage(query_tokens, doc_tokens):
    query = set(query_tokens)
    return len(query & set(doc_tokens)) / len(query) if query else 0.0
