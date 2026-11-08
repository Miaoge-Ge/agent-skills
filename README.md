# Agent Skills

[简体中文](README.md) | [English](README.en.md)

面向 AI 编程助手的 Agent Skills 合集：仓库自带 **2 个** 可直接安装的技能，另收录 **23 个** 第三方精选技能。

- [本仓库技能](#本仓库技能)
- [精选技能目录](#精选技能目录)
- [安装](#安装)
- [目录结构](#目录结构)
- [脚本](#脚本)
- [使用示例](#使用示例)
- [版本与维护](#版本与维护)

## 本仓库技能

两个技能都位于 `personal_skill/`，每个技能是独立目录，包含 `SKILL.md` 和配套的 `scripts/`、`references/` 等文件。

| 技能 | 说明 |
|---|---|
| [cpp-code-standard](personal_skill/cpp-code-standard/SKILL.md) | C/C++ 命名、排版、注释、类型及现代 C++ 用法规范，附文件头检查脚本。 |
| [installer-extract](personal_skill/installer-extract/SKILL.md) | Windows 安装包解包部署、快捷方式、启动验证与更新处理。 |

## 精选技能目录

本仓库只做索引，不包含这些技能的代码；版权与协议归上游仓库所有，使用前请阅读对应仓库的 LICENSE。

### 办公（4）

| 技能 | 说明 | 协议 |
|---|---|---|
| [ppt-master](https://github.com/hugohe3/ppt-master) | 根据文档或主题生成可编辑的原生 PowerPoint 演示文稿，支持图表、转场、动画与讲稿旁白。 | MIT |
| [answer-me-with-html](https://github.com/QingYunA/answer-me-with-html) | 把复杂问题的解答转化为图文并茂的单页 HTML。 | MIT |
| [patent-disclosure-skill](https://github.com/handsomestWei/patent-disclosure-skill) | 中国专利点挖掘与交底书（发明 / 实用 / 外观）编写，辅助解读专利、追踪政策与审查答复。 | MIT |
| [SoftwareCopyright-Skill](https://github.com/Fokkyp/SoftwareCopyright-Skill) | 读取本地项目，自动生成中国软件著作权申请所需的全套 .docx 材料（申请表、操作手册、代码材料等）。 | AGPL-3.0 |

> `SoftwareCopyright-Skill` 使用 AGPL-3.0，分发或修改前请阅读其 LICENSE。

### 编程（19）

#### 代码质量与效率（3）

| 技能 | 说明 | 协议 |
|---|---|---|
| [ponytail](https://github.com/DietrichGebert/ponytail) | 精简代码、减少过度设计与冗余复杂度，支持代码审查。 | MIT |
| [caveman](https://github.com/JuliusBrussee/caveman) | 精简 AI 编程助手回复并压缩上下文，降低 Token 消耗。 | Apache-2.0 |
| [i-have-adhd](https://github.com/ayghri/i-have-adhd) | 让编程智能体把答案放在最前面，输出更短、更直给，对 ADHD 友好。 | MIT |

#### 设计与可视化（4）

| 技能 | 说明 | 协议 |
|---|---|---|
| [archify](https://github.com/tt-a1i/archify) | 将想法、方案和代码架构转化为交互式可视化图表。 | Apache-2.0 |
| [hallmark](https://github.com/Nutlope/hallmark) | 网页界面设计与优化，减少 AI 生成页面的模板化风格。 | MIT |
| [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 为 AI 编程助手提供专业 UI/UX 设计能力。 | MIT |
| [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) | 把代码或资料转换为可交互、可搜索、可提问的知识图谱。 | MIT |

#### 逆向与安全（3）

| 技能 | 说明 | 协议 |
|---|---|---|
| [reagent](https://github.com/Dryxio/reagent) | AI 逆向工程智能体，从二进制程序重建并验证 C/C++ 代码。 | MIT |
| [rea](https://github.com/morluto/rea) | 逆向工程与软件行为分析工具集，覆盖应用行为与原生二进制。 | MIT |
| [security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 代码与架构安全审计，支持漏洞验证和结构化报告。 | MIT |

#### 网站克隆（1）

| 技能 | 说明 | 协议 |
|---|---|---|
| [ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) | 一条命令克隆任意网站。 | MIT |

#### 智能体与工程方法（2）

| 技能 | 说明 | 协议 |
|---|---|---|
| [ECC](https://github.com/affaan-m/ECC) | 面向 Claude Code、Codex 等智能体的性能优化系统：技能、本能、记忆、安全与研究优先开发。 | MIT |
| [superpowers](https://github.com/obra/superpowers) | 面向智能体的技能框架与软件开发方法论，覆盖从构思到交付的完整流程。 | MIT |

#### 技能合集（6）

| 技能 | 说明 | 协议 |
|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | Anthropic 官方 Agent Skills 示例合集，覆盖文档、设计、MCP、Web 测试等场景。 | Apache-2.0（逐技能） |
| [openai/skills](https://github.com/openai/skills) | OpenAI Codex 官方技能目录，包含 curated 与 experimental 技能；上游已标记弃用。 | 见各技能目录 |
| [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) | MiniMax 官方 Agent Skills 合集。 | MIT |
| [TheQtCompanyRnD/agent-skills](https://github.com/TheQtCompanyRnD/agent-skills) | Qt 官方 AI 编程技能集合，辅助 Qt / QML 开发与质量检查。 | BSD-3-Clause |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 面向 AI 编程智能体的生产级工程技能合集，覆盖定义、计划、构建、验证、评审与交付。 | MIT |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 面向真实工程的技能合集，来自作者日常使用的 .agents 目录。 | MIT |

## 安装

下面的提示词只安装本仓库自带的 2 个技能。精选目录中的第三方技能请按各自仓库的 README 安装。

把提示词发给具备联网和文件操作能力的编程助手：

```text
请从 https://github.com/Miaoge-Ge/agent-skills 安装仓库自带的全部技能。

仓库使用标准 Agent Skills 格式，技能位于 personal_skill/ 目录。
请递归查找该目录下所有包含 SKILL.md 的技能目录，先读取 SKILL.md，再把完整技能目录（包括 references、scripts 等全部文件）复制到当前工具支持的用户级技能目录。
如果已存在同名技能，先比较版本，保留本地自定义修改。
完成后列出已安装技能的名称、版本和安装路径。
```

只安装一个技能时，把提示词里的路径换成目标技能目录，例如：

```text
请从 https://github.com/Miaoge-Ge/agent-skills 安装 personal_skill/cpp-code-standard 技能。

仓库使用标准 Agent Skills 格式。请先读取该目录下的 SKILL.md，再把完整技能目录（包括 references、scripts 等全部文件）复制到当前工具支持的用户级技能目录。
如果已存在同名技能，先比较版本，保留本地自定义修改。
完成后报告技能名称、版本和安装路径。
```

## 目录结构

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

## 脚本

| 脚本 | 用途 |
|---|---|
| `scripts/validate_skills.py` | 校验全部技能的 frontmatter、名称、版本、相对链接和发现路径。 |
| `personal_skill/cpp-code-standard/scripts/check_headers.py` | 检查 C/C++ 文件头、头文件包含保护和头文件中的 `using namespace`。 |

```bash
python scripts/validate_skills.py
```

## 使用示例

```text
用 cpp-code-standard 检查当前 C/C++ 修改，先不要改代码。
```

```text
用 installer-extract 解包安装包，并验证快捷方式和启动。
```

## 版本与维护

版本号写在各技能 `SKILL.md` 的 `metadata.version` 中。新增或修改技能时同步更新版本号、本 README 的技能列表，并运行 `scripts/validate_skills.py`。新增或更新精选目录时，同步修改两个 README 中的列表与数量。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
