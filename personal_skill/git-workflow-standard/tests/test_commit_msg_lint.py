"""Tests for commit_msg_lint.py."""
from __future__ import annotations

import json
import random
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
from skill_test_utils import (  # noqa: E402
    SCRIPTS,
    commit,
    init_repo,
    run_script,
    temp_workspace,
    write,
)

sys.path.insert(0, str(SCRIPTS))
import commit_msg_lint as commit_lint  # noqa: E402


def lint(text: str, **options) -> commit_lint.Result:
    return commit_lint.lint_message(text, commit_lint.Options(**options))


class LintAssertions(unittest.TestCase):
    def assertValid(self, text: str, **options) -> commit_lint.Result:
        result = lint(text, **options)
        self.assertTrue(result.valid, f"expected valid, got {result.errors} for {text!r}")
        return result

    def assertInvalid(self, text: str, fragment: str | None = None, **options) -> commit_lint.Result:
        result = lint(text, **options)
        self.assertFalse(result.valid, f"expected invalid for {text!r}")
        if fragment:
            self.assertTrue(
                any(fragment in error for error in result.errors),
                f"expected an error containing {fragment!r}, got {result.errors}",
            )
        return result


class TestTypes(LintAssertions):
    def test_every_conventional_type_is_valid(self) -> None:
        for commit_type in commit_lint.DEFAULT_TYPES:
            with self.subTest(commit_type=commit_type):
                self.assertValid(f"{commit_type}: do something useful")

    def test_unknown_type_is_rejected(self) -> None:
        self.assertInvalid("feature: add login", "unknown type")

    def test_uppercase_type_is_rejected(self) -> None:
        result = self.assertInvalid("Feat: add login", "must be lowercase")
        self.assertTrue(any("unknown type" in error for error in result.errors))

    def test_custom_types_replace_the_defaults(self) -> None:
        self.assertValid("wip: draft the design", types=("wip",))
        self.assertInvalid("feat: add login", "unknown type", types=("wip",))

    def test_type_with_digits_is_unknown(self) -> None:
        self.assertInvalid("feat2: add login", "unknown type")


class TestHeader(LintAssertions):
    def test_scope_is_optional(self) -> None:
        self.assertValid("feat: add login")
        self.assertValid("feat(auth): add login")

    def test_scope_accepts_dots_underscores_and_slashes(self) -> None:
        for scope in ("api.v2", "user_profile", "api/v2", "web-ui", "a1"):
            with self.subTest(scope=scope):
                self.assertValid(f"feat({scope}): add login")

    def test_scope_must_be_lowercase(self) -> None:
        self.assertInvalid("feat(Auth): add login", "scope")

    def test_scope_must_not_contain_spaces(self) -> None:
        self.assertInvalid("feat(user profile): add login", "header must match")

    def test_empty_scope_is_rejected(self) -> None:
        self.assertInvalid("feat(): add login", "header must match")

    def test_missing_space_after_colon_is_rejected(self) -> None:
        self.assertInvalid("feat:add login", "header must match")

    def test_two_spaces_after_colon_are_rejected(self) -> None:
        self.assertInvalid("feat:  add login", "leading or trailing whitespace")

    def test_empty_description_is_rejected(self) -> None:
        self.assertInvalid("feat: ", "description must not be empty")
        self.assertInvalid("feat(auth):", "description must not be empty")

    def test_description_must_not_end_with_an_ascii_period(self) -> None:
        self.assertInvalid("feat: add login.", "must not end with a period")

    def test_description_must_not_end_with_a_chinese_period(self) -> None:
        self.assertInvalid("fix: 修复空指针。", "must not end with a period")

    def test_description_must_not_start_with_uppercase_ascii(self) -> None:
        self.assertInvalid("feat: Add login", "uppercase")

    def test_chinese_description_is_valid(self) -> None:
        self.assertValid("feat: 增加导出入口")
        self.assertValid("fix(parser): 拒绝尾随逗号")

    def test_description_may_start_with_a_digit(self) -> None:
        self.assertValid("docs: 2026 roadmap update")

    def test_header_limit_is_72_by_default(self) -> None:
        self.assertValid("feat: " + "a" * 66)
        self.assertInvalid("feat: " + "a" * 67, "limit is 72")

    def test_header_limit_can_be_raised(self) -> None:
        self.assertValid("feat: " + "a" * 70, max_header=100)

    def test_header_trailing_whitespace_produces_a_warning(self) -> None:
        result = self.assertValid("feat: add login   ")
        self.assertTrue(any("trailing whitespace" in warning for warning in result.warnings))

    def test_header_leading_whitespace_is_rejected(self) -> None:
        self.assertInvalid(" feat: add login", "must not start with whitespace")

    def test_header_must_not_contain_tabs(self) -> None:
        self.assertInvalid("feat:\tadd login", "tabs")

    def test_bare_message_is_rejected(self) -> None:
        self.assertInvalid("update stuff", "header must match")

    def test_wip_is_not_conventional(self) -> None:
        self.assertInvalid("WIP", "header must match")


