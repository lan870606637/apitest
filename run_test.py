"""一键运行测试脚本。

使用方法:
    python run_test.py                    # 运行全部测试
    python run_test.py test_audio         # 运行指定文件
    python run_test.py test_audio::TestAudio  # 运行指定类
    python run_test.py -m smoke           # 运行smoke测试
    python run_test.py -k "update"        # 按关键字运行
"""

import sys
import subprocess


def run_tests():
    """运行测试。"""
    args = sys.argv[1:]

    # 基础命令
    cmd = ["python", "-m", "pytest", "-v"]

    if not args:
        # 默认运行全部
        cmd.extend(["testcases", "--html=reports/report.html", "--self-contained-html"])
        print("🚀 运行全部测试...")
    elif args[0] == "-m" or args[0] == "-k":
        # 标记或关键字
        cmd.extend(args)
    elif "::" in args[0]:
        # 指定类或方法
        cmd.append(f"testcases/{args[0].replace('::', '.py::')}")
    else:
        # 指定文件
        cmd.append(f"testcases/{args[0]}.py")

    print(f"📋 执行命令: {' '.join(cmd)}\n")
    subprocess.run(cmd)


if __name__ == "__main__":
    run_tests()
