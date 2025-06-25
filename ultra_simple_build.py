#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超简化 macOS 打包脚本
===================
使用 --onefile 生成单一可执行文件，避免复杂的 .app 结构问题

运行：
    python3 ultra_simple_build.py

生成：
    dist/DeepSeekFileRenamer (单一可执行文件)
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 开始超简化打包...")
    
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
    
    # 构建命令 - 使用最简单的 onefile 模式
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm", 
        "--onefile",            # 单文件模式，最简单
        "--windowed",           # GUI 应用
        "--name", "DeepSeekFileRenamer",
        
        # 添加数据文件
        "--add-data", "config.json:.",
        "--add-data", "templates:templates", 
        "--add-data", "static:static",
        
        # 入口文件
        "app_final.py"
    ]
    
    print("📦 执行打包命令...")
    print(" ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ 打包成功！")
        
        # 检查生成的文件
        exe_path = Path("dist/DeepSeekFileRenamer")
        if exe_path.exists():
            print(f"📱 生成的可执行文件: {exe_path}")
            print(f"📏 大小: {exe_path.stat().st_size / (1024*1024):.1f} MB")
            
            # 设置权限
            setup_permissions(exe_path)
            
            print("\n🎉 打包完成！")
            print("📋 使用说明:")
            print("1. 可执行文件: dist/DeepSeekFileRenamer")
            print("2. 可直接拷贝到其他 macOS 设备")
            print("3. 在终端运行: ./DeepSeekFileRenamer")
            print("4. 或双击运行（如果设置了执行权限）")
            
        else:
            print("❌ 未找到生成的可执行文件")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        sys.exit(1)

def setup_permissions(exe_path):
    """设置可执行权限"""
    try:
        # 设置执行权限
        subprocess.run(["chmod", "+x", str(exe_path)], check=True)
        print("✅ 执行权限设置完成")
        
    except Exception as e:
        print(f"⚠️  权限设置失败: {e}")

if __name__ == "__main__":
    main() 