class TestBodyAndFooters(LintAssertions):
    def test_body_requires_a_blank_line_after_the_header(self) -> None:
        self.assertInvalid("feat: add login\nbecause reasons", "blank line")

    def test_body_with_blank_line_is_valid(self) -> None:
        self.assertValid("feat: add login\n\nBecause reasons.")

    def test_multiple_paragraphs_are_valid(self) -> None:
        self.assertValid(
            "fix(parser): reject trailing commas\n\n"
            "The old parser accepted trailing commas, which produced invalid\n"
            "JSON downstream.\n\n"
            "The new parser reports the position of the first offending comma."
        )

    def test_footer_block_is_valid(self) -> None:
        self.assertValid(
            "fix(api): return 404 for missing records\n\n"
            "Avoid leaking existence information through 500 responses.\n\n"
            "Closes: #123\n"
            "Refs: #99\n"
            "Co-authored-by: A <a@example.com>"
        )

    def test_breaking_change_footer_is_valid_without_bang(self) -> None:
        self.assertValid(
            "feat(api): remove the v1 session endpoint\n\n"
            "BREAKING CHANGE: use /v2/auth/session instead."
        )

    def test_bang_without_footer_produces_a_warning(self) -> None:
        result = self.assertValid("feat(api)!: remove the v1 session endpoint")
        self.assertTrue(any("BREAKING CHANGE" in warning for warning in result.warnings))

    def test_bang_with_footer_has_no_warning(self) -> None:
        result = self.assertValid(
            "feat(api)!: remove the v1 session endpoint\n\n"
            "BREAKING CHANGE: use /v2/auth/session instead."
        )
        self.assertEqual([], result.warnings)

    def test_empty_breaking_change_footer_is_rejected(self) -> None:
        self.assertInvalid("feat: drop v1\n\nBREAKING CHANGE:", "must have a value")
        self.assertInvalid("feat: drop v1\n\nBREAKING CHANGE:   ", "BREAKING CHANGE footer")

    def test_footer_with_spaces_in_token_is_rejected(self) -> None:
        self.assertInvalid("feat: add login\n\nReviewed By: A", "must use '-' instead of spaces")

    def test_footer_without_value_is_rejected(self) -> None:
        self.assertInvalid("feat: add login\n\nRefs:", "must have a value")

    def test_footer_continuation_line_is_valid(self) -> None:
        self.assertValid(
            "feat(api)!: remove v1\n\n"
            "BREAKING CHANGE: use v2 instead.\n"
            "  The v1 endpoint is gone; see the migration guide."
        )

    def test_long_body_line_is_only_a_warning(self) -> None:
        result = self.assertValid("feat: add login\n\n" + "x" * 80)
        self.assertTrue(any("recommended limit" in warning for warning in result.warnings))
        self.assertInvalid("feat: add login\n\n" + "x" * 80, strict=True)

    def test_body_line_at_the_limit_has_no_warning(self) -> None:
        result = self.assertValid("feat: add login\n\n" + "x" * 72)
        self.assertEqual([], result.warnings)

    def test_body_trailing_whitespace_is_a_warning(self) -> None:
        result = self.assertValid("feat: add login\n\nbody   ")
        self.assertTrue(any("trailing whitespace" in warning for warning in result.warnings))

    def test_extra_blank_line_after_header_is_a_warning(self) -> None:
        result = self.assertValid("feat: add login\n\n\nbody")
        self.assertTrue(any("multiple blank lines" in warning for warning in result.warnings))

    def test_comments_are_ignored(self) -> None:
        self.assertValid("feat: add login\n\n# Please enter the commit message.\nBody.")

    def test_comment_only_message_is_empty(self) -> None:
        self.assertInvalid("# comment only", "empty")

    def test_scissors_cut_the_verbose_diff(self) -> None:
        text = (
            "feat: add login\n"
            "# ------------------------ >8 ------------------------\n"
            "diff --git a/x b/x\n"
            "+not part of the message"
        )
        self.assertValid(text)


