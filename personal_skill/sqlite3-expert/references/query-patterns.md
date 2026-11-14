# 查询、写入与 SQLite 特殊语法

以下带 example 注释的 SQL 使用 [订单示例结构](../assets/order_schema.sql)，由行为测试直接读取执行。冒号参数必须由应用绑定，不是可直接替换的拼接模板。

## 查询与结果基数

- 指定需要的列和必要别名；应用接口避免 SELECT * 引起列顺序/结构变化问题。一次性探索可使用 *。
- 先明确一行表示一笔订单、一个客户还是一个明细。JOIN 一对多会扩行，不用 DISTINCT 掩盖错误连接；多组明细分别聚合后再关联，避免金额/计数成倍放大。
- 查找“存在匹配”优先考虑 EXISTS；查找“不存在匹配”考虑 NOT EXISTS，避免 NOT IN 子查询含 NULL 导致意外空结果。

```sql
-- example: empty_customers
SELECT s.customer_id
FROM customers AS s
WHERE NOT EXISTS (
    SELECT 1 FROM orders AS t WHERE t.customer_id = s.customer_id
)
ORDER BY s.customer_id;
```

保留无订单客户并统计已付款订单：右表的筛选条件放 ON 中，COUNT 使用非空右表键；若将 status 条件放 WHERE，会排掉无匹配客户。

```sql
-- example: customer_summary
SELECT s.customer_id, COUNT(t.order_id) AS paid_count
FROM customers AS s
LEFT JOIN orders AS t
    ON t.customer_id = s.customer_id AND t.status = 'paid'
GROUP BY s.customer_id
ORDER BY s.customer_id;
```

WHERE 过滤输入行，HAVING 过滤聚合结果。SQLite 允许部分“裸列”聚合写法，但除特殊规则外其取值不确定；不要用 SELECT order_id, MAX(created_at) GROUP BY customer_id 来稳定选择最新记录。

## 每组最新、窗口函数与 CTE

```sql
-- example: latest_per_customer
WITH ranked AS (
    SELECT order_id, customer_id, created_at,
           ROW_NUMBER() OVER (
               PARTITION BY customer_id
               ORDER BY created_at DESC, order_id DESC
           ) AS rn
    FROM orders
)
SELECT order_id, customer_id, created_at
FROM ranked
WHERE rn = 1
ORDER BY customer_id;
```

窗口函数保留输入行，GROUP BY 合并行；窗口结果通常需要外层查询过滤。同时间戳用唯一键确定顺序。计算运行总和时显式考虑 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW，避免默认 RANGE 对并列值的影响。

普通 WITH 不保证物化，不是建临时表；递归 CTE 需要终止条件与循环防护，图结构中不能无条件 UNION ALL 递归到底。MATERIALIZED/NOT MATERIALIZED 有版本要求且是优化提示，不作为语义依赖。

## 排序和分页

小数据量可用 LIMIT :limit OFFSET :offset，绑定非负整数并限制最大页大小。深分页优先考虑基于最后一个排序键的游标：

```sql
-- example: next_page
SELECT order_id, created_at
FROM orders
WHERE customer_id = :customer AND status = :status
  AND (created_at, order_id) < (:last_time, :last_id)
ORDER BY created_at DESC, order_id DESC
LIMIT :limit;
```

该例两列均降序、非 NULL，首屏应省略游标条件。混合升降序或含 NULL 的排序需重新推导条件；并发更新排序字段仍可能改变分页结果，需要一致快照时应明确事务范围。索引建议见[索引设计](index-design.md)。

## INSERT、UPSERT 和状态更新

插入明确列名，绑定所有外部值；批量写入复用语句并在适当大小的事务中执行，不逐行提交。

```sql
-- example: upsert_order
INSERT INTO orders (
    order_ref, customer_id, note, status,
    created_at, updated_at, version, metadata
)
VALUES (
    :reference, :customer, :note, :status,
    :created, :updated, :version, :metadata
)
ON CONFLICT(order_ref) DO UPDATE SET
    note = excluded.note,
    status = excluded.status,
    updated_at = excluded.updated_at,
    version = excluded.version,
    metadata = excluded.metadata
WHERE excluded.version > orders.version
RETURNING order_id, version;
```

此例要求 3.35+，假设订单号对应同一订单、customer_id/created_at 对既有订单不变，version 由可信业务流程单调递增。过期版本不覆盖新值且返回零行；若输入身份字段可能不一致，先验证或显式拒绝，不静默当成有效更新。这里演示已验证的同步写入，不代替支付业务的状态转换校验。

