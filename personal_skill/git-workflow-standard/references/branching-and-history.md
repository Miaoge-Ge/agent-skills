# 分支与历史

目标：默认分支始终可发布，功能分支短小，历史可读、可回滚、可审计。

## 选择集成模型

| 模型 | 适用场景 | 要点 |
|---|---|---|
| Trunk-based | 小团队、持续部署、功能开关成熟 | 分支存活不超过几天，频繁小 PR，默认分支受保护 |
| GitHub flow | 大多数产品仓库 | 功能分支 + PR + squash 合并，默认分支始终可发布 |
| Git flow | 有明确版本线、需并行维护旧版本 | `develop`、`release/*`、`hotfix/*`，流程重，非必要不引入 |

先看仓库现有约定（`CONTRIBUTING.md`、分支保护规则、CI 配置）；没有约定时默认 GitHub flow。

## 分支命名

格式：`<type>/<kebab-case-summary>`，可选带 issue 号。

| 前缀 | 用途 | 示例 |
|---|---|---|
| `feat/` | 新功能 | `feat/oauth-device-flow` |
| `fix/` | 缺陷修复 | `fix/123-null-pointer` |
| `docs/` | 文档 | `docs/quickstart` |
| `refactor/` | 重构 | `refactor/config-loader` |
| `perf/` | 性能 | `perf/cache-user-lookups` |
| `test/` | 测试 | `test/retry-backoff` |
| `build/` | 构建与依赖 | `build/vite-5` |
| `ci/` | 流水线 | `ci/windows-matrix` |
| `chore/` | 维护 | `chore/ignore-env` |
| `hotfix/` | 线上紧急修复 | `hotfix/session-leak` |
| `release/` | 发布准备 | `release/v1.4.0` |

规则：

- 全小写，单词用 `-` 连接；不用空格、下划线、中文和表情。
- 描述 2–5 个词，说明变更内容，不写 `test`、`tmp`、`new`。
- 分支名不要带日期或人名；issue 号放在描述前部即可。
- 分支名不承诺长期存在，合并后删除。

## 创建分支

```bash
git fetch --prune origin
git switch -c feat/oauth-device-flow origin/main
```

- 始终从最新的默认分支创建，不要从旧本地分支或别人的功能分支拉新分支。
- 分离 HEAD 状态下先 `git switch -c <branch>` 再提交。
- 一个分支只承载一个主题；需要并行处理时新建分支或 `git worktree add`。

## 同步与变基

```bash
git fetch --prune origin
git rebase origin/main
```

- 本地功能分支用 rebase 跟随默认分支，保持线性、易读的提交序列。
- 已推送且有人在用的分支不要 rebase；改用合并默认分支，避免他人历史被改写。
- `git pull` 默认可能产生合并提交；需要线性历史时配置 `git config pull.rebase true`，或显式 `git pull --rebase`。
- 冲突处理：
  1. `git status` 找出冲突文件，逐个理解双方意图，不要整段选一边了事。
  2. 编辑后 `git add <file>`，`git rebase --continue`。
  3. 拿不准时 `git rebase --abort` 回到起点，先备份 `git branch backup/<name>`。
- 变基后必须重新运行测试，冲突解决可能引入语义错误。

## 整理本地历史

```bash
# 合并最近 3 个提交并改写信息
git rebase -i HEAD~3

# 自动吸收 fixup! / squash! 提交
git commit --fixup=<sha>
git rebase -i --autosquash origin/main
```

- 只整理未共享的提交；共享后改写会让协作者的历史分叉。
- 合并提交时保留有价值的“为什么”，不要把所有正文压成一句标题。
- 整理后用 `git log --oneline origin/main..HEAD` 复查，确认每个提交都能独立解释。
- 改写前记下原 HEAD：`git branch backup/<name>` 或 `git reflog` 可恢复。

## 强制推送

仅在自有功能分支、且确认远端没有他人提交时使用：

```bash
git fetch origin
git log --oneline origin/feat/oauth-device-flow..HEAD   # 确认将要覆盖什么
git push --force-with-lease origin feat/oauth-device-flow
```

- `--force-with-lease` 在远端被他人更新时拒绝覆盖；`--force` 会无条件覆盖，禁止使用。
- 不要在 `main`、`develop`、`release/*`、`gh-pages` 等共享分支上强推。
- 强推后通知协作者重新拉取，不要让他们把旧历史合并回来。
- 平台的分支保护通常直接拒绝强推；不要尝试绕过保护规则。

## 合并策略

| 策略 | 历史形态 | 适用 |
|---|---|---|
| Squash merge（默认） | 默认分支每个 PR 一个提交 | 功能分支提交较碎、希望历史干净 |
| Rebase merge | 线性，保留每个提交 | 提交已经原子、信息完整，需要保留粒度 |
| Merge commit | 保留分支拓扑 | 发布分支同步、需要保留合并关系 |

- squash 时 PR 标题必须符合 Conventional Commits，因为它会成为最终提交标题；PR 描述中的要点进入提交正文。
- 合并前确认 CI 通过、评审完成、分支已同步默认分支。
- 合并后删除远端和本地分支：`git push origin --delete <branch>`、`git branch -d <branch>`；用 `-D` 前确认分支已合并。

## 撤销与恢复

| 场景 | 命令 | 说明 |
|---|---|---|
| 撤销已推送提交 | `git revert <sha>` | 生成反向提交，历史保留 |
| 撤销 merge | `git revert -m 1 <sha>` | `-m 1` 保留第一父提交主线 |
| 撤销未推送提交，保留改动 | `git reset --soft HEAD~1` | 改动回到暂存区 |
| 撤销未推送提交，保留工作区 | `git reset --mixed HEAD~1` | 默认模式 |
| 丢弃本地改动 | `git restore <file>` | 先确认不需要 |
| 暂存现场 | `git stash push -u -m "wip: ..."` | 含未跟踪文件用 `-u` |
| 找回误删提交 | `git reflog` + `git branch rescue <sha>` | reflog 默认保留 90 天 |

`git reset --hard` 会丢弃工作区和暂存区改动，只在明确要放弃时使用，并先 `git stash` 或建备份分支。已推送历史用 revert，不要 reset 后强推。

## 标签与发布

- 版本遵循 SemVer：`MAJOR.MINOR.PATCH`，标签加 `v` 前缀：`v1.4.0`。
- 在默认分支的发布提交上打带注释标签：

```bash
git switch main
git pull --ff-only
git tag -a v1.4.0 -m "v1.4.0"
git push origin v1.4.0
```

- 标签只打一次；已推送的标签不移动、不删除。标签打错时发新的 PATCH 版本并在发布说明中注明。
- 轻量标签（`git tag v1.4.0`）不记录打标签者和说明，发布用带注释标签。
- 维护旧版本时从标签拉维护分支：`git switch -c release/1.3 v1.3.2`。

## 分支保护建议

在 GitHub 上为默认分支启用：

- 禁止直接 push，必须走 PR。
- 要求至少 1 个评审通过、CI 检查通过、分支与默认分支同步。
- 要求线性历史（squash 或 rebase），禁止 force push 和删除分支。
- 管理员同样受规则约束；紧急绕过需记录原因并事后补 PR。
