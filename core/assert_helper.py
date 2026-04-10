"""断言工具 - 状态码、字段值、JSON Schema 校验。"""

import jsonschema
from requests import Response


def assert_status(resp: Response, expected: int = 200):
    """断言 HTTP 状态码。"""
    assert resp.status_code == expected, (
        f"期望状态码 {expected}，实际 {resp.status_code}，"
        f"响应: {resp.text[:300]}"
    )


def assert_json_key(resp: Response, key: str, expected):
    """断言 JSON 响应中某个顶层字段的值。"""
    data = resp.json()
    actual = data.get(key)
    assert actual == expected, (
        f"字段 '{key}' 期望值 {expected!r}，实际值 {actual!r}"
    )


def assert_json_contains(resp: Response, subset: dict):
    """断言 JSON 响应包含指定的键值对子集。"""
    data = resp.json()
    for k, v in subset.items():
        actual = data.get(k)
        assert actual == v, (
            f"字段 '{k}' 期望值 {v!r}，实际值 {actual!r}"
        )


def assert_json_schema(resp: Response, schema: dict):
    """使用 JSON Schema 校验响应体结构。"""
    data = resp.json()
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        raise AssertionError(f"JSON Schema 校验失败: {e.message}")


def assert_json_list_not_empty(resp: Response, key: str = None):
    """断言响应中的列表不为空。key 为 None 时断言整个响应体为非空列表。"""
    data = resp.json()
    target = data if key is None else data.get(key, [])
    assert isinstance(target, list) and len(target) > 0, (
        f"期望非空列表，实际: {target}"
    )
