# Agent Skills

[简体中文](README.md) | [English](README.en.md)

面向 AI 编程助手的标准 Agent Skills 合集。每个技能都是独立目录，包含 `SKILL.md` 和可选的 `references/`、`scripts/` 等支撑文件，可直接被支持 Agent Skills 的工具读取和使用。

共 **31 个技能**：

- `skill/`：原有通用技能，29 个，按语言、前端与 3D、后端、AI、DevOps、工程质量分类。
- `personal_skill/`：个人技能，2 个。

## 通用技能（skill/）

### 编程语言（languages/）

| 技能 | 说明 |
|---|---|
| [cpp-expert](skill/languages/cpp-expert/SKILL.md) | 现代 C++（17/20/23）、内存安全、模板、性能与未定义行为诊断。 |
| [python-code-standard](skill/languages/python-code-standard/SKILL.md) | Python 类型标注、异常处理、命名、结构与性能规范，附检查脚本。 |
| [python-expert](skill/languages/python-expert/SKILL.md) | Pythonic 代码、类型、异步、标准库与性能。 |
| [typescript-expert](skill/languages/typescript-expert/SKILL.md) | TypeScript 类型系统、泛型、类型收窄与严格模式安全。 |
| [rust-expert](skill/languages/rust-expert/SKILL.md) | Rust 所有权、生命周期、trait、异步与错误处理。 |
| [go-expert](skill/languages/go-expert/SKILL.md) | 地道 Go、并发、接口与错误处理。 |

### 前端与 3D（frontend/）

| 技能 | 说明 |
|---|---|
| [react-expert](skill/frontend/react-expert/SKILL.md) | 现代 React（18/19）hooks、组件设计、状态、性能与 Server Components。 |
| [nextjs-expert](skill/frontend/nextjs-expert/SKILL.md) | Next.js App Router、Server Components、缓存与 Server Actions。 |
| [tailwind-expert](skill/frontend/tailwind-expert/SKILL.md) | Tailwind CSS 工具类、响应式、主题与设计系统。 |
| [accessibility-expert](skill/frontend/accessibility-expert/SKILL.md) | Web 无障碍：WCAG、语义化 HTML、ARIA、键盘导航与读屏。 |
| [threejs](skill/frontend/threejs/SKILL.md) | Three.js 全流程：场景、几何、材质、灯光、纹理、动画、加载、着色器、后处理与交互，附场景脚手架。 |

### 后端与数据（backend/）

| 技能 | 说明 |
|---|---|
| [nodejs-backend-expert](skill/backend/nodejs-backend-expert/SKILL.md) | Node.js 服务（Express/Fastify/Hono）：路由、中间件、鉴权与异步。 |
| [api-design-expert](skill/backend/api-design-expert/SKILL.md) | REST/GraphQL API 设计：资源建模、版本化、分页、错误与契约。 |
| [sql-expert](skill/backend/sql-expert/SKILL.md) | SQL 查询、表结构设计、索引、查询优化与事务。 |

### AI / 大模型（ai/）

| 技能 | 说明 |
|---|---|
| [deep-learning-expert](skill/ai/deep-learning-expert/SKILL.md) | 模型架构设计、训练策略、调试与论文解读。 |
| [llm-testing-expert](skill/ai/llm-testing-expert/SKILL.md) | LLM 评测策略、提示词工程、红队与回归测试。 |
| [prompt-engineering-expert](skill/ai/prompt-engineering-expert/SKILL.md) | 提示词结构、few-shot、思维链与结构化输出。 |
| [rag-expert](skill/ai/rag-expert/SKILL.md) | RAG 分块、嵌入、向量/混合检索、重排与答案接地。 |

### DevOps 与系统（devops/）

| 技能 | 说明 |
|---|---|
| [docker-expert](skill/devops/docker-expert/SKILL.md) | Dockerfile、多阶段构建、镜像优化与 Compose。 |
| [kubernetes-expert](skill/devops/kubernetes-expert/SKILL.md) | Kubernetes 工作负载、Service、配置、探针与排障。 |
| [bash-scripting-expert](skill/devops/bash-scripting-expert/SKILL.md) | 健壮安全的 Bash 脚本：引号、错误处理与 POSIX 可移植性，附检查脚本。 |
| [github-master](skill/devops/github-master/SKILL.md) | Git/GitHub 工作流、PR、分支保护与 Actions CI/CD。 |

### 质量、架构与算法（engineering/）

