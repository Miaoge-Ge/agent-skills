# 提交信息规范

本规范以 [Conventional Commits 1.0.0](https://www.conventionalcommits.org/zh-hans/v1.0.0/) 为基础，补充团队可执行的写作细则。提交信息是历史的一部分：读者是未来的维护者、发布工具和代码审查者。

## 格式

```text
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

- 第一行是标题，包含类型、可选范围、可选破坏性标记和描述。
- 标题与正文之间必须空一行；正文与页脚之间也必须空一行。
- 页脚键值对每行一个，键名用 `-` 代替空格（`BREAKING CHANGE` 是唯一例外）。

## 类型

| 类型 | 用途 | 版本影响 | 示例 |
|---|---|---|---|
| `feat` | 面向用户的新能力 | MINOR | `feat(export): add CSV download` |
| `fix` | 修复缺陷 | PATCH | `fix(parser): reject trailing commas` |
| `docs` | 仅文档变更 | 无 | `docs(readme): clarify install steps` |
| `style` | 仅格式、空白、分号等，不改行为 | 无 | `style(ui): apply prettier` |
| `refactor` | 既不修缺陷也不加能力的代码调整 | 无 | `refactor(store): extract selectors` |
| `perf` | 性能优化 | PATCH | `perf(query): cache user lookups` |
| `test` | 仅测试代码 | 无 | `test(api): cover 429 retries` |
| `build` | 构建系统、依赖或打包 | 无 | `build(deps): bump vite to 5.4` |
| `ci` | CI 配置和脚本 | 无 | `ci: run tests on Windows` |
| `chore` | 杂项维护，不动 src 或 test | 无 | `chore: ignore local env files` |
| `revert` | 撤销既有提交 | 视被撤销提交 | `revert: feat(auth): add SSO` |

选择类型时问自己“这个变更的主要目的”：为修缺陷顺带重构，用 `fix`；为重构顺带修了缺陷，用 `refactor` 并在正文说明。发布工具只按类型推导版本，因此不要用 `feat` 标记内部重构。

## 范围（scope）

- 用模块、目录、子系统或功能名：`auth`、`api`、`parser`、`docs`、`deps`。
- 小写，短名词；多个词用 `-` 连接：`user-profile`。
- 不用人名、日期、工单号或“misc”“stuff”这类无信息范围。
- 跨模块变更可以省略范围，或在正文说明涉及模块；不要写 `feat(a, b):`。

## 描述（description）

- 紧接 `: `，只空一格；不要写成 `feat:add` 或 `feat:  add`。
- 动词开头，说明这次提交做了什么：
  - 英文：祈使句、首字母小写、结尾不加句号。写 `add retry`，不写 `added retry` 或 `adds retry`。
  - 中文：直接用动词短语，如 `修复空指针`、`增加导出入口`，结尾不加句号。
- 标题总长不超过 72 字符，描述本身尽量控制在 50 字符以内。
- 具体胜于笼统：`fix(parser): reject trailing commas` 优于 `fix: bug`。
- 不写无信息内容：`update`、`changes`、`wip`、`fix bug`、`minor fixes`。
- 不在标题里堆 issue 号；放到页脚 `Refs:`。

## 正文（body）

- 解释“为什么”和“影响”，代码本身已经说明“怎么做”。
- 每行建议不超过 72 字符，段落之间空行；可用 `-` 列表。
- 适合写：动机、取舍、迁移步骤、兼容性影响、性能数据、复现条件。
- 不适合写：逐行复述 diff、情绪化描述、与本次提交无关的计划。
- 正文可以分多段；不要把页脚混进正文段落。

## 页脚（footer）

| 页脚 | 用途 | 示例 |
|---|---|---|
| `BREAKING CHANGE:` | 描述不兼容变更和迁移方式 | `BREAKING CHANGE: remove /v1 API` |
| `BREAKING-CHANGE:` | 同上，连字符写法 | `BREAKING-CHANGE: config key renamed` |
| `Refs:` | 关联 issue、PR 或文档 | `Refs: #123, #456` |
| `Closes:` | 合并后关闭 issue | `Closes: #123` |
| `Co-authored-by:` | 共同作者 | `Co-authored-by: A <a@example.com>` |
| `Signed-off-by:` | DCO 签署 | `Signed-off-by: A <a@example.com>` |
| `Reviewed-by:` | 记录评审者 | `Reviewed-by: B <b@example.com>` |

页脚键名区分大小写；自定义键用 `-` 连接单词，例如 `Migration-Note:`。页脚值可以换行，续行需缩进。

## 破坏性变更

破坏性变更必须让读者和工具都能识别，推荐两种标记同时使用：

```text
feat(api)!: drop the legacy /v1/session endpoint

BREAKING CHANGE: /v1/session is removed; use /v2/auth/session instead.
Clients pinned to v1 must upgrade before 2026-06-01.
```

- `!` 放在类型或范围之后、冒号之前：`feat!:`、`feat(api)!:`。
- `BREAKING CHANGE:` 页脚说明影响与迁移路径；只写“breaking”没有信息量。
- 两者同时出现最稳妥：人读页脚，工具读 `!`。
- 破坏性变更对应 MAJOR 版本；发布前确认迁移文档和弃用周期。

## 撤销提交

优先用 `revert` 类型并保留可追溯信息：

```text
revert: feat(auth): add SSO login

This reverts commit 3f2a1c9d8e7b6a5c4d3e2f1a0b9c8d7e6f5a4b3c.

Reason: the identity provider rollout was paused; the change will return
after the vendor restores its staging environment.
```

- 不要用 `git revert` 默认生成的 `Revert "feat: ..."` 作为最终标题；用 `git revert --edit` 改成 `revert:` 类型。
- 撤销 merge commit 用 `git revert -m 1 <sha>`，并在正文说明保留的是哪一侧历史。
- 撤销后不要删除原提交；历史保留因果链。

## 正反例

| 不推荐 | 推荐 | 原因 |
|---|---|---|
| `update stuff` | `chore(deps): bump eslint to 9.12.0` | 说明对象和动作 |
| `fix bug` | `fix(parser): reject trailing commas` | 指出缺陷位置 |
| `feat: Added login.` | `feat(auth): add passwordless login` | 小写祈使句、无句号 |
| `WIP` | 合并前 squash 成完整提交 | 历史不保留半成品 |
| `fix: typo` | `docs(readme): fix broken install link` | 类型与范围匹配 |
| `refactor: fix crash` | `fix(core): handle missing config` | 按主要目的选类型 |
| `feat: add tests` | `test(api): cover retry backoff` | 测试变更用 test |
| `feat(api): add x (#123)` | `feat(api): add x` + `Closes: #123` | 工单号放页脚 |

## 原子提交

一个提交应满足：

- 只做一件事，标题不需要用“并且”连接两个目的。
- 可以独立回滚，不会牵连无关文件。
- 在提交点上尽量可构建、可测试；确实做不到时在正文说明。
- 不混入格式化、重命名、依赖升级等噪声；需要时单独提交。

常见拆分：

- 重构 + 行为变更：先 `refactor`，再 `feat` / `fix`。
- 修复 + 测试：测试与修复放同一提交，保证回归可验证。
- 依赖升级 + 适配代码：可以同一提交，但标题以 `build(deps):` 开头并在正文说明适配。

## 工具配置

commitlint 可作为团队强制校验：

```json
{
  "extends": ["@commitlint/config-conventional"],
  "rules": {
    "header-max-length": [2, "always", 72],
    "subject-case": [2, "always", ["lower-case", "sentence-case"]],
    "body-max-line-length": [1, "always", 72]
  }
}
```

没有 Node 工具链时，使用本技能自带的 `scripts/commit_msg_lint.py` 与 `scripts/install_hooks.py` 安装 commit-msg 钩子。校验器只是底线，标题是否清楚仍需人来判断。
