---
name: python-code-standard
description: 按统一规范编写、修改和审查 Python 代码，检查类型标注、异常处理、命名、结构与常见性能问题；用于用户明确要求采用本规范，或仓库已声明采用本规范的工程。
metadata:
  version: "1.0.0"
---

# Python 代码规范

## 执行流程

1. 读取适用的仓库指令、类型检查与格式化配置，确认修改范围、Python 版本和依赖约束。
2. 编写或修改代码前核对以下规则；完整审查时逐项检查。
3. 仅审查时不修改文件；修改时只处理指定范围，不扩大为无关重排。
4. 检查最终差异；涉及行为变化时运行相关测试、类型检查或静态检查，报告结果及未验证范围。

## 类型与异常

- 所有函数参数和返回值都标注类型，避免 `Any`；按仓库配置运行 `mypy`（严格模式优先）。
- 捕获具体异常类型，禁止裸 `except:` 或宽泛的 `except Exception:`；日志带上参数与上下文。
- 不吞异常：要么处理，要么保留原异常重新抛出；不要用异常控制正常流程。

## 性能与不可变

- 大数据用生成器（`yield`），简单映射/过滤可用推导式，字符串拼接用 `str.join`。
- 优先 `Final` 和 `frozen=True` 的 dataclass；禁止可变默认参数，用 `None` 在函数体内初始化。
- 用上下文管理器（`with`）管理资源，不手动打开/关闭文件。

## 命名

| 对象 | 规则 | 示例 |
|---|---|---|
| 类 | 大驼峰 | `HttpClient`、`DataProcessor` |
| 函数、变量、属性 | 小写下划线 | `fetch_data()`、`user_count` |
| 常量 | 全大写下划线 | `MAX_RETRIES`、`DEFAULT_TIMEOUT` |
| 私有成员 | 单下划线前缀 | `_internal_cache` |
| 模块 | 简短小写下划线 | `data_utils.py` |

## 结构

- 函数约 20 行以内，类公开方法约 5 个以内，模块约 500 行以内；超出时按职责拆分。
- 导入顺序：标准库 → 第三方 → 本地，组间空行；可用 `isort` 或仓库现有工具维护。
- 避免循环导入：仅类型需要时在 `TYPE_CHECKING` 下导入，或调整模块边界。

## 文档

- 公开 API 使用 Google 或 NumPy 风格 docstring，说明参数类型、返回值和可能抛出的异常。

## 示例

```python
from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path

logger = logging.getLogger(__name__)


def read_lines(path: Path) -> Iterator[str]:
    """逐行产出非空且去除首尾空白的行。

    Args:
        path: UTF-8 文本文件路径。

    Raises:
        FileNotFoundError: 文件不存在时抛出。
    """
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    yield stripped
    except FileNotFoundError:
        logger.error("File not found: %s", path)
        raise
```

反例：

```python
def read_lines(path, cache=[]):  # 可变默认参数
    f = open(path)               # 文件不会关闭
    try:
        lines = f.readlines()
    except:                      # 裸 except 吞掉所有异常
        return cache
    return lines
```
