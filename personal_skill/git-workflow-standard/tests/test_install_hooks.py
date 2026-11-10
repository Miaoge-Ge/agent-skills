"""Tests for install_hooks.py."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
from skill_test_utils import (  # noqa: E402
    commit,
    git,
    head,
    init_repo,
    run_script,
    stage,
    temp_workspace,
    write,
)


class HookTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._context = temp_workspace()
        self.temp = self._context.__enter__()
        self.repo = init_repo(self.temp / "repo")

    def tearDown(self) -> None:
        self._context.__exit__(None, None, None)

    def install(self, *args: str):
        return run_script("install_hooks.py", "--repo", str(self.repo), *args)

    def hook(self, name: str) -> Path:
        return self.repo / ".git" / "hooks" / name

    def commit(self, message: str, *paths: str, check: bool = True):
        return commit(self.repo, message, *paths, check=check)

    def git(self, *args: str, check: bool = True):
        return git(self.repo, *args, check=check)


class TestInstall(HookTestCase):
    def test_install_creates_both_hooks_and_scripts(self) -> None:
        completed = self.install()
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        for name in ("commit-msg", "pre-commit"):
            content = self.hook(name).read_text(encoding="utf-8")
            self.assertIn("managed by git-workflow-standard", content)
            self.assertIn("git-standard", content)
        self.assertTrue((self.repo / ".git" / "hooks" / "git-standard" / "commit_msg_lint.py").is_file())
        self.assertTrue((self.repo / ".git" / "hooks" / "git-standard" / "git_guard.py").is_file())

    def test_good_commit_passes(self) -> None:
        self.install()
        write(self.repo / "a.txt", "a")
        stage(self.repo, "a.txt")
        completed = self.commit("feat: add a")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertNotEqual("", head(self.repo))

    def test_bad_commit_is_blocked(self) -> None:
        self.install()
        write(self.repo / "a.txt", "a")
        stage(self.repo, "a.txt")
        completed = self.commit("bad message", check=False)
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("", head(self.repo))
        self.assertIn("FAIL", completed.stdout + completed.stderr)

    def test_pre_commit_blocks_env_file(self) -> None:
        self.install()
        write(self.repo / ".env", "TOKEN=secret\n")
        stage(self.repo, ".env")
        completed = self.commit("feat: add env", check=False)
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("secret-file", completed.stdout + completed.stderr)
        self.assertEqual("", head(self.repo))

    def test_no_verify_bypasses_hooks(self) -> None:
        self.install()
        write(self.repo / "a.txt", "a")
        stage(self.repo, "a.txt")
        completed = git(self.repo, "commit", "-q", "--no-verify", "-m", "bad message", check=False)
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertNotEqual("", head(self.repo))

    def test_reinstall_is_idempotent(self) -> None:
        self.assertEqual(0, self.install().returncode)
        first = self.hook("commit-msg").read_text(encoding="utf-8")
        self.assertEqual(0, self.install().returncode)
        self.assertEqual(first, self.hook("commit-msg").read_text(encoding="utf-8"))

    def test_chinese_commit_message_passes(self) -> None:
        self.install()
        write(self.repo / "a.txt", "a")
        stage(self.repo, "a.txt")
        completed = self.commit("feat: 增加导出入口")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_commit_body_and_footer_pass(self) -> None:
        self.install()
        write(self.repo / "a.txt", "a")
        stage(self.repo, "a.txt")
        message = "fix(api): return 404 for missing records\n\nAvoid leaking existence.\n\nCloses: #123"
        completed = self.commit(message)
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_commit_in_path_with_spaces(self) -> None:
        spaced = init_repo(self.temp / "repo with space")
        completed = run_script("install_hooks.py", "--repo", str(spaced))
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        write(spaced / "a.txt", "a")
        stage(spaced, "a.txt")
        completed = commit(spaced, "feat: add a")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_custom_hooks_path_is_respected(self) -> None:
        self.git("config", "core.hooksPath", ".githooks")
        completed = self.install()
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertTrue((self.repo / ".githooks" / "commit-msg").is_file())
        self.assertFalse((self.repo / ".git" / "hooks" / "commit-msg").exists())
        write(self.repo / "a.txt", "a")
        stage(self.repo, "a.txt")
        completed = self.commit("bad message", check=False)
        self.assertNotEqual(0, completed.returncode)


class TestForeignHooks(HookTestCase):
    def test_foreign_hook_is_not_overwritten_by_default(self) -> None:
        path = self.hook("commit-msg")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        completed = self.install()
        self.assertEqual(1, completed.returncode)
        self.assertIn("skipped", completed.stdout)
        self.assertEqual("#!/bin/sh\nexit 0\n", path.read_text(encoding="utf-8"))

    def test_force_replaces_and_backs_up_foreign_hook(self) -> None:
        path = self.hook("commit-msg")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        completed = self.install("--force")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("managed by git-workflow-standard", path.read_text(encoding="utf-8"))
        backup = path.with_name("commit-msg.bak")
        self.assertTrue(backup.is_file())
        self.assertEqual("#!/bin/sh\nexit 0\n", backup.read_text(encoding="utf-8"))

    def test_uninstall_leaves_foreign_hook_in_place(self) -> None:
        pre_commit = self.hook("pre-commit")
        pre_commit.parent.mkdir(parents=True, exist_ok=True)
        pre_commit.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.install()  # commit-msg installed, pre-commit skipped
        completed = self.install("--uninstall")
        self.assertEqual(0, completed.returncode)
        self.assertTrue(pre_commit.is_file())
        self.assertEqual("#!/bin/sh\nexit 0\n", pre_commit.read_text(encoding="utf-8"))


class TestUninstall(HookTestCase):
    def test_uninstall_removes_managed_hooks_and_scripts(self) -> None:
        self.install()
        completed = self.install("--uninstall")
        self.assertEqual(0, completed.returncode)
        self.assertFalse(self.hook("commit-msg").exists())
        self.assertFalse(self.hook("pre-commit").exists())
        self.assertFalse((self.repo / ".git" / "hooks" / "git-standard").exists())

    def test_uninstall_when_not_installed(self) -> None:
        completed = self.install("--uninstall")
        self.assertEqual(0, completed.returncode)
        self.assertIn("absent", completed.stdout)


class TestErrors(HookTestCase):
    def test_not_a_repository(self) -> None:
        completed = run_script("install_hooks.py", "--repo", str(self.temp / "missing"))
        self.assertEqual(2, completed.returncode)
        self.assertIn("not a git repository", completed.stderr)

    def test_missing_python_interpreter(self) -> None:
        completed = self.install("--python", "definitely-not-a-python")
        self.assertEqual(2, completed.returncode)
        self.assertIn("Python interpreter not found", completed.stderr)


if __name__ == "__main__":
    unittest.main()
