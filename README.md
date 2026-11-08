# Agent Skills

[简体中文](README.md) | [English](README.en.md)

面向 AI 编程助手的实用 Agent Skills 合集。每个技能都是独立目录，包含 `SKILL.md` 和配套的 `scripts/`、`references/` 等文件。

共 **2 个技能**：`personal_skill/` 下的 2 个个人技能。

另维护一份 [精选技能目录](CATALOG.md)，收录 17 个第三方技能（办公 3 个、编程 14 个）。

## 技能

| 技能 | 说明 |
|---|---|
| [cpp-code-standard](personal_skill/cpp-code-standard/SKILL.md) | C/C++ 命名、排版、注释、类型及现代 C++ 用法规范，附文件头检查脚本。 |
| [installer-extract](personal_skill/installer-extract/SKILL.md) | Windows 安装包解包部署、快捷方式、启动验证与更新处理。 |

## 精选技能目录

除本仓库自带的技能外，另按用途整理了 17 个值得使用的第三方技能：

- **办公**：PPT 生成、复杂问题 HTML 解答、专利交底书。
- **编程**：代码精简、Token 压缩、架构可视化、UI/UX 设计、逆向工程、安全审计、网站克隆、知识图谱，以及 Anthropic / OpenAI / MiniMax / Qt 官方技能合集。

完整列表、简介与开源协议见 [CATALOG.md](CATALOG.md)；英文版见 [CATALOG.en.md](CATALOG.en.md)。

## 安装

把下面的提示词发给具备联网和文件操作能力的编程助手，安装全部技能：

```text
请从 https://github.com/Miaoge-Ge/agent-skills 安装全部技能。

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
├── CATALOG.md
├── CATALOG.en.md
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

版本号写在各技能 `SKILL.md` 的 `metadata.version` 中。新增或修改技能时同步更新版本号、本 README 的技能列表，并运行 `scripts/validate_skills.py`。新增或更新精选目录时，同步修改 `CATALOG.md` 与 `CATALOG.en.md` 以及上方的数量。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
