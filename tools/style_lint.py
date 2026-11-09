"""Линтер корпоративного стиля кода портфеля.

Правила:
  ST001  у функции больше одного выхода (return и while считаются выходами);
  ST002  в теле функции больше двух инструкций;
  ST003  в Python-коде есть while, break или continue;
  ST004  в статических JS-модулях есть while, break или continue.

Запуск:  python tools/style_lint.py [пути...]
Код возврата: 0 — чисто, 1 — есть нарушения.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

MAX_STATEMENTS = 2
MAX_EXITS = 1
BANNED = {ast.While: "while", ast.Break: "break", ast.Continue: "continue"}
NESTED = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)
JS_BANNED = ("while (", "while(", "break;", "continue;")
SKIP_DIRS = {"__pycache__", ".pg", ".venv", "node_modules", ".pytest_cache", ".ruff_cache"}
DEFAULT_TARGETS = ["app", "tools", "tests", "static"]


def _children(node):
    return [child for child in ast.iter_child_nodes(node) if not isinstance(child, NESTED)]


def _flatten(nodes):
    return [node for parent in nodes for node in [parent, *_flatten(_children(parent))]]


def _is_docstring(node):
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(
        node.value.value, str
    )


def body(fn):
    return [stmt for stmt in fn.body if not _is_docstring(stmt)]


def _returns(fn):
    return [node for node in _flatten(fn.body) if isinstance(node, ast.Return)]


def _banned(fn):
    return [node for node in _flatten(fn.body) if isinstance(node, tuple(BANNED))]


def _functions(tree):
    return [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _issue(path, line, code, text):
    return {"file": str(path), "line": line, "code": code, "text": text}


def _exit_rules(path, fn):
    count = len(_returns(fn))
    return [_issue(path, fn.lineno, "ST001", f"{fn.name}: {count} выхода, разрешён один")] if count > MAX_EXITS else []


def _size_rules(path, fn):
    count = len(body(fn))
    return [_issue(path, fn.lineno, "ST002", f"{fn.name}: {count} инструкции в теле, разрешено {MAX_STATEMENTS}")] if count > MAX_STATEMENTS else []


def _banned_rules(path, fn):
    return [_issue(path, node.lineno, "ST003", f"{fn.name}: запрещена конструкция {BANNED[type(node)]}") for node in _banned(fn)]


def check_source(path, source):
    tree = ast.parse(source, filename=str(path))
    return [issue for fn in _functions(tree) for issue in [*_exit_rules(path, fn), *_size_rules(path, fn), *_banned_rules(path, fn)]]


def _is_comment(line):
    return line.strip().startswith(("//", "*", "/*"))


def check_js(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    return [_issue(path, number, "ST004", f"запрещена конструкция {token.strip(' (;')}") for number, line in enumerate(lines, 1) for token in JS_BANNED if token in line and not _is_comment(line)]


def iter_files(targets, suffix):
    return sorted({file for target in targets for file in Path(target).rglob(f"*{suffix}") if not SKIP_DIRS & set(file.parts)})


def existing(targets):
    return [target for target in targets if Path(target).exists()]


def _check_file(path):
    return check_js(path) if path.suffix == ".js" else check_source(path, path.read_text(encoding="utf-8"))


def collect(targets):
    files = iter_files(existing(targets), ".py") + iter_files(existing(targets), ".js")
    return [issue for path in files for issue in _check_file(path)]


def render(issues):
    head = f"style_lint: нарушений {len(issues)} (правила ST001-ST004)"
    return "\n".join([head, *[f"{item['file']}:{item['line']}: {item['code']} {item['text']}" for item in issues]])


def _report(issues):
    print(render(issues))
    return 0 if not issues else 1


def main(argv):
    return _report(collect(argv or DEFAULT_TARGETS))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
