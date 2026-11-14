"""Exercise shipped SQL and read-only tooling on isolated SQLite databases."""
from contextlib import closing, redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import unittest


SKILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "inspect_sqlite", SKILL / "scripts" / "inspect_sqlite.py"
)
inspector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inspector)
SCHEMA = (SKILL / "assets" / "order_schema.sql").read_text(encoding="utf-8")
EXAMPLES = dict(re.findall(
    r"```sql\n-- example: ([a-z_]+)\n(.*?)\n```",
    (SKILL / "references" / "query-patterns.md").read_text(encoding="utf-8"),
    re.DOTALL,
))


def has_json():
    with closing(sqlite3.connect(":memory:")) as con:
        try:
            return con.execute("SELECT json_valid('{}')").fetchone()[0] == 1
        except sqlite3.OperationalError:
            return False


@unittest.skipUnless(sqlite3.sqlite_version_info >= (3, 37, 0) and has_json(),
                     "Order examples require SQLite >= 3.37 and JSON")
class OrderExamples(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:", isolation_level=None)
        self.addCleanup(self.con.close)
        self.con.executescript(SCHEMA)
        self.con.executemany("INSERT INTO customers VALUES (?, ?, ?)",
                             [(1, "Ada", "ada@example.test"),
                              (2, "Ben", "ben@example.test"),
                              (3, "Cy", "cy@example.test")])
        self.con.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)",
                             [(1, "BOOK-01", "Notebook", 1250, 8),
                              (2, "PEN-01", "Pen", 350, 20)])
        self.con.executemany("""
            INSERT INTO orders(order_id, order_ref, customer_id, status,
                               created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            (1, "ORD-A", 1, "pending", 100, 100, '{"priority":2}'),
            (2, "ORD-B", 1, "paid", 200, 200, '{"priority":3}'),
            (3, "ORD-C", 1, "pending", 200, 200, '{}'),
            (4, "ORD-D", 2, "pending", 150, 150, '{}'),
        ])

    def test_outer_join_counts_zero_and_retains_empty_customers(self):
        self.assertEqual(self.con.execute(EXAMPLES["customer_summary"]).fetchall(),
                         [(1, 1), (2, 0), (3, 0)])

    def test_not_exists_finds_empty_customer(self):
        self.assertEqual(self.con.execute(EXAMPLES["empty_customers"]).fetchall(), [(3,)])

    def test_latest_per_group_breaks_timestamp_ties(self):
        self.assertEqual(self.con.execute(EXAMPLES["latest_per_customer"]).fetchall(),
                         [(3, 1, 200), (4, 2, 150)])

    def test_keyset_pagination_no_duplicate_or_missing_rows(self):
        self.con.execute("UPDATE orders SET status = 'pending' WHERE order_id = 2")
        params = {"customer": 1, "status": "pending", "last_time": 200,
                  "last_id": 3, "limit": 1}
        self.assertEqual(self.con.execute(EXAMPLES["next_page"], params).fetchall(), [(2, 200)])
        params.update(last_time=200, last_id=2)
        self.assertEqual(self.con.execute(EXAMPLES["next_page"], params).fetchall(), [(1, 100)])

    def test_upsert_preserves_identity_and_items_and_rejects_stale_version(self):
        self.con.execute("INSERT INTO order_items VALUES (1, 1, 2, 1200)")
        params = dict(reference="ORD-A", customer=1, note="Updated",
                      status="paid", created=100, updated=300,
                      version=2, metadata='{"priority":4}')
        self.assertEqual(self.con.execute(EXAMPLES["upsert_order"], params).fetchall(), [(1, 2)])
        params.update(version=1, note="Stale")
        self.assertEqual(self.con.execute(EXAMPLES["upsert_order"], params).fetchall(), [])
        self.assertEqual(self.con.execute("SELECT note FROM orders WHERE order_id=1").fetchone(),
                         ("Updated",))
        self.assertEqual(self.con.execute("SELECT * FROM order_items").fetchall(), [(1, 1, 2, 1200)])
        params.update(reference="ORD-NEW", version=1, note="New")
        inserted = self.con.execute(EXAMPLES["upsert_order"], params).fetchall()
        self.assertEqual(len(inserted), 1)
        self.assertNotEqual(inserted[0][0], 1)

    def test_compare_and_swap_reports_conflict(self):
        params = dict(id=1, now=300, expected_version=1)
        self.assertEqual(self.con.execute(EXAMPLES["pay_order"], params).fetchall(), [(1, 2)])
        self.assertEqual(self.con.execute(EXAMPLES["pay_order"], params).fetchall(), [])

    def test_percentage_and_empty_set(self):
        self.assertEqual(self.con.execute(EXAMPLES["paid_ratio"]).fetchone(), (25.0,))
        self.con.execute("DELETE FROM orders")
        self.assertEqual(self.con.execute(EXAMPLES["paid_ratio"]).fetchone(), (None,))

    def test_json_extract_and_json_array_update(self):
        self.con.execute("UPDATE orders SET metadata = ? WHERE order_id = 3", ('{"priority":"urgent"}',))
        self.assertEqual(self.con.execute(EXAMPLES["json_priority"], {"minimum": 3}).fetchall(), [(2, 3)])
        params = dict(id=1, tags='["gift", "express"]', now=300, expected_version=1)
        self.assertEqual(self.con.execute(EXAMPLES["json_update"], params).fetchall(), [(1,)])
        value = self.con.execute("SELECT metadata FROM orders WHERE order_id=1").fetchone()[0]
        self.assertEqual(json.loads(value)["tags"], ["gift", "express"])

    def test_schema_rejects_invalid_business_values(self):
        for column, value in [("status", "unknown"), ("version", 0),
                              ("metadata", "broken-json"), ("updated_at", 99),
                              ("order_ref", None), ("customer_id", 999)]:
            with self.subTest(column=column, value=value):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.con.execute(f"UPDATE orders SET {column} = ? WHERE order_id=1", (value,))
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("UPDATE products SET stock=-1 WHERE product_id=1")
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("INSERT INTO order_items VALUES(1,1,0,100)")

    def test_order_reference_uniqueness_is_distinct_from_primary_key(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("UPDATE orders SET order_ref = 'ORD-A' WHERE order_id = 2")

    def test_historical_item_price_does_not_change_with_catalog_price(self):
        self.con.execute("INSERT INTO order_items VALUES(1,1,2,1200)")
        self.con.execute("UPDATE products SET price_cents=1500 WHERE product_id=1")
        self.assertEqual(self.con.execute("SELECT SUM(quantity*unit_price_cents) FROM order_items").fetchone(),
                         (2400,))

    def test_covering_plan_and_index_preserve_results(self):
        sql = """SELECT order_id, created_at FROM orders
                 WHERE customer_id = ? AND status = ?
                 ORDER BY created_at DESC, order_id DESC LIMIT 10"""
        before = self.con.execute(sql, (1, "pending")).fetchall()
        plan = self.con.execute("EXPLAIN QUERY PLAN " + sql, (1, "pending")).fetchall()
        # Semantic fragments only, not a snapshot of version-specific plan text.
        self.assertTrue(any("COVERING INDEX" in row[3] for row in plan), plan)
        self.assertFalse(any("TEMP B-TREE" in row[3] for row in plan), plan)
        self.con.execute("DROP INDEX idx_orders_customer_status_created")
        self.assertEqual(before, self.con.execute(sql, (1, "pending")).fetchall())


@unittest.skipUnless(sys.version_info >= (3, 12) and sqlite3.sqlite_version_info >= (3, 37, 0) and has_json(),
                     "Python integration example requires 3.12+, SQLite 3.37+ and JSON")
class PythonIntegrationExample(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "orders.sqlite"
        with closing(sqlite3.connect(self.path)) as con:
            con.executescript(SCHEMA)
            con.execute("INSERT INTO products VALUES(1, 'BOOK', 'Notebook', 1250, 3)")
            con.commit()
        document = (SKILL / "references" / "integration-and-operations.md").read_text(encoding="utf-8")
        self.code = re.search(r"```python\n(.*?)\n```", document, re.DOTALL).group(1)

    def run_example(self, path, quantity):
        namespace = dict(database_path=path, quantity=quantity, product_id=1)
        exec(compile(self.code, "integration-and-operations.md", "exec"), namespace)
        return namespace

    def stock(self):
        with closing(sqlite3.connect(self.path)) as con:
            return con.execute("SELECT stock FROM products WHERE product_id=1").fetchone()[0]

    def test_stock_change_commits_and_returns_new_value(self):
        namespace = self.run_example(self.path, 2)
        self.assertEqual(namespace["rows"], [(1,)])
        self.assertEqual(self.stock(), 1)

    def test_insufficient_stock_rolls_back(self):
        with self.assertRaises(LookupError):
            self.run_example(self.path, 4)
        self.assertEqual(self.stock(), 3)

    def test_typo_path_does_not_create_database(self):
        missing = self.path.parent / "misspelled.sqlite"
        with self.assertRaises(FileNotFoundError):
            self.run_example(missing, 1)
        self.assertFalse(missing.exists())


class SQLiteSemantics(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:", isolation_level=None)
        self.addCleanup(self.con.close)
        self.con.execute("PRAGMA foreign_keys=ON")

    def test_nullable_primary_key_and_check_are_not_not_null(self):
        self.con.execute("CREATE TABLE legacy(id TEXT PRIMARY KEY, amount INTEGER CHECK(amount > 0))")
        self.con.execute("INSERT INTO legacy VALUES (NULL, NULL)")
        self.con.execute("INSERT INTO legacy VALUES (NULL, NULL)")
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM legacy").fetchone()[0], 2)

    def test_integer_division_and_null_in_not_in(self):
        self.assertEqual(self.con.execute("SELECT 1/2, 1.0/2, 2 NOT IN (1, NULL)").fetchone(),
                         (0, 0.5, None))

    def test_foreign_key_switch_inside_transaction_is_ineffective(self):
        self.con.execute("BEGIN")
        self.con.execute("PRAGMA foreign_keys=OFF")
        self.assertEqual(self.con.execute("PRAGMA foreign_keys").fetchone()[0], 1)
        self.con.execute("ROLLBACK")

    def test_replace_can_delete_children(self):
        self.con.executescript("""
            CREATE TABLE parent(id INTEGER PRIMARY KEY, value TEXT);
            CREATE TABLE child(id INTEGER REFERENCES parent(id) ON DELETE CASCADE);
            INSERT INTO parent VALUES(1, 'old');
            INSERT INTO child VALUES(1);
        """)
        self.con.execute("INSERT OR REPLACE INTO parent VALUES(1, 'new')")
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM child").fetchone()[0], 0)

    def test_savepoint_failure_preserves_outer_transaction(self):
        self.con.execute("CREATE TABLE data(id INTEGER PRIMARY KEY)")
        self.con.execute("BEGIN")
        self.con.execute("INSERT INTO data VALUES(1)")
        self.con.execute("SAVEPOINT part")
        self.con.execute("INSERT INTO data VALUES(2)")
        self.con.execute("ROLLBACK TO part")
        self.con.execute("RELEASE part")
        self.con.execute("COMMIT")
        self.assertEqual(self.con.execute("SELECT id FROM data").fetchall(), [(1,)])

    def test_partial_unique_index_enforces_only_active_rows(self):
        self.con.execute("CREATE TABLE users(email TEXT, active INTEGER NOT NULL)")
        self.con.execute("CREATE UNIQUE INDEX active_email ON users(email) WHERE active=1")
        self.con.execute("INSERT INTO users VALUES('a@example.test', 0), ('a@example.test', 0), ('a@example.test', 1)")
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("INSERT INTO users VALUES('a@example.test', 1)")


class InspectionTool(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # '?' cannot occur in Windows filenames; '#' must still be URI-escaped.
        self.path = Path(self.temp.name) / "订单 # sample.sqlite"
        with closing(sqlite3.connect(self.path)) as con:
            con.executescript('''
                CREATE TABLE "odd'\"\"table" (id TEXT PRIMARY KEY NOT NULL, value TEXT);
                CREATE INDEX idx_value ON "odd'\"\"table"(value COLLATE NOCASE DESC);
                CREATE INDEX idx_partial ON "odd'\"\"table"(value) WHERE value IS NOT NULL;
                CREATE INDEX idx_expression ON "odd'\"\"table"(length(value));
                INSERT INTO "odd'\"\"table" VALUES('id', 'secret-business-value');
            ''')

    def test_metadata_handles_quoted_identifiers_and_preserves_index_details(self):
        report = inspector.inspect_database(self.path, ['odd\'"table'], checks=True)
        self.assertTrue(report["checks"]["ok"])
        table = report["tables"][0]
        self.assertEqual(table["name"], 'odd\'"table')
        self.assertTrue(any(i["origin"] == "pk" and i["unique"] for i in table["indexes"]))
        by_name = {i["name"]: i for i in table["indexes"]}
        self.assertEqual(by_name["idx_partial"]["partial"], 1)
        key = next(c for c in by_name["idx_value"]["columns"] if c["key"])
        self.assertEqual((key["coll"], key["desc"]), ("NOCASE", 1))
        self.assertTrue(any(c["cid"] == -2 for c in by_name["idx_expression"]["columns"]))
        self.assertNotIn("secret-business-value", json.dumps(report))

    def test_missing_path_does_not_create_database(self):
        missing = self.path.parent / "missing.sqlite"
        with self.assertRaises(FileNotFoundError):
            inspector.inspect_database(missing)
        self.assertFalse(missing.exists())

    def test_readonly_connection_rejects_write_even_if_query_only_disabled(self):
        before = self.path.read_bytes()
        with closing(inspector.open_readonly(self.path)) as con:
            con.execute("PRAGMA query_only=OFF")
            with self.assertRaises(sqlite3.OperationalError):
                con.execute("CREATE TABLE unwanted(id INTEGER)")
        inspector.inspect_database(self.path)
        self.assertEqual(before, self.path.read_bytes())

    def test_unknown_table_fails_clearly(self):
        with self.assertRaisesRegex(ValueError, "Unknown table"):
            inspector.inspect_database(self.path, ["missing"])

    def test_foreign_key_violations_are_failure_exit_status(self):
        with closing(sqlite3.connect(self.path)) as con:
            con.executescript("""
                PRAGMA foreign_keys=OFF;
                CREATE TABLE p(id INTEGER PRIMARY KEY);
                CREATE TABLE c(pid INTEGER REFERENCES p(id));
                INSERT INTO c VALUES(999);
            """)
        output = io.StringIO()
        with redirect_stdout(output):
            status = inspector.main([str(self.path), "--checks"])
        self.assertEqual(status, 2)
        report = json.loads(output.getvalue())
        self.assertFalse(report["checks"]["ok"])
        self.assertEqual(len(report["checks"]["foreign_key_violations"]), 1)

    def test_cli_missing_file_returns_error_without_creating_file(self):
        missing = self.path.parent / "absent.sqlite"
        output = io.StringIO()
        with redirect_stderr(output):
            status = inspector.main([str(missing)])
        self.assertEqual(status, 1)
        self.assertIn("error", json.loads(output.getvalue()))
        self.assertFalse(missing.exists())

    @unittest.skipUnless(sqlite3.sqlite_version_info >= (3, 31, 0), "Generated columns require 3.31")
    def test_generated_columns_are_reported(self):
        with closing(sqlite3.connect(self.path)) as con:
            con.execute("CREATE TABLE generated(a INTEGER, b INTEGER GENERATED ALWAYS AS (a*2) VIRTUAL)")
        table = inspector.inspect_database(self.path, ["generated"])["tables"][0]
        self.assertEqual(next(c for c in table["columns"] if c["name"] == "b")["hidden"], 2)


class MigrationBehavior(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:", isolation_level=None)
        self.addCleanup(self.con.close)
        self.con.executescript("""
            PRAGMA foreign_keys=ON;
            CREATE TABLE parents(id INTEGER PRIMARY KEY, name TEXT);
            CREATE TABLE children(parent_id INTEGER REFERENCES parents(id));
            CREATE TABLE audit(parent_id INTEGER);
            CREATE INDEX idx_parent_name ON parents(name);
            CREATE TRIGGER parent_audit AFTER UPDATE ON parents
            BEGIN INSERT INTO audit VALUES(NEW.id); END;
            CREATE VIEW parent_names AS SELECT id, name FROM parents;
            INSERT INTO parents VALUES(1, 'Original');
            INSERT INTO children VALUES(1);
        """)

    def rebuild(self, new_id):
        original_fk = self.con.execute("PRAGMA foreign_keys").fetchone()[0]
        objects = self.con.execute("""
            SELECT type, name, sql FROM sqlite_schema
            WHERE name IN ('idx_parent_name', 'parent_audit', 'parent_names')
        """).fetchall()
        self.con.execute("PRAGMA foreign_keys=OFF")
        try:
            self.con.execute("BEGIN IMMEDIATE")
            self.con.execute("CREATE TABLE new_parents(id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
            self.con.execute("INSERT INTO new_parents SELECT ?, name FROM parents", (new_id,))
            self.con.execute("DROP VIEW parent_names")
            self.con.execute("DROP TABLE parents")
            self.con.execute("ALTER TABLE new_parents RENAME TO parents")
            for _, _, sql in objects:
                self.con.execute(sql)
            if self.con.execute("PRAGMA foreign_key_check").fetchall():
                raise RuntimeError("Migration would break foreign keys")
            self.con.execute("PRAGMA user_version=1")
            self.con.execute("COMMIT")
        except BaseException:
            if self.con.in_transaction:
                self.con.execute("ROLLBACK")
            raise
        finally:
            self.con.execute(f"PRAGMA foreign_keys={original_fk}")

    def test_rebuild_preserves_rows_foreign_keys_view_trigger_and_index(self):
        self.rebuild(1)
        self.assertEqual(self.con.execute("SELECT * FROM parent_names").fetchall(), [(1, "Original")])
        self.assertEqual(self.con.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.assertEqual(self.con.execute("PRAGMA foreign_keys").fetchone()[0], 1)
        self.assertEqual(self.con.execute("PRAGMA user_version").fetchone()[0], 1)
        self.con.execute("UPDATE parents SET name='Changed' WHERE id=1")
        self.assertEqual(self.con.execute("SELECT * FROM audit").fetchall(), [(1,)])
        self.assertTrue(any(row[1] == "idx_parent_name" for row in self.con.execute("PRAGMA index_list(parents)")))

    def test_failed_foreign_key_check_rolls_back_entire_migration(self):
        with self.assertRaisesRegex(RuntimeError, "foreign keys"):
            self.rebuild(2)
        self.assertEqual(self.con.execute("SELECT * FROM parent_names").fetchall(), [(1, "Original")])
        self.assertEqual(self.con.execute("PRAGMA foreign_keys").fetchone()[0], 1)
        self.assertEqual(self.con.execute("PRAGMA user_version").fetchone()[0], 0)
        self.assertEqual(self.con.execute("SELECT name FROM sqlite_schema WHERE name='new_parents'").fetchall(), [])
        self.con.execute("UPDATE parents SET name='Still working'")
        self.assertEqual(self.con.execute("SELECT * FROM audit").fetchall(), [(1,)])


if __name__ == "__main__":
    unittest.main()
