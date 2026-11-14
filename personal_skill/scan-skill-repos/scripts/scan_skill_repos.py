#!/usr/bin/env python3
"""Discover third-party Agent Skill repositories on GitHub.

The script searches GitHub for skill-like repositories above a star threshold,
then also scans code for ``filename:SKILL.md`` so repositories whose name or
description never says "skill" are still discovered. It verifies the layout,
resolves a version, guesses a catalog category, and prints a Markdown report.
With ``--apply`` it also merges the new rows into ``third_party_skill/README.md``
and ``third_party_skill/README.en.md``.

Requires the authenticated ``gh`` CLI (``gh auth login``), which keeps token
handling out of this script and uses the same credentials as the rest of the
repository workflow. All GitHub reads are public read-only API calls.

Usage:
    python personal_skill/scan-skill-repos/scripts/scan_skill_repos.py
    python personal_skill/scan-skill-repos/scripts/scan_skill_repos.py --min-stars 5000 --limit 50
    python personal_skill/scan-skill-repos/scripts/scan_skill_repos.py --apply
    python personal_skill/scan-skill-repos/scripts/scan_skill_repos.py --report candidates.md
    python personal_skill/scan-skill-repos/scripts/scan_skill_repos.py --json
    python personal_skill/scan-skill-repos/scripts/scan_skill_repos.py \
        --query "topic:agent-skills" --exclude some/repo
    python personal_skill/scan-skill-repos/scripts/scan_skill_repos.py \
        --refresh --refresh-stars-only --apply

Notes:
  * ``--apply`` uses ``references/descriptions.json`` (repo -> zh/en) when it has
    an entry; otherwise it copies the upstream description, which may be English
    in the Chinese catalog. Review and translate new rows before committing.
  * Descriptions are truncated to keep one skill per table row; literal pipes are
    escaped so they do not break the table.
  * Candidates without a license are skipped unless ``--allow-no-license`` is set.
  * ``--refresh`` re-reads stars (and versions unless ``--refresh-stars-only``)
    for every repository already in the catalog and re-sorts each category.
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
import time
import unicodedata
from pathlib import Path
from urllib.parse import quote

def find_repo_root(start: Path) -> Path:
    """Walk up until the catalog is found; works from source and installed copies."""
    for parent in (start, *start.parents):
        if (parent / "third_party_skill" / "README.md").is_file():
            return parent
    return start.parents[2]


ROOT = find_repo_root(Path(__file__).resolve().parent)
ZH_DOC = ROOT / "third_party_skill" / "README.md"
EN_DOC = ROOT / "third_party_skill" / "README.en.md"
DESCRIPTIONS_PATH = Path(__file__).resolve().parent.parent / "references" / "descriptions.json"


def load_descriptions() -> dict[str, dict]:
    """Load known bilingual descriptions keyed by lower-case repo name."""
    try:
        data = json.loads(DESCRIPTIONS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {key.lower(): value for key, value in data.items()}


DESCRIPTIONS = load_descriptions()

DEFAULT_QUERIES = [
    "topic:agent-skills",
    "topic:claude-skills",
    '"agent skills" in:name,description',
    '"SKILL.md" in:readme',
]

CATEGORY_KEYWORDS = [
    ("论文与学术", "Academic research", [
        "academic", "paper", "research", "thesis", "citation", "scholar",
        "scientific", "论文", "学术",
    ]),
    ("写作与润色", "Writing and editing", [
        "writing", "prose", "humanize", "slop", "tone", "copywriting",
        "写作", "润色",
    ]),
    ("文档与演示", "Documents and presentations", [
        "ppt", "slide", "deck", "docx", "word", "pdf", "office",
        "presentation", "document", "文档", "演示",
    ]),
    ("设计与 UI", "Design and UI", [
        "design", "ui ", "ux", "figma", "css", "component", "shadcn",
        "interface", "设计",
    ]),
    ("图表与可视化", "Diagrams and visualization", [
        "diagram", "graph", "chart", "visualiz", "drawio",
        "knowledge graph", "图表",
    ]),
    ("图像与插画", "Images and illustration", [
        "image", "illustration", "drawing", "插画", "图像",
    ]),
    ("视频与媒体", "Video and media", [
        "video", "film", "movie", "media", "subtitle", "caption", "视频",
    ]),
    ("代码质量与效率", "Code quality and efficiency", [
        "code review", "lint", "refactor", "debug", "code quality", "代码",
    ]),
    ("逆向工程", "Reverse engineering", [
        "reverse", "binary", "decompile", "ghidra", "逆向",
    ]),
    ("安全与审计", "Security and audit", [
        "security", "audit", "vulnerab", "pentest", "jailbreak", "安全",
    ]),
    ("网页采集", "Web scraping", [
        "scrap", "crawl", "browser automation", "data extraction", "seo",
        "采集",
    ]),
    ("记忆与上下文", "Memory and context", [
        "memory", "context", "recall", "knowledge base", "second brain",
        "记忆",
    ]),
    ("技能管理与加载", "Skill management", [
        "skill loader", "skills manager", "plugin", "marketplace", "catalog",
        "技能管理",
    ]),
    ("智能体框架", "Agent frameworks", [
        "agent", "workflow", "mcp", "orchestrat", "framework", "prompt",
        "智能体",
    ]),
    ("学习与知识", "Learning and knowledge", [
        "learn", "tutor", "study", "course", "book", "学习",
    ]),
    ("AI 工具与应用", "AI tools and apps", [
        "app", "tool", "assistant", "productivity", "工具",
    ]),
    ("技能合集", "Skill collections", [
        "awesome", "collection", "curated", "合集",
    ]),
    ("网站克隆", "Website cloning", [
        "clone website", "website clone", "clone any website",
    ]),
]

DEFAULT_CATEGORY = ("智能体框架", "Agent frameworks")


def gh_json(path: str, retries: int = 3):
    """Run ``gh api <path>`` and parse JSON, retrying on rate limits."""
    last_error = ""
    for attempt in range(retries):
        proc = subprocess.run(
            ["gh", "api", path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode == 0:
            return json.loads(proc.stdout)
        last_error = proc.stderr.strip() or f"gh api failed: {path}"
        if "rate limit" in last_error.lower() or "secondary rate" in last_error.lower():
            time.sleep(5 * (attempt + 1))
            continue
        break
    raise RuntimeError(last_error)


def try_gh_json(path: str):
    try:
        return gh_json(path)
    except Exception:
        return None


def gh_graphql(query: str, retries: int = 3):
    """Run a GraphQL query through ``gh api graphql`` with the same retries."""
    last_error = ""
    for attempt in range(retries):
        proc = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={query}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode == 0:
            return json.loads(proc.stdout).get("data", {})
        last_error = proc.stderr.strip() or "gh graphql failed"
        if "rate limit" in last_error.lower() or "secondary rate" in last_error.lower():
            time.sleep(5 * (attempt + 1))
            continue
        break
    raise RuntimeError(last_error)


def normalize_graphql_repo(node: dict) -> dict:
    full_name = node["nameWithOwner"]
    owner, name = full_name.split("/", 1)
    topics = [
        entry["topic"]["name"]
        for entry in (node.get("repositoryTopics") or {}).get("nodes", [])
        if entry and entry.get("topic")
    ]
    return {
        "full_name": full_name,
        "name": name,
        "html_url": f"https://github.com/{full_name}",
        "stargazers_count": node.get("stargazerCount", 0),
        "archived": bool(node.get("isArchived")),
        "fork": bool(node.get("isFork")),
        "description": node.get("description"),
        "license": {"spdx_id": node["licenseInfo"]["spdxId"]} if node.get("licenseInfo") else None,
        "default_branch": (node.get("defaultBranchRef") or {}).get("name") or "main",
        "topics": topics,
    }


def graphql_repo_metadata(full_names: list[str]) -> dict[str, dict]:
    """Batch repository metadata (stars, license, topics, ...) via GraphQL."""
    result: dict[str, dict] = {}
    for start in range(0, len(full_names), 40):
        chunk = full_names[start : start + 40]
        parts = []
        for index, full_name in enumerate(chunk):
            owner, name = full_name.split("/", 1)
            parts.append(
                f'r{index}: repository(owner: "{owner}", name: "{name}") {{'
                " nameWithOwner stargazerCount isArchived isFork description"
                " licenseInfo { spdxId }"
                " defaultBranchRef { name }"
                " repositoryTopics(first: 20) { nodes { topic { name } } } }"
            )
        query = "query {\n" + "\n".join(parts) + "\n}"
        try:
            data = gh_graphql(query)
        except Exception:
            continue
        for index, full_name in enumerate(chunk):
            node = data.get(f"r{index}")
            if node:
                result[full_name.lower()] = normalize_graphql_repo(node)
    return result


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


def is_skill_path(path: str) -> bool:
    """True for a root SKILL.md or a ``skills/<name>/SKILL.md`` layout.

    This deliberately rejects lookalikes such as ``docs/skill/SKILL.md`` or
    ``examples/demo/SKILL.md`` while accepting nested plugin layouts.
    """
    parts = path.split("/")
    if len(parts) == 1:
        return parts[0].lower() == "skill.md"
    if len(parts) == 2:
        return parts[0].lower() == "skills" and parts[1].lower() == "skill.md"
    return parts[-3].lower() == "skills" and parts[-1].lower() == "skill.md"


def search_code_repos(max_pages: int, max_repos: int) -> dict[str, dict]:
    """Find repositories that contain a SKILL.md, whatever the repo is called.

    Repository search only matches names/descriptions/topics, so a skill repo
    without the word "skill" in its metadata is invisible to it. Code search on
    the file name closes that gap; metadata (stars, license) is fetched later.
    """
    repos: dict[str, dict] = {}
    query = "filename:SKILL.md"
    for page in range(1, max_pages + 1):
        data = try_gh_json("search/code?q=" + quote(query) + f"&per_page=100&page={page}")
        if not data:
            break
        items = data.get("items", [])
        for item in items:
            if not is_skill_path(item.get("path", "")):
                continue
            repo = item.get("repository") or {}
            full_name = repo.get("full_name")
            if full_name:
                repos.setdefault(
                    full_name.lower(),
                    {"full_name": full_name, "_skill_path": item["path"]},
                )
            if len(repos) >= max_repos:
                break
        if len(repos) >= max_repos or len(items) < 100:
            break
    return repos


def find_skill(repo: dict) -> tuple[bool, str | None]:
    """Return (has_skill_layout, SKILL.md path)."""
    stored = repo.get("_skill_path")
    if stored:
        return True, stored
    full_name = repo["full_name"]
    branch = repo.get("default_branch") or "main"
    tree = try_gh_json(f"repos/{full_name}/git/trees/{branch}?recursive=1")
    for entry in (tree or {}).get("tree", []):
        if is_skill_path(entry["path"]):
            return True, entry["path"]
    names = {
        entry.get("name", "").lower()
        for entry in (try_gh_json(f"repos/{full_name}/contents") or [])
        if isinstance(entry, dict)
    }
    return bool(names & {"skills", ".claude-plugin", "plugin.json"}), None


def verify_skill(repo: dict, skill_path: str) -> bool:
    """Check that the SKILL.md has Agent Skills frontmatter and real content."""
    entry = try_gh_json(f"repos/{repo['full_name']}/contents/{quote(skill_path)}")
    if not entry or not entry.get("content"):
        return False
    try:
        text = base64.b64decode(entry["content"]).decode("utf-8", errors="replace")
    except Exception:
        return False
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not match:
        return False
    frontmatter = match.group(1)
    if not re.search(r"(?m)^name:\s*\S", frontmatter):
        return False
    if not re.search(r"(?m)^description:\s*\S", frontmatter):
        return False
    return len(text[match.end():].strip()) >= 100


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
        if data.get("private"):
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
    if name.lower() in {"skills", "agent-skills", "agent_skills"}:
        return repo["full_name"]
    return name


def display_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1 for char in text)


def shorten(text: str, limit: int = 40) -> str:
    text = re.sub(r"\s+", " ", text or "").strip().replace("|", "\\|")
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:-") + "…"


def build_candidates(
    min_stars: int,
    limit: int,
    max_pages: int,
    queries: list[str] | None = None,
    excludes: list[str] | None = None,
    allow_no_license: bool = False,
    code_search: bool = True,
    code_pages: int = 10,
    max_code_repos: int = 300,
    verify: bool = True,
) -> list[dict]:
    known = existing_repos()
    skipped = {value.lower() for value in (excludes or [])}
    found: dict[str, dict] = {}
    for query in (queries or DEFAULT_QUERIES):
        found.update(search(query, min_stars, max_pages))

    if code_search:
        code_repos = search_code_repos(code_pages, max_code_repos)
        pending = {
            key: repo
            for key, repo in code_repos.items()
            if key not in known and key not in skipped and key not in found
        }
        metadata = graphql_repo_metadata([repo["full_name"] for repo in pending.values()])
        for key, repo in pending.items():
            info = metadata.get(key) or try_gh_json(f"repos/{repo['full_name']}")
            if info:
                info["_skill_path"] = repo.get("_skill_path")
                found[key] = info
        if pending:
            print(f"  resolved metadata for {len(pending)} code-search repositories", file=sys.stderr)

    ranked = sorted(found.values(), key=lambda repo: repo.get("stargazers_count", 0), reverse=True)
    candidates: list[dict] = []
    seen: set[str] = set()
    for repo in ranked:
        if len(candidates) >= limit:
            break
        full_name = repo["full_name"]
        key = full_name.lower()
        if key in known or key in seen or key in skipped:
            continue
        if repo.get("archived") or repo.get("fork"):
            continue
        if repo.get("stargazers_count", 0) < min_stars:
            continue
        if not allow_no_license and not repo.get("license"):
            continue
        branch = repo.get("default_branch") or "main"
        has_layout, skill_path = find_skill(repo)
        if not has_layout:
            continue
        if verify and (not skill_path or not verify_skill(repo, skill_path)):
            continue
        seen.add(key)
        zh, en = infer_category(repo)
        name = display_name(repo)
        version = resolve_version(full_name, branch)
        budget = min(40, max(16, 88 - display_width(name) - display_width(version) - 8))
        description = shorten(repo.get("description") or f"Skill repository: {full_name}", budget)
        override = DESCRIPTIONS.get(key)
        zh_desc = override["zh"] if override else description
        en_desc = override["en"] if override else description
        candidates.append(
            {
                "full_name": full_name,
                "name": name,
                "url": repo["html_url"],
                "stars": repo["stargazers_count"],
                "description": description,
                "zh_desc": zh_desc,
                "en_desc": en_desc,
                "zh": zh,
                "en": en,
                "branch": branch,
                "version": version,
            }
        )
    return candidates


def split_row(row: str) -> list[str]:
    """Split a Markdown table row without breaking on escaped pipes."""
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", row.strip().strip("|"))]


def join_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def parse_stars(row: str) -> int:
    return int(split_row(row)[-1].replace(",", ""))


def update_doc(path: Path, candidates: list[dict], heading_key: str, desc_key: str = "description") -> int:
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
            f"| {candidate.get(desc_key) or candidate['description']} "
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


def catalog_records(path: Path) -> list[dict]:
    """Return unique catalog rows with their current version and stars."""
    records: list[dict] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ["):
            continue
        cells = split_row(line)
        if len(cells) != 4:
            continue
        match = re.search(r"github\.com/([^)]+)\)", cells[0])
        if not match:
            continue
        repo = match.group(1)
        if repo.lower() in seen:
            continue
        seen.add(repo.lower())
        records.append({"repo": repo, "version": cells[2], "stars": int(cells[3].replace(",", ""))})
    return records


def refresh_metadata(records: list[dict], stars_only: bool = False) -> dict[str, dict]:
    updates: dict[str, dict] = {}
    metadata = graphql_repo_metadata([record["repo"] for record in records])
    for record in records:
        repo = record["repo"]
        info = metadata.get(repo.lower()) or try_gh_json(f"repos/{repo}")
        if not info:
            continue
        branch = info.get("default_branch") or "main"
        version = record["version"] if stars_only else resolve_version(repo, branch)
        updates[repo.lower()] = {"stars": info["stargazers_count"], "version": version}
    return updates


def apply_refresh(path: Path, updates: dict[str, dict]) -> int:
    """Rewrite version/star cells for existing rows and re-sort each section."""
    lines = path.read_text(encoding="utf-8").splitlines()
    changed = 0
    i = 0
    while i < len(lines):
        if not lines[i].startswith("## "):
            i += 1
            continue
        end = i + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        block = lines[i:end]
        row_indexes = [j for j, line in enumerate(block) if line.startswith("| [")]
        if row_indexes:
            first, last = row_indexes[0], row_indexes[-1]
            rows = block[first : last + 1]
            for j, row in enumerate(rows):
                cells = split_row(row)
                if len(cells) != 4:
                    continue
                match = re.search(r"github\.com/([^)]+)\)", cells[0])
                if not match:
                    continue
                update = updates.get(match.group(1).lower())
                if not update:
                    continue
                new_stars = f"{update['stars']:,}"
                if cells[2] != update["version"] or cells[3] != new_stars:
                    changed += 1
                cells[2] = update["version"]
                cells[3] = new_stars
                rows[j] = join_row(cells)
            rows.sort(key=parse_stars, reverse=True)
            block[first : last + 1] = rows
        lines[i:end] = block
        i = end
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


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
    parser.add_argument("--query", action="append", default=[], help="search query (repeatable; replaces the defaults)")
    parser.add_argument("--exclude", action="append", default=[], help="owner/repo to skip (repeatable)")
    parser.add_argument("--allow-no-license", action="store_true", help="keep candidates without a license")
    parser.add_argument("--no-verify", dest="verify", action="store_false", help="skip SKILL.md frontmatter verification")
    parser.add_argument("--no-code-search", dest="code_search", action="store_false", help="disable filename:SKILL.md code search")
    parser.add_argument("--code-pages", type=int, default=10, help="code search pages (100 files/page)")
    parser.add_argument("--max-code-repos", type=int, default=300, help="max repositories to resolve from code search")
    parser.add_argument("--apply", action="store_true", help="merge candidates into both catalog docs")
    parser.add_argument("--refresh", action="store_true", help="refresh stars and versions of existing rows")
    parser.add_argument("--refresh-stars-only", action="store_true", help="skip version lookups during refresh")
    parser.add_argument("--json", action="store_true", help="print candidates as JSON")
    parser.add_argument("--report", type=Path, help="write the Markdown report to this path")
    args = parser.parse_args()

    if args.refresh or args.refresh_stars_only:
        records = catalog_records(ZH_DOC)
        updates = refresh_metadata(records, stars_only=args.refresh_stars_only)
        print(f"refreshed metadata for {len(updates)} repositories", file=sys.stderr)
        if args.apply:
            zh_count = apply_refresh(ZH_DOC, updates)
            en_count = apply_refresh(EN_DOC, updates)
            print(f"updated {zh_count} Chinese rows and {en_count} English rows", file=sys.stderr)
        else:
            print("dry run: pass --apply to write the refreshed rows", file=sys.stderr)
        return 0

    candidates = build_candidates(
        args.min_stars,
        args.limit,
        args.max_pages,
        queries=args.query or None,
        excludes=args.exclude,
        allow_no_license=args.allow_no_license,
        code_search=args.code_search,
        code_pages=args.code_pages,
        max_code_repos=args.max_code_repos,
        verify=args.verify,
    )
    report = render_report(candidates, args.min_stars)
    print(json.dumps(candidates, ensure_ascii=False, indent=2) if args.json else report)

    if args.report:
        args.report.write_text(report, encoding="utf-8")
        print(f"report written to {args.report}", file=sys.stderr)

    if args.apply:
        zh_count = update_doc(ZH_DOC, candidates, "zh", "zh_desc")
        en_count = update_doc(EN_DOC, candidates, "en", "en_desc")
        print(f"applied {zh_count} Chinese rows and {en_count} English rows", file=sys.stderr)
        print("review the diff and translate upstream descriptions where needed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
