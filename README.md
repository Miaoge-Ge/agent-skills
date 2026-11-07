# Agent Skills

[简体中文](README.md) | [English](README.en.md)

面向 AI 编程助手的标准 Agent Skills 合集。每个技能都是独立目录，包含 `SKILL.md` 和可选的 `references/` 等支撑文件，可直接被支持 Agent Skills 的工具读取和使用。

仓库按来源分为两类：

- `skill/`：原有通用技能。
- `cyg_skill/`：新合并的 cyg 系列技能。

共 40 个技能：`skill/` 38 个，`cyg_skill/` 2 个。

## 通用技能（skill/）

### 编程语言与规范

| 技能 | 说明 |
|---|---|
| [python-code-standard](skill/python-code-standard/SKILL.md) | Python 类型标注、异常处理、命名、结构与性能规范。 |
| [cpp-expert](skill/cpp-expert/SKILL.md) | 现代 C++（17/20/23）、内存安全、模板、性能与未定义行为诊断。 |
| [python-expert](skill/python-expert/SKILL.md) | Pythonic 代码、类型、异步、标准库与性能。 |
| [typescript-expert](skill/typescript-expert/SKILL.md) | TypeScript 类型系统、泛型、类型收窄与严格模式安全。 |
| [rust-expert](skill/rust-expert/SKILL.md) | Rust 所有权、生命周期、trait、异步与错误处理。 |
| [go-expert](skill/go-expert/SKILL.md) | 地道 Go、并发、接口与错误处理。 |

### 前端与 3D

| 技能 | 说明 |
|---|---|
| [react-expert](skill/react-expert/SKILL.md) | 现代 React（18/19）hooks、组件设计、状态、性能与 Server Components。 |
| [nextjs-expert](skill/nextjs-expert/SKILL.md) | Next.js App Router、Server Components、缓存与 Server Actions。 |
| [tailwind-expert](skill/tailwind-expert/SKILL.md) | Tailwind CSS 工具类、响应式、主题与设计系统。 |
| [accessibility-expert](skill/accessibility-expert/SKILL.md) | Web 无障碍：WCAG、语义化 HTML、ARIA、键盘导航与读屏。 |
| [threejs-fundamentals](skill/threejs-fundamentals/SKILL.md) | Three.js 场景、相机、渲染器与对象层级。 |
| [threejs-geometry](skill/threejs-geometry/SKILL.md) | 几何体、BufferGeometry、自定义几何与实例化。 |
| [threejs-materials](skill/threejs-materials/SKILL.md) | PBR、基础、Phong 与着色器材质。 |
| [threejs-lighting](skill/threejs-lighting/SKILL.md) | 灯光类型、阴影与环境光照。 |
| [threejs-textures](skill/threejs-textures/SKILL.md) | 纹理类型、UV、环境贴图与纹理设置。 |
| [threejs-animation](skill/threejs-animation/SKILL.md) | 关键帧、骨骼动画、变形目标与动画混合。 |
| [threejs-loaders](skill/threejs-loaders/SKILL.md) | GLTF、纹理、HDR 等资源加载与异步模式。 |
| [threejs-shaders](skill/threejs-shaders/SKILL.md) | GLSL、ShaderMaterial、uniform 与自定义效果。 |
| [threejs-postprocessing](skill/threejs-postprocessing/SKILL.md) | EffectComposer、泛光、景深与屏幕后处理。 |
| [threejs-interaction](skill/threejs-interaction/SKILL.md) | 射线拾取、控制器与鼠标/触摸交互。 |

### 后端与数据

| 技能 | 说明 |
|---|---|
| [nodejs-backend-expert](skill/nodejs-backend-expert/SKILL.md) | Node.js 服务（Express/Fastify/Hono）：路由、中间件、鉴权与异步。 |
| [api-design-expert](skill/api-design-expert/SKILL.md) | REST/GraphQL API 设计：资源建模、版本化、分页、错误与契约。 |
| [sql-expert](skill/sql-expert/SKILL.md) | SQL 查询、表结构设计、索引、查询优化与事务。 |

### AI / 大模型

| 技能 | 说明 |
|---|---|
| [deep-learning-expert](skill/deep-learning-expert/SKILL.md) | 模型架构设计、训练策略、调试与论文解读。 |
| [llm-testing-expert](skill/llm-testing-expert/SKILL.md) | LLM 评测策略、提示词工程、红队与回归测试。 |
| [prompt-engineering-expert](skill/prompt-engineering-expert/SKILL.md) | 提示词结构、few-shot、思维链与结构化输出。 |
| [rag-expert](skill/rag-expert/SKILL.md) | RAG 分块、嵌入、向量/混合检索、重排与答案接地。 |

