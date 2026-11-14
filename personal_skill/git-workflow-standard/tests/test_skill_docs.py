"""Validate the skill package structure and documentation."""
from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = SKILL_ROOT / "SKILL.md"
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


class TestSkillMetadata(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL_MD.read_text(encoding="utf-8")
        match = FRONTMATTER.match(self.text)
        self.assertIsNotNone(match, "SKILL.md must start with YAML frontmatter")
        self.frontmatter = match.group(1)

    def test_name_matches_directory(self) -> None:
        self.assertIn("name: git-workflow-standard", self.frontmatter)
        self.assertEqual("git-workflow-standard", SKILL_ROOT.name)

    def test_version_is_semver(self) -> None:
        self.assertRegex(self.frontmatter, r'version:\s*"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"')

    def test_description_is_present(self) -> None:
        self.assertRegex(self.frontmatter, r"description:\s*\S")

    def test_description_mentions_git_and_conventional_commits(self) -> None:
        self.assertIn("Git", self.frontmatter)
        self.assertIn("Conventional Commits", self.frontmatter)


class TestSkillLinks(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL_MD.read_text(encoding="utf-8")

    def test_every_relative_link_resolves(self) -> None:
        body = FRONTMATTER.sub("", self.text, count=1)
        checked = 0
        for target in LINK.findall(body):
            target = target.split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            checked += 1
            self.assertTrue((SKILL_ROOT / target).exists(), f"broken link: {target}")
        self.assertGreaterEqual(checked, 5)

    def test_all_references_are_linked(self) -> None:
        for path in sorted((SKILL_ROOT / "references").glob("*.md")):
            relative = path.relative_to(SKILL_ROOT).as_posix()
            self.assertIn(relative, self.text, f"{relative} is not linked from SKILL.md")

    def test_all_scripts_exist(self) -> None:
        for name in ("commit_msg_lint.py", "git_guard.py", "install_hooks.py"):
            self.assertTrue((SKILL_ROOT / "scripts" / name).is_file(), name)

    def test_no_crlf_in_documentation(self) -> None:
        for path in [SKILL_MD, *sorted((SKILL_ROOT / "references").glob("*.md"))]:
            self.assertNotIn(b"\r\n", path.read_bytes(), f"CRLF found in {path.name}")


class TestRepositoryValidation(unittest.TestCase):
    def test_repository_skill_validator_passes(self) -> None:
        validator = SKILL_ROOT.parents[1] / "scripts" / "validate_skills.py"
        if not validator.is_file():
            self.skipTest("repository validator is not available in this installation")
        completed = subprocess.run(
            [sys.executable, str(validator)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("skills validated", completed.stdout)


if __name__ == "__main__":
    unittest.main()
