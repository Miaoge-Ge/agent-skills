# Agent Skills

[简体中文](README.md) | [English](README.en.md)

A collection of Agent Skills for AI coding assistants: **2** installable skills in this repository plus **23** curated third-party skills.

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

This repository only indexes these skills; the code, copyright, and licenses remain with the upstream repositories. Read the upstream LICENSE before use.

### Office (4)

| Skill | Description | License |
|---|---|---|
| [ppt-master](https://github.com/hugohe3/ppt-master) | Turn documents or topics into editable native PowerPoint decks, with charts, transitions, animations, and narration from speaker notes. | MIT |
| [answer-me-with-html](https://github.com/QingYunA/answer-me-with-html) | Answer hard questions with a single, readable HTML page. | MIT |
| [patent-disclosure-skill](https://github.com/handsomestWei/patent-disclosure-skill) | Chinese patent mining and disclosure drafting (invention / utility model / design), with patent reading, policy tracking, and office-action support. | MIT |
| [SoftwareCopyright-Skill](https://github.com/Fokkyp/SoftwareCopyright-Skill) | Read a local project and generate the full set of .docx materials for a Chinese software copyright application (application form, manual, source-code excerpts, and more). | AGPL-3.0 |

> `SoftwareCopyright-Skill` is licensed under AGPL-3.0; read its LICENSE before redistributing or modifying it.

### Coding (19)

#### Code quality and efficiency (3)

| Skill | Description | License |
|---|---|---|
| [ponytail](https://github.com/DietrichGebert/ponytail) | Trim code, over-engineering, and redundant complexity; supports code review. | MIT |
| [caveman](https://github.com/JuliusBrussee/caveman) | Compress coding-agent replies and context to cut token usage. | Apache-2.0 |
| [i-have-adhd](https://github.com/ayghri/i-have-adhd) | Puts the answer first and keeps coding-agent output short and direct — ADHD-friendly. | MIT |

#### Design and visualization (4)

| Skill | Description | License |
|---|---|---|
| [archify](https://github.com/tt-a1i/archify) | Turn ideas, plans, and architectures into interactive diagrams. | Apache-2.0 |
| [hallmark](https://github.com/Nutlope/hallmark) | Web UI design and polish that avoids templated AI-generated looks. | MIT |
| [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Professional UI/UX design intelligence for coding agents. | MIT |
| [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) | Convert code into an interactive, searchable, queryable knowledge graph. | MIT |

#### Reverse engineering and security (3)

| Skill | Description | License |
|---|---|---|
| [reagent](https://github.com/Dryxio/reagent) | AI reverse-engineering agent that reconstructs and validates C/C++ from binaries. | MIT |
| [rea](https://github.com/morluto/rea) | Reverse-engineering and behavior-analysis toolkit for apps and native binaries. | MIT |
| [security-audit-skill](https://github.com/cloudflare/security-audit-skill) | Code and architecture security audits with verified findings and structured reports. | MIT |

#### Website cloning (1)

| Skill | Description | License |
|---|---|---|
| [ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) | Clone any website with one command. | MIT |

#### Agent methods (2)

| Skill | Description | License |
|---|---|---|
| [ECC](https://github.com/affaan-m/ECC) | A performance-optimization system for agent harnesses: skills, instincts, memory, security, and research-first development for Claude Code, Codex, and more. | MIT |
| [superpowers](https://github.com/obra/superpowers) | An agentic skills framework and software-development methodology covering the full path from idea to delivery. | MIT |

#### Skill collections (6)

| Skill | Description | License |
|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | Anthropic's official Agent Skills examples for documents, design, MCP, web testing, and more. | Apache-2.0 (per skill) |
| [openai/skills](https://github.com/openai/skills) | OpenAI Codex official skill catalog with curated and experimental skills; deprecated upstream. | See each skill |
| [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) | MiniMax official Agent Skills collection. | MIT |
| [TheQtCompanyRnD/agent-skills](https://github.com/TheQtCompanyRnD/agent-skills) | Qt's official AI engineering skills for Qt / QML development and quality checks. | BSD-3-Clause |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Production-grade engineering skills for AI coding agents, covering define, plan, build, verify, review, and ship. | MIT |
| [mattpocock/skills](https://github.com/mattpocock/skills) | Everyday engineering skills from the author's own .agents directory. | MIT |

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

Versions are recorded in each skill's `metadata.version` inside `SKILL.md`. When adding or updating a skill, bump its version, update the skill list in both READMEs, and run `scripts/validate_skills.py`. When adding or updating catalog entries, also update the lists and counts in both READMEs.

## License

MIT — see [LICENSE](LICENSE).