class TestSpecialCommits(LintAssertions):
    def test_merge_commit_is_allowed_by_default(self) -> None:
        self.assertValid("Merge branch 'feature' into main")

    def test_merge_commit_can_be_rejected(self) -> None:
        self.assertInvalid("Merge branch 'feature' into main", "merge commits", allow_merge=False)

    def test_fixup_commit_is_allowed_with_a_warning(self) -> None:
        result = self.assertValid("fixup! feat: add login")
        self.assertTrue(any("fixup" in warning for warning in result.warnings))

    def test_fixup_commit_can_be_rejected(self) -> None:
        self.assertInvalid("fixup! feat: add login", "fixup", allow_fixup=False)

    def test_fixup_commit_is_rejected_in_strict_mode(self) -> None:
        self.assertInvalid("fixup! feat: add login", "fixup", strict=True)

    def test_squash_and_amend_prefixes_are_allowed(self) -> None:
        self.assertValid("squash! feat: add login")
        self.assertValid("amend! feat: add login")

    def test_git_default_revert_is_rejected_by_default(self) -> None:
        self.assertInvalid('Revert "feat: add login"', "revert: <subject>")

    def test_git_default_revert_can_be_allowed(self) -> None:
        self.assertValid('Revert "feat: add login"', allow_git_revert=True)

    def test_conventional_revert_is_valid(self) -> None:
        self.assertValid(
            "revert: feat(auth): add SSO login\n\n"
            "This reverts commit 3f2a1c9d8e7b6a5c4d3e2f1a0b9c8d7e6f5a4b3c.\n\n"
            "Reason: the rollout was paused."
        )


class TestRobustness(LintAssertions):
    def test_random_input_never_crashes(self) -> None:
        rng = random.Random(20260101)
        alphabet = "abcdefghij:()! \n\t.-_#/0123456789中文"
        for _ in range(300):
            text = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 240)))
            result = commit_lint.lint_message(text, commit_lint.Options())
            self.assertIsInstance(result, commit_lint.Result)
            self.assertIsInstance(result.errors, list)
            self.assertIsInstance(result.warnings, list)

    def test_random_text_never_crashes_the_scanner(self) -> None:
        import git_guard as guard_module

        rng = random.Random(20260102)
        for _ in range(120):
            content = bytes(rng.randrange(256) for _ in range(rng.randint(0, 400)))
            findings = guard_module.scan_text(".", "random.bin", content, [])
            self.assertIsInstance(findings, list)


class TestNormalization(LintAssertions):
    def test_crlf_and_bom_are_normalized(self) -> None:
        self.assertValid("\ufefffeat: add login\r\n\r\nbody\r\n")

    def test_trailing_blank_lines_are_ignored(self) -> None:
        self.assertValid("feat: add login\n\n\n\n")

    def test_empty_message_is_rejected(self) -> None:
        self.assertInvalid("", "empty")
        self.assertInvalid("   \n\n", "empty")