- ON CONFLICT 目标须匹配主键/唯一约束或合适的唯一索引；它不处理任意 CHECK、NOT NULL、外键错误。
- INSERT OR REPLACE 冲突时可能先删除旧行再插入，触发外键动作并影响默认值/标识；它不等同于 UPDATE/UPSERT。
- INSERT OR IGNORE 会忽略某些错误行，不能作为批量导入默认纠错方案。要求可追踪的拒绝行和原因。
- INSERT ... SELECT ... ON CONFLICT 遇到语法歧义时，在 SELECT 中显式加 WHERE true。
- RETURNING 只返回直接修改行，不能作为 PostgreSQL 风格的可写 CTE 数据源；不保证返回顺序，也不直接反映 AFTER 触发器后续修改。消费/结束语句再提交，不把返回行误认为事务已持久化。

并发修改可使用“预期修订号”做乐观并发控制：

```sql
-- example: pay_order
UPDATE orders
SET status = 'paid', version = version + 1, updated_at = :now
WHERE order_id = :id AND status = 'pending' AND version = :expected_version
RETURNING order_id, version;
```

零行表示记录不存在、状态不允许或发生冲突；不能直接报告成功。UPDATE FROM 的源若对同一目标匹配多行，先消除歧义，否则不能依赖选中哪一行。

删除先用相同谓词确认目标与影响；执行时在合适的事务中重新核实，不把很久前的 SELECT 当作锁。UPDATE/DELETE 的 ORDER BY/LIMIT 依赖编译选项，便携方案可使用限定主键的子查询，不盲目生成。

## 数值、时间、JSON

```sql
-- example: paid_ratio
SELECT 100.0 * SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END)
       / NULLIF(COUNT(*), 0) AS paid_percent
FROM orders;
```

空集返回 NULL，在展示层按业务决定是否转 0。按天筛选 UTC 秒时间戳优先用起止秒的半开区间，避免在索引列上套日期函数。strftime 的替换项可能有版本要求。

```sql
-- example: json_priority
SELECT order_id, json_extract(metadata, '$.priority') AS priority
FROM orders
WHERE json_type(metadata, '$.priority') IN ('integer', 'real')
  AND json_extract(metadata, '$.priority') >= :minimum
ORDER BY order_id;
```

json_extract 单路径提取标量时可返回 SQL 数值、文本或 NULL，不总是 JSON 字符串。数值比较先约束 JSON 类型，避免文本与数值按 SQLite 存储类别规则比较而意外入选。JSON null 和缺失路径都可能得到 SQL NULL，用 json_type 区分。json_each 展开数组会扩行，应考虑空数组与重复元素。

```sql
-- example: json_update
UPDATE orders
SET metadata = json_set(metadata, '$.tags', json(:tags)),
    version = version + 1, updated_at = :now
WHERE order_id = :id AND version = :expected_version
RETURNING order_id;
```

json(:tags) 将有效数组/对象文本作为 JSON 值，缺少它可能写入字符串。若要求必须是数组，还需在应用或约束中验证 json_type；先探测 JSON 支持。JSONB 的存储与兼容性要单独确认，不默认将现有文本列改为 BLOB。

## 触发器与方言边界

- 触发器只用于确有必要的数据库级行为，核实递归、冲突策略与副作用；不把外部 I/O 放入事务或自定义函数中执行。
- 用 OLD/NEW 明确引用行。SQLite 通常是行级触发器；不要生成其他引擎的语句级触发器语法。
- 不直接生成 MySQL 的 AUTO_INCREMENT/ON DUPLICATE KEY、SQL Server 的 TOP/IDENTITY 或 PostgreSQL 的 SERIAL/ILIKE/DML CTE。RIGHT/FULL JOIN 不是永远不支持，要看版本。

## 来源

- [SELECT 与裸列聚合](https://www.sqlite.org/lang_select.html)
- [UPSERT](https://www.sqlite.org/lang_upsert.html)、[冲突处理](https://www.sqlite.org/lang_conflict.html)
- [RETURNING](https://www.sqlite.org/lang_returning.html)、[窗口函数](https://www.sqlite.org/windowfunctions.html)
- [行值比较与分页](https://www.sqlite.org/rowvalue.html)
- [JSON](https://www.sqlite.org/json1.html)、[触发器](https://www.sqlite.org/lang_createtrigger.html)
