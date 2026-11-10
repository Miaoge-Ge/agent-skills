#!/usr/bin/env python3
"""Guard the Git index and branch name before committing.

Checks staged files for secret-like filenames, private keys and tokens,
oversized blobs, conflict markers, and whitespace errors. Also validates
branch names and warns about commits on protected branches.

Usage:
    python git_guard.py --staged
    python git_guard.py --staged --json
    python git_guard.py --branch feat/oauth-device-flow
    python git_guard.py --staged --protect-main

Exit codes:
    0  no blocking errors
    1  at least one blocking error
    2  usage or git error
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_MAX_SIZE_MB = 5
SCAN_LIMIT = 2 * 1024 * 1024
IGNORE_MARKER = "git-guard:ignore"

BRANCH_RE = re.compile(
    r"^(?:feat|fix|docs|refactor|perf|test|build|ci|chore|revert|release|hotfix)/"
    r"[a-z0-9][a-z0-9._-]*$"
)
PROTECTED_BRANCHES = {"main", "master", "develop", "trunk"}
PROTECTED_PREFIXES = ("release/",)
ALLOWED_ENV_FILES = {
    ".env.example",
    ".env.sample",
    ".env.template",
    ".env.dist",
    ".env.test.example",
}
SECRET_FILE_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*.keystore",
    "*.jks",
)
SECRET_FILE_NAMES = {
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
}
PLACEHOLDER_RE = re.compile(
    r"(?i)^(?:x{3,}|\*{3,}|\.{3,}|<[^>]*>|\$\{[^}]*\}"
    r"|changeme|change_me|example|sample|dummy|test|placeholder|redacted"
    r"|none|null|your[-_].*)$"
)
GENERIC_RE = re.compile(
    r"""(?ix)
    \b(password|passwd|pwd|secret|token|api[_-]?key|apikey|access[_-]?key|client[_-]?secret)\b
    \s*[:=]\s*
    (['"])(?P<value>[^'"]{8,})\2
    """
)

SECRET_PATTERNS = (
    (
        "private-key",
        "error",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
        "private key material",
    ),
    (
        "aws-access-key",
        "error",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "AWS access key ID",
    ),
    (
        "github-token",
        "error",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b"),
        "GitHub token",
    ),
    (
        "slack-token",
        "error",
        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
        "Slack token",
    ),
    (
        "slack-webhook",
        "error",
        re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/_-]{20,}"),
        "Slack webhook URL",
    ),
    (
        "stripe-secret",
        "error",
        re.compile(r"\bsk_live_[0-9A-Za-z]{16,}\b"),
        "Stripe live secret key",
    ),
    (
        "openai-key",
        "error",
        re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b"),
        "OpenAI-style secret key",
    ),
    (
        "google-api-key",
        "error",
        re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
        "Google API key",
    ),
    (
        "npm-token",
        "error",
        re.compile(r"\bnpm_[A-Za-z0-9]{36}\b"),
        "npm token",
    ),
    (
        "jwt",
        "warning",
        re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
        "JSON Web Token",
    ),
)


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    path: str | None = None
    line: int | None = None


def run_git(repo: str, *args: str, text: bool = True) -> subprocess.CompletedProcess:
    command = ["git", "-C", repo, *args]
    return subprocess.run(
        command,
        capture_output=True,
        text=text,
        encoding="utf-8" if text else None,
        errors="replace" if text else None,
    )


def git_output(repo: str, *args: str) -> str:
    completed = run_git(repo, *args)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git command failed")
    return completed.stdout


def repo_root(repo: str) -> str:
    return git_output(repo, "rev-parse", "--show-toplevel").strip()


def normalize(path: str) -> str:
    return path.replace("\\", "/")


def path_is_allowed(path: str, allow_paths: list[str]) -> bool:
    normalized = normalize(path)
    for pattern in allow_paths:
        normalized_pattern = normalize(pattern)
        if fnmatch.fnmatch(normalized, normalized_pattern):
            return True
        if fnmatch.fnmatch(Path(normalized).name, normalized_pattern):
            return True
    return False


def staged_paths(repo: str) -> list[str]:
    output = git_output(repo, "diff", "--cached", "--name-status", "-z", "--diff-filter=ACMR")
    tokens = output.split("\0")
    paths: list[str] = []
    index = 0
    while index < len(tokens):
        status = tokens[index]
        index += 1
        if not status:
            continue
        if status[0] in ("R", "C"):
            if index + 1 >= len(tokens):
                break
            index += 1  # old path
            new_path = tokens[index]
            index += 1
            paths.append(new_path)
        else:
            paths.append(tokens[index])
            index += 1
    return [path for path in paths if path]


def index_entry(repo: str, path: str) -> tuple[str, int]:
    output = git_output(repo, "ls-files", "-s", "-z", "--", path)
    for entry in output.split("\0"):
        if not entry:
            continue
        meta, _, entry_path = entry.partition("\t")
        if normalize(entry_path) != normalize(path):
            continue
        fields = meta.split()
        if len(fields) >= 2:
            blob = fields[1]
            size = int(git_output(repo, "cat-file", "-s", blob).strip())
            return blob, size
    raise RuntimeError(f"could not read staged entry for {path}")


def staged_bytes(repo: str, path: str) -> bytes:
    completed = run_git(repo, "cat-file", "blob", f":{path}", text=False)
    if completed.returncode != 0:
        return b""
    return completed.stdout or b""


def is_secret_filename(path: str) -> bool:
    name = Path(normalize(path)).name.lower()
    if name in ALLOWED_ENV_FILES:
        return False
    if name in SECRET_FILE_NAMES:
        return True
    for pattern in SECRET_FILE_PATTERNS:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def scan_text(
    repo: str,
    path: str,
    content: bytes,
    allow_paths: list[str],
) -> list[Finding]:
    findings: list[Finding] = []
    if b"\0" in content[:8192]:
        return findings
    if len(content) > SCAN_LIMIT:
        content = content[:SCAN_LIMIT]
    text = content.decode("utf-8", errors="replace")
    in_fence = False
    previous_ignored = False
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
        ignored = IGNORE_MARKER in line.lower() or previous_ignored
        previous_ignored = IGNORE_MARKER in line.lower()

        if not in_fence and not ignored:
            if line.startswith("<<<<<<< ") or line.startswith(">>>>>>> "):
                findings.append(
                    Finding("error", "conflict-marker", "unresolved conflict marker", path, number)
                )

        if ignored:
            continue
        for code, severity, pattern, description in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(Finding(severity, code, f"possible {description}", path, number))
                break
        else:
            generic = GENERIC_RE.search(line)
            if generic:
                value = generic.group("value").strip()
                lowered = value.lower()
                looks_like_placeholder = bool(PLACEHOLDER_RE.match(value)) or any(
                    token in lowered
                    for token in ("getenv", "os.environ", "process.env", "${", "<", "example")
                )
                if not looks_like_placeholder:
                    findings.append(
                        Finding(
                            "warning",
                            "generic-credential",
                            "hard-coded credential assignment; use an environment variable or secret manager",
                            path,
                            number,
                        )
                    )
    return findings


def check_staged(repo: str, args: argparse.Namespace) -> tuple[list[Finding], int, list[str]]:
    findings: list[Finding] = []
    paths = staged_paths(repo)
    max_bytes = int(args.max_size_mb * 1024 * 1024)

    for path in paths:
        if path_is_allowed(path, args.allow_path):
            continue
        if is_secret_filename(path):
            findings.append(
                Finding(
                    "error",
                    "secret-file",
                    "secret-like file must not be committed; remove it from the index and add it to .gitignore",
                    path,
                )
            )
        try:
            _, size = index_entry(repo, path)
        except RuntimeError:
            size = 0
        if size > max_bytes:
            findings.append(
                Finding(
                    "error",
                    "large-file",
                    f"staged blob is {size / (1024 * 1024):.1f} MiB; limit is {args.max_size_mb:g} MiB (use Git LFS or an artifact store)",
                    path,
                )
            )
        content = staged_bytes(repo, path)
        findings.extend(scan_text(repo, path, content, args.allow_path))

    findings.extend(whitespace_findings(repo))
    return findings, len(paths), paths


def whitespace_findings(repo: str) -> list[Finding]:
    completed = run_git(repo, "diff", "--cached", "--check")
    findings: list[Finding] = []
    pattern = re.compile(r"^(?P<path>.*?):(?P<line>\d+): (?P<message>.+)$")
    for line in completed.stdout.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        message = match.group("message").strip()
        if "trailing whitespace" in message or "space before tab" in message:
            findings.append(
                Finding(
                    "warning",
                    "whitespace",
                    message.rstrip("."),
                    normalize(match.group("path")),
                    int(match.group("line")),
                )
            )
    return findings


def current_branch(repo: str) -> str | None:
    completed = run_git(repo, "symbolic-ref", "--short", "-q", "HEAD")
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def is_protected(branch: str) -> bool:
    return branch in PROTECTED_BRANCHES or branch.startswith(PROTECTED_PREFIXES)


def branch_findings(branch: str, strict_protection: bool) -> list[Finding]:
    findings: list[Finding] = []
    if is_protected(branch):
        findings.append(
            Finding(
                "error" if strict_protection else "warning",
                "protected-branch",
                "protected branch; commit on a feature branch and merge through a pull request",
            )
        )
        return findings
    if not BRANCH_RE.match(branch):
        findings.append(
            Finding(
                "error",
                "branch-name",
                "branch must look like '<type>/<kebab-case-summary>', for example 'feat/oauth-device-flow' or 'fix/123-null-pointer'",
            )
        )
        return findings
    if ".." in branch or branch.endswith(".lock") or "@{" in branch:
        findings.append(
            Finding("error", "branch-name", "branch name contains a sequence Git refuses or misreads")
        )
    return findings


def print_human(findings: list[Finding], checked_files: int, branch: str | None) -> None:
    for finding in sorted(
        findings,
        key=lambda item: (item.severity != "error", item.path or "", item.line or 0, item.code),
    ):
        location = ""
        if finding.path:
            location = finding.path
            if finding.line:
                location += f":{finding.line}"
        label = "ERROR" if finding.severity == "error" else "WARN "
        code = f"[{finding.code}]"
        print(f"{label} {code} {location + '  ' if location else ''}{finding.message}")
    errors = sum(1 for finding in findings if finding.severity == "error")
    warnings = len(findings) - errors
    scope = f"{checked_files} staged file(s)"
    if branch:
        scope += f", branch '{branch}'"
    if errors:
        print(f"\nFAILED: {errors} error(s), {warnings} warning(s) in {scope}.")
    elif warnings:
        print(f"\nOK: {warnings} warning(s) in {scope}.")
    elif checked_files:
        print(f"OK: {checked_files} staged file(s) passed checks.")
    elif branch:
        print(f"OK: branch '{branch}' is valid.")
    else:
        print("OK: nothing staged to check.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Guard the Git index and branch names before committing.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--staged", action="store_true", help="scan files staged in the index")
    parser.add_argument("--branch", metavar="NAME", help="validate an explicit branch name")
    parser.add_argument(
        "--protect-main",
        action="store_true",
        help="treat commits or validation on protected branches as errors",
    )
    parser.add_argument("--max-size-mb", type=float, default=DEFAULT_MAX_SIZE_MB, help="staged blob size limit")
    parser.add_argument(
        "--allow-path",
        action="append",
        default=[],
        metavar="GLOB",
        help="skip files matching this glob (repeatable)",
    )
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--repo", default=".", help="repository path")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.staged and not args.branch:
        parser.error("use --staged and/or --branch")
    if args.max_size_mb <= 0:
        parser.error("--max-size-mb must be positive")

    try:
        root = repo_root(args.repo)
    except (OSError, RuntimeError) as error:
        print(f"error: not a git repository: {error}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    checked_files = 0
    branch: str | None = args.branch

    try:
        if args.staged:
            staged_findings, checked_files, _ = check_staged(root, args)
            findings.extend(staged_findings)
            if branch is None:
                branch = current_branch(root)
                if branch is None:
                    findings.append(
                        Finding(
                            "error" if args.protect_main else "warning",
                            "detached-head",
                            "HEAD is detached; create a branch before committing",
                        )
                    )
        if branch is not None:
            findings.extend(branch_findings(branch, args.protect_main))
    except (OSError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.strict:
        for finding in findings:
            finding.severity = "error"

    if args.json:
        payload = {
            "valid": all(finding.severity != "error" for finding in findings),
            "repo": root,
            "branch": branch,
            "checked_files": checked_files,
            "findings": [asdict(finding) for finding in findings],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_human(findings, checked_files, branch)

    return 1 if any(finding.severity == "error" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
