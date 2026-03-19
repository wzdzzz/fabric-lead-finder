#!/usr/bin/env python3
"""
一键启动管理后台
用法: python start.py
"""

import os
import sys
import subprocess

# 确保项目根目录在 path 中
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


def check_deps():
    """检查并安装依赖"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
    except ImportError:
        print("正在安装依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


def check_frontend():
    """检查前端是否已构建"""
    dist = os.path.join(ROOT, "web", "dist", "index.html")
    if not os.path.exists(dist):
        print("前端未构建，请先运行:")
        print("  cd web && npm install && npm run build")
        print()
        print("或者分别启动开发模式:")
        print("  终端1: python start.py        (后端)")
        print("  终端2: cd web && npm run dev   (前端)")
        print()
        print("继续启动后端...")


def main():
    check_deps()
    check_frontend()

    print()
    print("=" * 50)
    print("  布匹中介获客工具 - 管理后台")
    print("  后端: http://127.0.0.1:8000")
    print("  API文档: http://127.0.0.1:8000/docs")
    print()

    dist = os.path.join(ROOT, "web", "dist", "index.html")
    if os.path.exists(dist):
        print("  前端: http://127.0.0.1:8000")
    else:
        print("  前端(开发): http://localhost:5173")

    print()
    print("  默认账号: admin / admin123")
    print("=" * 50)
    print()

    import uvicorn
    uvicorn.run("server.app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
