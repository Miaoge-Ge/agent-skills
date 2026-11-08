# Agent Skills

[简体中文](README.md) | [English](README.en.md)

A collection of Agent Skills for AI coding assistants: **2** installable skills in this repository plus a maintained index of **23** third-party skills.

- [Repository skills](#repository-skills)
- [Curated catalog](#curated-catalog)
- [Installation](#installation)
- [Repository layout](#repository-layout)
- [Scripts](#scripts)
- [Usage examples](#usage-examples)
- [Versioning](#versioning)

## Repository skills

Both skills live under `personal_skill/`; each is a self-contained directory with a `SKILL.md` plus `scripts/`, `references/`, and other supporting files.

| Skill | Description |
|---|---|
| [cpp-code-standard](personal_skill/cpp-code-standard/SKILL.md) | C/C++ naming, formatting, comments, types, and modern C++ practices, with a header checker. |
| [installer-extract](personal_skill/installer-extract/SKILL.md) | Windows installer extraction and deployment, shortcuts, launch verification, and updates. |

## Curated catalog

An index of 23 third-party skills worth using, grouped by purpose. This repository only indexes them; the code, copyright, and licenses remain with the upstream repositories.

| Category | Count | Coverage |
|---|---|---|
| [Office](catalog/office.en.md) | 4 | Presentations, HTML answers, patent disclosures, software copyright materials |
| [Coding](catalog/coding.en.md) | 19 | Code quality, design and visualization, reverse engineering and security, website cloning, agent methods, skill collections |

See [catalog/README.en.md](catalog/README.en.md) for the full list, licenses, and usage notes; the Chinese version is [catalog/README.md](catalog/README.md).

## Installation

The prompt below installs only the 2 skills bundled in this repository. Third-party skills in the catalog must be installed from their own repositories.

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
│   └── installer-extract/
│       └── SKILL.md
├── catalog/
│   ├── README.md
│   ├── README.en.md
│   ├── office.md
│   ├── office.en.md
│   ├── coding.md
│   └── coding.en.md
├── scripts/
│   └── validate_skills.py
├── skills.sh.json
├── README.md
├── README.en.md
└── LICENSE
```

## Scripts

| Script | Purpose |
|---|---|
| `scripts/validate_skills.py` | Validate frontmatter, names, versions, relative links, and discovery paths for all skills. |
| `personal_skill/cpp-code-standard/scripts/check_headers.py` | Check C/C++ file headers, include guards, and `using namespace` in headers. |

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

## Versioning

Versions are recorded in each skill's `metadata.version` inside `SKILL.md`. When adding or updating a skill, bump its version, update the skill list in both READMEs, and run `scripts/validate_skills.py`. When adding or updating catalog entries, also update the pages under `catalog/` and the counts in the root READMEs.

## License

MIT — see [LICENSE](LICENSE).
