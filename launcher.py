#!/usr/bin/env python3
"""
PyInstaller 入口 - 启动后端服务并自动打开浏览器
"""

import os
import sys
import traceback

# 最早期：确定 exe 所在目录，写日志到文件
if getattr(sys, 'frozen', False):
    _app_dir = os.path.dirname(sys.executable)
else:
    _app_dir = os.path.dirname(os.path.abspath(__file__))

_log_file = os.path.join(_app_dir, 'crash.log')


def _write_log(msg):
    with open(_log_file, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')


try:
    import time
    import threading
    import webbrowser
    import logging
    import socket

    _write_log("=== 启动 ===")

    # 确保路径正确
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
        sys.path.insert(0, base)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, base)

    _write_log(f"base={base}")
    _write_log(f"app_dir={_app_dir}")
    _write_log(f"python={sys.version}")

    # Windows 控制台 UTF-8
    if sys.platform == 'win32':
        os.system('chcp 65001 >nul 2>&1')
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')

    HOST = "127.0.0.1"
    BASE_PORT = 8000

    def find_free_port(start=BASE_PORT):
        """找到一个可用端口"""
        for port in range(start, start + 100):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind((HOST, port))
                    return port
                except OSError:
                    continue
        return start

    def open_browser(port):
        """等待服务启动后自动打开浏览器"""
        import urllib.request
        url = f"http://{HOST}:{port}"
        for _ in range(30):
            time.sleep(0.5)
            try:
                urllib.request.urlopen(f"{url}/api/config/keywords", timeout=2)
                webbrowser.open(url)
                return
            except Exception:
                pass

    def main():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        )

        port = find_free_port()
        url = f"http://{HOST}:{port}"

        _write_log(f"port={port}")

        print()
        print("=" * 50)
        print("  布匹中介获客工具 - 管理后台")
        print(f"  地址: {url}")
        print("  默认账号: admin / admin123")
        print("  关闭此窗口即可停止服务")
        print("=" * 50)
        print()

        threading.Thread(target=open_browser, args=(port,), daemon=True).start()

        _write_log("importing uvicorn...")
        import uvicorn
        _write_log("starting uvicorn...")
        uvicorn.run(
            "server.app:app",
            host=HOST,
            port=port,
            log_level="info",
        )

    main()

except Exception:
    err = traceback.format_exc()
    _write_log("!!! 启动失败 !!!")
    _write_log(err)
    # 也尝试在控制台显示
    try:
        print()
        print("!" * 50)
        print("  启动失败！错误日志已写入:")
        print(f"  {_log_file}")
        print("!" * 50)
        print(err)
        input("按回车键退出...")
    except Exception:
        pass
