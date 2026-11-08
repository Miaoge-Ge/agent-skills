# Agent Skills

[简体中文](README.md) | [English](README.en.md)

A practical collection of Agent Skills for AI coding assistants. Every skill is a self-contained directory with a `SKILL.md` plus `scripts/`, `references/`, and other supporting files.

**2 skills** in total, both under `personal_skill/`.

It also maintains a [curated third-party skill catalog](catalog/README.en.md) with 23 skills (4 office, 19 coding).

## Skills

| Skill | Description |
|---|---|
| [cpp-code-standard](personal_skill/cpp-code-standard/SKILL.md) | C/C++ naming, formatting, comments, types, and modern C++ practices, with a header checker. |
| [installer-extract](personal_skill/installer-extract/SKILL.md) | Windows installer extraction and deployment, shortcuts, launch verification, and updates. |

## Curated Skill Catalog

Beyond the skills bundled here, the repo indexes 23 third-party skills worth using:

- **Office**: PPT generation, HTML answers for hard questions, patent disclosures, and software copyright materials.
- **Coding**: code trimming, token compression, architecture diagrams, UI/UX design, reverse engineering, security audits, website cloning, knowledge graphs, agent methods, and the Anthropic / OpenAI / MiniMax / Qt / Addy Osmani / Matt Pocock collections.

See [catalog/README.en.md](catalog/README.en.md) for the full list: [Office](catalog/office.en.md) (4) and [Coding](catalog/coding.en.md) (19); the Chinese version is [catalog/README.md](catalog/README.md).

## Installation

Send the prompt below to a coding assistant with network and file access to install every skill:

```text
Install all skills from https://github.com/Miaoge-Ge/agent-skills.

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

## Repository Layout

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
├── catalog/
│   ├── README.md
│   ├── README.en.md
│   ├── office.md
│   ├── office.en.md
│   ├── coding.md
│   └── coding.en.md
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

## Usage Examples

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
