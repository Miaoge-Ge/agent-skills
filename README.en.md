# Agent Skills

[简体中文](README.md) | [English](README.en.md)

A practical collection of Agent Skills for AI coding assistants. The `skill/` folder keeps only skills backed by scripts or executable tooling; every skill is a self-contained directory with a `SKILL.md` plus `scripts/`, `references/`, and other supporting files.

**5 skills** in total:

- `skill/`: 3 universal skills.
- `personal_skill/`: 2 personal skills.

It also maintains a [curated third-party skill catalog](CATALOG.en.md) with 17 skills (3 office, 14 coding).

## Skills

### Languages (languages/)

| Skill | Description |
|---|---|
| [python-code-standard](skill/languages/python-code-standard/SKILL.md) | Python typing, exception handling, naming, structure, and performance standards, with a checker. |

### Frontend & 3D (frontend/)

| Skill | Description |
|---|---|
| [threejs](skill/frontend/threejs/SKILL.md) | Full Three.js workflow: scenes, geometry, materials, lighting, textures, animation, loaders, shaders, post-processing, and interaction, with a scene scaffolder and 10 topic references. |

### DevOps & Systems (devops/)

| Skill | Description |
|---|---|
| [bash-scripting-expert](skill/devops/bash-scripting-expert/SKILL.md) | Robust, safe Bash scripts: quoting, error handling, and POSIX portability, with syntax and ShellCheck scripts. |

### Personal Skills (personal_skill/)

| Skill | Description |
|---|---|
| [cpp-code-standard](personal_skill/cpp-code-standard/SKILL.md) | C/C++ naming, formatting, comments, types, and modern C++ practices, with a header checker. |
| [installer-extract](personal_skill/installer-extract/SKILL.md) | Windows installer extraction and deployment, shortcuts, launch verification, and updates. |

## Curated Skill Catalog

Beyond the skills bundled here, the repo indexes 17 third-party skills worth using:

- **Office**: PPT generation, HTML answers for hard questions, and patent disclosures.
- **Coding**: code trimming, token compression, architecture diagrams, UI/UX design, reverse engineering, security audits, website cloning, knowledge graphs, and the Anthropic / OpenAI / MiniMax / Qt official collections.

See [CATALOG.en.md](CATALOG.en.md) for the full list, descriptions, and licenses; the Chinese version is [CATALOG.md](CATALOG.md).

## Installation

Send the prompt below to a coding assistant with network and file access to install every skill:

```text
Install all skills from https://github.com/Miaoge-Ge/agent-skills.

The repository uses the standard Agent Skills format. Skills live under skill/ and personal_skill/; skill/ is grouped into languages, frontend, and devops.
Recursively find every skill directory containing a SKILL.md under those two folders, read the SKILL.md first, then copy the complete skill directory (including references, scripts, and all other supporting files) into the user-level skills directory supported by this tool.
If a skill with the same name already exists, compare versions first and preserve local customizations.
When done, list the installed skill names, versions, and installation paths.
```

To install a single skill, replace the path with the target skill directory, for example:

```text
Install the skill skill/languages/python-code-standard from https://github.com/Miaoge-Ge/agent-skills.

The repository uses the standard Agent Skills format. Read the SKILL.md in that directory first, then copy the complete skill directory (including references, scripts, and all other supporting files) into the user-level skills directory supported by this tool.
If a skill with the same name already exists, compare versions first and preserve local customizations.
When done, report the skill name, version, and installation path.
```

## Repository Layout

```text
agent-skills/
├── skill/
│   ├── languages/
│   │   └── python-code-standard/
│   │       ├── SKILL.md
│   │       └── scripts/check_python.py
│   ├── frontend/
│   │   └── threejs/
│   │       ├── SKILL.md
│   │       ├── references/    # 10 topic references
│   │       └── scripts/create_scene.mjs
│   └── devops/
│       └── bash-scripting-expert/
│           ├── SKILL.md
│           └── scripts/check_script.sh
├── personal_skill/
│   ├── cpp-code-standard/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── scripts/check_headers.py
│   └── installer-extract/
│       └── SKILL.md
├── scripts/
│   └── validate_skills.py
├── CATALOG.md
├── CATALOG.en.md
├── skills.sh.json
├── README.md
├── README.en.md
└── LICENSE
```

## Scripts

| Script | Purpose |
|---|---|
| `scripts/validate_skills.py` | Validate frontmatter, names, versions, relative links, and discovery paths for all skills. |
| `skill/languages/python-code-standard/scripts/check_python.py` | Check Python syntax, type annotations, bare `except`, mutable defaults, and wildcard imports. |
| `skill/frontend/threejs/scripts/create_scene.mjs` | Scaffold a runnable Three.js scene with camera, lights, OrbitControls, and a render loop. |
| `skill/devops/bash-scripting-expert/scripts/check_script.sh` | Run `bash -n`/`sh -n` and `shellcheck -x` when ShellCheck is installed. |
| `personal_skill/cpp-code-standard/scripts/check_headers.py` | Check C/C++ file headers, include guards, and `using namespace` in headers. |

```bash
python scripts/validate_skills.py
```

## Usage Examples

```text
Use python-code-standard to check my current Python changes, and do not modify code yet.
```

```text
Use threejs to add lights and shadows to the scene.
```

## Versioning

Versions are recorded in each skill's `metadata.version` inside `SKILL.md`. When adding or updating a skill, bump its version, update the skill list in both READMEs, and run `scripts/validate_skills.py`. When adding or updating catalog entries, also update `CATALOG.md`, `CATALOG.en.md`, and the counts above.

## License

MIT — see [LICENSE](LICENSE).
