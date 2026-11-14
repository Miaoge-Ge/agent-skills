# 事务、锁和保留数据的迁移

## 事务选择与失败处理

- 一组必须共同成功的修改放在同一事务。BEGIN 默认 DEFERRED，真正写入时才竞争写事务；已知将写且需要先读后写时，可考虑 BEGIN IMMEDIATE 提前获得写事务。
- 同一数据库同一时刻通常只有一个写者，WAL 不提供多个并发写者。保持事务短，不在持锁期间等待用户、网络或大量外部计算。
- BEGIN 不能嵌套；可组合的子操作使用 SAVEPOINT、ROLLBACK TO 和 RELEASE。ROLLBACK TO 后保存点仍存在，需要 RELEASE 或整体回滚。
- busy_timeout 设置有界等待，不保证所有 BUSY 都等待到超时；读事务升级或 SQLITE_BUSY_SNAPSHOT 可能需要回滚并从事务开始重试。
- 重试应有总时间/次数上限，仅针对明确的可重试锁错误。不能只重放事务中最后一条写入，也不能在提交结果不明确时无条件重做非幂等操作。
- 某些语句错误只回滚该语句，另一些错误可能终止事务；检查连接事务状态，确保失败路径回滚并报告。COMMIT 失败时也不能假定已提交。
- DDL 可以参与显式事务，但框架和驱动可能自己管理事务；尤其核实 Python executescript 的行为。

## WAL 与持久性

- WAL 适用于同主机本地文件上的读写并发场景；不是所有数据库都应开启。PRAGMA journal_mode=WAL 是数据库配置变更，应在任务授权和部署条件内进行并读回结果。
- 长读事务可能阻碍检查点推进，导致 WAL 增长；先检查读事务生命周期，再处理检查点。不要通过删除 -wal/-shm 文件解决锁问题。
- synchronous 是持久性选择。WAL + NORMAL 通常保持一致性，但断电可能丢失近期已提交事务；不要为提速默认 OFF 或将 NORMAL 等同 FULL 的持久性。
- SQLite WAL 不适合不同主机共享的网络文件系统。附加数据库的多库事务在 WAL 下也不是跨库整体原子提交，不能扩展保证。
- 索引、WAL、检查点和 VACUUM 都有成本，先解决查询/事务问题，不批量设置“调优 PRAGMA”。

## 备份和初始检查

对已有库做迁移前，确定原路径、连接者、恢复点和目标版本；先在可恢复副本演练。在线备份使用 SQLite backup API、CLI .backup 或合适的 VACUUM INTO。活动数据库不能仅复制主 .db 文件而忽略 WAL 中的提交。

检查外键、旧数据重复/NULL、触发器、视图、索引、生成列、STRICT/WITHOUT ROWID、应用引用和 user_version。sqlite_schema 的 tbl_name 不能发现所有依赖：视图及其他表的触发器可能引用目标表，需读取相关定义而不是只筛目标表名。

## 迁移选择

1. 若目标运行时原生 ALTER TABLE 能正确完成，优先使用原生操作，并检查限制与依赖。
2. ADD COLUMN、RENAME COLUMN、DROP COLUMN 有不同版本和限制；新增 NOT NULL 列需要可接受的默认值或分步回填，不能随意用虚假默认值糊过去。
3. 新版 SQLite 对部分约束已有 ALTER 支持，查目标版本，勿断言“SQLite 永远不能修改约束”。不支持的类型/约束调整使用表重建。
4. CREATE TABLE IF NOT EXISTS 只在不存在时创建，不会检查旧列、约束或索引是否与目标一致。

## 通用表重建顺序

这是需由宿主程序检查每一步结果的流程，不是可以盲目复制的一串自动提交 SQL。

1. 完成备份，保存全部相关 DDL 与外键开关；确保迁移连接没有活动事务，协调应用写入。需要临时禁用外键时，在 BEGIN **之前** 设置 foreign_keys=OFF，并读回验证。
2. BEGIN IMMEDIATE；创建不冲突的 new_table，包含目标列、约束和表选项。不要先把旧表重命名成 old_table，这可能改写其他对象的引用。
3. 使用明确列清单 INSERT INTO new_table (...) SELECT ... FROM old_table。排除生成列；明确默认值、类型转换、主键/rowid 保留和特殊序列表策略。AUTOINCREMENT 若要求永不复用历史值，须保留旧 sqlite_sequence 高水位，不能只取当前 MAX(id)。
4. 比较行数、业务键集合、转换后的关键值、NULL 与唯一性；不能仅靠行数证明数据无损。发现坏行应回滚或按已明确的业务方案处理，不使用 OR IGNORE 偷跳数据。
5. 处理可能在重命名阶段造成无效引用的相关视图，必要时先保存并在本事务内删除；删除旧表后，将新表改成正式名称。按依赖重建索引、触发器、视图。重放原 DDL 前需适配变更列，不能机械复制。
6. 在 COMMIT **之前** 读取 PRAGMA foreign_key_check 的全部结果，并执行适当完整性/业务验证。只要出现违规就由程序抛错、ROLLBACK；执行 PRAGMA 本身不会自动拒绝迁移。
7. 验证通过后更新 user_version 或项目迁移记录并 COMMIT。即使此前外键关闭，也应显式验证重建后的关系。
8. 成功或失败都在事务外恢复原 foreign_keys 设置，读回核实；应用正常连接若依赖外键，应始终启用。重新检查关键查询、视图和触发器行为。

若失败，回滚原事务并确认原表数据与定义仍在；若已提交，只能使用预先设计的逆向迁移或备份恢复，不声称 ROLLBACK 能撤销过去提交。

## 验证不止一条 integrity_check

- quick_check/integrity_check 验证数据库结构，不能替代 foreign_key_check。
- foreign_key_check 的结果行代表违规，不是成功日志；要主动判断并阻止提交。
- 结构合法不代表业务数据映射正确，还要对比关键值、关系、默认值、唯一性和依赖对象。
- 为失败路径做一次真实演练：例如新约束拒绝旧数据或复制后发生外键违规，验证事务恢复与连接开关恢复。

## 来源

- [事务](https://www.sqlite.org/lang_transaction.html)、[保存点](https://www.sqlite.org/lang_savepoint.html)
- [WAL](https://www.sqlite.org/wal.html)、[隔离](https://www.sqlite.org/isolation.html)
- [ALTER TABLE 官方重建流程](https://www.sqlite.org/lang_altertable.html#making_other_kinds_of_table_schema_changes)
- [备份 API](https://www.sqlite.org/backup.html)、[VACUUM](https://www.sqlite.org/lang_vacuum.html)
- [外键 PRAGMA](https://www.sqlite.org/pragma.html#pragma_foreign_keys)
