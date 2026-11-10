# 安全与恢复

Git 操作里真正危险的是不可逆的历史改写和文件删除。执行前先明确：影响哪个分支、是否已推送、是否有备份、能否用 revert 代替。

## 提交前检查

```bash
git status --short --branch
git diff --cached --stat
git diff --cached
python scripts/git_guard.py --staged
```

确认：

- 暂存内容只包含本次变更，没有 `git add -A` 带进来的无关文件。
- 没有密钥、令牌、私钥、证书、`.env`、数据库转储、真实用户数据。
- 没有超过仓库限制的大文件；二进制和模型文件用 Git LFS 或制品库。
- 没有冲突标记、调试输出、被注释掉的代码。
- 当前不在分离 HEAD，也没有进行到一半的 merge / rebase / cherry-pick。

## 绝不提交

- API key、访问令牌、密码、cookie、私钥、证书私钥、SSH key。
- `.env`、`credentials.json`、`.npmrc` 中的认证行、云服务配置文件中的密钥。
- 生产数据库转储、包含个人信息的日志、客户数据。
- 构建产物、依赖目录、IDE 配置、操作系统缓存（应由 `.gitignore` 排除）。
- 体积过大的二进制、模型、视频；改用 LFS 或外部制品存储。

`.gitignore` 只能防止误加入，不能保护已经提交的内容。密钥扫描应同时存在于本地钩子和 CI。

## 密钥已经提交怎么办

1. 立即轮换或吊销密钥；清理历史不能替代轮换，因为密钥可能已被克隆或缓存。
2. 评估影响范围：哪些系统、哪些权限、是否有访问日志。
3. 从当前代码移除，并加入 `.gitignore` 和扫描规则。
4. 清理历史（需要团队协调）：

   ```bash
   git filter-repo --path path/to/secret --invert-paths
   # 或替换文本
   git filter-repo --replace-text replacements.txt
   ```

5. 强制推送所有受影响分支和标签，通知协作者重新克隆；旧对象可能仍存在于平台缓存和 fork 中。
6. 在事故记录中写明时间线、根因和防复发措施。

不要只在新提交里删除密钥就认为问题解决；历史仍可检出。

## 危险命令

| 命令 | 影响 | 更安全的替代 |
|---|---|---|
| `git reset --hard` | 丢弃暂存区和工作区改动 | `git stash push -u`、`git restore` |
| `git clean -fd` | 删除未跟踪文件和目录 | 先 `git clean -nd` 预览，再逐个删除 |
| `git clean -fdx` | 连忽略文件一起删除（构建产物、本地配置） | 明确知道会删什么再用 |
| `git push --force` | 无条件覆盖远端历史 | `git push --force-with-lease`，且仅限自有分支 |
| `git branch -D` | 强制删除未合并分支 | `git branch -d`，或先确认已合并 |
| `git checkout -- <file>` | 丢弃文件改动 | `git restore <file>`，先看 diff |
| `git rebase` 共享分支 | 改写他人历史 | 只 rebase 本地未共享提交 |
| `git commit --no-verify` | 跳过本地检查 | 修复问题或修复钩子 |
| `git update-ref -d` | 直接删除引用 | 用 `git branch -d` / `git tag -d` 并确认 |

破坏性命令执行前：

1. `git status` 确认当前状态。
2. 建备份分支 `git branch backup/<name>` 或 `git stash push -u -m "before ..."`。
3. 向用户说明将丢失什么，取得明确同意。
4. 执行后立即验证 `git status`、`git log` 和远端状态。

## 恢复操作

| 情况 | 恢复方式 |
|---|---|
| 误删分支 | `git reflog` 找到提交，`git branch <name> <sha>` |
| 误 reset | `git reflog`，`git reset --hard <old-sha>`（确认后） |
| 误 rebase | `git reflog` 找到 rebase 前 HEAD，`git reset --hard <sha>` |
| 误 amend | `git reflog`，恢复旧提交后重新整理 |
| 误删标签 | `git reflog` 或远端 `git fetch --tags`；本地删除未推送标签可直接重建 |
| 误强推 | 从本地 reflog 或平台事件恢复；协作者本地副本也可能保留 |
| 误 stash pop 冲突 | `git stash list`，必要时 `git stash branch <name> <stash>` |
| 文件被误删未提交 | `git restore <file>`；已提交则 `git checkout <sha> -- <file>` |

`git reflog` 默认保留 HEAD 移动记录 90 天、可达对象 30 天；发现误操作后尽快恢复，不要继续大量提交覆盖记录。

## 大文件与 LFS

- 超过 5 MiB 的二进制默认不入库；确需版本化时用 Git LFS：`git lfs track "*.psd"`，提交 `.gitattributes`。
- 已经提交的大文件不能靠删除新提交解决，历史仍会保留；用 `git filter-repo --strip-blobs-bigger-than 5M` 清理并协调强推。
- 构建产物、依赖目录、日志、缓存加入 `.gitignore`，并在 CI 中检查仓库体积。

## 钩子与检查

- 本技能的 `install_hooks.py` 安装 `commit-msg` 和 `pre-commit` 钩子；已有他人钩子时默认拒绝覆盖，需 `--force`。
- 钩子失败时修复问题，不要用 `--no-verify` 绕过；如果钩子本身有缺陷，修钩子并单独提交。
- 团队应在 CI 中重复关键检查（提交信息、密钥扫描、测试），本地钩子可被跳过，不能作为唯一防线。
- `core.hooksPath` 指向自定义目录时，钩子应安装到该目录；脚本通过 `git rev-parse --git-path hooks` 自动识别。

## 网络与远端

- 推送前 `git fetch --prune`，确认远端分支状态和权限。
- 不把凭据写进 remote URL；使用凭据管理器、SSH key 或短期令牌。
- 公共仓库推送前确认没有内部地址、客户名称、未公开漏洞细节。
- 推送后核对 `git status -sb` 与平台 CI 状态；推送失败不要反复重试强推。
