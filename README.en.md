# Coding Agent Skills

[简体中文](README.md) | [English](README.en.md)

A collection of standard Agent Skills for AI coding assistants. Every skill lives under `skills/` as a self-contained directory with a `SKILL.md` plus optional supporting files such as `references/`, ready to be read and used by any tool that supports Agent Skills. Only universal skills are published here.

## Skills

40 skills in total.

### Coding Standards

| Skill | Description |
|---|---|
| [cpp-code-standard](skills/cpp-code-standard/SKILL.md) | C/C++ naming, formatting, comments, types, and modern C++ practices. |
| [python-code-standard](skills/python-code-standard/SKILL.md) | Python typing, exception handling, naming, structure, and performance standards. |

### Languages

| Skill | Description |
|---|---|
| [cpp-expert](skills/cpp-expert/SKILL.md) | Modern C++ (17/20/23), memory safety, templates, performance, and UB diagnosis. |
| [python-expert](skills/python-expert/SKILL.md) | Pythonic code, typing, async, the standard library, and performance. |
| [typescript-expert](skills/typescript-expert/SKILL.md) | TypeScript type system, generics, narrowing, and strict-mode safety. |
| [rust-expert](skills/rust-expert/SKILL.md) | Rust ownership, lifetimes, traits, async, and idiomatic error handling. |
| [go-expert](skills/go-expert/SKILL.md) | Idiomatic Go: goroutines, channels, interfaces, and error handling. |

### Frontend & 3D

| Skill | Description |
|---|---|
| [react-expert](skills/react-expert/SKILL.md) | Modern React (18/19): hooks, component design, state, performance, and Server Components. |
| [nextjs-expert](skills/nextjs-expert/SKILL.md) | Next.js App Router, Server Components, caching, and Server Actions. |
| [tailwind-expert](skills/tailwind-expert/SKILL.md) | Tailwind CSS utility-first styling, responsive design, theming, and design systems. |
| [accessibility-expert](skills/accessibility-expert/SKILL.md) | Web accessibility: WCAG, semantic HTML, ARIA, keyboard navigation, and screen readers. |
| [threejs-fundamentals](skills/threejs-fundamentals/SKILL.md) | Three.js scenes, cameras, renderers, and Object3D hierarchy. |
| [threejs-geometry](skills/threejs-geometry/SKILL.md) | Geometries, BufferGeometry, custom geometry, and instancing. |
| [threejs-materials](skills/threejs-materials/SKILL.md) | PBR, basic, Phong, and shader materials. |
| [threejs-lighting](skills/threejs-lighting/SKILL.md) | Light types, shadows, and environment lighting. |
| [threejs-textures](skills/threejs-textures/SKILL.md) | Texture types, UV mapping, environment maps, and texture settings. |
| [threejs-animation](skills/threejs-animation/SKILL.md) | Keyframe animation, skeletal animation, morph targets, and animation mixing. |
| [threejs-loaders](skills/threejs-loaders/SKILL.md) | Loading GLTF, textures, HDR environments, and async patterns. |
| [threejs-shaders](skills/threejs-shaders/SKILL.md) | GLSL, ShaderMaterial, uniforms, and custom effects. |
| [threejs-postprocessing](skills/threejs-postprocessing/SKILL.md) | EffectComposer, bloom, depth of field, and screen effects. |
| [threejs-interaction](skills/threejs-interaction/SKILL.md) | Raycasting, controls, and mouse/touch interaction. |

### Backend & Data

| Skill | Description |
|---|---|
| [nodejs-backend-expert](skills/nodejs-backend-expert/SKILL.md) | Node.js services (Express/Fastify/Hono): routing, middleware, auth, and async. |
| [api-design-expert](skills/api-design-expert/SKILL.md) | REST/GraphQL API design: resource modeling, versioning, pagination, errors, and contracts. |
| [sql-expert](skills/sql-expert/SKILL.md) | SQL queries, schema design, indexing, query optimization, and transactions. |

### AI / LLM

| Skill | Description |
|---|---|
| [deep-learning-expert](skills/deep-learning-expert/SKILL.md) | Model architecture, training strategies, debugging, and paper interpretation. |
| [llm-testing-expert](skills/llm-testing-expert/SKILL.md) | LLM evaluation, prompt engineering, red teaming, and regression testing. |
| [prompt-engineering-expert](skills/prompt-engineering-expert/SKILL.md) | Prompt structure, few-shot, chain-of-thought, and structured output. |
| [rag-expert](skills/rag-expert/SKILL.md) | RAG chunking, embeddings, vector/hybrid search, reranking, and grounded answers. |

### DevOps & Systems

| Skill | Description |
|---|---|
| [docker-expert](skills/docker-expert/SKILL.md) | Dockerfiles, multi-stage builds, image optimization, and Compose. |
| [kubernetes-expert](skills/kubernetes-expert/SKILL.md) | Kubernetes workloads, Services, config, probes, and troubleshooting. |
| [bash-scripting-expert](skills/bash-scripting-expert/SKILL.md) | Robust, safe Bash scripts: quoting, error handling, and POSIX portability. |
| [github-master](skills/github-master/SKILL.md) | Git/GitHub workflows, PRs, branch protection, and Actions CI/CD. |
| [installer-extract](skills/installer-extract/SKILL.md) | Windows installer extraction and deployment, shortcuts, launch verification, and updates. |

### Quality, Architecture & Algorithms

| Skill | Description |
|---|---|
| [testing-expert](skills/testing-expert/SKILL.md) | Unit/integration/e2e testing, TDD, test doubles, and coverage. |
| [debugging-expert](skills/debugging-expert/SKILL.md) | Systematic reproduction, bisection, and root-cause analysis. |
| [refactoring-expert](skills/refactoring-expert/SKILL.md) | Safe, incremental, behavior-preserving refactoring and tech-debt cleanup. |
| [performance-expert](skills/performance-expert/SKILL.md) | Profiling and optimizing CPU, memory, I/O, and rendering. |
| [security-expert](skills/security-expert/SKILL.md) | Secure coding and review (OWASP Top 10), authn/authz, and secrets. |
| [software-architect](skills/software-architect/SKILL.md) | System design, technology selection, and architecture trade-offs. |
| [competitive-programming-expert](skills/competitive-programming-expert/SKILL.md) | Algorithmic problem solving, complexity analysis, and optimization. |

## Installation

Send the prompt below to a coding assistant with network and file access to install every skill:

```text
Install all skills from https://github.com/Miaoge-Ge/coding-agent-skills.

The repository uses the standard Agent Skills format. Every skill lives under skills/ with a SKILL.md and optional supporting files such as references/.
Read each target skill's SKILL.md first, then copy the complete skill directory (including references and all other supporting files) into the user-level skills directory supported by this tool.
If a skill with the same name already exists, compare versions first and preserve local customizations.
When done, list the installed skill names, versions, and installation paths.
```

To install a single skill, replace "all skills" with a concrete path, for example:

```text
Install the skill skills/cpp-code-standard from https://github.com/Miaoge-Ge/coding-agent-skills.

The repository uses the standard Agent Skills format. Read the SKILL.md in that directory first, then copy the complete skill directory (including references and all other supporting files) into the user-level skills directory supported by this tool.
If a skill with the same name already exists, compare versions first and preserve local customizations.
When done, report the skill name, version, and installation path.
```

## Repository Layout

```text
coding-agent-skills/
├── skills/
│   ├── cpp-code-standard/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── threejs-fundamentals/
│   │   └── SKILL.md
│   └── ...
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
