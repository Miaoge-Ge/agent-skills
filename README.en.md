# Agent Skills

[简体中文](README.md) | [English](README.en.md)

A collection of standard Agent Skills for AI coding assistants. Every skill is a self-contained directory with a `SKILL.md` plus optional supporting files such as `references/` and `scripts/`, ready to be read and used by any tool that supports Agent Skills.

**31 skills** in total:

- `skill/`: 29 universal skills, grouped by languages, frontend & 3D, backend, AI, DevOps, and engineering quality.
- `personal_skill/`: 2 personal skills.

## Universal Skills (skill/)

### Languages (languages/)

| Skill | Description |
|---|---|
| [cpp-expert](skill/languages/cpp-expert/SKILL.md) | Modern C++ (17/20/23), memory safety, templates, performance, and UB diagnosis. |
| [python-code-standard](skill/languages/python-code-standard/SKILL.md) | Python typing, exception handling, naming, structure, and performance standards, with a checker. |
| [python-expert](skill/languages/python-expert/SKILL.md) | Pythonic code, typing, async, the standard library, and performance. |
| [typescript-expert](skill/languages/typescript-expert/SKILL.md) | TypeScript type system, generics, narrowing, and strict-mode safety. |
| [rust-expert](skill/languages/rust-expert/SKILL.md) | Rust ownership, lifetimes, traits, async, and idiomatic error handling. |
| [go-expert](skill/languages/go-expert/SKILL.md) | Idiomatic Go: goroutines, channels, interfaces, and error handling. |

### Frontend & 3D (frontend/)

| Skill | Description |
|---|---|
| [react-expert](skill/frontend/react-expert/SKILL.md) | Modern React (18/19): hooks, component design, state, performance, and Server Components. |
| [nextjs-expert](skill/frontend/nextjs-expert/SKILL.md) | Next.js App Router, Server Components, caching, and Server Actions. |
| [tailwind-expert](skill/frontend/tailwind-expert/SKILL.md) | Tailwind CSS utility-first styling, responsive design, theming, and design systems. |
| [accessibility-expert](skill/frontend/accessibility-expert/SKILL.md) | Web accessibility: WCAG, semantic HTML, ARIA, keyboard navigation, and screen readers. |
| [threejs](skill/frontend/threejs/SKILL.md) | Full Three.js workflow: scenes, geometry, materials, lighting, textures, animation, loaders, shaders, post-processing, and interaction, with a scene scaffolder. |

### Backend & Data (backend/)

| Skill | Description |
|---|---|
| [nodejs-backend-expert](skill/backend/nodejs-backend-expert/SKILL.md) | Node.js services (Express/Fastify/Hono): routing, middleware, auth, and async. |
| [api-design-expert](skill/backend/api-design-expert/SKILL.md) | REST/GraphQL API design: resource modeling, versioning, pagination, errors, and contracts. |
| [sql-expert](skill/backend/sql-expert/SKILL.md) | SQL queries, schema design, indexing, query optimization, and transactions. |

### AI / LLM (ai/)

| Skill | Description |
|---|---|
| [deep-learning-expert](skill/ai/deep-learning-expert/SKILL.md) | Model architecture, training strategies, debugging, and paper interpretation. |
| [llm-testing-expert](skill/ai/llm-testing-expert/SKILL.md) | LLM evaluation, prompt engineering, red teaming, and regression testing. |
| [prompt-engineering-expert](skill/ai/prompt-engineering-expert/SKILL.md) | Prompt structure, few-shot, chain-of-thought, and structured output. |
| [rag-expert](skill/ai/rag-expert/SKILL.md) | RAG chunking, embeddings, vector/hybrid search, reranking, and grounded answers. |

### DevOps & Systems (devops/)

| Skill | Description |
|---|---|
| [docker-expert](skill/devops/docker-expert/SKILL.md) | Dockerfiles, multi-stage builds, image optimization, and Compose. |
| [kubernetes-expert](skill/devops/kubernetes-expert/SKILL.md) | Kubernetes workloads, Services, config, probes, and troubleshooting. |
| [bash-scripting-expert](skill/devops/bash-scripting-expert/SKILL.md) | Robust, safe Bash scripts: quoting, error handling, and POSIX portability, with a checker. |
| [github-master](skill/devops/github-master/SKILL.md) | Git/GitHub workflows, PRs, branch protection, and Actions CI/CD. |

### Quality, Architecture & Algorithms (engineering/)

