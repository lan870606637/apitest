"""数据驱动工具 - 从 Excel 读取测试数据供 parametrize 使用。"""

from pathlib import Path
from openpyxl import load_workbook


def read_excel_data(file_name: str, sheet_name: str = None) -> list[dict]:
    """读取 Excel 文件，返回字典列表（每行一条数据，表头为 key）。

    Args:
        file_name: 文件名（相对于 data/ 目录）或绝对路径
        sheet_name: 工作表名，默认读取第一个 sheet

    Returns:
        [{"col1": val1, "col2": val2}, ...]
    """
    file_path = Path(__file__).parent / file_name
    wb = load_workbook(file_path, read_only=True, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active

    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        return []

    headers = [str(h).strip() for h in rows[0]]
    data = []
    for row in rows[1:]:
        record = dict(zip(headers, row))
        # 跳过全空行
        if any(v is not None for v in row):
            data.append(record)

    wb.close()
    return data


def read_excel_parametrize(file_name: str, sheet_name: str = None):
    """读取 Excel 并返回 pytest.mark.parametrize 需要的格式。

    Returns:
        (ids, argnames, argvalues) 元组
        - ids: 每条数据的标识（取 case_name 列，否则用序号）
        - argnames: 参数名列表
        - argvalues: 参数值列表
    """
    data = read_excel_data(file_name, sheet_name)
    if not data:
        return [], [], []

    argnames = list(data[0].keys())
    argvalues = [tuple(d.values()) for d in data]
    ids = [d.get("case_name", f"case_{i}") for i, d in enumerate(data)]
    return ids, argnames, argvalues
