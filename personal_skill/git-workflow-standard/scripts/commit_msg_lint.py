#!/usr/bin/env python3
"""Lint Git commit messages against the Conventional Commits specification.

Usage:
    python commit_msg_lint.py --message "feat(auth): add login"
    python commit_msg_lint.py --file .git/COMMIT_EDITMSG
    python commit_msg_lint.py --range origin/main..HEAD
    python commit_msg_lint.py --stdin < message.txt

Exit codes:
    0  every checked message is valid
    1  at least one message has errors
    2  usage, I/O, or git error
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_TYPES = (
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
)

HEADER_RE = re.compile(
    r"^(?P<type>[^\s():!]+)"
    r"(?:\((?P<scope>[^()\s]+)\))?"
    r"(?P<breaking>!)?"
    r": (?P<description>.*)$"
)
SCOPE_RE = re.compile(r"^[a-z0-9][a-z0-9._/-]*$")
BREAKING_FOOTER_RE = re.compile(r"^BREAKING[ -]CHANGE:(?P<value>.*)$")
FOOTER_RE = re.compile(r"^(?P<token>[A-Za-z][A-Za-z0-9-]*(?:[ ][A-Za-z][A-Za-z0-9-]*)?):(?P<rest>.*)$")
SCISSORS = "------------------------ >8 ------------------------"
FIXUP_RE = re.compile(r"^(?:fixup|squash|amend)! ")


@dataclass
class Options:
    types: tuple[str, ...] = DEFAULT_TYPES
    max_header: int = 72
    max_body: int = 72
    allow_merge: bool = True
    allow_fixup: bool = True
    allow_git_revert: bool = False
    strict: bool = False


@dataclass
class Result:
    header: str = ""
    sha: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors


def strip_comments(text: str) -> list[str]:
    """Drop Git comment lines and everything after the verbose scissors line."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("\ufeff"):
        text = text[1:]
    lines: list[str] = []
    for line in text.split("\n"):
        if line.startswith("#"):
            if SCISSORS in line:
                break
            continue
        lines.append(line)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def footer_block_start(lines: list[str]) -> int | None:
    """Return the index where a trailing footer block starts, if there is one."""
    if not lines:
        return None
    start = 0
    for index, line in enumerate(lines):
        if not line.strip():
            start = index + 1
    block = lines[start:]
    if not block or not block[0].strip():
        return None
    has_footer = False
    for line in block:
        if not line.strip():
            return None
        if line[0] in (" ", "\t"):
            if not has_footer:
                return None
            continue
        match = FOOTER_RE.match(line)
        if not match:
            return None
        has_footer = True
    return start if has_footer else None


def lint_message(text: str, options: Options) -> Result:
    result = Result()
    lines = strip_comments(text)
    if not lines:
        result.errors.append("commit message is empty")
        return result

    header = lines[0]
    result.header = header.strip()
    if not result.header:
        result.errors.append("header must not be empty")
        return result
    if header != header.rstrip():
        result.warnings.append("header has trailing whitespace")
    if header != header.lstrip():
        result.errors.append("header must not start with whitespace")
    header = header.strip()
    if "\t" in header:
        result.errors.append("header must not contain tabs")

    if re.fullmatch(r"[^\s():!]+(?:\([^()\s]+\))?!?: *", header):
        result.errors.append("description must not be empty")
        return result

    if header.startswith("Merge "):
        if options.allow_merge:
            return result
        result.errors.append(
            "merge commits are not allowed here; squash the branch and use a Conventional Commits subject"
        )
        return result

    if FIXUP_RE.match(header):
        if options.allow_fixup and not options.strict:
            result.warnings.append("temporary fixup commit; consolidate before merging")
            return result
        result.errors.append("fixup/squash/amend commits are not allowed; consolidate before merging")
        return result

    if header.startswith('Revert "'):
        if options.allow_git_revert:
            return result
        result.errors.append(
            "Git's default revert subject is not Conventional Commits; "
            "rewrite it as 'revert: <subject>' (use 'git revert --edit')"
        )
        return result

    match = HEADER_RE.match(header)
    if not match:
        result.errors.append(
            "header must match '<type>(<scope>)!: <description>', for example 'feat(auth): add login'"
        )
        return result

    commit_type = match.group("type")
    scope = match.group("scope")
    description = match.group("description")

    if commit_type != commit_type.lower():
        result.errors.append(f"type '{commit_type}' must be lowercase")
    if commit_type not in options.types:
        result.errors.append(
            f"unknown type '{commit_type}'; use one of {', '.join(options.types)}"
        )
    if scope is not None and not SCOPE_RE.match(scope):
        result.errors.append(
            f"scope '{scope}' must be lowercase and contain only letters, digits, '.', '_', '/' or '-'"
        )
    if not description:
        result.errors.append("description must not be empty")
    else:
        if description != description.strip():
            result.errors.append("description must not have leading or trailing whitespace")
        if description.endswith((".", "。")):
            result.errors.append("description must not end with a period")
        first = description[0]
        if first.isascii() and first.isupper():
            result.errors.append("description must not start with an uppercase letter")
    if len(header) > options.max_header:
        result.errors.append(
            f"header is {len(header)} characters; limit is {options.max_header}"
        )

    body_lines = lines[1:]
    if body_lines:
        if body_lines[0].strip():
            result.errors.append("body must be separated from the header by a blank line")
        else:
            body_lines = body_lines[1:]
    if body_lines and not body_lines[0].strip():
        result.warnings.append("multiple blank lines after the header")
    while body_lines and not body_lines[0].strip():
        body_lines = body_lines[1:]

    start = footer_block_start(body_lines)
    footer_lines = body_lines[start:] if start is not None else []
    body = body_lines[:start] if start is not None else body_lines

    breaking_from_footer = False
    for line in footer_lines:
        if line[0] in (" ", "\t"):
            continue
        footer = FOOTER_RE.match(line)
        if not footer:
            continue
        token = footer.group("token")
        rest = footer.group("rest")
        if " " in token and token not in ("BREAKING CHANGE",):
            result.errors.append(
                f"footer token '{token}' must use '-' instead of spaces"
            )
        if not rest.strip():
            result.errors.append(f"footer '{token}:' must have a value")
        if BREAKING_FOOTER_RE.match(line):
            breaking_from_footer = True
            if not BREAKING_FOOTER_RE.match(line).group("value").strip():
                result.errors.append("BREAKING CHANGE footer must describe the impact")
    if match.group("breaking") and not breaking_from_footer:
        result.warnings.append(
            "breaking change uses '!' but has no 'BREAKING CHANGE:' footer explaining migration"
        )

    for index, line in enumerate(body, start=0):
        if line != line.rstrip():
            result.warnings.append(f"body line {index + 2} has trailing whitespace")
        if len(line) > options.max_body:
            result.warnings.append(
                f"body line {index + 2} is {len(line)} characters; recommended limit is {options.max_body}"
            )

    if options.strict and result.warnings:
        result.errors.extend(result.warnings)
        result.warnings = []
    return result


