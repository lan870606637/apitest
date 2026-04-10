"""数据模型 - SQLite 存储测试用例和执行记录。"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "test_platform.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """初始化数据库表。"""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS test_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            module TEXT NOT NULL DEFAULT '默认模块',
            method TEXT NOT NULL DEFAULT 'GET',
            path TEXT NOT NULL,
            headers TEXT DEFAULT '{}',
            params TEXT DEFAULT '{}',
            body TEXT DEFAULT '{}',
            expected_status INTEGER DEFAULT 200,
            expected_json TEXT DEFAULT '{}',
            description TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS test_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_type TEXT NOT NULL DEFAULT 'manual',
            status TEXT NOT NULL DEFAULT 'running',
            total INTEGER DEFAULT 0,
            passed INTEGER DEFAULT 0,
            failed INTEGER DEFAULT 0,
            skipped INTEGER DEFAULT 0,
            duration REAL DEFAULT 0,
            report_path TEXT DEFAULT '',
            log TEXT DEFAULT '',
            started_at TEXT DEFAULT (datetime('now', 'localtime')),
            finished_at TEXT
        );

        CREATE TABLE IF NOT EXISTS environments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            base_url TEXT NOT NULL,
            is_active INTEGER DEFAULT 0,
            extra TEXT DEFAULT '{}'
        );
    """)
    # 插入默认环境（如果不存在）
    envs = conn.execute("SELECT COUNT(*) as c FROM environments").fetchone()["c"]
    if envs == 0:
        conn.executemany(
            "INSERT INTO environments (name, base_url, is_active) VALUES (?, ?, ?)",
            [
                ("dev", "http://localhost:8080/api", 1),
                ("qa", "http://qa.example.com/api", 0),
                ("prod", "https://api.example.com", 0),
            ],
        )
    conn.commit()
    conn.close()


# ---- 测试用例 CRUD ----

def create_case(data: dict) -> int:
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO test_cases (name, module, method, path, headers, params, body,
           expected_status, expected_json, description)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["name"], data.get("module", "默认模块"),
            data.get("method", "GET"), data["path"],
            json.dumps(data.get("headers", {}), ensure_ascii=False),
            json.dumps(data.get("params", {}), ensure_ascii=False),
            json.dumps(data.get("body", {}), ensure_ascii=False),
            data.get("expected_status", 200),
            json.dumps(data.get("expected_json", {}), ensure_ascii=False),
            data.get("description", ""),
        ),
    )
    conn.commit()
    case_id = cur.lastrowid
    conn.close()
    return case_id


def update_case(case_id: int, data: dict):
    conn = get_db()
    conn.execute(
        """UPDATE test_cases SET name=?, module=?, method=?, path=?, headers=?,
           params=?, body=?, expected_status=?, expected_json=?, description=?,
           updated_at=datetime('now','localtime')
           WHERE id=?""",
        (
            data["name"], data.get("module", "默认模块"),
            data.get("method", "GET"), data["path"],
            json.dumps(data.get("headers", {}), ensure_ascii=False),
            json.dumps(data.get("params", {}), ensure_ascii=False),
            json.dumps(data.get("body", {}), ensure_ascii=False),
            data.get("expected_status", 200),
            json.dumps(data.get("expected_json", {}), ensure_ascii=False),
            data.get("description", ""),
            case_id,
        ),
    )
    conn.commit()
    conn.close()


def delete_case(case_id: int):
    conn = get_db()
    conn.execute("DELETE FROM test_cases WHERE id=?", (case_id,))
    conn.commit()
    conn.close()


def get_case(case_id: int) -> dict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM test_cases WHERE id=?", (case_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_cases(module: str = None) -> list[dict]:
    conn = get_db()
    if module:
        rows = conn.execute(
            "SELECT * FROM test_cases WHERE module=? ORDER BY id DESC", (module,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM test_cases ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_modules() -> list[str]:
    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT module FROM test_cases ORDER BY module"
    ).fetchall()
    conn.close()
    return [r["module"] for r in rows]


# ---- 执行记录 ----

def create_run(run_type: str = "manual") -> int:
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO test_runs (run_type) VALUES (?)", (run_type,)
    )
    conn.commit()
    run_id = cur.lastrowid
    conn.close()
    return run_id


def update_run(run_id: int, data: dict):
    conn = get_db()
    conn.execute(
        """UPDATE test_runs SET status=?, total=?, passed=?, failed=?, skipped=?,
           duration=?, report_path=?, log=?, finished_at=datetime('now','localtime')
           WHERE id=?""",
        (
            data["status"], data["total"], data["passed"],
            data["failed"], data["skipped"], data["duration"],
            data.get("report_path", ""), data.get("log", ""),
            run_id,
        ),
    )
    conn.commit()
    conn.close()


def list_runs(limit: int = 20) -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM test_runs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_run(run_id: int) -> dict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM test_runs WHERE id=?", (run_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---- 环境管理 ----

def list_envs() -> list[dict]:
    conn = get_db()
    rows = conn.execute("SELECT * FROM environments ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def switch_env(env_id: int):
    conn = get_db()
    conn.execute("UPDATE environments SET is_active=0")
    conn.execute("UPDATE environments SET is_active=1 WHERE id=?", (env_id,))
    conn.commit()
    conn.close()


def get_active_env() -> dict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM environments WHERE is_active=1").fetchone()
    conn.close()
    return dict(row) if row else None
