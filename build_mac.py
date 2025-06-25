#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS 打包脚本
================
使用 PyInstaller 将 DeepSeek 智能文件重命名工具打包成 .app，
自动包含静态资源、模板、配置文件及所有依赖。

运行：
    python build_mac.py

生成：
    dist/DeepSeekFileRenamer.app
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

APP_NAME = "DeepSeekFileRenamer"
ENTRY_SCRIPT = "app_final.py"
# CLI 构建，避免复杂 spec 错误
ICON_FILE = "app_icon.icns"  # 可选，如存在将打包图标

# 需要包含的数据： (源路径, 目标相对路径)
DATA_FILES = [
    ("config.json", "."),
    ("templates/index.html", "templates"),
    ("static/styles.css", "static"),
    ("static/script.js", "static"),
]

HIDDEN_IMPORTS = [
    "tkinter",  # GUI 对话框依赖
    "objc", "AppKit",  # macOS PyObjC 关键模块（已随 pyobjc 安装）
]

def check_pyinstaller() -> bool:
    try:
        import PyInstaller  # noqa: F401
        return True
    except ImportError:
        return False

def install_pyinstaller() -> bool:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"])
        return True
    except subprocess.CalledProcessError:
        return False

def generate_pyinstaller_cmd():
    """生成 PyInstaller CLI 命令"""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean", "--noconfirm",
        "--windowed", "--onedir",
        "--name", APP_NAME,
    ]
    # 添加数据文件
    for src, dst in DATA_FILES:
        src_path = Path(src)
        if not src_path.exists():
            print(f"❌ 缺少文件: {src}")
            sys.exit(1)
        cmd += ["--add-data", f"{src}{os.pathsep}{dst}"]
    # 隐藏导入
    for hidden in HIDDEN_IMPORTS:
        cmd += ["--hidden-import", hidden]
    # 图标
    if Path(ICON_FILE).exists():
        cmd += ["--icon", ICON_FILE]

    cmd.append(ENTRY_SCRIPT)
    return cmd

def build_app():
    print("🚀 开始构建 macOS 应用 (.app)...")
    cmd = generate_pyinstaller_cmd()
    try:
        print("运行:", " ".join(cmd))
        subprocess.check_call(cmd)
        print("🎉 构建完成！输出目录：dist")
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        sys.exit(1)

def main():
    print("=== DeepSeek File Renamer macOS 打包 ===")
    if not check_pyinstaller():
        print("PyInstaller 未安装，正在安装...")
        if not install_pyinstaller():
            print("❌ 安装 PyInstaller 失败，请手动安装后重试")
            sys.exit(1)
    build_app()
    print("👜 打包完成，可在 dist 目录找到 .app 包")

if __name__ == "__main__":
    main() 