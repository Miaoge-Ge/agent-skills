#!/usr/bin/env python3
"""Install the commit-msg and pre-commit hooks for this skill.

The hooks are small POSIX sh shims that call the bundled linters with an
absolute Python path, so they keep working when the skill directory moves.
Existing hooks are never overwritten unless --force is given, and foreign
hooks are left untouched by --uninstall.

Usage:
    python install_hooks.py
    python install_hooks.py --repo ../my-project
    python install_hooks.py --uninstall
"""
from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

MARKER = "# managed by git-workflow-standard"
SCRIPT_DIR = Path(__file__).resolve().parent
BUNDLED = ("commit_msg_lint.py", "git_guard.py")
HOOK_SCRIPTS = {
    "commit-msg": ("commit_msg_lint.py", '--file "$1" --quiet'),
    "pre-commit": ("git_guard.py", "--staged"),
}


@dataclass
class HookResult:
    name: str
    status: str
    detail: str


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def git_output(repo: Path, *args: str) -> str:
    completed = run_git(repo, *args)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git command failed")
    return completed.stdout


def hooks_directory(repo: Path) -> Path:
    output = git_output(repo, "rev-parse", "--git-path", "hooks").strip()
    path = Path(output)
    if not path.is_absolute():
        path = repo / path
    return path.resolve()


def quote(value: str) -> str:
    return shlex.quote(value.replace("\\", "/"))


def hook_body(python: str, hooks_dir: Path, script: str, arguments: str) -> str:
    target = hooks_dir / "git-standard" / script
    line = f"exec {quote(python)} {quote(str(target))}"
    if arguments:
        line += f" {arguments}"
    return f"#!/bin/sh\n{MARKER}\n{line}\n"


def backup(path: Path) -> Path:
    candidate = path.with_name(path.name + ".bak")
    counter = 1
    while candidate.exists():
        candidate = path.with_name(f"{path.name}.bak-{counter}")
        counter += 1
    shutil.copy2(path, candidate)
    return candidate


def install(repo: Path, python: str, force: bool, results: list[HookResult]) -> None:
    try:
        hooks_dir = hooks_directory(repo)
    except (OSError, RuntimeError) as error:
        raise RuntimeError(f"not a git repository: {error}") from error

    bundled_dir = hooks_dir / "git-standard"
    bundled_dir.mkdir(parents=True, exist_ok=True)
    for script in BUNDLED:
        source = SCRIPT_DIR / script
        target = bundled_dir / script
        shutil.copy2(source, target)
        try:
            target.chmod(0o755)
        except OSError:
            pass

    for name, (script, arguments) in HOOK_SCRIPTS.items():
        path = hooks_dir / name
        body = hook_body(python, hooks_dir, script, arguments)
        if path.exists():
            existing = path.read_text(encoding="utf-8", errors="replace")
            if MARKER not in existing:
                if not force:
                    results.append(
                        HookResult(
                            name,
                            "skipped",
                            f"existing hook is not managed by this skill; re-run with --force to replace it ({path})",
                        )
                    )
                    continue
                saved = backup(path)
                results.append(HookResult(name, "backup", f"saved existing hook to {saved}"))
        path.write_text(body, encoding="utf-8", newline="\n")
        try:
            path.chmod(0o755)
        except OSError:
            pass
        results.append(HookResult(name, "installed", str(path)))

    results.append(HookResult("scripts", "installed", str(bundled_dir)))


def uninstall(repo: Path, results: list[HookResult]) -> None:
    try:
        hooks_dir = hooks_directory(repo)
    except (OSError, RuntimeError) as error:
        raise RuntimeError(f"not a git repository: {error}") from error

    for name in HOOK_SCRIPTS:
        path = hooks_dir / name
        if not path.exists():
            results.append(HookResult(name, "absent", str(path)))
            continue
        existing = path.read_text(encoding="utf-8", errors="replace")
        if MARKER not in existing:
            results.append(HookResult(name, "skipped", f"not managed by this skill: {path}"))
            continue
        path.unlink()
        results.append(HookResult(name, "removed", str(path)))

    bundled_dir = hooks_dir / "git-standard"
    if bundled_dir.exists():
        shutil.rmtree(bundled_dir)
        results.append(HookResult("scripts", "removed", str(bundled_dir)))
    else:
        results.append(HookResult("scripts", "absent", str(bundled_dir)))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install or remove the git-workflow-standard hooks.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--repo", default=".", help="repository path")
    parser.add_argument("--python", default=sys.executable, help="Python interpreter used by the hooks")
    parser.add_argument("--force", action="store_true", help="replace hooks not managed by this skill")
    parser.add_argument("--uninstall", action="store_true", help="remove hooks managed by this skill")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo = Path(args.repo).resolve()
    results: list[HookResult] = []
    try:
        if args.uninstall:
            uninstall(repo, results)
        else:
            python = Path(args.python)
            if not python.is_file():
                located = shutil.which(args.python)
                if located is None:
                    print(f"error: Python interpreter not found: {args.python}", file=sys.stderr)
                    return 2
                python = Path(located)
            install(repo, str(python.resolve()), args.force, results)
    except (OSError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    for result in results:
        print(f"{result.status:9} {result.name}: {result.detail}")
    skipped = [result for result in results if result.status == "skipped"]
    return 1 if skipped and not args.uninstall else 0


if __name__ == "__main__":
    raise SystemExit(main())
