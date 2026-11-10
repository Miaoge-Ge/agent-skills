"""Tests for git_guard.py."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
from skill_test_utils import (  # noqa: E402
    SCRIPTS,
    commit,
    git,
    init_repo,
    run_script,
    stage,
    temp_workspace,
    write,
)

sys.path.insert(0, str(SCRIPTS))
import git_guard as guard  # noqa: E402


class TestSecretFilenames(unittest.TestCase):
    def test_secret_like_filenames_are_blocked(self) -> None:
        for path in (
            ".env",
            "config/.env",
            ".env.local",
            "id_rsa",
            "keys/server.pem",
            "cert.key",
            "store.p12",
            "app.pfx",
            "release.keystore",
            "debug.jks",
            "sub/dir/id_ed25519",
            "keys/SERVER.PEM",
            ".ENV.LOCAL",
        ):
            with self.subTest(path=path):
                self.assertTrue(guard.is_secret_filename(path), path)

    def test_safe_filenames_are_allowed(self) -> None:
        for path in (
            ".env.example",
            ".env.sample",
            ".env.template",
            ".env.test.example",
            "id_rsa.pub",
            "README.md",
            "src/main.py",
            "docs/environment.md",
            "keyboard.py",
        ):
            with self.subTest(path=path):
                self.assertFalse(guard.is_secret_filename(path), path)


class TestSecretScan(unittest.TestCase):
    def scan(self, text: str, path: str = "src/app.py") -> list[guard.Finding]:
        return guard.scan_text(".", path, text.encode("utf-8"), [])

    def codes(self, text: str) -> list[str]:
        return [finding.code for finding in self.scan(text)]

    def test_aws_access_key(self) -> None:
        self.assertIn("aws-access-key", self.codes("key = AKIAIOSFODNN7EXAMPLE"))

    def test_github_token(self) -> None:
        self.assertIn("github-token", self.codes("token = 'ghp_" + "a" * 36 + "'"))

    def test_github_fine_grained_token(self) -> None:
        self.assertIn("github-token", self.codes("token = github_pat_" + "a" * 50))

    def test_private_key(self) -> None:
        self.assertIn("private-key", self.codes("-----BEGIN OPENSSH PRIVATE KEY-----"))

    def test_slack_token(self) -> None:
        self.assertIn("slack-token", self.codes("xoxb-1234567890-abcdefghij"))

    def test_slack_webhook(self) -> None:
        self.assertIn(
            "slack-webhook",
            self.codes("https://hooks.slack.com/services/T000/B000/XXXXXXXXXXXXXXXXXXXX"),
        )

    def test_stripe_secret(self) -> None:
        self.assertIn("stripe-secret", self.codes("sk_live_" + "a" * 24))

    def test_openai_key(self) -> None:
        self.assertIn("openai-key", self.codes("sk-proj-" + "a" * 32))

    def test_google_api_key(self) -> None:
        self.assertIn("google-api-key", self.codes("AIza" + "a" * 35))

    def test_npm_token(self) -> None:
        self.assertIn("npm-token", self.codes("npm_" + "a" * 36))

    def test_jwt_is_a_warning(self) -> None:
        token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.c2lnbmF0dXJl"
        findings = self.scan(token)
        self.assertEqual(["jwt"], [finding.code for finding in findings])
        self.assertEqual("warning", findings[0].severity)

    def test_generic_credential_is_a_warning(self) -> None:
        findings = self.scan('password = "hunter2hunter2"')
        self.assertEqual(["generic-credential"], [finding.code for finding in findings])
        self.assertEqual("warning", findings[0].severity)

    def test_placeholder_credentials_are_ignored(self) -> None:
        for text in (
            'password = "changeme"',
            'password = "${DB_PASSWORD}"',
            'password = "your-password"',
            'api_key = "example-key"',
            'token = "<token>"',
            'secret = "***"',
            'password = os.getenv("DB_PASSWORD")',
            'password = process.env.DB_PASSWORD',
        ):
            with self.subTest(text=text):
                self.assertEqual([], self.scan(text))

    def test_inline_ignore_marker(self) -> None:
        text = 'key = "AKIAIOSFODNN7EXAMPLE"  # git-guard:ignore'
        self.assertEqual([], self.scan(text))

    def test_ignore_marker_on_previous_line(self) -> None:
        text = '# git-guard:ignore\nkey = "AKIAIOSFODNN7EXAMPLE"'
        self.assertEqual([], self.scan(text))

    def test_binary_content_is_skipped(self) -> None:
        content = b"\x00\x01AKIAIOSFODNN7EXAMPLE"
        self.assertEqual([], guard.scan_text(".", "image.bin", content, []))

    def test_conflict_markers_are_errors(self) -> None:
        text = "<<<<<<< HEAD\nours\n=======\ntheirs\n>>>>>>> feature\n"
        findings = self.scan(text)
        self.assertEqual(2, len([finding for finding in findings if finding.code == "conflict-marker"]))
        self.assertTrue(all(finding.severity == "error" for finding in findings))

    def test_conflict_markers_inside_code_fence_are_ignored(self) -> None:
        text = "```text\n<<<<<<< HEAD\n>>>>>>> branch\n```\n"
        self.assertEqual([], self.scan(text, "docs/conflicts.md"))

    def test_certificate_block_is_not_a_private_key(self) -> None:
        self.assertEqual([], self.scan("-----BEGIN CERTIFICATE-----"))

    def test_line_numbers_are_reported(self) -> None:
        findings = self.scan("line one\nline two\nkey = AKIAIOSFODNN7EXAMPLE\n")
        self.assertEqual(3, findings[0].line)


class TestBranchNames(unittest.TestCase):
    def test_valid_branch_names(self) -> None:
        for branch in (
            "feat/oauth-device-flow",
            "fix/123-null-pointer",
            "docs/quickstart",
            "refactor/config-loader",
            "perf/cache-user-lookups",
            "test/retry-backoff",
            "build/vite-5",
            "ci/windows-matrix",
            "chore/ignore-env",
            "revert/bad-merge",
            "hotfix/session-leak",
        ):
            with self.subTest(branch=branch):
                self.assertEqual([], guard.branch_findings(branch, False), branch)

    def test_invalid_branch_names(self) -> None:
        for branch in (
            "feature/oauth",
            "feat/Bad-Name",
            "feat/",
            "feat/with space",
            "fix/",
            "Feat/upper",
            "feat/x..y",
            "feat/x.lock",
            "feat/x@{1}",
        ):
            with self.subTest(branch=branch):
                findings = guard.branch_findings(branch, False)
                self.assertTrue(
                    any(finding.code == "branch-name" for finding in findings),
                    f"{branch} should be rejected: {findings}",
                )

    def test_protected_branch_warns_by_default(self) -> None:
        findings = guard.branch_findings("main", False)
        self.assertEqual("warning", findings[0].severity)
        self.assertEqual("protected-branch", findings[0].code)

    def test_protected_branch_is_an_error_in_strict_mode(self) -> None:
        findings = guard.branch_findings("release/v1.4.0", True)
        self.assertEqual("error", findings[0].severity)


class GuardCliAssertions(unittest.TestCase):
    def guard(self, repo: Path, *args: str):
        return run_script("git_guard.py", "--repo", str(repo), *args)


class TestStagedFiles(GuardCliAssertions):
    def test_safe_file_passes(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / "app.py", "print('hello')\n")
            stage(repo, "app.py")
            completed = self.guard(repo, "--staged")
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_env_file_blocks(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / ".env", "TOKEN=secret\n")
            stage(repo, ".env")
            completed = self.guard(repo, "--staged")
            self.assertEqual(1, completed.returncode)
            self.assertIn("secret-file", completed.stdout)

    def test_env_example_is_allowed(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / ".env.example", "TOKEN=replace-me\n")
            stage(repo, ".env.example")
            completed = self.guard(repo, "--staged")
            self.assertEqual(0, completed.returncode, completed.stdout)

    def test_secret_in_file_content_blocks(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / "config.py", 'AWS_KEY = "AKIAIOSFODNN7EXAMPLE"\n')
            stage(repo, "config.py")
            completed = self.guard(repo, "--staged")
            self.assertEqual(1, completed.returncode)
            self.assertIn("aws-access-key", completed.stdout)

    def test_allow_path_skips_scanning(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / "docs/security.md", "Example: AKIAIOSFODNN7EXAMPLE\n")
            stage(repo, "docs/security.md")
            self.assertEqual(1, self.guard(repo, "--staged").returncode)
            completed = self.guard(repo, "--staged", "--allow-path", "docs/*")
            self.assertEqual(0, completed.returncode, completed.stdout)

    def test_large_file_blocks(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / "blob.bin", "x" * 2048)
            stage(repo, "blob.bin")
            completed = self.guard(repo, "--staged", "--max-size-mb", "0.001")
            self.assertEqual(1, completed.returncode)
            self.assertIn("large-file", completed.stdout)
            self.assertEqual(0, self.guard(repo, "--staged", "--max-size-mb", "5").returncode)

    def test_trailing_whitespace_warns(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / "app.py", "value = 1   \n")
            stage(repo, "app.py")
            completed = self.guard(repo, "--staged")
            self.assertEqual(0, completed.returncode)
            self.assertIn("whitespace", completed.stdout)
            self.assertEqual(1, self.guard(repo, "--staged", "--strict").returncode)

    def test_conflict_marker_blocks(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / "merge.py", "<<<<<<< HEAD\nours\n=======\ntheirs\n>>>>>>> feature\n")
            stage(repo, "merge.py")
            completed = self.guard(repo, "--staged")
            self.assertEqual(1, completed.returncode)
            self.assertIn("conflict-marker", completed.stdout)

    def test_deleted_file_is_not_scanned(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / "a.txt", "a")
            commit(repo, "feat: add a", "a.txt")
            git(repo, "rm", "-q", "a.txt")
            completed = self.guard(repo, "--staged")
            self.assertEqual(0, completed.returncode, completed.stdout)

    def test_renamed_file_is_scanned_without_crashing(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / "old.txt", "safe\n")
            commit(repo, "feat: add old", "old.txt")
            git(repo, "mv", "old.txt", "new.txt")
            completed = self.guard(repo, "--staged")
            self.assertEqual(0, completed.returncode, completed.stdout)

    def test_path_with_spaces_is_supported(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / "my file.txt", "safe\n")
            stage(repo, "my file.txt")
            completed = self.guard(repo, "--staged")
            self.assertEqual(0, completed.returncode, completed.stdout)

    def test_json_output(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / ".env", "TOKEN=secret\n")
            stage(repo, ".env")
            completed = self.guard(repo, "--staged", "--json")
            self.assertEqual(1, completed.returncode)
            payload = json.loads(completed.stdout)
            self.assertFalse(payload["valid"])
            self.assertEqual(1, payload["checked_files"])
            self.assertEqual("secret-file", payload["findings"][0]["code"])


class TestBranches(GuardCliAssertions):
    def test_valid_branch_passes(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            completed = self.guard(repo, "--branch", "feat/oauth-device-flow")
            self.assertEqual(0, completed.returncode)
            self.assertIn("is valid", completed.stdout)

    def test_invalid_branch_fails(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            completed = self.guard(repo, "--branch", "Bad Branch")
            self.assertEqual(1, completed.returncode)
            self.assertIn("branch-name", completed.stdout)

    def test_current_protected_branch_only_warns(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / "a.txt", "a")
            stage(repo, "a.txt")
            completed = self.guard(repo, "--staged")
            self.assertEqual(0, completed.returncode)
            self.assertIn("protected-branch", completed.stdout)

    def test_protect_main_makes_it_an_error(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / "a.txt", "a")
            stage(repo, "a.txt")
            completed = self.guard(repo, "--staged", "--protect-main")
            self.assertEqual(1, completed.returncode)

    def test_detached_head_warns(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            write(repo / "a.txt", "a")
            commit(repo, "feat: add a", "a.txt")
            write(repo / "a.txt", "b")
            stage(repo, "a.txt")
            git(repo, "checkout", "--detach", "-q")
            completed = self.guard(repo, "--staged")
            self.assertEqual(0, completed.returncode)
            self.assertIn("detached-head", completed.stdout)
            self.assertEqual(1, self.guard(repo, "--staged", "--protect-main").returncode)


class TestUsage(GuardCliAssertions):
    def test_not_a_repository(self) -> None:
        with temp_workspace() as temp:
            completed = self.guard(temp / "missing", "--staged")
            self.assertEqual(2, completed.returncode)
            self.assertIn("not a git repository", completed.stderr)

    def test_no_arguments_is_a_usage_error(self) -> None:
        completed = run_script("git_guard.py")
        self.assertEqual(2, completed.returncode)

    def test_invalid_size_limit_is_a_usage_error(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(temp / "repo")
            completed = self.guard(repo, "--staged", "--max-size-mb", "0")
            self.assertEqual(2, completed.returncode)


if __name__ == "__main__":
    unittest.main()
