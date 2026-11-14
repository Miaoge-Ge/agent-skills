# 运行时、类型和方言边界

## 最小环境证据

在实际应用连接运行以下语句，保留结果。不要为回答一条 SELECT 而读取整库。

```sql
SELECT sqlite_version(), sqlite_source_id();
PRAGMA compile_options;
PRAGMA foreign_keys;
PRAGMA journal_mode;
PRAGMA busy_timeout;
```

PRAGMA 读值属于当前连接/数据库上下文；其中 foreign_keys 和 busy_timeout 是连接设置，journal_mode 涉及数据库模式。不认识的 PRAGMA 可能静默无效，设置后应读回核实。函数/扩展有时取决于构建配置，不能只看版本：例如用 SELECT json_valid('{}') 探测 JSON，不因没有 ENABLE_JSON1 编译选项就认定 JSON 不可用。

读取结构优先 sqlite_schema、PRAGMA table_xinfo、index_list、index_xinfo、foreign_key_list；较老版本必要时回退 sqlite_master、table_info，并说明可能遗漏生成列/隐藏列。sqlite_schema 中自动索引的 SQL 可为 NULL，不能因此认定索引不存在。

## 版本门槛

以下是常用功能的引入版本，不是“当前最新版本”，也不替代构建能力探测。

- 3.8.0：部分索引。
- 3.9.0：表达式索引。
- 3.24.0：基本 UPSERT（ON CONFLICT ... DO UPDATE）。
- 3.25.0：窗口函数、RENAME COLUMN。
- 3.31.0：生成列。
- 3.33.0：UPDATE FROM。
- 3.35.0：RETURNING、DROP COLUMN、多 ON CONFLICT 子句等 UPSERT 扩展。
- 3.37.0：STRICT 表。
- 3.38.0：JSON 默认内置（仍可在构建时省略）、-> 和 ->>。
- 3.39.0：RIGHT/FULL OUTER JOIN、IS DISTINCT FROM。
- 3.45.0：SQLite JSONB；不是 PostgreSQL JSONB 的二进制兼容格式。
- 3.46.0：PRAGMA optimize 的分析范围限制得到改进；仍需考虑执行上下文。
- 3.53.0：ALTER TABLE 对部分约束的修改能力扩展；官方明确支持 ALTER COLUMN SET/DROP NOT NULL。先查该版本语法并测试，不推断为任意 ALTER COLUMN TYPE 或 MySQL MODIFY 支持。

旧运行时需要兼容方案时，RETURNING 可改为同连接下的受控后续查询，窗口函数可改写相关子查询，复杂约束修改可用经过验证的表重建。不要盲目替换，应保持原语义。

## 类型语义

- 五种存储类别：NULL、INTEGER、REAL、TEXT、BLOB。普通表的声明类型决定亲和性，值仍可能以其他类别存储；typeof() 可检查实际存储类别。
- INTEGER 是有符号 64 位整数范围；REAL 是近似浮点。金额优先用约定单位的整数并检查范围，DECIMAL(10,2) 不保证精确十进制或两位小数。
- TEXT/CHAR/CLOB 等声明得到 TEXT 亲和性；ntext 也如此。VARCHAR(20) 不限制长度，需使用 CHECK(length(name) <= 20) 并决定是否允许 NULL。
- 类型匹配按 SQLite 规则处理；BOOLEAN、DATE、DATETIME 通常得到 NUMERIC 亲和性，并非独立强制类型。
- 布尔值通常用 INTEGER，并按业务加 NOT NULL CHECK(flag IN (0,1))；TRUE/FALSE 是值语法，不是独立存储类别。
- 时间统一采用 UTC Unix 时间或固定格式 ISO 文本，并明确秒/毫秒。不要在同列混存两种单位。datetime(created_at, 'unixepoch') 解释秒；毫秒需先除以 1000.0。
- 文本业务编号保留 TEXT，尤其是前导零、字母前缀或超出整数范围的标识。create_time 用 INTEGER 可合理，不要仅凭列名推断类型。
- STRICT 表只接受 INT、INTEGER、REAL、TEXT、BLOB、ANY；仍允许无损类型转换。ANY 在 STRICT 中可保留原值类型，非 STRICT 中行为不同，不要将 STRICT 理解为拒绝所有字符串数字。

## 容易改变查询结果的边界

- 两个整数相除会截断；比例用 1.0 * numerator / NULLIF(denominator, 0)。NULLIF 的结果为 NULL 时，是否显示 0 由业务决定。
- 普通比较遇到 NULL 通常产生 UNKNOWN，WHERE 只保留真；IS NULL/IS NOT NULL 判断空值。SQLite 的 IS/IS NOT 可用于空值安全比较。
- UNIQUE 允许多个 NULL；CHECK 在表达式结果为 NULL 时不拒绝行。需要必填必须另加 NOT NULL。
- 普通 rowid 表中的非 INTEGER PRIMARY KEY 可能允许 NULL；明确声明 NOT NULL。STRICT、WITHOUT ROWID 等有额外规则，不能把其他引擎的假设直接套过来。
- COUNT(*) 计行，COUNT(column) 排除该列 NULL；SUM 无非空输入时返回 NULL，TOTAL 返回 0.0。不要把未知值一律 COALESCE 成 0。
- 使用单引号表示字符串，双引号表示标识符。SQLite 接受部分历史宽松语法，生成代码不要依赖双引号字符串。
- 默认 NOCASE 和 LIKE 的大小写折叠不能当作完整 Unicode 规则；需要国际化比较时确定排序规则/ICU 的部署与索引兼容性。
- UNION 去重，UNION ALL 保留重复。SQL 没有 ORDER BY 就没有结果顺序保证。

## 来源

- [类型与亲和性](https://www.sqlite.org/datatype3.html)
- [STRICT 表](https://www.sqlite.org/stricttables.html)
- [SQL 表达式](https://www.sqlite.org/lang_expr.html)
- [SQLite 历史兼容行为](https://www.sqlite.org/quirks.html)
- [版本记录](https://www.sqlite.org/changes.html)、[3.53.0 更新](https://www.sqlite.org/releaselog/3_53_0.html)
- [PRAGMA](https://www.sqlite.org/pragma.html)
