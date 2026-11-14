---
name: scan-skill-repos
description: "扫描 GitHub 上符合标准的 Agent Skill 仓库，校验 SKILL.md 布局与 frontmatter，解析版本和分类，并把通过复核的条目合并进 third_party_skill 的中英文目录。用于发现新 skill、刷新目录 Star 与版本、按关键词或星标阈值筛选候选时。"
metadata:
  version: "1.0.0"
---

# 扫描 GitHub 技能仓库

用 `scripts/scan_skill_repos.py` 发现、校验并收录第三方 Agent Skill。脚本只读取公开 GitHub 数据，写入只发生在 `--apply` 时。

## 前置条件

- 已安装并登录 GitHub CLI：`gh auth login`。
- 在包含 `third_party_skill/README.md` 的仓库根目录运行；脚本会自动向上查找目录。
- 需要写目录时使用 `--apply`，否则只输出候选清单。

## 工作流

1. **扫描候选**（dry run）：

   ```bash
   python personal_skill/scan-skill-repos/scripts/scan_skill_repos.py \
       --min-stars 10000 --limit 200 --report candidates.md
   ```

   脚本同时用仓库搜索和 `filename:SKILL.md` 代码搜索，因此名称/描述里没有 "skill" 的仓库也能被发现。

2. **人工复核**。重点看两点：
   - 仓库是否以 skill 为主体，而不是产品/工具顺带放了一个 `skills/` 目录；
   - 分类是否合理，说明是否适合目标语言。
   默认会校验 `SKILL.md` 的 `name`、`description` frontmatter 和正文长度；`--no-verify` 可关闭。

3. **写入目录**：

   ```bash
   python personal_skill/scan-skill-repos/scripts/scan_skill_repos.py \
       --min-stars 10000 --limit 200 --apply
   ```

   已知仓库的中英文说明优先取 [descriptions.json](references/descriptions.json)；没有覆盖时使用上游描述。写入后检查 `git diff`，必要时补充中文说明。

4. **刷新已有条目**：

   ```bash
   python personal_skill/scan-skill-repos/scripts/scan_skill_repos.py \
       --refresh --refresh-stars-only --apply
   ```

   只刷 Star 不查版本；去掉 `--refresh-stars-only` 会同时刷新版本，速度较慢。

## 常用参数

| 参数 | 作用 |
|---|---|
| `--min-stars` | 星标阈值，默认 3000 |
| `--limit` | 最多校验多少个候选 |
| `--query` | 替换默认搜索词，可重复 |
| `--exclude` | 跳过指定 `owner/repo`，可重复 |
| `--no-code-search` | 关闭 `filename:SKILL.md` 代码搜索 |
| `--code-pages` / `--max-code-repos` | 代码搜索页数与仓库上限 |
| `--apply` | 把候选写入两份目录文档 |
| `--refresh` / `--refresh-stars-only` | 刷新已有条目的 Star/版本 |
| `--json` / `--report` | JSON 输出或 Markdown 报告 |

## 校验与安全

- 只接受根目录 `SKILL.md` 或 `skills/<名称>/SKILL.md`（含嵌套插件布局），拒绝 `docs/skill/SKILL.md` 等仿冒路径。
- 默认要求仓库有 LICENSE、未归档、非 fork；`--allow-no-license` 可放开。
- 分类由关键词推断，只作初筛，写入前必须人工确认。
- GitHub 代码搜索最多返回 1000 个文件结果，大规模扫描时调大 `--code-pages` 和 `--max-code-repos`。
- 描述会转义表格管道符并按行宽截断；中文目录用中文说明，英文目录用英文说明。