| Skill | Description |
|---|---|
| [testing-expert](skill/engineering/testing-expert/SKILL.md) | Unit/integration/e2e testing, TDD, test doubles, and coverage. |
| [debugging-expert](skill/engineering/debugging-expert/SKILL.md) | Systematic reproduction, bisection, and root-cause analysis. |
| [refactoring-expert](skill/engineering/refactoring-expert/SKILL.md) | Safe, incremental, behavior-preserving refactoring and tech-debt cleanup. |
| [performance-expert](skill/engineering/performance-expert/SKILL.md) | Profiling and optimizing CPU, memory, I/O, and rendering. |
| [security-expert](skill/engineering/security-expert/SKILL.md) | Secure coding and review (OWASP Top 10), authn/authz, and secrets. |
| [software-architect](skill/engineering/software-architect/SKILL.md) | System design, technology selection, and architecture trade-offs. |
| [competitive-programming-expert](skill/engineering/competitive-programming-expert/SKILL.md) | Algorithmic problem solving, complexity analysis, and optimization. |

## Personal Skills (personal_skill/)

| Skill | Description |
|---|---|
| [cpp-code-standard](personal_skill/cpp-code-standard/SKILL.md) | C/C++ naming, formatting, comments, types, and modern C++ practices, with a header checker. |
| [installer-extract](personal_skill/installer-extract/SKILL.md) | Windows installer extraction and deployment, shortcuts, launch verification, and updates. |

## Installation

Send the prompt below to a coding assistant with network and file access to install every skill:

```text
Install all skills from https://github.com/Miaoge-Ge/agent-skills.

The repository uses the standard Agent Skills format. Skills live under skill/ and personal_skill/; skill/ is grouped into languages, frontend, backend, AI, DevOps, and engineering quality.
Recursively find every skill directory containing a SKILL.md under those two folders, read the SKILL.md first, then copy the complete skill directory (including references, scripts, and all other supporting files) into the user-level skills directory supported by this tool.
If a skill with the same name already exists, compare versions first and preserve local customizations.
When done, list the installed skill names, versions, and installation paths.
```

To install a single skill, replace "all skills" with a concrete path, for example:

```text
Install the skill skill/languages/cpp-expert from https://github.com/Miaoge-Ge/agent-skills.

The repository uses the standard Agent Skills format. Read the SKILL.md in that directory first, then copy the complete skill directory (including references, scripts, and all other supporting files) into the user-level skills directory supported by this tool.
If a skill with the same name already exists, compare versions first and preserve local customizations.
When done, report the skill name, version, and installation path.
```

## Repository Layout

```text
agent-skills/
├── skill/
│   ├── languages/          # cpp-expert, python-code-standard, python-expert, ...
│   ├── frontend/           # react-expert, nextjs-expert, tailwind-expert, accessibility-expert
│   │   └── threejs/        # merged Three.js skill
│   │       ├── SKILL.md
│   │       ├── references/ # 10 topic references
│   │       └── scripts/    # create_scene.mjs
│   ├── backend/            # nodejs-backend-expert, api-design-expert, sql-expert
│   ├── ai/                 # deep-learning-expert, llm-testing-expert, ...
│   ├── devops/             # docker-expert, kubernetes-expert, bash-scripting-expert, github-master
│   └── engineering/        # testing-expert, debugging-expert, ...
├── personal_skill/
│   ├── cpp-code-standard/  # SKILL.md + references/ + scripts/
│   └── installer-extract/
├── scripts/
│   └── validate_skills.py  # repository-wide skill validation
├── skills.sh.json          # discovery paths for the skills CLI
├── README.md
├── README.en.md
└── LICENSE
```

## Scripts & Validation

| Script | Purpose |
|---|---|
| `scripts/validate_skills.py` | Validate frontmatter, names, versions, relative links, and discovery paths for all skills. |
| `skill/frontend/threejs/scripts/create_scene.mjs` | Scaffold a runnable Three.js scene with camera, lights, OrbitControls, and a render loop. |
| `skill/languages/python-code-standard/scripts/check_python.py` | Check Python syntax, type annotations, bare `except`, mutable defaults, and wildcard imports. |
| `personal_skill/cpp-code-standard/scripts/check_headers.py` | Check C/C++ file headers, include guards, and `using namespace` in headers. |
| `skill/devops/bash-scripting-expert/scripts/check_script.sh` | Run `bash -n`/`sh -n` and `shellcheck -x` when ShellCheck is installed. |

```bash
python scripts/validate_skills.py
```

## Usage Examples

```text
Use cpp-code-standard to review my current changes, list every violation, and do not modify code yet.
```

```text
Use threejs to add lights and shadows to the scene.
```

## Versioning

Versions are recorded in each skill's `metadata.version` inside `SKILL.md`. When adding or updating a skill, bump its version, update the skill list in both READMEs, and run `scripts/validate_skills.py`.

## License

MIT — see [LICENSE](LICENSE).