class TestCli(unittest.TestCase):
    def test_message_valid_exits_zero(self) -> None:
        completed = run_script("commit_msg_lint.py", "--message", "feat: add login")
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("OK", completed.stdout)

    def test_message_invalid_exits_one(self) -> None:
        completed = run_script("commit_msg_lint.py", "--message", "update stuff")
        self.assertEqual(1, completed.returncode)
        self.assertIn("FAIL", completed.stdout)

    def test_quiet_suppresses_success(self) -> None:
        completed = run_script("commit_msg_lint.py", "--message", "feat: add login", "--quiet")
        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stdout.strip())

    def test_quiet_still_shows_warnings(self) -> None:
        message = "feat: add login\n\n" + "x" * 80
        completed = run_script("commit_msg_lint.py", "--message", message, "--quiet")
        self.assertEqual(0, completed.returncode)
        self.assertIn("warning:", completed.stdout)

    def test_json_output(self) -> None:
        completed = run_script("commit_msg_lint.py", "--message", "feat: add login", "--json")
        self.assertEqual(0, completed.returncode)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual(1, payload["checked"])
        self.assertEqual([], payload["results"][0]["errors"])

    def test_json_reports_errors(self) -> None:
        completed = run_script("commit_msg_lint.py", "--message", "feat: Bad.", "--json")
        self.assertEqual(1, completed.returncode)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["valid"])
        self.assertGreaterEqual(len(payload["results"][0]["errors"]), 2)

    def test_file_source(self) -> None:
        with temp_workspace() as temp:
            message_file = Path(temp) / "COMMIT_EDITMSG"
            write(message_file, "feat(cli): read message from file\n")
            completed = run_script("commit_msg_lint.py", "--file", str(message_file))
            self.assertEqual(0, completed.returncode, completed.stderr)

    def test_stdin_source(self) -> None:
        completed = run_script(
            "commit_msg_lint.py", "--stdin", stdin="fix: handle empty input\n"
        )
        self.assertEqual(0, completed.returncode, completed.stderr)

    def test_no_source_is_a_usage_error(self) -> None:
        completed = run_script("commit_msg_lint.py")
        self.assertEqual(2, completed.returncode)

    def test_empty_types_is_a_usage_error(self) -> None:
        completed = run_script("commit_msg_lint.py", "--message", "feat: x", "--types", ",")
        self.assertEqual(2, completed.returncode)

    def test_strict_promotes_warnings_to_errors(self) -> None:
        message = "feat: add login\n\n" + "x" * 80
        self.assertEqual(0, run_script("commit_msg_lint.py", "--message", message).returncode)
        completed = run_script("commit_msg_lint.py", "--message", message, "--strict")
        self.assertEqual(1, completed.returncode)

    def test_no_fixup_flag(self) -> None:
        completed = run_script("commit_msg_lint.py", "--message", "fixup! feat: add login", "--no-fixup")
        self.assertEqual(1, completed.returncode)

    def test_allow_git_revert_flag(self) -> None:
        message = 'Revert "feat: add login"'
        self.assertEqual(1, run_script("commit_msg_lint.py", "--message", message).returncode)
        completed = run_script(
            "commit_msg_lint.py", "--message", message, "--allow-git-revert"
        )
        self.assertEqual(0, completed.returncode)

    def test_custom_body_limit(self) -> None:
        message = "feat: add login\n\n" + "x" * 40
        completed = run_script("commit_msg_lint.py", "--message", message, "--max-body", "20")
        self.assertEqual(0, completed.returncode)
        self.assertIn("recommended limit is 20", completed.stdout)

    def test_missing_file_is_an_io_error(self) -> None:
        completed = run_script("commit_msg_lint.py", "--file", "does-not-exist.txt")
        self.assertEqual(2, completed.returncode)
        self.assertIn("error:", completed.stderr)

    def test_range_source(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(Path(temp) / "repo")
            write(repo / "a.txt", "a")
            commit(repo, "feat: add a", "a.txt")
            write(repo / "b.txt", "b")
            commit(repo, "bad message", "b.txt")
            write(repo / "c.txt", "c")
            commit(repo, "fix: add c", "c.txt")
            completed = run_script(
                "commit_msg_lint.py", "--range", "HEAD~2..HEAD", "--repo", str(repo)
            )
            self.assertEqual(1, completed.returncode)
            self.assertIn("1 of 2", completed.stdout)
            completed = run_script(
                "commit_msg_lint.py", "--range", "HEAD~1..HEAD", "--repo", str(repo)
            )
            self.assertEqual(0, completed.returncode)
            self.assertIn("OK", completed.stdout)

    def test_invalid_range_is_an_error(self) -> None:
        with temp_workspace() as temp:
            repo = init_repo(Path(temp) / "repo")
            completed = run_script(
                "commit_msg_lint.py", "--range", "does-not-exist..HEAD", "--repo", str(repo)
            )
            self.assertEqual(2, completed.returncode)
            self.assertIn("error:", completed.stderr)


if __name__ == "__main__":
    unittest.main()
