#!/usr/bin/env python3
"""Lightweight checker for the python-code-standard skill.

Checks syntax, missing type annotations, bare excepts, mutable default
arguments, wildcard imports, and (with --strict) missing docstrings on
public modules, classes, and functions. This is not a replacement for
mypy, ruff, or pytest.

Usage:
    python check_python.py [paths...] [--strict]
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

MUTABLE_CALLS = {"list", "dict", "set", "bytearray"}


class Checker(ast.NodeVisitor):
    def __init__(self, path: Path, strict: bool) -> None:
        self.path = path
        self.strict = strict
        self.problems: list[tuple[int, int, str, str]] = []

    def add(self, node: ast.AST, rule: str, message: str) -> None:
        line = getattr(node, "lineno", 0)
        col = getattr(node, "col_offset", 0)
        self.problems.append((line, col, rule, message))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        args = [*node.args.posonlyargs, *node.args.args]
        for arg in args:
            if arg.arg in {"self", "cls"}:
                continue
            if arg.annotation is None:
                self.add(arg, "ANN001", f"missing type annotation for '{arg.arg}'")
        if node.args.vararg and node.args.vararg.annotation is None:
            self.add(node.args.vararg, "ANN001", f"missing type annotation for '*{node.args.vararg.arg}'")
        if node.args.kwarg and node.args.kwarg.annotation is None:
            self.add(node.args.kwarg, "ANN001", f"missing type annotation for '**{node.args.kwarg.arg}'")
        if node.returns is None:
            self.add(node, "ANN201", f"missing return annotation for '{node.name}'")

        for default in [*node.args.defaults, *node.args.kw_defaults]:
            if default is None:
                continue
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.add(default, "B006", f"mutable default argument in '{node.name}'")
            elif isinstance(default, ast.Call) and isinstance(default.func, ast.Name):
                if default.func.id in MUTABLE_CALLS:
                    self.add(default, "B006", f"mutable default argument in '{node.name}'")

        if self.strict and not node.name.startswith("_") and ast.get_docstring(node) is None:
            self.add(node, "D103", f"public function '{node.name}' is missing a docstring")

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if self.strict and not node.name.startswith("_") and ast.get_docstring(node) is None:
            self.add(node, "D101", f"public class '{node.name}' is missing a docstring")
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is None:
            self.add(node, "E722", "bare except")
        elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
            self.add(node.type, "BLE001", "catching broad 'Exception'")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name == "*":
                self.add(node, "F403", "wildcard import")
        self.generic_visit(node)


def iter_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.py")))
            files.extend(sorted(path.rglob("*.pyi")))
        elif path.is_file():
            files.append(path)
        else:
            print(f"{raw}: no such file or directory", file=sys.stderr)
    return [f for f in files if "__pycache__" not in f.parts]


def check_file(path: Path, strict: bool) -> list[tuple[int, int, str, str]]:
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [(0, 0, "E000", "file is not valid UTF-8")]
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [(exc.lineno or 0, exc.offset or 0, "E999", exc.msg)]

    problems: list[tuple[int, int, str, str]] = []
    if strict and ast.get_docstring(tree) is None:
        problems.append((1, 0, "D100", "module is missing a docstring"))
    checker = Checker(path, strict)
    checker.visit(tree)
    problems.extend(checker.problems)
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Python code against python-code-standard.")
    parser.add_argument("paths", nargs="*", default=["."], help="Files or directories (default: .)")
    parser.add_argument("--strict", action="store_true", help="Also check public docstrings")
    args = parser.parse_args()

    files = iter_files(args.paths)
    if not files:
        print("No Python files found.", file=sys.stderr)
        return 1

    total = 0
    failed = 0
    for path in files:
        problems = check_file(path, args.strict)
        if not problems:
            continue
        failed += 1
        for line, col, rule, message in problems:
            print(f"{path}:{line}:{col}: {rule} {message}")
            total += 1

    print(f"\nChecked {len(files)} file(s); {total} problem(s) in {failed} file(s).", file=sys.stderr)
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
