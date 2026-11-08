#!/usr/bin/env python3
"""Validate every skill in this repository.

Checks:
  * every SKILL.md has YAML frontmatter with name and description
  * name matches the containing directory
  * version, when present, looks like x.y.z
  * relative Markdown links resolve
  * skill names are unique
  * skills.sh.json discovery paths exist

Usage:
    python scripts/validate_skills.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTAINERS = [ROOT / "personal_skill"]
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def field(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"^{key}:\s*(.+?)\s*$", frontmatter, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip().strip('"').strip("'")


def relative_links(text: str) -> list[str]:
    links: list[str] = []
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        links.append(target.split("#", 1)[0])
    return links


def validate(skill_md: Path) -> list[str]:
    problems: list[str] = []
    rel = skill_md.relative_to(ROOT)
    text = skill_md.read_text(encoding="utf-8")

    match = FRONTMATTER_RE.match(text)
    if not match:
        return [f"{rel}: missing frontmatter"]
    frontmatter = match.group(1)

    name = field(frontmatter, "name")
    description = field(frontmatter, "description")
    version = re.search(r"^\s+version:\s*(.+?)\s*$", frontmatter, re.MULTILINE)

    if not name:
        problems.append(f"{rel}: missing name")
    else:
        if name != skill_md.parent.name:
            problems.append(f"{rel}: name '{name}' does not match directory '{skill_md.parent.name}'")
        if not NAME_RE.match(name):
            problems.append(f"{rel}: name '{name}' must match [a-z0-9-]+")
    if not description:
        problems.append(f"{rel}: missing description")
    if version and not re.fullmatch(r"\"?\d+\.\d+\.\d+\"?", version.group(1).strip()):
        problems.append(f"{rel}: version '{version.group(1).strip()}' is not x.y.z")

    body_start = match.end()
    for link in relative_links(text[body_start:]):
        if link and not (skill_md.parent / link).exists():
            problems.append(f"{rel}: broken link '{link}'")
    return problems


def main() -> int:
    skills = []
    for container in CONTAINERS:
        if not container.is_dir():
            print(f"missing container: {container.relative_to(ROOT)}", file=sys.stderr)
            return 1
        skills.extend(sorted(container.rglob("SKILL.md")))

    problems: list[str] = []
    seen: dict[str, Path] = {}
    for skill_md in skills:
        name = skill_md.parent.name
        if name in seen:
            problems.append(f"duplicate skill name '{name}': {seen[name].relative_to(ROOT)} and {skill_md.relative_to(ROOT)}")
        seen[name] = skill_md
        problems.extend(validate(skill_md))

    config = ROOT / "skills.sh.json"
    if config.exists():
        data = json.loads(config.read_text(encoding="utf-8"))
        for entry in data.get("paths", []):
            target = ROOT / entry
            if not target.is_dir():
                problems.append(f"skills.sh.json: path '{entry}' does not exist")

    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        print(f"\n{len(problems)} problem(s) in {len(skills)} skill(s).", file=sys.stderr)
        return 1

    print(f"OK: {len(skills)} skills validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
