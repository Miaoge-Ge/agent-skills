"""Shared helpers for the git-workflow-standard tests."""
from __future__ import annotations

import contextlib
import os
import shutil
import stat
import subprocess
import sys
import uuid
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
PYTHON = sys.executable
WORK_ROOT = SKILL_ROOT / "tests" / "work"


def _force_remove(function, target, _error):
    try:
        os.chmod(target, stat.S_IWRITE)
    except OSError:
        pass
    try:
        function(target)
    except OSError:
        pass


@contextlib.contextmanager
def temp_workspace():
    """Create a temporary directory inside the workspace.

    The directory is created with Path.mkdir so it inherits the workspace
    ACL; tempfile.mkdtemp creates an owner-only DACL that the Windows
    sandbox can refuse. Git marks objects read-only on Windows, so cleanup
    resets permissions before removing the tree.
    """
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    path = WORK_ROOT / f"case-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, onerror=_force_remove)


def run_script(
    name: str,
    *args: str,
    cwd: Path | str | None = None,
    stdin: str | None = None,
    timeout: int = 120,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(SCRIPTS / name), *args],
        cwd=str(cwd) if cwd else None,
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    if check and completed.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} failed ({completed.returncode}):\n"
            f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
        )
    return completed


def init_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q", "-b", "main")
    git(path, "config", "user.name", "Test User")
    git(path, "config", "user.email", "test@example.com")
    git(path, "config", "commit.gpgsign", "false")
    return path


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def stage(repo: Path, *paths: str) -> None:
    git(repo, "add", "--", *paths)


def commit(
    repo: Path,
    message: str,
    *paths: str,
    allow_empty: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess:
    if paths:
        stage(repo, *paths)
    args = ["commit", "-q", "-m", message]
    if allow_empty:
        args.append("--allow-empty")
    return git(repo, *args, check=check)


def head(repo: Path) -> str:
    completed = git(repo, "rev-parse", "HEAD", check=False)
    return completed.stdout.strip() if completed.returncode == 0 else ""


def current_branch(repo: Path) -> str:
    return git(repo, "symbolic-ref", "--short", "HEAD").stdout.strip()
