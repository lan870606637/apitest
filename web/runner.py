"""测试执行器 - 调用 pytest 运行用例并收集结果。"""

from __future__ import annotations

import subprocess
import time
import json
import sys
from pathlib import Path
from web.models import create_run, update_run, list_cases, get_active_env

PROJECT_ROOT = Path(__file__).parent.parent
REPORT_DIR = PROJECT_ROOT / "reports"


def run_pytest_cases(case_ids: list[int] = None, markers: str = None) -> int:
    """执行测试用例，返回 run_id。

    Args:
        case_ids: 指定用例 ID 列表（从数据库中的用例生成临时测试文件）
        markers: pytest marker 表达式，如 "smoke" 或 "user and not order"
    """
    run_id = create_run("manual")
    allure_dir = REPORT_DIR / f"allure-results-{run_id}"
    allure_dir.mkdir(parents=True, exist_ok=True)

    # 构建 pytest 命令
    cmd = [
        sys.executable, "-m", "pytest",
        str(PROJECT_ROOT / "testcases"),
        f"--alluredir={allure_dir}",
        "-v", "--tb=short",
    ]

    if markers:
        cmd.extend(["-m", markers])

    # 如果指定了数据库中的用例，生成临时测试文件执行
    if case_ids:
        temp_file = _generate_temp_test(case_ids)
        if temp_file:
            cmd[2] = str(temp_file)

    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=300,
            cwd=str(PROJECT_ROOT),
        )
        duration = time.time() - start
        stats = _parse_pytest_output(result.stdout)
        update_run(run_id, {
            "status": "passed" if result.returncode == 0 else "failed",
            "total": stats["total"],
            "passed": stats["passed"],
            "failed": stats["failed"],
            "skipped": stats["skipped"],
            "duration": round(duration, 2),
            "report_path": str(allure_dir),
            "log": result.stdout[-5000:] + "\n" + result.stderr[-2000:],
        })
    except subprocess.TimeoutExpired:
        update_run(run_id, {
            "status": "timeout",
            "total": 0, "passed": 0, "failed": 0, "skipped": 0,
            "duration": 300,
            "log": "执行超时（300秒）",
        })
    except Exception as e:
        update_run(run_id, {
            "status": "error",
            "total": 0, "passed": 0, "failed": 0, "skipped": 0,
            "duration": time.time() - start,
            "log": str(e),
        })

    return run_id


def run_db_cases(case_ids: list[int] = None) -> int:
    """执行数据库中录入的接口用例。"""
    run_id = create_run("db_cases")
    cases = list_cases()
    if case_ids:
        cases = [c for c in cases if c["id"] in case_ids]

    env = get_active_env()
    base_url = env["base_url"] if env else "http://localhost:8080/api"

    import requests
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})

    total = len(cases)
    passed = failed = skipped = 0
    logs = []
    start = time.time()

    for case in cases:
        if not case.get("is_active"):
            skipped += 1
            continue

        url = base_url.rstrip("/") + "/" + case["path"].lstrip("/")
        method = case["method"].upper()
        headers = json.loads(case.get("headers") or "{}")
        params = json.loads(case.get("params") or "{}")
        body = json.loads(case.get("body") or "{}")
        expected_status = case.get("expected_status", 200)

        try:
            resp = session.request(
                method, url, headers=headers, params=params,
                json=body if method in ("POST", "PUT", "PATCH") else None,
                timeout=15,
            )
            if resp.status_code == expected_status:
                passed += 1
                logs.append(f"[PASS] {case['name']} - {method} {case['path']} -> {resp.status_code}")
            else:
                failed += 1
                logs.append(
                    f"[FAIL] {case['name']} - {method} {case['path']} "
                    f"期望 {expected_status} 实际 {resp.status_code}\n  响应: {resp.text[:200]}"
                )
        except Exception as e:
            failed += 1
            logs.append(f"[ERROR] {case['name']} - {method} {case['path']} -> {e}")

    duration = round(time.time() - start, 2)
    update_run(run_id, {
        "status": "passed" if failed == 0 else "failed",
        "total": total, "passed": passed, "failed": failed, "skipped": skipped,
        "duration": duration,
        "log": "\n".join(logs),
    })
    return run_id


def _generate_temp_test(case_ids: list[int]) -> Path | None:
    """根据数据库用例生成临时 pytest 文件。"""
    cases = [c for c in list_cases() if c["id"] in case_ids]
    if not cases:
        return None

    lines = [
        '"""自动生成的临时测试文件。"""',
        "import requests",
        "import pytest",
        "from web.models import get_active_env",
        "",
        "BASE = (get_active_env() or {}).get('base_url', 'http://localhost:8080/api')",
        "",
    ]

    for c in cases:
        func_name = f"test_case_{c['id']}"
        lines.append(f"def {func_name}():")
        lines.append(f'    """用例: {c["name"]}"""')
        lines.append(f'    url = BASE.rstrip("/") + "/{c["path"].lstrip("/")}"')
        lines.append(f'    resp = requests.request("{c["method"]}", url, timeout=15)')
        lines.append(f'    assert resp.status_code == {c["expected_status"]}')
        lines.append("")

    temp_file = PROJECT_ROOT / "testcases" / "_temp_generated_test.py"
    temp_file.write_text("\n".join(lines), encoding="utf-8")
    return temp_file


def _parse_pytest_output(output: str) -> dict:
    """从 pytest 输出中解析统计数据。"""
    stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
    for line in output.splitlines():
        line = line.strip()
        # 匹配类似 "= 5 passed, 2 failed, 1 skipped in 3.21s ="
        if "passed" in line or "failed" in line or "error" in line:
            import re
            for key in ["passed", "failed", "skipped", "error"]:
                m = re.search(rf"(\d+)\s+{key}", line)
                if m:
                    if key == "error":
                        stats["failed"] += int(m.group(1))
                    else:
                        stats[key] = int(m.group(1))
    stats["total"] = stats["passed"] + stats["failed"] + stats["skipped"]
    return stats
