"""路径管理 - 统一处理开发模式和打包模式的路径差异"""

import os
import sys


def is_bundled():
    """是否是 PyInstaller 打包后运行"""
    return getattr(sys, 'frozen', False)


def get_bundle_dir():
    """获取代码/资源所在目录（打包后是临时解压目录）"""
    if is_bundled():
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_app_dir():
    """获取应用数据目录（.exe 所在目录或项目根目录）
    数据库、输出文件等应放在这里"""
    if is_bundled():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# 常用路径
BUNDLE_DIR = get_bundle_dir()
APP_DIR = get_app_dir()
DATA_DIR = os.path.join(APP_DIR, "data")
OUTPUT_DIR = os.path.join(APP_DIR, "output")
STATIC_DIR = os.path.join(BUNDLE_DIR, "web", "dist")
