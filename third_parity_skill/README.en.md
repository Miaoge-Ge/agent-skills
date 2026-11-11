# Third-Party Skills

[简体中文](README.md) | [Back to repository](../README.en.md)

A maintained index of third-party Agent Skills and tools, grouped into 8 categories by use. This directory is an index only; all skill code lives in its upstream repository. Copyright and licenses belong to the respective authors and organizations. Read the upstream LICENSE before using, modifying, or redistributing a skill. Inclusion here does not imply endorsement and does not change the upstream license.

Star counts are GitHub data as of 2026-11-11; entries are sorted by stars in descending order within each category.

## Office

| Skill | Description | Stars |
| --- | --- | ---: |
| [ppt-master](https://github.com/hugohe3/ppt-master) | Turn documents or topics into editable native PowerPoint decks, with charts, transitions, animations, and narration from speaker notes. | 75,655 |
| [patent-disclosure-skill](https://github.com/handsomestWei/patent-disclosure-skill) | Chinese patent mining and disclosure drafting (invention / utility model / design), with patent reading, policy tracking, and office-action support. | 13,296 |
| [SoftwareCopyright-Skill](https://github.com/Fokkyp/SoftwareCopyright-Skill) | Read a local project and generate the full set of .docx materials for a Chinese software copyright application (application form, manual, source-code excerpts, and more). | 6,322 |
| [answer-me-with-html](https://github.com/QingYunA/answer-me-with-html) | Answer hard questions with a single, readable HTML page. | 6,210 |

## Code quality and efficiency

| Skill | Description | Stars |
| --- | --- | ---: |
| [ponytail](https://github.com/DietrichGebert/ponytail) | Trim code, over-engineering, and redundant complexity; supports code review. | 188,420 |
| [caveman](https://github.com/JuliusBrussee/caveman) | Compress coding-agent replies and context to cut token usage. | 118,903 |
| [i-have-adhd](https://github.com/ayghri/i-have-adhd) | Puts the answer first and keeps coding-agent output short and direct — ADHD-friendly. | 60,778 |

## Design and visualization

| Skill | Description | Stars |
| --- | --- | ---: |
| [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Professional UI/UX design intelligence for coding agents. | 147,815 |
| [archify](https://github.com/tt-a1i/archify) | Turn ideas, plans, and architectures into interactive diagrams. | 95,390 |
| [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) | Convert code into an interactive, searchable, queryable knowledge graph. | 91,898 |
| [diagram-design](https://github.com/cathrynlavery/diagram-design) | Editorial diagram design for coding agents: 45 diagram types as self-contained HTML + SVG. | 66,329 |
| [hallmark](https://github.com/Nutlope/hallmark) | Web UI design and polish that avoids templated AI-generated looks. | 52,641 |

## Reverse engineering and security

| Skill | Description | Stars |
| --- | --- | ---: |
| [rea](https://github.com/morluto/rea) | Reverse-engineering and behavior-analysis toolkit for apps and native binaries. | 450,086 |
| [security-audit-skill](https://github.com/cloudflare/security-audit-skill) | Code and architecture security audits with verified findings and structured reports. | 69,370 |
| [craft-anything](https://github.com/storytold/craft-anything) | Study how any website, app, or game works, then have a coding agent rebuild, compare, and refine it; a Rust engine exposes CLI and MCP interfaces. | 26,409 |
| [reagent](https://github.com/Dryxio/reagent) | AI reverse-engineering agent that reconstructs and validates C/C++ from binaries. | 2,426 |

## Website cloning

| Skill | Description | Stars |
| --- | --- | ---: |
| [ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) | Clone any website with one command. | 38,963 |

## Data collection

| Skill | Description | Stars |
| --- | --- | ---: |
| [Scrapling](https://github.com/D4Vinci/Scrapling) | Adaptive web-scraping framework covering single requests through full crawls, with stealth, dynamic pages, and MCP. | 101,157 |

## Agent methods

| Skill | Description | Stars |
| --- | --- | ---: |
| [superpowers](https://github.com/obra/superpowers) | An agentic skills framework and software-development methodology covering the full path from idea to delivery. | 315,774 |
| [ECC](https://github.com/affaan-m/ECC) | A performance-optimization system for mainstream coding agents: skills, instincts, memory, security, and research-first development. | 300,831 |

## Skill collections

| Skill | Description | Stars |
| --- | --- | ---: |
| [mattpocock/skills](https://github.com/mattpocock/skills) | Everyday engineering skills from the author's own .agents directory. | 320,965 |
| [anthropics/skills](https://github.com/anthropics/skills) | Anthropic's official Agent Skills examples for documents, design, MCP, web testing, and more. | 192,364 |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Production-grade engineering skills for AI coding agents, covering define, plan, build, verify, review, and ship. | 115,195 |
| [openai/skills](https://github.com/openai/skills) | OpenAI Codex official skill catalog with curated and experimental skills; deprecated upstream. | 28,669 |
| [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) | MiniMax official Agent Skills collection. | 13,815 |
| [google-gemini/gemini-skills](https://github.com/google-gemini/gemini-skills) | Official skills for the Gemini API, SDK, and model/agent interactions. | 4,448 |
| [TheQtCompanyRnD/agent-skills](https://github.com/TheQtCompanyRnD/agent-skills) | Qt's official AI engineering skills for Qt / QML development and quality checks. | 537 |
| [zai-org/GLM-skills](https://github.com/zai-org/GLM-skills) | Official skills for the GLM family of models, covering multimodal, OCR, vision, and more. | 473 |

## How to use

Each upstream repository defines its own installation method, commonly one of:

- install as a Claude Code / Codex plugin or skill directory;
- copy the directory containing `SKILL.md` into your user-level skills directory;
- clone the repository and follow its README.

## Inclusion criteria

- A public repository and a LICENSE.
- Still maintained, or still useful; deprecated projects are marked in their description.
- One entry per repository, filed under its primary use.
