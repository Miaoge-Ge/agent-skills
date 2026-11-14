#!/usr/bin/env python3
"""Read SQLite metadata without creating or changing a database.

Python >= 3.9, linked SQLite >= 3.26. No third-party dependencies.
The JSON describes this connection, not an application's connection settings.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import sys


def open_readonly(path: Path, timeout: float = 5.0) -> sqlite3.Connection:
    resolved = path.expanduser().resolve(strict=True)
    if not resolved.is_file():
        raise ValueError(f"Not a regular file: {resolved}")
    connection = sqlite3.connect(
        resolved.as_uri() + "?mode=ro", uri=True,
        isolation_level=None, timeout=timeout,
    )
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        if connection.execute("PRAGMA query_only").fetchone()[0] != 1:
            raise RuntimeError("Could not enable query_only")
    except BaseException:
        connection.close()
        raise
    return connection


def records(connection: sqlite3.Connection, sql: str, parameters=()) -> list[dict]:
    return [dict(row) for row in connection.execute(sql, parameters).fetchall()]


def quoted_identifier(name: str) -> str:
    if "\x00" in name:
        raise ValueError("NUL is not permitted in an identifier")
    return '"' + name.replace('"', '""') + '"'


def inspect_database(path: Path, tables: list[str] | None = None,
                     checks: bool = False) -> dict:
    if sqlite3.sqlite_version_info < (3, 26, 0):
        raise RuntimeError("This helper requires SQLite >= 3.26 for table_xinfo")
    with closing(open_readonly(path)) as connection:
        # Keep schema and optional checks in one read snapshot. No write PRAGMAs.
        connection.execute("BEGIN")
        schema = records(connection, """
            SELECT type, name, tbl_name, sql FROM sqlite_master
            WHERE name NOT GLOB 'sqlite_*'
            ORDER BY type, name
        """)
        available = {row["name"] for row in schema if row["type"] == "table"}
        requested = set(tables) if tables else available
        missing = requested - available
        if missing:
            raise ValueError("Unknown table(s): " + ", ".join(sorted(missing)))
        report = {
            "database": str(path.expanduser().resolve(strict=True)),
            "runtime": {
                "sqlite_version": connection.execute("SELECT sqlite_version()").fetchone()[0],
                "sqlite_source_id": connection.execute("SELECT sqlite_source_id()").fetchone()[0],
                "python_version": sys.version.split()[0],
                "compile_options": [row[0] for row in connection.execute("PRAGMA compile_options")],
            },
            "connection": {
                "mode": "ro",
                "settings_scope": "inspection connection, not application connections",
                **{key: connection.execute("PRAGMA " + key).fetchone()[0]
                   for key in ("query_only", "foreign_keys", "journal_mode", "busy_timeout")},
            },
            "user_version": connection.execute("PRAGMA user_version").fetchone()[0],
            "schema": schema,
            "tables": [],
        }
        try:
            report["runtime"]["json_available"] = (
                connection.execute("SELECT json_valid('{}')").fetchone()[0] == 1
            )
        except sqlite3.OperationalError as error:
            report["runtime"]["json_available"] = False
            report["runtime"]["json_probe_error"] = str(error)

        for name in sorted(requested):
            quoted = quoted_identifier(name)
            indexes = records(connection, f"PRAGMA main.index_list({quoted})")
            for index in indexes:
                index["columns"] = records(
                    connection, f"PRAGMA main.index_xinfo({quoted_identifier(index['name'])})"
                )
                row = connection.execute(
                    "SELECT sql FROM sqlite_master WHERE type = 'index' AND name = ?",
                    (index["name"],),
                ).fetchone()
                index["sql"] = row[0] if row else None
            report["tables"].append({
                "name": name,
                "columns": records(connection, f"PRAGMA main.table_xinfo({quoted})"),
                "foreign_keys": records(connection, f"PRAGMA main.foreign_key_list({quoted})"),
                "indexes": indexes,
            })

        if checks:
            quick = [row[0] for row in connection.execute("PRAGMA quick_check")]
            violations = records(connection, "PRAGMA foreign_key_check")
            report["checks"] = {
                "scope": "entire database",
                "quick_check": quick,
                "foreign_key_violations": violations,
                "ok": quick == ["ok"] and not violations,
            }
        connection.execute("ROLLBACK")
        return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path, help="Existing database file")
    parser.add_argument("--table", action="append", dest="tables",
                        help="Limit detailed table metadata; repeat for multiple tables")
    parser.add_argument("--checks", action="store_true",
                        help="Run whole-database quick_check and foreign_key_check")
    args = parser.parse_args(argv)
    try:
        report = inspect_database(args.database, args.tables, args.checks)
    except (OSError, ValueError, RuntimeError, sqlite3.Error) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=True), file=sys.stderr)
        return 1
    # ASCII escapes keep JSON valid even on legacy Windows console encodings.
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report.get("checks", {}).get("ok", True) else 2


if __name__ == "__main__":
    raise SystemExit(main())
