#!/usr/bin/env python3
"""Discover third-party Agent Skill repositories on GitHub.

The script searches GitHub for skill-like repositories above a star threshold,
verifies that they actually contain a ``SKILL.md`` (or a ``skills/`` /
``.claude-plugin/`` layout), resolves a version, guesses a catalog category, and
prints a Markdown report. With ``--apply`` it also merges the new rows into
``third_party_skill/README.md`` and ``third_party_skill/README.en.md``.

Requires the authenticated ``gh`` CLI (``gh auth login``), which keeps token
handling out of this script and uses the same credentials as the rest of the
repository workflow. All GitHub reads are public read-only API calls.

Usage:
    python scripts/scan_skill_repos.py                     # dry run, default 3k stars
    python scripts/scan_skill_repos.py --min-stars 5000 --limit 50
    python scripts/scan_skill_repos.py --apply             # write both catalog docs
    python scripts/scan_skill_repos.py --report candidates.md

Notes:
  * ``--apply`` copies the upstream GitHub description verbatim, so auto-added
    rows may be English in the Chinese catalog. Review and translate them before
    committing if that matters.
  * Descriptions are truncated to keep one skill per table row.
  * On Windows, the console may misdecode UTF-8 output; use ``--report <path>``
    or set ``PYTHONIOENCODING=utf-8``.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
ZH_DOC = ROOT / "third_party_skill" / "README.md"
EN_DOC = ROOT / "third_party_skill" / "README.en.md"

DEFAULT_QUERIES = [
    "topic:agent-skills",
    "topic:claude-skills",
    '"agent skills" in:name,description',
    '"SKILL.md" in:readme',
]

CATEGORY_KEYWORDS = [
    ("设计与可视化", "Design and visualization", [
        "design", "ui ", "ux", "figma", "css", "component", "diagram",
        "visual", "style", "theme", "frontend", "shadcn",
    ]),
    ("逆向与安全", "Reverse engineering and security", [
        "security", "reverse", "pentest", "vulnerab", "audit", "jailbreak",
        "exploit", "malware", "penetration",
    ]),
    ("数据采集", "Data collection", [
        "scrap", "crawl", "spider", "data extraction", "browser automation",
    ]),
    ("网站克隆", "Website cloning", [
        "clone website", "website clone", "clone any website",
    ]),
    ("办公", "Office", [
        "ppt", "powerpoint", "docx", "word", "pdf", "patent", "copyright",
        "writing", "paper", "academic", "excel", "slides",
    ]),
    ("代码质量与效率", "Code quality and efficiency", [
        "code quality", "lint", "code review", "refactor", "test",
        "token", "context", "coding", "debug",
    ]),
]

DEFAULT_CATEGORY = ("智能体与工程方法", "Agent methods", [
    "agent", "mcp", "workflow", "framework", "memory", "prompt",
])


def gh_json(path: str):
    """Run ``gh api <path>`` and parse JSON, raising on failure."""
    proc = subprocess.run(
        ["gh", "api", path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"gh api failed: {path}")
    return json.loads(proc.stdout)


def try_gh_json(path: str):
    try:
        return gh_json(path)
    except Exception:
        return None


def existing_repos() -> set[str]:
    repos: set[str] = set()
    for doc in (ZH_DOC, EN_DOC):
        if not doc.exists():
            continue
        for match in re.finditer(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", doc.read_text(encoding="utf-8")):
            repos.add(match.group(1).rstrip(").").lower())
    return repos


def search(query: str, min_stars: int, max_pages: int) -> dict[str, dict]:
    results: dict[str, dict] = {}
    full_query = f"{query} stars:>={min_stars}"
    for page in range(1, max_pages + 1):
        path = (
            "search/repositories?q="
            + quote(full_query)
            + "&sort=stars&order=desc&per_page=100&page="
            + str(page)
        )
        data = try_gh_json(path)
        if not data:
            break
        items = data.get("items", [])
        for item in items:
            results[item["full_name"].lower()] = item
        if len(items) < 100:
            break
    return results


SKILL_TOPICS = {"agent-skills", "agent-skill", "claude-skills", "claude-skill", "skills", "skill"}


def is_skill_related(repo: dict) -> bool:
    haystack = f"{repo.get('name', '')} {repo.get('description') or ''}".lower()
    topics = {topic.lower() for topic in repo.get("topics", [])}
    return "skill" in haystack or bool(topics & SKILL_TOPICS)


def is_skill_repo(repo: dict) -> bool:
    if not is_skill_related(repo):
        return False
    full_name = repo["full_name"]
    branch = repo.get("default_branch") or "main"
    tree = try_gh_json(f"repos/{full_name}/git/trees/{branch}?recursive=1")
    for entry in (tree or {}).get("tree", []):
        parts = entry["path"].split("/")
        if parts[-1].lower() == "skill.md" and len(parts) <= 3:
            return True
    names = {
        entry.get("name", "").lower()
        for entry in (try_gh_json(f"repos/{full_name}/contents") or [])
        if isinstance(entry, dict)
    }
    return bool(names & {"skills", ".claude-plugin", "plugin.json"})


def normalize_tag(tag: str) -> str:
    tag = tag.strip()
    # shadcn@4.23.0, plugin-v1.0.0, rea-agents-6.9.0 -> 4.23.0, 1.0.0, 6.9.0
    match = re.search(r"(\d+(?:\.\d+)*(?:[-.][0-9A-Za-z]+)?)$", tag)
    return match.group(1) if match else tag


def resolve_version(full_name: str, branch: str) -> str:
    release = try_gh_json(f"repos/{full_name}/releases/latest")
    if release and release.get("tag_name"):
        return normalize_tag(release["tag_name"])

    tags = try_gh_json(f"repos/{full_name}/tags?per_page=1")
    if tags and tags[0].get("name"):
        return normalize_tag(tags[0]["name"])

    for path in (".claude-plugin/plugin.json", "plugin.json", "package.json", "gemini-extension.json"):
        entry = try_gh_json(f"repos/{full_name}/contents/{quote(path)}")
        if not entry or not entry.get("content"):
            continue
        try:
            data = json.loads(base64.b64decode(entry["content"]).decode("utf-8"))
        except Exception:
            continue
        if data.get("version"):
            return str(data["version"])

    commits = try_gh_json(f"repos/{full_name}/commits")
    if commits:
        return f"{branch}@{commits[0]['sha'][:7]}"
    return f"{branch}@unknown"


def infer_category(repo: dict) -> tuple[str, str]:
    haystack = " ".join(
        [
            repo.get("name", ""),
            repo.get("description") or "",
            " ".join(repo.get("topics", [])),
        ]
    ).lower()
    for zh, en, keywords in CATEGORY_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            return zh, en
    return DEFAULT_CATEGORY[0], DEFAULT_CATEGORY[1]


def display_name(repo: dict) -> str:
    name = repo["name"]
    if name.lower() in {"skills", "agent-skills", "agent_skills", "agent-skills"}:
        return repo["full_name"]
    return name


def shorten(text: str, limit: int = 40) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def build_candidates(min_stars: int, limit: int, max_pages: int) -> list[dict]:
    known = existing_repos()
    found: dict[str, dict] = {}
    for query in DEFAULT_QUERIES:
        found.update(search(query, min_stars, max_pages))

    ranked = sorted(found.values(), key=lambda repo: repo.get("stargazers_count", 0), reverse=True)
    candidates: list[dict] = []
    seen: set[str] = set()
    for repo in ranked:
        if len(candidates) >= limit:
            break
        full_name = repo["full_name"]
        key = full_name.lower()
        if key in known or key in seen:
            continue
        if repo.get("archived") or repo.get("fork"):
            continue
        if repo.get("stargazers_count", 0) < min_stars:
            continue
        branch = repo.get("default_branch") or "main"
        if not is_skill_repo(repo):
            continue
        seen.add(key)
        zh, en = infer_category(repo)
        description = shorten(repo.get("description") or f"Skill repository: {full_name}")
        candidates.append(
            {
                "full_name": full_name,
                "name": display_name(repo),
                "url": repo["html_url"],
                "stars": repo["stargazers_count"],
                "description": description,
                "zh": zh,
                "en": en,
                "branch": branch,
                "version": resolve_version(full_name, branch),
            }
        )
    return candidates


def parse_stars(row: str) -> int:
    cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
    return int(cells[-1].replace(",", ""))


def update_doc(path: Path, candidates: list[dict], heading_key: str) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    updated = 0
    for candidate in candidates:
        heading = f"## {candidate[heading_key]}"
        try:
            start = lines.index(heading)
        except ValueError:
            continue
        end = start + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        block = lines[start:end]
        row = (
            f"| [{candidate['name']}]({candidate['url']}) "
            f"| {candidate['description']} "
            f"| {candidate['version']} "
            f"| {candidate['stars']:,} |"
        )
        row_start = next(
            (i for i, line in enumerate(block) if line.startswith("| [")),
            None,
        )
        if row_start is None:
            continue
        row_end = row_start
        while row_end < len(block) and block[row_end].startswith("|"):
            row_end += 1
        rows = block[row_start:row_end]
        if any(candidate["url"] in row_text for row_text in rows):
            continue
        rows.append(row)
        rows.sort(key=parse_stars, reverse=True)
        lines[start:end] = block[:row_start] + rows + block[row_end:]
        updated += 1
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return updated


def render_report(candidates: list[dict], min_stars: int) -> str:
    lines = [
        f"# Skill candidates (>= {min_stars:,} stars, not in catalog)",
        "",
        f"Found **{len(candidates)}** candidates.",
        "",
        "| 技能 | 分类 | 版本 | Stars | 说明 |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for candidate in candidates:
        lines.append(
            f"| [{candidate['name']}]({candidate['url']}) "
            f"| {candidate['zh']} "
            f"| {candidate['version']} "
            f"| {candidate['stars']:,} "
            f"| {candidate['description']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--min-stars", type=int, default=3000)
    parser.add_argument("--limit", type=int, default=50, help="max candidates to verify")
    parser.add_argument("--max-pages", type=int, default=3, help="search pages per query (100 repos/page)")
    parser.add_argument("--apply", action="store_true", help="merge candidates into both catalog docs")
    parser.add_argument("--report", type=Path, help="write the Markdown report to this path")
    args = parser.parse_args()

    candidates = build_candidates(args.min_stars, args.limit, args.max_pages)
    report = render_report(candidates, args.min_stars)
    print(report)

    if args.report:
        args.report.write_text(report, encoding="utf-8")
        print(f"report written to {args.report}", file=sys.stderr)

    if args.apply:
        zh_count = update_doc(ZH_DOC, candidates, "zh")
        en_count = update_doc(EN_DOC, candidates, "en")
        print(f"applied {zh_count} Chinese rows and {en_count} English rows", file=sys.stderr)
        print("review the diff and translate upstream descriptions where needed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
