"""启动 Web 管理界面。

使用方式：
    python run_web.py          # 默认 8888 端口
    python run_web.py 9000     # 自定义端口
"""

import sys
import uvicorn

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    print(f"\n  API 测试平台启动中...")
    print(f"  访问地址: http://localhost:{port}\n")
    uvicorn.run("web.app:app", host="0.0.0.0", port=port, reload=True)
