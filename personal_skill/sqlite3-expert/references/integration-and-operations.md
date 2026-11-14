# 应用集成和常用操作

## sqlite3 命令行

只读查看已有数据库，先确认路径存在；以下为 shell 命令：

```text
sqlite3 -readonly "app.db"
```

以下在 SQLite CLI 内输入；点命令不是 SQL，不放到 Python execute 或 C prepare 中。

```text
.headers on
.mode box
.tables
.schema orders
.indexes orders
.eqp on
```

CLI 的 .schema 不替代索引和约束 PRAGMA；自动索引可能没有可打印的 CREATE INDEX。应用 SQL 中查询 sqlite_schema，数据库参数使用正确绑定。

执行初始化/迁移脚本时用可写连接，启用 .bail on 或 CLI -bail 遇错停止，并使用明确事务和结果检查；“遇错停止”不等于自动回滚之前提交的内容。PowerShell 不支持 Bash 风格输入重定向，不直接复制 sqlite3 app.db < script.sql；可使用 CLI .read 并正确引用路径。

## CSV、备份、空间维护

- 导入前明确编码、表头、分隔符、空值约定和目标列顺序。CLI .import 常把 CSV 空字段读成空字符串，不能假定它们都是 NULL。
- 对不可信或脏 CSV，先导入明确的暂存表，校验/转换后写目标表；统计输入、接受、拒绝行数并保留原因。不要为了导入成功删除目标约束。
- .import --csv --skip 1 等选项依 CLI 版本，先用 .help import 核实；已有表与自动建表的表头行为不同。
- 导出用 .mode csv、.headers on 和 .once "export.csv" 配合明确 SELECT；确定覆盖目标和是否允许导出相应数据。
- .backup "backup.db" 提供一致备份，备份目标必须明确，不能覆盖唯一恢复副本。.dump 是 SQL 逻辑导出，恢复需在干净目标验证，不能把导出成功等同恢复成功。
- DELETE 不必立即缩小主文件；VACUUM 用于需要回收空间的场景，需额外空间且不能在事务中运行。不要在每次写入后 VACUUM。
- ATTACH 的数据库路径可绑定，schema 标识符需白名单；不要把 ATTACH 多库事务当作所有日志模式下都整体原子。

## Python sqlite3

Python 标准库使用的引擎由 sqlite3.sqlite_version 或连接内 sqlite_version() 检查，不能用 Python 版本代替。连接上下文管理器处理事务但不会自动关闭连接；明确关闭。

下面是 Python 3.12+ 的显式 SQL 事务示例。它要求已有数据库和 SQLite 3.35+；路径 URI 用 Path.as_uri() 处理空格、#、? 等字符。autocommit=True 时使用 SQL BEGIN/COMMIT/ROLLBACK 管理事务，不依赖 Connection.commit()。

```python
from pathlib import Path
import sqlite3

db = Path(database_path).resolve(strict=True)
con = sqlite3.connect(db.as_uri() + '?mode=rw', uri=True,
                      autocommit=True, timeout=5.0)
try:
    con.execute('PRAGMA foreign_keys = ON')
    if con.execute('PRAGMA foreign_keys').fetchone()[0] != 1:
        raise RuntimeError('Foreign keys are not enabled')
    con.execute('BEGIN IMMEDIATE')
    rows = con.execute(
        '''UPDATE products SET stock = stock - ?
           WHERE product_id = ? AND stock >= ? RETURNING stock''',
        (quantity, product_id, quantity),
    ).fetchall()
    if len(rows) != 1:
        raise LookupError('Product missing or insufficient stock')
    con.execute('COMMIT')
except BaseException:
    if con.in_transaction:
        con.execute('ROLLBACK')
    raise
finally:
    con.close()
```

- 示例中的 quantity 必须由调用者验证为正整数；若扣库存还要创建订单/明细，把这些操作放在同一个事务，不能只提交库存变化。
- Python 3.11 及更早版本可使用 isolation_level=None 控制显式 SQL 事务；3.12+ 的 autocommit=False 会管理持续事务，不能在其内部随意切换 foreign_keys。先明确使用哪一种事务模型，不混搭。
- 值用 ? 或命名参数；单元素参数元组为 (value,)。绑定参数不能代替表名/列名，动态标识符必须经过白名单并转义双引号。
- executemany 适合复用写语句，但会丢弃 RETURNING 的结果，不能据此获取每行 ID。逐条执行或使用可验证的批次方案。
- executescript 不支持值参数绑定；在 legacy 事务模式下可能先提交现有事务。已有迁移事务中优先逐条 execute，并处理每步结果。
- 不在脚本内无条件覆盖调用者的事务策略；连接池每个连接都要初始化外键、等待策略和必要函数/排序规则。
- 默认线程检查不能简单通过 check_same_thread=False 当作并发方案；共享连接需要串行化事务，通常使用每工作单元独立连接。
- 内存库默认每个连接独立，连接关闭即消失；不能用另一个普通 :memory: 连接验证前一个连接的数据。

## C/C++ sqlite3 接口

- 读取已有库用 sqlite3_open_v2 的 SQLITE_OPEN_READONLY；写已有库可用 READWRITE 而不带 CREATE，避免路径拼错生成空库。新建必须明确允许 CREATE。
- prepare_v2/prepare_v3 后逐项 bind，step 读取 SQLITE_ROW 或确认 SQLITE_DONE，reset 复用，最终 finalize。失败路径也释放语句和连接；C++ 可以使用 RAII。
- bind 索引从 1 开始。字符串/二进制数据生命周期不确定时用 SQLITE_TRANSIENT；读取 column_text/blob 的指针后，下一次 step/reset/finalize 前复制需要长期保留的数据。
- sqlite3_reset 不清除已有绑定；复用时重新绑定所有参数或 clear_bindings，避免意外沿用旧值。检查 prepare、bind、step、reset、finalize 的相关返回值，不只检查 open。
- sqlite3_exec 的错误信息按 API 要求 sqlite3_free；不要记录含敏感值的完整展开 SQL。用 extended error codes 区分锁、约束、只读等错误。
- sqlite3_last_insert_rowid 不是通用业务 ID：不覆盖 WITHOUT ROWID，不应在共享连接并发插入时使用；需要返回写入值时优先在兼容版本使用 RETURNING 并完整消费语句。
- 保持 prepared statement 的数量、事务和连接生命周期可控；不为普通查询加载来源不明的扩展。

## 只读检查工具

[inspect_sqlite.py](../scripts/inspect_sqlite.py) 用 Python 3.9+ 标准库运行。其 SQLite 引擎需要 3.26+；若应用使用更老版本或扩展构建，直接在应用连接获取等价证据。

默认输出结构，不输出业务行或 COUNT(*)；--table 可重复，只限制详细表元数据，schema 仍包含全库对象以便查看跨表依赖。--checks 显式执行全库 quick_check/foreign_key_check。退出码：0 表示读取完成且所选检查通过，1 表示读取/运行失败，2 表示检查发现违规。

mode=ro 防止修改数据库内容；WAL 读取仍可能需要共享内存或目录权限，所以不能承诺整个目录无任何系统文件活动。不要为绕过错误自动设置 immutable=1、删旁路文件或调整 journal_mode。

## 来源

- [CLI](https://www.sqlite.org/cli.html)、[URI 文件名](https://www.sqlite.org/uri.html)
- [Python sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [C/C++ 接口](https://www.sqlite.org/c3ref/intro.html)
- [连接打开](https://www.sqlite.org/c3ref/open.html)、[绑定参数](https://www.sqlite.org/c3ref/bind_blob.html)
