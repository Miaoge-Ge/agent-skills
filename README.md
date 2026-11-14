# Agent Skills

[简体中文](README.md) | [English](README.en.md)

一套面向 AI 编程助手的 Agent Skills：把工程规范写成智能体可执行的指令，让它在写 C/C++、处理 Git 提交和部署 Windows 环境时保持一致的习惯；同时整理了一份按用途分类的第三方技能索引，供继续探索。自带技能遵循标准 Agent Skills 格式，复制到支持该格式的工具中即可使用。

- [本仓库技能](#本仓库技能)
- [第三方技能](#第三方技能)
- [安装](#安装)
- [目录结构](#目录结构)
- [使用示例](#使用示例)

## 本仓库技能

自带技能都位于 `personal_skill/`，每个技能是独立目录，包含 `SKILL.md` 和配套的 `scripts/`、`references/` 等文件。

| 技能 | 版本 | 说明 |
|---|---|---|
| [cpp-code-standard](personal_skill/cpp-code-standard/SKILL.md) | 1.0.3 | C/C++ 命名、排版、注释、类型及现代 C++ 用法规范，附文件头检查脚本。 |
| [git-workflow-standard](personal_skill/git-workflow-standard/SKILL.md) | 1.0.0 | Git 工作流规范：Conventional Commits 提交信息、分支命名、合并与发布、历史安全，附提交校验、暂存区扫描和钩子安装脚本。 |
| [installer-extract](personal_skill/installer-extract/SKILL.md) | 1.0.2 | Windows 安装包解包部署、快捷方式、启动验证与更新处理。 |
| [scan-skill-repos](personal_skill/scan-skill-repos/SKILL.md) | 1.0.0 | 扫描 GitHub 技能仓库，校验后维护第三方目录及 Star/版本。 |

## 第三方技能

第三方技能与工具按用途整理在 [third_party_skill/](third_party_skill/README.md)：[中文版](third_party_skill/README.md) | [English](third_party_skill/README.en.md)。

本仓库只做索引，不包含这些技能的代码；版权与协议归上游仓库所有，使用前请阅读对应仓库的 LICENSE。

## 安装

下面的提示词只安装本仓库自带的技能。第三方技能请按各自仓库的 README 安装。

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
│   ├── installer-extract/
│   │   └── SKILL.md
│   └── scan-skill-repos/
│       ├── SKILL.md
│       ├── references/descriptions.json
│       └── scripts/scan_skill_repos.py
├── third_party_skill/ # 第三方技能索引
│   ├── README.md
│   └── README.en.md
├── cyg_skill/          # 私有 submodule，本仓库只存指针
├── scripts/
│   └── validate_skills.py
├── skills.sh.json
├── README.md
├── README.en.md
└── LICENSE
```

`cyg_skill/` 是指向私有仓库 [cyg-skills](https://github.com/Miaoge-Ge/cyg-skills) 的 submodule：本仓库只保存一个提交指针，目录内容不在公开代码中。

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

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
