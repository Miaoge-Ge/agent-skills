# Agent Skills

[简体中文](README.md) | [English](README.en.md)

面向 AI 编程助手的实用 Agent Skills 合集。`skill/` 只保留带脚本或可执行工具的技能；每个技能都是独立目录，包含 `SKILL.md` 和配套的 `scripts/`、`references/` 等文件。

共 **5 个技能**：

- `skill/`：3 个通用技能。
- `personal_skill/`：2 个个人技能。

另维护一份 [精选技能目录](CATALOG.md)，收录 17 个第三方技能（办公 3 个、编程 14 个）。

## 技能

### 编程语言（languages/）

| 技能 | 说明 |
|---|---|
| [python-code-standard](skill/languages/python-code-standard/SKILL.md) | Python 类型标注、异常处理、命名、结构与性能规范，附检查脚本。 |

### 前端与 3D（frontend/）

| 技能 | 说明 |
|---|---|
| [threejs](skill/frontend/threejs/SKILL.md) | Three.js 全流程：场景、几何、材质、灯光、纹理、动画、加载、着色器、后处理与交互，附场景脚手架和 10 个主题参考。 |

### DevOps 与系统（devops/）

| 技能 | 说明 |
|---|---|
| [bash-scripting-expert](skill/devops/bash-scripting-expert/SKILL.md) | 健壮安全的 Bash 脚本：引号、错误处理与 POSIX 可移植性，附语法与 ShellCheck 检查脚本。 |

### 个人技能（personal_skill/）

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

仓库使用标准 Agent Skills 格式，技能分布在 skill/ 和 personal_skill/ 两个目录，skill/ 下按语言、前端和 DevOps 分类。
请递归查找这两个目录下所有包含 SKILL.md 的技能目录，先读取 SKILL.md，再把完整技能目录（包括 references、scripts 等全部文件）复制到当前工具支持的用户级技能目录。
如果已存在同名技能，先比较版本，保留本地自定义修改。
完成后列出已安装技能的名称、版本和安装路径。
```

只安装一个技能时，把提示词里的路径换成目标技能目录，例如：

```text
请从 https://github.com/Miaoge-Ge/agent-skills 安装 skill/languages/python-code-standard 技能。

仓库使用标准 Agent Skills 格式。请先读取该目录下的 SKILL.md，再把完整技能目录（包括 references、scripts 等全部文件）复制到当前工具支持的用户级技能目录。
如果已存在同名技能，先比较版本，保留本地自定义修改。
完成后报告技能名称、版本和安装路径。
```

## 目录结构

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
│   │       ├── references/    # 10 个主题参考
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

## 脚本

| 脚本 | 用途 |
|---|---|
| `scripts/validate_skills.py` | 校验全部技能的 frontmatter、名称、版本、相对链接和发现路径。 |
| `skill/languages/python-code-standard/scripts/check_python.py` | 检查 Python 语法、类型标注、裸 `except`、可变默认参数和通配导入。 |
| `skill/frontend/threejs/scripts/create_scene.mjs` | 生成可运行的 Three.js 场景，包含相机、灯光、OrbitControls 和渲染循环。 |
| `skill/devops/bash-scripting-expert/scripts/check_script.sh` | 运行 `bash -n`/`sh -n`，有 ShellCheck 时运行 `shellcheck -x`。 |
| `personal_skill/cpp-code-standard/scripts/check_headers.py` | 检查 C/C++ 文件头、头文件包含保护和头文件中的 `using namespace`。 |

```bash
python scripts/validate_skills.py
```

## 使用示例

```text
用 python-code-standard 检查当前 Python 修改，先不要改代码。
```

```text
按 threejs 技能给场景加灯光和阴影。
```

## 版本与维护

版本号写在各技能 `SKILL.md` 的 `metadata.version` 中。新增或修改技能时同步更新版本号、本 README 的技能列表，并运行 `scripts/validate_skills.py`。新增或更新精选目录时，同步修改 `CATALOG.md` 与 `CATALOG.en.md` 以及上方的数量。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
