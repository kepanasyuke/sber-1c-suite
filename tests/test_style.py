"""Правила стиля проверяются тестом: нарушение роняет сборку."""

from tools.style_lint import collect

TARGETS = ["app", "tools", "tests", "static"]


def test_style_rules_pass():
    assert collect(TARGETS) == []
