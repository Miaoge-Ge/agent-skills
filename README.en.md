# Agent Skills

[简体中文](README.md) | [English](README.en.md)

A collection of Agent Skills for AI coding assistants: **3** installable skills (C/C++ standards, Git workflow standards, Windows installer extraction) plus **26** curated third-party skills.

- [Repository skills](#repository-skills)
- [Curated catalog](#curated-catalog)
- [Installation](#installation)
- [Repository layout](#repository-layout)
- [Scripts](#scripts)
- [Usage examples](#usage-examples)
- [Versioning](#versioning)

## Repository skills

All three skills live under `personal_skill/`; each is a self-contained directory with a `SKILL.md` plus `scripts/`, `references/`, and other supporting files.

| Skill | Description |
|---|---|
| [cpp-code-standard](personal_skill/cpp-code-standard/SKILL.md) | C/C++ naming, formatting, comments, types, and modern C++ practices, with a header checker. |
| [git-workflow-standard](personal_skill/git-workflow-standard/SKILL.md) | Git workflow standards: Conventional Commits, branch naming, merging and releases, and history safety, with commit linting, index scanning, and hook installation scripts. |
| [installer-extract](personal_skill/installer-extract/SKILL.md) | Windows installer extraction and deployment, shortcuts, launch verification, and updates. |

## Curated catalog

This repository only indexes these skills; the code, copyright, and licenses remain with the upstream repositories. Read the upstream LICENSE before use.

### Office (4)

| Skill | Description |
|---|---|
| [ppt-master](https://github.com/hugohe3/ppt-master) | Turn documents or topics into editable native PowerPoint decks, with charts, transitions, animations, and narration from speaker notes. |
| [answer-me-with-html](https://github.com/QingYunA/answer-me-with-html) | Answer hard questions with a single, readable HTML page. |
| [patent-disclosure-skill](https://github.com/handsomestWei/patent-disclosure-skill) | Chinese patent mining and disclosure drafting (invention / utility model / design), with patent reading, policy tracking, and office-action support. |
| [SoftwareCopyright-Skill](https://github.com/Fokkyp/SoftwareCopyright-Skill) | Read a local project and generate the full set of .docx materials for a Chinese software copyright application (application form, manual, source-code excerpts, and more). |

> `SoftwareCopyright-Skill` is licensed under AGPL-3.0; check compliance before redistributing or modifying it.

### Coding (22)

#### Code quality and efficiency (3)

| Skill | Description |
|---|---|
| [ponytail](https://github.com/DietrichGebert/ponytail) | Trim code, over-engineering, and redundant complexity; supports code review. |
| [caveman](https://github.com/JuliusBrussee/caveman) | Compress coding-agent replies and context to cut token usage. |
| [i-have-adhd](https://github.com/ayghri/i-have-adhd) | Puts the answer first and keeps coding-agent output short and direct — ADHD-friendly. |

#### Design and visualization (5)

| Skill | Description |
|---|---|
| [archify](https://github.com/tt-a1i/archify) | Turn ideas, plans, and architectures into interactive diagrams. |
| [diagram-design](https://github.com/cathrynlavery/diagram-design) | Editorial diagram design for coding agents: 45 diagram types as self-contained HTML + SVG. |
| [hallmark](https://github.com/Nutlope/hallmark) | Web UI design and polish that avoids templated AI-generated looks. |
| [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Professional UI/UX design intelligence for coding agents. |
| [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) | Convert code into an interactive, searchable, queryable knowledge graph. |

#### Reverse engineering and security (3)

| Skill | Description |
|---|---|
| [reagent](https://github.com/Dryxio/reagent) | AI reverse-engineering agent that reconstructs and validates C/C++ from binaries. |
| [rea](https://github.com/morluto/rea) | Reverse-engineering and behavior-analysis toolkit for apps and native binaries. |
| [security-audit-skill](https://github.com/cloudflare/security-audit-skill) | Code and architecture security audits with verified findings and structured reports. |

#### Website cloning (1)

| Skill | Description |
|---|---|
| [ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) | Clone any website with one command. |

#### Agent methods (2)

| Skill | Description |
|---|---|
| [ECC](https://github.com/affaan-m/ECC) | A performance-optimization system for mainstream coding agents: skills, instincts, memory, security, and research-first development. |
| [superpowers](https://github.com/obra/superpowers) | An agentic skills framework and software-development methodology covering the full path from idea to delivery. |

#### Skill collections (8)

| Skill | Description |
|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | Anthropic's official Agent Skills examples for documents, design, MCP, web testing, and more. |
| [openai/skills](https://github.com/openai/skills) | OpenAI Codex official skill catalog with curated and experimental skills; deprecated upstream. |
| [google-gemini/gemini-skills](https://github.com/google-gemini/gemini-skills) | Official skills for the Gemini API, SDK, and model/agent interactions. |
| [zai-org/GLM-skills](https://github.com/zai-org/GLM-skills) | Official skills for the GLM family of models, covering multimodal, OCR, vision, and more. |
| [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) | MiniMax official Agent Skills collection. |
| [TheQtCompanyRnD/agent-skills](https://github.com/TheQtCompanyRnD/agent-skills) | Qt's official AI engineering skills for Qt / QML development and quality checks. |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Production-grade engineering skills for AI coding agents, covering define, plan, build, verify, review, and ship. |
| [mattpocock/skills](https://github.com/mattpocock/skills) | Everyday engineering skills from the author's own .agents directory. |

## Installation

The prompt below installs only the 3 skills bundled in this repository. Third-party skills in the catalog must be installed from their own repositories.

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

Versions are recorded in each skill's `metadata.version` inside `SKILL.md`. When adding or updating a skill, bump its version, update the skill list in both READMEs, and run `scripts/validate_skills.py`. Skills with automated tests should run their suite before release, for example `cd personal_skill/git-workflow-standard && python -m unittest discover -s tests`. When adding or updating catalog entries, also update the lists and counts in both READMEs.

## License

MIT — see [LICENSE](LICENSE).