| 技能 | 说明 |
|---|---|
| [testing-expert](skill/engineering/testing-expert/SKILL.md) | 单元/集成/e2e 测试、TDD、测试替身与覆盖率。 |
| [debugging-expert](skill/engineering/debugging-expert/SKILL.md) | 系统化复现、二分定位与根因分析。 |
| [refactoring-expert](skill/engineering/refactoring-expert/SKILL.md) | 安全、增量、保持行为的重构与技术债清理。 |
| [performance-expert](skill/engineering/performance-expert/SKILL.md) | CPU、内存、I/O 与渲染性能剖析和优化。 |
| [security-expert](skill/engineering/security-expert/SKILL.md) | 安全编码与代码审查（OWASP Top 10）、鉴权与密钥管理。 |
| [software-architect](skill/engineering/software-architect/SKILL.md) | 系统设计、技术选型与架构权衡。 |
| [competitive-programming-expert](skill/engineering/competitive-programming-expert/SKILL.md) | 算法竞赛解题、复杂度分析与优化。 |

## 个人技能（personal_skill/）

| 技能 | 说明 |
|---|---|
| [cpp-code-standard](personal_skill/cpp-code-standard/SKILL.md) | C/C++ 命名、排版、注释、类型及现代 C++ 用法规范，附文件头检查脚本。 |
| [installer-extract](personal_skill/installer-extract/SKILL.md) | Windows 安装包解包部署、快捷方式、启动验证与更新处理。 |

## 安装

把下面的提示词发给具备联网和文件操作能力的编程助手，安装全部技能：

```text
请从 https://github.com/Miaoge-Ge/agent-skills 安装全部技能。

仓库使用标准 Agent Skills 格式，技能分布在 skill/ 和 personal_skill/ 两个目录，skill/ 下按语言、前端、后端、AI、DevOps 和工程质量分类。
请递归查找这两个目录下所有包含 SKILL.md 的技能目录，先读取 SKILL.md，再把完整技能目录（包括 references、scripts 等全部文件）复制到当前工具支持的用户级技能目录。
如果已存在同名技能，先比较版本，保留本地自定义修改。
完成后列出已安装技能的名称、版本和安装路径。
```

只安装一个技能时，把提示词里的“全部技能”和“所有技能”换成具体路径，例如：

```text
请从 https://github.com/Miaoge-Ge/agent-skills 安装 skill/languages/cpp-expert 技能。

仓库使用标准 Agent Skills 格式。请先读取该目录下的 SKILL.md，再把完整技能目录（包括 references、scripts 等全部文件）复制到当前工具支持的用户级技能目录。
如果已存在同名技能，先比较版本，保留本地自定义修改。
完成后报告技能名称、版本和安装路径。
```

## 目录结构

```text
agent-skills/
├── skill/
│   ├── languages/          # cpp-expert, python-code-standard, python-expert, ...
│   ├── frontend/           # react-expert, nextjs-expert, tailwind-expert, accessibility-expert
│   │   └── threejs/        # 合并后的 Three.js 技能
│   │       ├── SKILL.md
│   │       ├── references/ # 10 个主题参考
│   │       └── scripts/    # create_scene.mjs
│   ├── backend/            # nodejs-backend-expert, api-design-expert, sql-expert
│   ├── ai/                 # deep-learning-expert, llm-testing-expert, ...
│   ├── devops/             # docker-expert, kubernetes-expert, bash-scripting-expert, github-master
│   └── engineering/        # testing-expert, debugging-expert, ...
├── personal_skill/
│   ├── cpp-code-standard/  # SKILL.md + references/ + scripts/
│   └── installer-extract/
├── scripts/
│   └── validate_skills.py  # 全仓库技能校验
├── skills.sh.json          # skills CLI 的发现路径
├── README.md
├── README.en.md
└── LICENSE
```

## 脚本与校验

| 脚本 | 用途 |
|---|---|
| `scripts/validate_skills.py` | 校验全部技能的 frontmatter、名称、版本、相对链接和发现路径。 |
| `skill/frontend/threejs/scripts/create_scene.mjs` | 生成可直接运行的 Three.js 场景、相机、灯光、OrbitControls 和渲染循环。 |
| `skill/languages/python-code-standard/scripts/check_python.py` | 按技能规则检查 Python 语法、类型标注、裸 `except`、可变默认参数和通配导入。 |
| `personal_skill/cpp-code-standard/scripts/check_headers.py` | 检查 C/C++ 文件头、头文件包含保护和头文件中的 `using namespace`。 |
| `skill/devops/bash-scripting-expert/scripts/check_script.sh` | 运行 `bash -n`/`sh -n`，并在安装 ShellCheck 时运行 `shellcheck -x`。 |

```bash
python scripts/validate_skills.py
```

## 使用示例

```text
用 cpp-code-standard 审查当前修改，逐项指出不符合项，先不要改代码。
```

```text
按 threejs 技能给场景加灯光和阴影。
```

## 版本与维护

版本号写在各技能 `SKILL.md` 的 `metadata.version` 中。新增或修改技能时同步更新版本号、本 README 的技能列表，并运行 `scripts/validate_skills.py`。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
