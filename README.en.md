# Agent Skills

[简体中文](README.md) | [English](README.en.md)

Agent Skills for AI coding assistants: engineering standards written as instructions an agent can follow, so C/C++, Git commits, and Windows deployments stay consistent; plus a curated, use-based index of third-party skills to explore. Bundled skills follow the standard Agent Skills format and work in any tool that supports it.

- [Repository skills](#repository-skills)
- [Third-party skills](#third-party-skills)
- [Installation](#installation)
- [Repository layout](#repository-layout)
- [Scripts](#scripts)
- [Usage examples](#usage-examples)
- [Versioning](#versioning)

## Repository skills

All bundled skills live under `personal_skill/`; each is a self-contained directory with a `SKILL.md` plus `scripts/`, `references/`, and other supporting files.

| Skill | Description |
|---|---|
| [cpp-code-standard](personal_skill/cpp-code-standard/SKILL.md) | C/C++ naming, formatting, comments, types, and modern C++ practices, with a header checker. |
| [git-workflow-standard](personal_skill/git-workflow-standard/SKILL.md) | Git workflow standards: Conventional Commits, branch naming, merging and releases, and history safety, with commit linting, index scanning, and hook installation scripts. |
| [installer-extract](personal_skill/installer-extract/SKILL.md) | Windows installer extraction and deployment, shortcuts, launch verification, and updates. |

## Third-party skills

Third-party skills and tools are indexed by use under [third_parity_skill/](third_parity_skill/README.en.md): [Chinese](third_parity_skill/README.md) | [English](third_parity_skill/README.en.md).

This repository only indexes these skills; the code, copyright, and licenses remain with the upstream repositories. Read the upstream LICENSE before use.

## Installation

The prompt below installs only the skills bundled in this repository. Third-party skills must be installed from their own repositories.

Send this prompt to a coding assistant with network and file access:

```text
Install all bundled skills from https://github.com/Miaoge-Ge/agent-skills.

The repository uses the standard Agent Skills format. Skills live under personal_skill/.
Recursively find every skill directory containing a SKILL.md under that folder, read the SKILL.md first, then copy the complete skill directory (including references, scripts, and all other supporting files) into the user-level skills directory supported by this tool.
If a skill with the same name already exists, compare versions first and preserve local customizations.
When done, list the installed skill names, versions, and installation paths.
```

To install a single skill, replace the path with the target skill directory, for example:

```text
Install the skill personal_skill/cpp-code-standard from https://github.com/Miaoge-Ge/agent-skills.

The repository uses the standard Agent Skills format. Read the SKILL.md in that directory first, then copy the complete skill directory (including references, scripts, and all other supporting files) into the user-level skills directory supported by this tool.
If a skill with the same name already exists, compare versions first and preserve local customizations.
When done, report the skill name, version, and installation path.
```

## Repository layout

```text
agent-skills/
├── personal_skill/
│   ├── cpp-code-standard/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── scripts/check_headers.py
│   ├── git-workflow-standard/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── scripts/
│   │   └── tests/
│   └── installer-extract/
│       └── SKILL.md
├── third_parity_skill/ # third-party skill index
│   ├── README.md
│   └── README.en.md
├── cyg_skill/          # private submodule, pointer only
├── scripts/
│   └── validate_skills.py
├── skills.sh.json
├── README.md
├── README.en.md
└── LICENSE
```

`cyg_skill/` is a submodule pointing at the private [cyg-skills](https://github.com/Miaoge-Ge/cyg-skills) repository: this public repository stores only a commit pointer, never the files. Without access to that private repository, cloning skips it, which is expected.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/validate_skills.py` | Validate frontmatter, names, versions, relative links, and discovery paths for all skills. |
| `personal_skill/cpp-code-standard/scripts/check_headers.py` | Check C/C++ file headers, include guards, and `using namespace` in headers. |
| `personal_skill/git-workflow-standard/scripts/` | `commit_msg_lint.py` validates Conventional Commits; `git_guard.py` scans the index for secrets, large files, and conflict markers; `install_hooks.py` installs or removes the commit-msg and pre-commit hooks. |

```bash
python scripts/validate_skills.py
```

## Usage examples

```text
Use cpp-code-standard to check my current C/C++ changes, and do not modify code yet.
```

```text
Use installer-extract to unpack the installer and verify shortcuts and launch.
```

```text
Use git-workflow-standard to check the commit messages on this branch and write a Conventional Commits commit.
```

## Versioning

Versions are recorded in each skill's `metadata.version` inside `SKILL.md`. When adding or updating a skill, bump its version, update the skill list in both READMEs, and run `scripts/validate_skills.py`. Skills with automated tests should run their suite before release, for example `cd personal_skill/git-workflow-standard && python -m unittest discover -s tests`. When adding or updating third-party entries, update [third_parity_skill/README.md](third_parity_skill/README.md) and [third_parity_skill/README.en.md](third_parity_skill/README.en.md).

## License

MIT — see [LICENSE](LICENSE).