def read_range(repo: str, rev_range: str) -> list[tuple[str, str]]:
    command = [
        "git",
        "-C",
        repo,
        "log",
        "--no-decorate",
        "--format=%H%x1f%B%x1e",
        rev_range,
    ]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
    except OSError as error:
        raise RuntimeError(f"failed to run git: {error}") from error
    if completed.returncode != 0:
        message = completed.stderr.strip() or "git log failed"
        raise RuntimeError(message)
    messages: list[tuple[str, str]] = []
    for record in completed.stdout.split("\x1e"):
        record = record.strip("\n")
        if not record.strip():
            continue
        if "\x1f" not in record:
            continue
        sha, message = record.split("\x1f", 1)
        messages.append((sha.strip(), message))
    return messages


def shorten(header: str, width: int = 100) -> str:
    return header if len(header) <= width else header[: width - 3] + "..."


def print_human(results: list[Result], quiet: bool) -> None:
    for result in results:
        if result.valid:
            if not quiet:
                label = result.sha[:8] if result.sha else "-"
                print(f"OK   {label}  {shorten(result.header)}")
                for warning in result.warnings:
                    print(f"  warning: {warning}")
            continue
        label = result.sha[:8] if result.sha else "-"
        print(f"FAIL {label}  {shorten(result.header)}")
        for error in result.errors:
            print(f"  error: {error}")
        for warning in result.warnings:
            print(f"  warning: {warning}")

    invalid = sum(1 for result in results if not result.valid)
    if invalid:
        print(f"\nFAILED: {invalid} of {len(results)} commit message(s) invalid.")
    elif not quiet:
        print(f"\nOK: {len(results)} commit message(s) valid.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lint commit messages against Conventional Commits.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--message", metavar="TEXT", help="lint a single message")
    source.add_argument("--file", metavar="PATH", help="lint a commit message file")
    source.add_argument("--range", dest="rev_range", metavar="REV", help="lint a git revision range")
    source.add_argument("--stdin", action="store_true", help="read the message from stdin")
    parser.add_argument(
        "--types",
        default=",".join(DEFAULT_TYPES),
        help="comma-separated allowed types",
    )
    parser.add_argument("--max-header", type=int, default=72, help="maximum header length")
    parser.add_argument("--max-body", type=int, default=72, help="recommended body line length")
    parser.add_argument("--no-merge", action="store_true", help="reject merge commits")
    parser.add_argument("--no-fixup", action="store_true", help="reject fixup!/squash!/amend! commits")
    parser.add_argument(
        "--allow-git-revert",
        action="store_true",
        help='accept Git\'s default Revert "<subject>" message',
    )
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--repo", default=".", help="repository used by --range")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument("--quiet", action="store_true", help="suppress success output")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    types = tuple(item.strip() for item in args.types.split(",") if item.strip())
    if not types:
        parser.error("--types must contain at least one type")

    options = Options(
        types=types,
        max_header=args.max_header,
        max_body=args.max_body,
        allow_merge=not args.no_merge,
        allow_fixup=not args.no_fixup,
        allow_git_revert=args.allow_git_revert,
        strict=args.strict,
    )

    results: list[Result] = []
    try:
        if args.message is not None:
            results.append(lint_message(args.message, options))
        elif args.file is not None:
            text = Path(args.file).read_text(encoding="utf-8", errors="replace")
            results.append(lint_message(text, options))
        elif args.stdin:
            results.append(lint_message(sys.stdin.read(), options))
        else:
            for sha, message in read_range(args.repo, args.rev_range):
                result = lint_message(message, options)
                result.sha = sha
                results.append(result)
    except (OSError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.json:
        payload = {
            "valid": all(result.valid for result in results),
            "checked": len(results),
            "results": [
                {
                    "sha": result.sha,
                    "header": result.header,
                    "valid": result.valid,
                    "errors": result.errors,
                    "warnings": result.warnings,
                }
                for result in results
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_human(results, args.quiet)
    return 0 if all(result.valid for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
