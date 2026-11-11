# Agent Skills

[简体中文](README.md) | [English](README.en.md)

Agent Skills for AI coding assistants: engineering standards written as instructions an agent can follow, so C/C++, Git commits, and Windows deployments stay consistent; plus a curated, use-based index of third-party skills to explore. Bundled skills follow the standard Agent Skills format and work in any tool that supports it.

- [Repository skills](#repository-skills)
- [Curated catalog](#curated-catalog)
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

## Curated catalog

Third-party skills and tools, grouped by use; repository links, one-line descriptions, and licenses live on the per-type pages under [catalog/](catalog/README.en.md). This repository only indexes these skills; the code, copyright, and licenses remain with the upstream repositories. Read the upstream LICENSE before use.

### Office (4) · [details](catalog/office.en.md)

[ppt-master](https://github.com/hugohe3/ppt-master), [answer-me-with-html](https://github.com/QingYunA/answer-me-with-html), [patent-disclosure-skill](https://github.com/handsomestWei/patent-disclosure-skill), [SoftwareCopyright-Skill](https://github.com/Fokkyp/SoftwareCopyright-Skill)

> `SoftwareCopyright-Skill` is licensed under AGPL-3.0; check compliance before redistributing or modifying it.

### Code quality and efficiency (3) · [details](catalog/code-quality.en.md)

[ponytail](https://github.com/DietrichGebert/ponytail), [caveman](https://github.com/JuliusBrussee/caveman), [i-have-adhd](https://github.com/ayghri/i-have-adhd)

### Design and visualization (5) · [details](catalog/design.en.md)

[archify](https://github.com/tt-a1i/archify), [diagram-design](https://github.com/cathrynlavery/diagram-design), [hallmark](https://github.com/Nutlope/hallmark), [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)

### Reverse engineering and security (4) · [details](catalog/reverse-engineering.en.md)

[reagent](https://github.com/Dryxio/reagent), [rea](https://github.com/morluto/rea), [security-audit-skill](https://github.com/cloudflare/security-audit-skill), [craft-anything](https://github.com/storytold/craft-anything)

### Website cloning (1) · [details](catalog/website-cloning.en.md)

[ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template)

### Data collection (1) · [details](catalog/data-collection.en.md)

[Scrapling](https://github.com/D4Vinci/Scrapling)

### Agent methods (2) · [details](catalog/agent-methods.en.md)

[ECC](https://github.com/affaan-m/ECC), [superpowers](https://github.com/obra/superpowers)

### Skill collections (8) · [details](catalog/collections.en.md)

[anthropics/skills](https://github.com/anthropics/skills), [openai/skills](https://github.com/openai/skills), [google-gemini/gemini-skills](https://github.com/google-gemini/gemini-skills), [zai-org/GLM-skills](https://github.com/zai-org/GLM-skills), [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills), [TheQtCompanyRnD/agent-skills](https://github.com/TheQtCompanyRnD/agent-skills), [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), [mattpocock/skills](https://github.com/mattpocock/skills)

## Installation

The prompt below installs only the skills bundled in this repository. Third-party skills in the catalog must be installed from their own repositories.

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
├── catalog/            # third-party skill index, one page per type
│   ├── README.md / README.en.md
│   ├── office.md / office.en.md
│   ├── code-quality.md / code-quality.en.md
│   ├── design.md / design.en.md
│   ├── reverse-engineering.md / reverse-engineering.en.md
│   ├── website-cloning.md / website-cloning.en.md
│   ├── data-collection.md / data-collection.en.md
│   ├── agent-methods.md / agent-methods.en.md
│   └── collections.md / collections.en.md
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

Versions are recorded in each skill's `metadata.version` inside `SKILL.md`. When adding or updating a skill, bump its version, update the skill list in both READMEs, and run `scripts/validate_skills.py`. Skills with automated tests should run their suite before release, for example `cd personal_skill/git-workflow-standard && python -m unittest discover -s tests`. When adding or updating catalog entries, also update the matching category page, the counts in [catalog/README.en.md](catalog/README.en.md), and the skill list in both root READMEs.

## License

MIT — see [LICENSE](LICENSE).
