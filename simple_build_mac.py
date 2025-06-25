#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版 macOS 打包脚本
====================
使用最基础的 PyInstaller 参数，生成可靠的 .app 包

运行：
    python3 simple_build_mac.py

生成：
    dist/app_final.app (可重命名为 DeepSeekFileRenamer.app)
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 开始简化打包...")
    
    # 检查入口文件
    if not Path("app_final.py").exists():
        print("❌ 找不到 app_final.py")
        sys.exit(1)
    
    # 检查依赖文件
    required_files = ["config.json", "templates/index.html", "static/styles.css", "static/script.js"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 缺少文件: {file}")
            sys.exit(1)
    
    # 构建命令 - 使用最简单的参数
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm", 
        "--windowed",           # GUI 应用
        "--onedir",             # 目录模式，更稳定
        "--name", "DeepSeekFileRenamer",
        
        # 添加数据文件
        "--add-data", "config.json:.",
        "--add-data", "templates:templates", 
        "--add-data", "static:static",
        
        # 隐藏导入（只保留必要的）
        "--hidden-import", "tkinter",
        "--hidden-import", "objc",
        "--hidden-import", "AppKit",
        
        # 入口文件
        "app_final.py"
    ]
    
    print("📦 执行打包命令...")
    print(" ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 打包成功！")
        
        # 检查生成的文件
        app_path = Path("dist/DeepSeekFileRenamer.app")
        if app_path.exists():
            print(f"📱 生成的应用: {app_path}")
            print(f"📏 大小: {get_dir_size(app_path):.1f} MB")
            
            # 设置权限和签名
            setup_app_permissions(app_path)
            
            print("\n🎉 打包完成！")
            print("📋 使用说明:")
            print("1. 应用位置: dist/DeepSeekFileRenamer.app")
            print("2. 可直接拷贝到其他 macOS 设备")
            print("3. 首次运行可能需要右键选择'打开'")
            
        else:
            print("❌ 未找到生成的 .app 文件")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        sys.exit(1)

def get_dir_size(path):
    """计算目录大小（MB）"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total += os.path.getsize(filepath)
    return total / (1024 * 1024)

def setup_app_permissions(app_path):
    """设置应用权限和签名"""
    try:
        # 移除隔离属性
        subprocess.run(["xattr", "-dr", "com.apple.quarantine", str(app_path)], 
                      capture_output=True)
        
        # 设置执行权限
        executable = app_path / "Contents/MacOS/DeepSeekFileRenamer"
        if executable.exists():
            subprocess.run(["chmod", "+x", str(executable)], capture_output=True)
        
        # ad-hoc 签名
        subprocess.run(["codesign", "--force", "--deep", "--sign", "-", str(app_path)], 
                      capture_output=True)
        
        print("✅ 权限和签名设置完成")
        
    except Exception as e:
        print(f"⚠️  权限设置失败: {e}")
        print("可以手动执行以下命令:")
        print(f"xattr -dr com.apple.quarantine {app_path}")
        print(f"codesign --force --deep --sign - {app_path}")

if __name__ == "__main__":
    main() 