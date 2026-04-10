"""Web 管理界面 - FastAPI 应用主入口。"""

import json
import threading
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from web.models import (
    init_db, create_case, update_case, delete_case, get_case,
    list_cases, list_modules, list_runs, get_run,
    list_envs, switch_env, get_active_env,
)
from web.runner import run_pytest_cases, run_db_cases

app = FastAPI(title="API 自动化测试平台")

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 启动时初始化数据库
init_db()


def _render(request: Request, template: str, context: dict) -> HTMLResponse:
    """统一渲染模板，兼容新版 Starlette。"""
    return templates.TemplateResponse(request=request, name=template, context=context)


# ==================== 页面路由 ====================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """仪表盘首页。"""
    runs = list_runs(10)
    cases = list_cases()
    modules = list_modules()
    env = get_active_env()
    return _render(request, "index.html", {
        "runs": runs,
        "total_cases": len(cases),
        "modules": modules,
        "active_env": env,
        "page": "dashboard",
    })


@app.get("/cases", response_class=HTMLResponse)
async def cases_page(request: Request, module: str = None):
    """用例管理页面。"""
    cases = list_cases(module)
    modules = list_modules()
    for c in cases:
        for field in ("headers", "params", "body", "expected_json"):
            try:
                c[field] = json.loads(c[field]) if isinstance(c[field], str) else c[field]
            except (json.JSONDecodeError, TypeError):
                c[field] = {}
    return _render(request, "cases.html", {
        "cases": cases,
        "modules": modules,
        "current_module": module,
        "page": "cases",
    })


@app.get("/cases/new", response_class=HTMLResponse)
async def new_case_page(request: Request):
    """新建用例页面。"""
    modules = list_modules()
    return _render(request, "case_form.html", {
        "case": None,
        "modules": modules,
        "page": "cases",
    })


@app.get("/cases/{case_id}/edit", response_class=HTMLResponse)
async def edit_case_page(request: Request, case_id: int):
    """编辑用例页面。"""
    case = get_case(case_id)
    modules = list_modules()
    if case:
        for field in ("headers", "params", "body", "expected_json"):
            try:
                val = json.loads(case[field]) if isinstance(case[field], str) else case[field]
                case[field] = json.dumps(val, indent=2, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError):
                case[field] = "{}"
    return _render(request, "case_form.html", {
        "case": case,
        "modules": modules,
        "page": "cases",
    })


@app.post("/cases/save")
async def save_case(
    request: Request,
    case_id: str = Form(default=""),
    name: str = Form(...),
    module: str = Form(default="默认模块"),
    method: str = Form(default="GET"),
    path: str = Form(...),
    headers: str = Form(default="{}"),
    params: str = Form(default="{}"),
    body: str = Form(default="{}"),
    expected_status: int = Form(default=200),
    expected_json: str = Form(default="{}"),
    description: str = Form(default=""),
):
    """保存用例（新建或更新）。"""
    data = {
        "name": name, "module": module, "method": method, "path": path,
        "headers": json.loads(headers or "{}"),
        "params": json.loads(params or "{}"),
        "body": json.loads(body or "{}"),
        "expected_status": expected_status,
        "expected_json": json.loads(expected_json or "{}"),
        "description": description,
    }
    if case_id:
        update_case(int(case_id), data)
    else:
        create_case(data)
    return RedirectResponse("/cases", status_code=303)


@app.post("/cases/{case_id}/delete")
async def remove_case(case_id: int):
    """删除用例。"""
    delete_case(case_id)
    return RedirectResponse("/cases", status_code=303)


# ==================== 执行相关 ====================

@app.get("/runs", response_class=HTMLResponse)
async def runs_page(request: Request):
    """执行记录页面。"""
    runs = list_runs(50)
    return _render(request, "runs.html", {
        "runs": runs,
        "page": "runs",
    })


@app.get("/runs/{run_id}", response_class=HTMLResponse)
async def run_detail(request: Request, run_id: int):
    """执行详情页面。"""
    run = get_run(run_id)
    return _render(request, "run_detail.html", {
        "run": run,
        "page": "runs",
    })


@app.post("/run/pytest")
async def trigger_pytest(markers: str = Form(default="")):
    """触发 pytest 用例执行（后台运行）。"""
    def _run():
        run_pytest_cases(markers=markers or None)
    threading.Thread(target=_run, daemon=True).start()
    return RedirectResponse("/runs", status_code=303)


@app.post("/run/db-cases")
async def trigger_db_cases():
    """触发数据库中录入的用例执行（后台运行）。"""
    def _run():
        run_db_cases()
    threading.Thread(target=_run, daemon=True).start()
    return RedirectResponse("/runs", status_code=303)


# ==================== 环境管理 ====================

@app.get("/envs", response_class=HTMLResponse)
async def envs_page(request: Request):
    """环境管理页面。"""
    envs = list_envs()
    return _render(request, "envs.html", {
        "envs": envs,
        "page": "envs",
    })


@app.post("/envs/{env_id}/switch")
async def switch_environment(env_id: int):
    """切换活跃环境。"""
    switch_env(env_id)
    return RedirectResponse("/envs", status_code=303)


# ==================== API 接口（供前端 AJAX 调用） ====================

@app.get("/api/runs")
async def api_list_runs():
    return list_runs(20)


@app.get("/api/runs/{run_id}")
async def api_get_run(run_id: int):
    return get_run(run_id)


@app.get("/api/cases")
async def api_list_cases(module: str = None):
    return list_cases(module)
