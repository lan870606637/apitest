"""参数提取器 - 用 JSONPath 或正则从响应中提取关联参数。"""

import re
from jsonpath_ng.ext import parse as jsonpath_parse
from requests import Response


def extract_jsonpath(resp: Response, expr: str):
    """用 JSONPath 表达式从响应 JSON 中提取第一个匹配值。

    Args:
        resp: requests 响应对象
        expr: JSONPath 表达式，例如 "$.data.token"

    Returns:
        匹配到的第一个值，未匹配到时返回 None
    """
    data = resp.json()
    matches = jsonpath_parse(expr).find(data)
    return matches[0].value if matches else None


def extract_jsonpath_all(resp: Response, expr: str) -> list:
    """用 JSONPath 表达式提取所有匹配值。"""
    data = resp.json()
    matches = jsonpath_parse(expr).find(data)
    return [m.value for m in matches]


def extract_regex(text: str, pattern: str, group: int = 1):
    """用正则表达式从文本中提取内容。

    Args:
        text: 待匹配文本
        pattern: 正则表达式（需包含分组）
        group: 返回第几个分组，默认 1

    Returns:
        匹配到的字符串，未匹配到时返回 None
    """
    match = re.search(pattern, text)
    return match.group(group) if match else None


def extract_header(resp: Response, header_name: str) -> str | None:
    """从响应头中提取指定字段。"""
    return resp.headers.get(header_name)
