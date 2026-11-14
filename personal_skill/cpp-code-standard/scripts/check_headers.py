#!/usr/bin/env python3
"""Check file documentation, include guards and common C/C++ declarations.

--strict checks adjacent Doxygen @brief comments on recognizable function
signatures. This is lexical checking, not an AST/preprocessor or full doc audit.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx"}
HEADER_SUFFIXES = {".h", ".hh", ".hpp", ".hxx"}
ALL_SUFFIXES = SOURCE_SUFFIXES | HEADER_SUFFIXES
TOKENS = re.compile(
    r'//[^\n]*|/\*.*?\*/|R"(?P<raw>[^\s()\\]{0,16})\(.*?\)(?P=raw)"'
    r'|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', re.DOTALL,
)
CALLABLE = re.compile(r'(?P<name>~?[A-Za-z_]\w*|operator\s*[^\s(]+)\s*\(')
NON_FUNCTIONS = {"if", "while", "for", "switch", "catch", "sizeof", "alignof",
                 "alignas", "decltype", "noexcept", "static_assert", "requires"}


def blank(match):
    return re.sub(r"[^\n]", " ", match.group(0))


def lex(text):
    docs = [m for m in TOKENS.finditer(text) if m.group().startswith("/**")]
    return TOKENS.sub(blank, text), docs


def iter_files(paths):
    files = set()
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files.update(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in ALL_SUFFIXES)
        elif path.is_file() and path.suffix.lower() in ALL_SUFFIXES:
            files.add(path)
        elif not path.exists():
            raise FileNotFoundError(f"{raw}: no such file or directory")
        else:
            raise ValueError(f"{raw}: not a supported C/C++ source file")
    return sorted(files)


def has_guard(code):
    if re.search(r"^\s*#\s*pragma\s+once\b", code, re.MULTILINE):
        return True
    match = re.match(r"\s*#\s*ifndef\s+(\w+)\s*\n\s*#\s*define\s+\1\b[^\n]*", code)
    if not match:
        return False
    depth = 0
    directives = list(re.finditer(r"^\s*#\s*(if|ifdef|ifndef|endif)\b[^\n]*", code, re.MULTILINE))
    for directive in directives:
        depth += -1 if directive.group(1) == "endif" else 1
        if depth == 0:
            return not code[directive.end():].strip()
        if depth < 0:
            return False
    return False


def function_name(segment, original):
    if re.match(r"\s*(using|typedef|static_assert)\b", segment):
        return None
    for match in CALLABLE.finditer(segment):
        name = match.group("name")
        prefix = segment[:match.start()]
        if name in NON_FUNCTIONS or prefix.count("(") != prefix.count(")"):
            continue
        if "=" in prefix or "[" in prefix.replace("[[", "").replace("]]", ""):
            continue
        after = original[match.end():].lstrip()
        if after and (after[0].isdigit() or after[0] in "\"'"):
            continue  # direct initialization, not a function parameter list
        return name
    return None


def declaration_problems(text, code, docs):
    # Ignore preprocessing lines and access labels, preserving all offsets.
    code = re.sub(r"^[ \t]*#[^\n]*(?:\\\n[^\n]*)*", blank, code, flags=re.MULTILINE)
    code = re.sub(r"\b(?:public|private|protected)\s*:", blank, code)
    problems = []
    scopes = []
    start = 0
    parens = 0
    for offset, char in enumerate(code):
        if char == "(":
            parens += 1
        elif char == ")":
            parens -= 1
        elif char in ";{}" and parens == 0:
            segment = code[start:offset]
            inside_function = any(scopes)
            name = None if inside_function or char == "}" else function_name(segment, text[start:offset])
            if name:
                first = start + len(segment) - len(segment.lstrip())
                previous = next((d for d in reversed(docs) if d.end() <= first), None)
                documented = (previous is not None and not text[previous.end():first].strip()
                              and re.search(r"@brief\b", previous.group())
                              and not re.search(r"@file\b", previous.group()))
                if not documented:
                    line = text.count("\n", 0, first) + 1
                    problems.append((line, "DOC003", f"function {name} has no adjacent Doxygen @brief"))
            if char == "{":
                scopes.append(inside_function or name is not None)
            elif char == "}" and scopes:
                scopes.pop()
            start = offset + 1
    return problems


def check_file(path: Path, strict: bool):
    text = path.read_text(encoding="utf-8-sig")
    code, docs = lex(text)
    problems = []
    first_doc = docs[0] if docs and not text[:docs[0].start()].strip() else None
    header = first_doc.group() if first_doc else ""
    for tag, rule in (("file", "DOC001"), ("brief", "DOC002")):
        if not re.search(r"@" + tag + r"\b", header):
            problems.append((1, rule, f"missing Doxygen @{tag} in the leading file comment"))
    if path.suffix.lower() in HEADER_SUFFIXES:
        if not has_guard(code):
            problems.append((1, "HDR001", "header needs #pragma once or a matching enclosing include guard"))
        for match in re.finditer(r"\busing\s+namespace\b", code):
            problems.append((text.count("\n", 0, match.start()) + 1, "NS001", "using namespace in a header"))
        if strict:
            problems.extend(declaration_problems(text, code, docs))
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", default=["."])
    parser.add_argument("--strict", action="store_true", help="Check adjacent comments on common function signatures")
    args = parser.parse_args(argv)
    try:
        files = iter_files(args.paths)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    if not files:
        print("No C/C++ files found.", file=sys.stderr)
        return 1
    total = 0
    io_failed = False
    for path in files:
        try:
            problems = check_file(path, args.strict)
        except (OSError, UnicodeError) as error:
            print(f"{path}: cannot inspect: {error}", file=sys.stderr)
            io_failed = True
            continue
        for line, rule, message in problems:
            print(f"{path}:{line}: {rule} {message}")
        total += len(problems)
    print(f"Checked {len(files)} file(s); {total} problem(s).", file=sys.stderr)
    return 2 if io_failed else (1 if total else 0)


if __name__ == "__main__":
    raise SystemExit(main())
