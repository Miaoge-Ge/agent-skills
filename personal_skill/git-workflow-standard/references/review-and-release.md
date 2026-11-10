# 评审与发布

## PR 标题

PR 标题在 squash 合并时成为默认分支上的提交标题，因此必须遵循 [Conventional Commits](commit-message.md)：

```text
feat(auth): add device authorization flow
fix(parser): reject trailing commas in JSON input
docs: document the release process
```

- 一个 PR 一个主题；标题里出现“并且”“顺便”时考虑拆分。
- 草稿 PR 用平台 Draft 状态，不要用 `WIP` 标题进入可评审队列。
- 标题不带 issue 号；关联关系写进描述和提交页脚。

## PR 描述模板

```markdown
## 变更

- 简述用户可见或系统行为上的变化。

## 动机

为什么需要这个变更；关联 issue：Closes #123。

## 验证

- [ ] 单元测试：`python -m unittest discover -s tests`
- [ ] 手动验证步骤与结果
- [ ] 受影响平台 / 版本

## 风险与回滚

- 风险：兼容性、性能、数据迁移、配置变更。
- 回滚：revert 本 PR 是否安全；是否需要数据回滚脚本。

## 截图 / 日志

仅在与界面或错误行为相关时提供，避免粘贴密钥和用户数据。
```

## 提交前自查

- [ ] `git diff --cached` 只包含本次主题的文件，没有无关格式化、编辑器配置、构建产物。
- [ ] 没有密钥、令牌、私钥、`.env`、真实用户数据；已运行 `git_guard.py --staged`。
- [ ] 没有调试输出、临时注释、被注释掉的代码、`TODO` 占位实现。
- [ ] 新增和修改的行为有测试；测试在本地通过。
- [ ] 提交信息符合规范，标题能独立说明变更。
- [ ] 文档、示例、配置、迁移说明已同步。
- [ ] 依赖升级检查了许可证、安全公告和 lockfile 一致性。

## 评审者清单

- 正确性：边界条件、错误路径、并发与资源释放。
- 安全性：输入校验、权限检查、密钥处理、注入与反序列化风险。
- 兼容性：公开 API、配置键、数据格式、数据库迁移是否向后兼容。
- 可维护性：命名、抽象层级、重复逻辑；不把个人偏好当阻断项。
- 测试：覆盖回归点，断言有意义，不依赖执行顺序和真实网络。
- 可观测性：日志、指标、错误信息是否足以排查问题。
- 性能：是否引入 N+1 查询、无界内存、阻塞调用。

评审意见区分“阻断”与“建议”；风格问题交给格式化工具，不在评审里反复拉锯。

## 版本与变更日志

| 提交类型 | SemVer 影响 | 变更日志分组 |
|---|---|---|
| `feat` | MINOR | 新功能 |
| `fix` | PATCH | 修复 |
| `perf` | PATCH | 性能 |
| `refactor` | 无（除非行为变化） | 重构 |
| `docs`、`style`、`test`、`build`、`ci`、`chore` | 无 | 通常省略或归入维护 |
| 带 `!` 或 `BREAKING CHANGE:` | MAJOR | 破坏性变更（置顶） |
| `revert` | 视被撤销提交 | 撤销 |

从上一个标签生成变更日志草稿：

```bash
git log --no-merges --pretty=format:"%h %s" v1.3.0..HEAD
```

按类型分组后人工改写：删除内部噪声，合并重复项，为破坏性变更补迁移说明。发布说明面向使用者，不是提交列表的复读。

## 发布流程

1. 确认默认分支 CI 全绿，没有未合并的阻断 PR。
2. 确定版本号：有破坏性变更升 MAJOR，有 `feat` 升 MINOR，否则升 PATCH。
3. 更新版本文件、变更日志和升级说明，提交 `chore(release): v1.4.0`（或仓库既有发布提交约定）。
4. 在发布提交上打带注释标签并推送：

   ```bash
   git tag -a v1.4.0 -m "v1.4.0"
   git push origin main
   git push origin v1.4.0
   ```

5. 在代码托管平台创建 Release，附变更日志和制品校验值。
6. 验证发布制品：安装、启动、版本号、关键路径。
7. 发布后观察错误率和反馈；需要修复时走 `hotfix/` 分支和新 PATCH 版本。

## 热修复

```bash
git fetch --prune origin
git switch -c hotfix/session-leak origin/main
# 修复、测试、提交
git push -u origin hotfix/session-leak
```

- 热修复 PR 同样走评审和 CI，不因紧急而跳过。
- 合并后立即发布 PATCH 版本，并把修复回合到仍在维护的发布分支。
- 发布后补写事故记录：影响范围、根因、检测方式、后续改进。

## 发布检查表

- [ ] 版本号与 SemVer 一致，标签格式为 `vX.Y.Z`。
- [ ] 变更日志包含破坏性变更、迁移步骤和贡献者。
- [ ] lockfile、生成代码、文档与源码一致。
- [ ] 制品可复现，校验值已记录。
- [ ] 回滚方案经过验证；数据库迁移可向前兼容。
- [ ] 发布通知发给使用者和值班人员。
