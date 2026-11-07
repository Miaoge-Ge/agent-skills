# Agent Skills

[简体中文](README.md) | [English](README.en.md)

A collection of standard Agent Skills for AI coding assistants. Every skill is a self-contained directory with a `SKILL.md` plus optional supporting files such as `references/`, ready to be read and used by any tool that supports Agent Skills.

The repository is split by origin:

- `skill/`: the original universal skills.
- `cyg_skill/`: newly merged cyg-series skills.

40 skills in total: 38 under `skill/` and 2 under `cyg_skill/`.

## Universal Skills (skill/)

### Languages & Standards

| Skill | Description |
|---|---|
| [python-code-standard](skill/python-code-standard/SKILL.md) | Python typing, exception handling, naming, structure, and performance standards. |
| [cpp-expert](skill/cpp-expert/SKILL.md) | Modern C++ (17/20/23), memory safety, templates, performance, and UB diagnosis. |
| [python-expert](skill/python-expert/SKILL.md) | Pythonic code, typing, async, the standard library, and performance. |
| [typescript-expert](skill/typescript-expert/SKILL.md) | TypeScript type system, generics, narrowing, and strict-mode safety. |
| [rust-expert](skill/rust-expert/SKILL.md) | Rust ownership, lifetimes, traits, async, and idiomatic error handling. |
| [go-expert](skill/go-expert/SKILL.md) | Idiomatic Go: goroutines, channels, interfaces, and error handling. |

### Frontend & 3D

| Skill | Description |
|---|---|
| [react-expert](skill/react-expert/SKILL.md) | Modern React (18/19): hooks, component design, state, performance, and Server Components. |
| [nextjs-expert](skill/nextjs-expert/SKILL.md) | Next.js App Router, Server Components, caching, and Server Actions. |
| [tailwind-expert](skill/tailwind-expert/SKILL.md) | Tailwind CSS utility-first styling, responsive design, theming, and design systems. |
| [accessibility-expert](skill/accessibility-expert/SKILL.md) | Web accessibility: WCAG, semantic HTML, ARIA, keyboard navigation, and screen readers. |
| [threejs-fundamentals](skill/threejs-fundamentals/SKILL.md) | Three.js scenes, cameras, renderers, and Object3D hierarchy. |
| [threejs-geometry](skill/threejs-geometry/SKILL.md) | Geometries, BufferGeometry, custom geometry, and instancing. |
| [threejs-materials](skill/threejs-materials/SKILL.md) | PBR, basic, Phong, and shader materials. |
| [threejs-lighting](skill/threejs-lighting/SKILL.md) | Light types, shadows, and environment lighting. |
| [threejs-textures](skill/threejs-textures/SKILL.md) | Texture types, UV mapping, environment maps, and texture settings. |
| [threejs-animation](skill/threejs-animation/SKILL.md) | Keyframe animation, skeletal animation, morph targets, and animation mixing. |
| [threejs-loaders](skill/threejs-loaders/SKILL.md) | Loading GLTF, textures, HDR environments, and async patterns. |
| [threejs-shaders](skill/threejs-shaders/SKILL.md) | GLSL, ShaderMaterial, uniforms, and custom effects. |
| [threejs-postprocessing](skill/threejs-postprocessing/SKILL.md) | EffectComposer, bloom, depth of field, and screen effects. |
| [threejs-interaction](skill/threejs-interaction/SKILL.md) | Raycasting, controls, and mouse/touch interaction. |

### Backend & Data

| Skill | Description |
|---|---|
| [nodejs-backend-expert](skill/nodejs-backend-expert/SKILL.md) | Node.js services (Express/Fastify/Hono): routing, middleware, auth, and async. |
| [api-design-expert](skill/api-design-expert/SKILL.md) | REST/GraphQL API design: resource modeling, versioning, pagination, errors, and contracts. |
| [sql-expert](skill/sql-expert/SKILL.md) | SQL queries, schema design, indexing, query optimization, and transactions. |

### AI / LLM

| Skill | Description |
|---|---|
| [deep-learning-expert](skill/deep-learning-expert/SKILL.md) | Model architecture, training strategies, debugging, and paper interpretation. |
| [llm-testing-expert](skill/llm-testing-expert/SKILL.md) | LLM evaluation, prompt engineering, red teaming, and regression testing. |
| [prompt-engineering-expert](skill/prompt-engineering-expert/SKILL.md) | Prompt structure, few-shot, chain-of-thought, and structured output. |
| [rag-expert](skill/rag-expert/SKILL.md) | RAG chunking, embeddings, vector/hybrid search, reranking, and grounded answers. |

