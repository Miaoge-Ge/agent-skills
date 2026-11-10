"""End-to-end tests against real Git repositories and installed hooks."""
from __future__ import annotations

import subprocess
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


class IntegrationCase(unittest.TestCase):
    def setUp(self) -> None:
        self._context = temp_workspace()
        self.temp = self._context.__enter__()
        self.repo = init_repo(self.temp / "repo")
        self.install()

    def tearDown(self) -> None:
        self._context.__exit__(None, None, None)

    def install(self, *args: str):
        return run_script("install_hooks.py", "--repo", str(self.repo), *args)

    def git(self, *args: str, check: bool = True):
        return git(self.repo, *args, check=check)

    def commit(self, message: str, *paths: str, check: bool = True):
        return commit(self.repo, message, *paths, check=check)

    def lint(self, *args: str):
        return run_script("commit_msg_lint.py", "--repo", str(self.repo), *args)

    def guard(self, *args: str):
        return run_script("git_guard.py", "--repo", str(self.repo), *args)


class TestWorkflow(IntegrationCase):
    def test_full_feature_branch_workflow(self) -> None:
        write(self.repo / "README.md", "# demo\n")
        self.assertEqual(0, self.commit("chore: initialize repository", "README.md").returncode)

        self.git("switch", "-c", "feat/oauth-device-flow")
        write(self.repo / "auth.py", "def login():\n    return True\n")
        stage(self.repo, "auth.py")
        completed = self.commit(
            "feat(auth): add device authorization flow\n\n"
            "Support headless login on CI.\n\n"
            "Refs: #412"
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

        linted = self.lint("--range", "main..HEAD")
        self.assertEqual(0, linted.returncode, linted.stdout)
        guarded = self.guard("--staged")
        self.assertEqual(0, guarded.returncode, guarded.stdout)
        self.assertIn("feat/oauth-device-flow", guarded.stdout)

    def test_bad_commit_does_not_create_history(self) -> None:
        write(self.repo / "a.txt", "a")
        stage(self.repo, "a.txt")
        completed = self.commit("update stuff", check=False)
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("", head(self.repo))

    def test_breaking_change_commit_passes(self) -> None:
        write(self.repo / "api.py", "VERSION = 2\n")
        stage(self.repo, "api.py")
        message = (
            "feat(api)!: drop the legacy /v1/session endpoint\n\n"
            "BREAKING CHANGE: /v1/session is removed; use /v2/auth/session."
        )
        completed = self.commit(message)
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_merge_commit_passes_the_hook(self) -> None:
        write(self.repo / "a.txt", "a")
        self.commit("feat: add a", "a.txt")
        self.git("switch", "-c", "feat/add-b")
        write(self.repo / "b.txt", "b")
        self.commit("feat: add b", "b.txt")
        self.git("switch", "main")
        completed = self.git(
            "merge", "--no-ff", "-m", "Merge branch 'feat/add-b' into main", "feat/add-b", check=False
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_fixup_commit_passes_then_stays_temporary(self) -> None:
        write(self.repo / "a.txt", "a")
        self.commit("feat: add a", "a.txt")
        write(self.repo / "a.txt", "b")
        stage(self.repo, "a.txt")
        completed = self.git("commit", "-q", "--fixup", "HEAD", check=False)
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("fixup! feat: add a", self.git("log", "-1", "--format=%s").stdout)

    def test_conventional_revert_passes(self) -> None:
        write(self.repo / "a.txt", "a")
        self.commit("feat: add a", "a.txt")
        self.git("revert", "--no-commit", "HEAD")
        completed = self.commit("revert: feat: add a")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_amend_with_bad_message_is_blocked(self) -> None:
        write(self.repo / "a.txt", "a")
        self.commit("feat: add a", "a.txt")
        before = head(self.repo)
        completed = self.git("commit", "--amend", "-m", "bad amend", check=False)
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual(before, head(self.repo))

    def test_lint_history_after_multiple_commits(self) -> None:
        write(self.repo / "a.txt", "a")
        self.commit("feat: add a", "a.txt")
        write(self.repo / "b.txt", "b")
        self.commit("fix(b): handle empty input", "b.txt")
        write(self.repo / "c.txt", "c")
        self.commit("docs: describe the workflow", "c.txt")
        write(self.repo / "d.txt", "d")
        self.commit("chore: ignore build output", "d.txt")
        completed = self.lint("--range", "HEAD~3..HEAD")
        self.assertEqual(0, completed.returncode, completed.stdout)
        self.assertIn("3 commit message(s) valid", completed.stdout)

    def test_uninstall_removes_hook_enforcement(self) -> None:
        self.install("--uninstall")
        write(self.repo / "a.txt", "a")
        stage(self.repo, "a.txt")
        completed = self.commit("bad message", check=False)
        self.assertEqual(0, completed.returncode, completed.stderr)


class TestInstalledFiles(IntegrationCase):
    def test_hook_files_use_lf_and_absolute_python(self) -> None:
        for name in ("commit-msg", "pre-commit"):
            data = (self.repo / ".git" / "hooks" / name).read_bytes()
            self.assertNotIn(b"\r\n", data, name)
            self.assertIn(b"python", data.lower(), name)
        content = (self.repo / ".git" / "hooks" / "commit-msg").read_text(encoding="utf-8")
        self.assertIn(sys.executable.replace("\\", "/"), content)

    def test_bundled_scripts_are_runnable_copies(self) -> None:
        scripts = self.repo / ".git" / "hooks" / "git-standard"
        self.assertTrue((scripts / "commit_msg_lint.py").is_file())
        self.assertTrue((scripts / "git_guard.py").is_file())
        completed = subprocess.run(
            [sys.executable, str(scripts / "commit_msg_lint.py"), "--message", "feat: add a"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)


if __name__ == "__main__":
    unittest.main()
