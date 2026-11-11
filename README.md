# Agent Skills

[简体中文](README.md) | [English](README.en.md)

面向 AI 编程助手的 Agent Skills 合集：仓库自带 **3 个** 可直接安装的技能（C/C++ 规范、Git 工作流规范、Windows 安装包处理），另收录 **28 个** 第三方精选技能与工具。

- [本仓库技能](#本仓库技能)
- [精选技能目录](#精选技能目录)
- [安装](#安装)
- [目录结构](#目录结构)
- [脚本](#脚本)
- [使用示例](#使用示例)
- [版本与维护](#版本与维护)

## 本仓库技能

三个技能都位于 `personal_skill/`，每个技能是独立目录，包含 `SKILL.md` 和配套的 `scripts/`、`references/` 等文件。

| 技能 | 说明 |
|---|---|
| [cpp-code-standard](personal_skill/cpp-code-standard/SKILL.md) | C/C++ 命名、排版、注释、类型及现代 C++ 用法规范，附文件头检查脚本。 |
| [git-workflow-standard](personal_skill/git-workflow-standard/SKILL.md) | Git 工作流规范：Conventional Commits 提交信息、分支命名、合并与发布、历史安全，附提交校验、暂存区扫描和钩子安装脚本。 |
| [installer-extract](personal_skill/installer-extract/SKILL.md) | Windows 安装包解包部署、快捷方式、启动验证与更新处理。 |

## 精选技能目录

按用途收录 **28 个** 第三方技能与工具；每个条目的仓库链接、一句话说明和协议见 [catalog/](catalog/README.md) 下按类型划分的分类页。本仓库只做索引，不包含这些技能的代码；版权与协议归上游仓库所有，使用前请阅读对应仓库的 LICENSE。

### 办公（4） · [详情](catalog/office.md)

[ppt-master](https://github.com/hugohe3/ppt-master)、[answer-me-with-html](https://github.com/QingYunA/answer-me-with-html)、[patent-disclosure-skill](https://github.com/handsomestWei/patent-disclosure-skill)、[SoftwareCopyright-Skill](https://github.com/Fokkyp/SoftwareCopyright-Skill)

> `SoftwareCopyright-Skill` 使用 AGPL-3.0，分发或修改前请确认合规。

### 代码质量与效率（3） · [详情](catalog/code-quality.md)

[ponytail](https://github.com/DietrichGebert/ponytail)、[caveman](https://github.com/JuliusBrussee/caveman)、[i-have-adhd](https://github.com/ayghri/i-have-adhd)

### 设计与可视化（5） · [详情](catalog/design.md)

[archify](https://github.com/tt-a1i/archify)、[diagram-design](https://github.com/cathrynlavery/diagram-design)、[hallmark](https://github.com/Nutlope/hallmark)、[ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)、[Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)

### 逆向与安全（4） · [详情](catalog/reverse-engineering.md)

[reagent](https://github.com/Dryxio/reagent)、[rea](https://github.com/morluto/rea)、[security-audit-skill](https://github.com/cloudflare/security-audit-skill)、[craft-anything](https://github.com/storytold/craft-anything)

### 网站克隆（1） · [详情](catalog/website-cloning.md)

[ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template)

### 数据采集（1） · [详情](catalog/data-collection.md)

[Scrapling](https://github.com/D4Vinci/Scrapling)

### 智能体与工程方法（2） · [详情](catalog/agent-methods.md)

[ECC](https://github.com/affaan-m/ECC)、[superpowers](https://github.com/obra/superpowers)

### 技能合集（8） · [详情](catalog/collections.md)

[anthropics/skills](https://github.com/anthropics/skills)、[openai/skills](https://github.com/openai/skills)、[google-gemini/gemini-skills](https://github.com/google-gemini/gemini-skills)、[zai-org/GLM-skills](https://github.com/zai-org/GLM-skills)、[MiniMax-AI/skills](https://github.com/MiniMax-AI/skills)、[TheQtCompanyRnD/agent-skills](https://github.com/TheQtCompanyRnD/agent-skills)、[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)、[mattpocock/skills](https://github.com/mattpocock/skills)

## 安装

下面的提示词只安装本仓库自带的 3 个技能。精选目录中的第三方技能请按各自仓库的 README 安装。

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
│   ├── git-workflow-standard/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── scripts/
│   │   └── tests/
│   └── installer-extract/
│       └── SKILL.md
├── catalog/            # 第三方精选技能索引，按类型分页
│   ├── README.md / README.en.md
│   ├── office.md / office.en.md
│   ├── code-quality.md / code-quality.en.md
│   ├── design.md / design.en.md
│   ├── reverse-engineering.md / reverse-engineering.en.md
│   ├── website-cloning.md / website-cloning.en.md
│   ├── data-collection.md / data-collection.en.md
│   ├── agent-methods.md / agent-methods.en.md
│   └── collections.md / collections.en.md
├── cyg_skill/          # 私有 submodule，本仓库只存指针
├── scripts/
│   └── validate_skills.py
├── skills.sh.json
├── README.md
├── README.en.md
└── LICENSE
```

`cyg_skill/` 是指向私有仓库 [cyg-skills](https://github.com/Miaoge-Ge/cyg-skills) 的 submodule：本仓库只保存一个提交指针，目录内容不在公开代码中。没有该私有仓库权限时，克隆会跳过它，属于预期行为。

## 脚本

| 脚本 | 用途 |
|---|---|
| `scripts/validate_skills.py` | 校验全部技能的 frontmatter、名称、版本、相对链接和发现路径。 |
| `personal_skill/cpp-code-standard/scripts/check_headers.py` | 检查 C/C++ 文件头、头文件包含保护和头文件中的 `using namespace`。 |
| `personal_skill/git-workflow-standard/scripts/` | `commit_msg_lint.py` 校验 Conventional Commits；`git_guard.py` 扫描暂存区的密钥、大文件和冲突标记；`install_hooks.py` 安装或卸载 commit-msg / pre-commit 钩子。 |

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

```text
用 git-workflow-standard 检查当前分支的提交信息，并按 Conventional Commits 生成提交。
```

## 版本与维护

版本号写在各技能 `SKILL.md` 的 `metadata.version` 中。新增或修改技能时同步更新版本号、本 README 的技能列表，并运行 `scripts/validate_skills.py`。带自动化测试的技能在发布前运行自己的测试，例如 `cd personal_skill/git-workflow-standard && python -m unittest discover -s tests`。新增或更新精选目录时，同步修改对应分类页、[catalog/README.md](catalog/README.md) 的数量，以及两个 README 中的技能清单。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