### DevOps 与系统

| 技能 | 说明 |
|---|---|
| [docker-expert](skill/docker-expert/SKILL.md) | Dockerfile、多阶段构建、镜像优化与 Compose。 |
| [kubernetes-expert](skill/kubernetes-expert/SKILL.md) | Kubernetes 工作负载、Service、配置、探针与排障。 |
| [bash-scripting-expert](skill/bash-scripting-expert/SKILL.md) | 健壮安全的 Bash 脚本：引号、错误处理与 POSIX 可移植性。 |
| [github-master](skill/github-master/SKILL.md) | Git/GitHub 工作流、PR、分支保护与 Actions CI/CD。 |

### 质量、架构与算法

| 技能 | 说明 |
|---|---|
| [testing-expert](skill/testing-expert/SKILL.md) | 单元/集成/e2e 测试、TDD、测试替身与覆盖率。 |
| [debugging-expert](skill/debugging-expert/SKILL.md) | 系统化复现、二分定位与根因分析。 |
| [refactoring-expert](skill/refactoring-expert/SKILL.md) | 安全、增量、保持行为的重构与技术债清理。 |
| [performance-expert](skill/performance-expert/SKILL.md) | CPU、内存、I/O 与渲染性能剖析和优化。 |
| [security-expert](skill/security-expert/SKILL.md) | 安全编码与代码审查（OWASP Top 10）、鉴权与密钥管理。 |
| [software-architect](skill/software-architect/SKILL.md) | 系统设计、技术选型与架构权衡。 |
| [competitive-programming-expert](skill/competitive-programming-expert/SKILL.md) | 算法竞赛解题、复杂度分析与优化。 |

## cyg 系列技能（cyg_skill/）

| 技能 | 说明 |
|---|---|
| [cpp-code-standard](cyg_skill/cpp-code-standard/SKILL.md) | C/C++ 命名、排版、注释、类型及现代 C++ 用法规范。 |
| [installer-extract](cyg_skill/installer-extract/SKILL.md) | Windows 安装包解包部署、快捷方式、启动验证与更新处理。 |

## 安装

把下面的提示词发给具备联网和文件操作能力的编程助手，安装全部技能：

```text
请从 https://github.com/Miaoge-Ge/agent-skills 安装全部技能。

仓库使用标准 Agent Skills 格式，技能分布在 skill/ 和 cyg_skill/ 两个目录，每个技能目录包含 SKILL.md 和可选的 references 等支撑文件。
请先读取目标技能的 SKILL.md，再把完整技能目录（包括 references 等全部文件）复制到当前工具支持的用户级技能目录。
如果已存在同名技能，先比较版本，保留本地自定义修改。
完成后列出已安装技能的名称、版本和安装路径。
```

只安装一个技能时，把提示词里的“全部技能”和“指定技能”换成具体路径，例如：

```text
请从 https://github.com/Miaoge-Ge/agent-skills 安装 cyg_skill/cpp-code-standard 技能。

仓库使用标准 Agent Skills 格式。请先读取该目录下的 SKILL.md，再把完整技能目录（包括 references 等全部文件）复制到当前工具支持的用户级技能目录。
如果已存在同名技能，先比较版本，保留本地自定义修改。
完成后报告技能名称、版本和安装路径。
```

## 目录结构

```text
agent-skills/
├── skill/            # 原有通用技能，38 个
│   ├── cpp-expert/
│   │   └── SKILL.md
│   └── ...
├── cyg_skill/        # 新合并的 cyg 系列技能，2 个
│   ├── cpp-code-standard/
│   │   ├── SKILL.md
│   │   └── references/
│   └── installer-extract/
│       └── SKILL.md
├── skills.sh.json    # skills CLI 的发现路径
├── README.md
├── README.en.md
└── LICENSE
```

## 使用示例

```text
用 cpp-code-standard 审查当前修改，逐项指出不符合项，先不要改代码。
```

```text
按 threejs-lighting 技能给场景加灯光和阴影。
```

## 版本与维护

版本号写在各技能 `SKILL.md` 的 `metadata.version` 中。新增或修改技能时同步更新版本号和本 README 的技能列表。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