### DevOps & Systems

| Skill | Description |
|---|---|
| [docker-expert](skill/docker-expert/SKILL.md) | Dockerfiles, multi-stage builds, image optimization, and Compose. |
| [kubernetes-expert](skill/kubernetes-expert/SKILL.md) | Kubernetes workloads, Services, config, probes, and troubleshooting. |
| [bash-scripting-expert](skill/bash-scripting-expert/SKILL.md) | Robust, safe Bash scripts: quoting, error handling, and POSIX portability. |
| [github-master](skill/github-master/SKILL.md) | Git/GitHub workflows, PRs, branch protection, and Actions CI/CD. |

### Quality, Architecture & Algorithms

| Skill | Description |
|---|---|
| [testing-expert](skill/testing-expert/SKILL.md) | Unit/integration/e2e testing, TDD, test doubles, and coverage. |
| [debugging-expert](skill/debugging-expert/SKILL.md) | Systematic reproduction, bisection, and root-cause analysis. |
| [refactoring-expert](skill/refactoring-expert/SKILL.md) | Safe, incremental, behavior-preserving refactoring and tech-debt cleanup. |
| [performance-expert](skill/performance-expert/SKILL.md) | Profiling and optimizing CPU, memory, I/O, and rendering. |
| [security-expert](skill/security-expert/SKILL.md) | Secure coding and review (OWASP Top 10), authn/authz, and secrets. |
| [software-architect](skill/software-architect/SKILL.md) | System design, technology selection, and architecture trade-offs. |
| [competitive-programming-expert](skill/competitive-programming-expert/SKILL.md) | Algorithmic problem solving, complexity analysis, and optimization. |

## cyg-series Skills (cyg_skill/)

| Skill | Description |
|---|---|
| [cpp-code-standard](cyg_skill/cpp-code-standard/SKILL.md) | C/C++ naming, formatting, comments, types, and modern C++ practices. |
| [installer-extract](cyg_skill/installer-extract/SKILL.md) | Windows installer extraction and deployment, shortcuts, launch verification, and updates. |

## Installation

Send the prompt below to a coding assistant with network and file access to install every skill:

```text
Install all skills from https://github.com/Miaoge-Ge/agent-skills.

The repository uses the standard Agent Skills format. Skills live under skill/ and cyg_skill/, and every skill directory contains a SKILL.md plus optional supporting files such as references/.
Read each target skill's SKILL.md first, then copy the complete skill directory (including references and all other supporting files) into the user-level skills directory supported by this tool.
If a skill with the same name already exists, compare versions first and preserve local customizations.
When done, list the installed skill names, versions, and installation paths.
```

To install a single skill, replace "all skills" with a concrete path, for example:

```text
Install the skill cyg_skill/cpp-code-standard from https://github.com/Miaoge-Ge/agent-skills.

The repository uses the standard Agent Skills format. Read the SKILL.md in that directory first, then copy the complete skill directory (including references and all other supporting files) into the user-level skills directory supported by this tool.
If a skill with the same name already exists, compare versions first and preserve local customizations.
When done, report the skill name, version, and installation path.
```

## Repository Layout

```text
agent-skills/
├── skill/            # original universal skills (38)
│   ├── cpp-expert/
│   │   └── SKILL.md
│   └── ...
├── cyg_skill/        # newly merged cyg-series skills (2)
│   ├── cpp-code-standard/
│   │   ├── SKILL.md
│   │   └── references/
│   └── installer-extract/
│       └── SKILL.md
├── skills.sh.json    # discovery paths for the skills CLI
├── README.md
├── README.en.md
└── LICENSE
```

## Usage Examples

```text
Use cpp-code-standard to review my current changes, list every violation, and do not modify code yet.
```

```text
Use threejs-lighting to add lights and shadows to the scene.
```

## Versioning

Versions are recorded in each skill's `metadata.version` inside `SKILL.md`. When adding or updating a skill, bump its version and update the skill list in both READMEs.

## License

MIT — see [LICENSE](LICENSE).
