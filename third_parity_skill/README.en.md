# Third-Party Skills

[简体中文](README.md) | [Back to repository](../README.en.md)

A maintained index of third-party Agent Skills and tools, grouped into 8 categories by use. This directory is an index only; all skill code lives in its upstream repository. Copyright and licenses belong to the respective authors and organizations. Read the upstream LICENSE before using, modifying, or redistributing a skill. Inclusion here does not imply endorsement and does not change the upstream license.

Star counts are GitHub data as of 2026-11-12; entries are sorted by stars in descending order within each category.

## Office

| Skill | Description | Stars |
| --- | --- | ---: |
| [ppt-master](https://github.com/hugohe3/ppt-master) | Turn documents or topics into editable native PowerPoint decks, with charts, transitions, animations, and narration from speaker notes. | 75,959 |
| [patent-disclosure-skill](https://github.com/handsomestWei/patent-disclosure-skill) | Chinese patent mining and disclosure drafting (invention / utility model / design), with patent reading, policy tracking, and office-action support. | 13,336 |
| [SoftwareCopyright-Skill](https://github.com/Fokkyp/SoftwareCopyright-Skill) | Read a local project and generate the full set of .docx materials for a Chinese software copyright application (application form, manual, source-code excerpts, and more). | 6,331 |
| [answer-me-with-html](https://github.com/QingYunA/answer-me-with-html) | Answer hard questions with a single, readable HTML page. | 6,239 |

## Code quality and efficiency

| Skill | Description | Stars |
| --- | --- | ---: |
| [ponytail](https://github.com/DietrichGebert/ponytail) | Trim code, over-engineering, and redundant complexity; supports code review. | 189,149 |
| [caveman](https://github.com/JuliusBrussee/caveman) | Compress coding-agent replies and context to cut token usage. | 119,136 |
| [i-have-adhd](https://github.com/ayghri/i-have-adhd) | Puts the answer first and keeps coding-agent output short and direct — ADHD-friendly. | 60,890 |

## Design and visualization

| Skill | Description | Stars |
| --- | --- | ---: |
| [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Professional UI/UX design intelligence for coding agents. | 148,215 |
| [archify](https://github.com/tt-a1i/archify) | Turn ideas, plans, and architectures into interactive diagrams. | 95,637 |
| [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) | Convert code into an interactive, searchable, queryable knowledge graph. | 92,180 |
| [diagram-design](https://github.com/cathrynlavery/diagram-design) | Editorial diagram design for coding agents: 45 diagram types as self-contained HTML + SVG. | 66,530 |
| [hallmark](https://github.com/Nutlope/hallmark) | Web UI design and polish that avoids templated AI-generated looks. | 53,396 |
| [handraw-style](https://github.com/yang0/handraw-style) | Numbered hand-drawn style gallery and bilingual prompt library: combine 365 hand-drawn/realistic styles, 170 layout types, and 36 classic monochrome palettes into image-generation prompts. | 7,460 |

## Reverse engineering and security

| Skill | Description | Stars |
| --- | --- | ---: |
| [rea](https://github.com/morluto/rea) | Reverse-engineering and behavior-analysis toolkit for apps and native binaries. | 452,705 |
| [security-audit-skill](https://github.com/cloudflare/security-audit-skill) | Code and architecture security audits with verified findings and structured reports. | 70,361 |
| [craft-anything](https://github.com/storytold/craft-anything) | Study how any website, app, or game works, then have a coding agent rebuild, compare, and refine it; a Rust engine exposes CLI and MCP interfaces. | 28,371 |
| [reagent](https://github.com/Dryxio/reagent) | AI reverse-engineering agent that reconstructs and validates C/C++ from binaries. | 2,426 |

## Website cloning

| Skill | Description | Stars |
| --- | --- | ---: |
| [ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) | Clone any website with one command. | 39,022 |

## Data collection

| Skill | Description | Stars |
| --- | --- | ---: |
| [Scrapling](https://github.com/D4Vinci/Scrapling) | Adaptive web-scraping framework covering single requests through full crawls, with stealth, dynamic pages, and MCP. | 101,634 |

## Agent methods

| Skill | Description | Stars |
| --- | --- | ---: |
| [superpowers](https://github.com/obra/superpowers) | An agentic skills framework and software-development methodology covering the full path from idea to delivery. | 316,301 |
| [ECC](https://github.com/affaan-m/ECC) | A performance-optimization system for mainstream coding agents: skills, instincts, memory, security, and research-first development. | 301,366 |
| [agent-browser](https://github.com/vercel-labs/agent-browser) | Browser automation CLI for AI agents: reads pages as an accessibility tree with element refs, then acts one command at a time and re-reads the result. | 49,864 |
| [improve](https://github.com/shadcn/improve) | Use your most capable model to audit a codebase and write self-contained implementation plans for cheaper models to execute; the skill never implements anything itself. | 10,870 |

## Skill collections

| Skill | Description | Stars |
| --- | --- | ---: |
| [mattpocock/skills](https://github.com/mattpocock/skills) | Everyday engineering skills from the author's own .agents directory. | 322,015 |
| [anthropics/skills](https://github.com/anthropics/skills) | Anthropic's official Agent Skills examples for documents, design, MCP, web testing, and more. | 193,118 |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Production-grade engineering skills for AI coding agents, covering define, plan, build, verify, review, and ship. | 115,928 |
| [openai/skills](https://github.com/openai/skills) | OpenAI Codex official skill catalog with curated and experimental skills; deprecated upstream. | 28,693 |
| [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) | MiniMax official Agent Skills collection. | 13,823 |
| [google-gemini/gemini-skills](https://github.com/google-gemini/gemini-skills) | Official skills for the Gemini API, SDK, and model/agent interactions. | 4,456 |
| [TheQtCompanyRnD/agent-skills](https://github.com/TheQtCompanyRnD/agent-skills) | Qt's official AI engineering skills for Qt / QML development and quality checks. | 538 |
| [zai-org/GLM-skills](https://github.com/zai-org/GLM-skills) | Official skills for the GLM family of models, covering multimodal, OCR, vision, and more. | 475 |

## How to use

Each upstream repository defines its own installation method, commonly one of:

- install as a Claude Code / Codex plugin or skill directory;
- copy the directory containing `SKILL.md` into your user-level skills directory;
- clone the repository and follow its README.

## Inclusion criteria

- A public repository and a LICENSE.
- Still maintained, or still useful; deprecated projects are marked in their description.
- One entry per repository, filed under its primary use.
