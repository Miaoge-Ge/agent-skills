# 索引设计：查询证据优先

## 开始前获取四类证据

- 目标 SQL、绑定参数的代表值、输出字段、排序/LIMIT，以及每条查询的频率。
- 表规模、筛选后的行数、数据分布、读写比例；缺少时先提出候选，不捏造性能数字。
- 现有主键、唯一约束、普通/部分/表达式索引及完整定义。PRAGMA index_list 的 origin 与 unique/partial、index_xinfo 的列/表达式/排序规则都影响判断。
- 当前 EXPLAIN QUERY PLAN，必要时测量真实耗时。测试应消费同样的结果，比较相同参数、数据、缓存条件与事务上下文。

普通 SQLite 索引用有序 B 树组织键。rowid 表的二级索引通常携带 rowid，定位后按需回表；WITHOUT ROWID 表二级索引携带主键信息。覆盖索引包含查询所需数据时可省去回表。不要将所有引擎都说成同一 B+ 树实现。

## 联合索引到底如何使用

对于索引 (customer_id, status, created_at, order_id)：

- customer_id = ?：能使用最左列定位。
- customer_id = ? AND status = ?：能使用前两列定位。
- customer_id = ? AND status = ? AND created_at >= ?：前两列等值加第三列范围可缩小扫描区间。
- customer_id = ? AND created_at >= ?：缺少 status，通常只用 customer_id 形成连续查找前缀；created_at 仍可过滤，不能说“整个索引失效”。
- 只查 status：通常不适合常规前缀查找；统计信息和分布合适时 SQLite 可能 skip-scan，不要写成绝对不使用。
- 将 WHERE 条件交换书写位置不会改变索引的字段顺序。
- 范围之后的列通常不能继续缩小普通索引扫描区间，但可能服务过滤、覆盖与排序。IN、多范围和 ORDER BY 的组合要查看计划。

“等值字段在前、范围在后”是常见起点，不是无条件排序公式。多个等值字段的先后需照顾其他查询的前缀复用；不能永远把区分度最高的列放第一位。

## 将筛选、排序和分页一起设计

```sql
SELECT order_id, created_at
FROM orders
WHERE customer_id = :customer AND status = :status
ORDER BY created_at DESC, order_id DESC
LIMIT :limit;

CREATE INDEX idx_orders_customer_status_created
ON orders(customer_id, status, created_at DESC, order_id DESC);
```

前两列等值使后两列可按需要输出顺序；order_id 提供确定性并列顺序。示例的 order_id 是 rowid 别名，普通二级索引本已携带它，显式指定 DESC 是为了控制相同时间内的方向，不是为了重复存一份覆盖列。此查询可由索引覆盖；若需要返回很大的 metadata，不要为了覆盖把它也塞进索引。

只按客户而不限制 status、只按某一天查询、或排序方向组合改变时，不能直接承诺上述索引消除排序。完整反向扫描可以服务相反方向，混合方向需要具体分析。

## 特殊索引与常见误区

- **部分索引**：例如 ON orders(customer_id, created_at DESC) WHERE status = 'pending'。查询条件必须让规划器能证明满足索引谓词；动态参数不应未经验证就假定能匹配所有部分谓词。部分唯一索引可表达“仅活动记录唯一”。
- **表达式索引**：例如 ON orders(json_extract(metadata, '$.priority'))。查询表达式应与索引表达式匹配，SQLite 不会普遍进行代数等价证明；a + b 的索引不能假定服务 b + a。函数需满足确定性限制。
- **函数与时间筛选**：对列应用 date() 可能阻碍普通列索引定位；若时间存 Unix 秒，优先绑定起止边界，用 created_at >= :start AND created_at < :end；注意时区与半开区间。
- **LIKE**：前缀匹配可能优化，前导通配符通常不行；还受排序规则、大小写设置及函数是否被重载影响。全文搜索需要匹配的 FTS 模块及分词需求，不能把 B 树索引当全文索引。
- **低基数字段**：不直接否定。若状态只有三种，但目标状态只占 0.1%，索引或部分索引可能有效。
- **OR**：SQLite 在满足条件时可以对多个分支使用不同索引并合并结果。“一张表每条查询永远只能用一个索引”是过度概括。
- **重复索引**：比较键、排序规则、方向、表达式、WHERE 谓词、唯一性与约束来源。前缀重叠只说明候选冗余；UNIQUE(a) 与普通 (a,b) 不能相互替代约束。

## 验证与维护

1. 在代表性副本上执行原查询并保存结果与计划；有分页时同时验证顺序。
2. 每次只引入有理由的候选索引，复测参数、结果、耗时与写入成本。
3. 解读 SEARCH、SCAN、USING COVERING INDEX 和 USE TEMP B-TREE 的含义。SCAN 可能是合理的有序索引扫描，不见 SEARCH 就断言慢是错误的。
4. 数据分布变化、索引创建后按需要更新统计信息。PRAGMA optimize/ANALYZE 会写入统计信息，不属于纯只读诊断；在允许修改的环境中执行。
5. EXPLAIN QUERY PLAN 输出格式会随版本变化，不把其整段文本作为稳定 API。性能结论报告测试条件，不能从树结构推导毫秒数。
6. 只删除验证确实无用的索引，保留业务唯一性/外键父键要求和应用显式引用。通常无需用 INDEXED BY 强迫规划器；它更适合受控的计划回归约束，不是通用优化提示。

## 来源

- [查询规划](https://www.sqlite.org/queryplanner.html)
- [优化器与最左前缀、skip-scan、LIKE](https://www.sqlite.org/optoverview.html)
- [表达式索引](https://www.sqlite.org/expridx.html)、[部分索引](https://www.sqlite.org/partialindex.html)
- [查询计划输出](https://www.sqlite.org/eqp.html)
- [PRAGMA optimize](https://www.sqlite.org/pragma.html#pragma_optimize)
