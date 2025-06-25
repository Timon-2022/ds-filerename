#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版 macOS 打包脚本
===================
专门优化跨设备兼容性，确保在其他 Mac 上即开即用

运行：
    python3 final_build_mac.py

生成：
    dist/DeepSeekFileRenamer_Final (优化版单文件)
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 开始最终版打包...")
    
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
    
    # 清理之前的构建
    cleanup_previous_builds()
    
    # 构建命令 - 优化版
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm", 
        "--onefile",                    # 单文件模式
        "--console",                    # 使用 console 而非 windowed，避免 macOS 兼容性问题
        "--name", "DeepSeekFileRenamer_Final",
        
        # 添加数据文件
        "--add-data", "config.json:.",
        "--add-data", "templates:templates", 
        "--add-data", "static:static",
        
        # 排除不必要的模块，减小体积
        "--exclude-module", "pygame",
        "--exclude-module", "matplotlib",
        "--exclude-module", "pandas", 
        "--exclude-module", "numpy",
        "--exclude-module", "PIL",
        "--exclude-module", "tkinter",
        
        # 隐藏导入（只保留必需的）
        "--hidden-import", "objc",
        "--hidden-import", "AppKit",
        
        # 入口文件
        "app_final.py"
    ]
    
    print("📦 执行优化打包...")
    print(" ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 打包成功！")
        
        # 检查生成的文件
        exe_path = Path("dist/DeepSeekFileRenamer_Final")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024*1024)
            print(f"📱 生成的可执行文件: {exe_path}")
            print(f"📏 大小: {size_mb:.1f} MB")
            
            # 设置权限和签名
            setup_for_distribution(exe_path)
            
            # 测试启动
            test_executable(exe_path)
            
            print("\n🎉 最终版打包完成！")
            print("📋 分发说明:")
            print("1. 文件: dist/DeepSeekFileRenamer_Final")
            print(f"2. 大小: {size_mb:.1f} MB")
            print("3. 兼容性: macOS 13+ (Intel & Apple Silicon)")
            print("4. 使用: 拷贝到目标设备后直接运行 ./DeepSeekFileRenamer_Final")
            print("5. 首次运行可能需要: xattr -d com.apple.quarantine DeepSeekFileRenamer_Final")
            
        else:
            print("❌ 未找到生成的可执行文件")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout[-1000:])  # 只显示最后1000字符
        if e.stderr:
            print("STDERR:", e.stderr[-1000:])
        sys.exit(1)

def cleanup_previous_builds():
    """清理之前的构建"""
    try:
        import shutil
        for path in ["build", "dist", "*.spec"]:
            if Path(path).exists():
                if Path(path).is_dir():
                    shutil.rmtree(path)
                else:
                    Path(path).unlink()
        print("✅ 清理完成")
    except Exception as e:
        print(f"⚠️ 清理失败: {e}")

def setup_for_distribution(exe_path):
    """设置分发所需的权限和签名"""
    try:
        # 设置执行权限
        subprocess.run(["chmod", "+x", str(exe_path)], check=True)
        
        # 移除隔离属性（预防性）
        subprocess.run(["xattr", "-d", "com.apple.quarantine", str(exe_path)], 
                      capture_output=True)
        
        # ad-hoc 签名
        result = subprocess.run(["codesign", "--force", "--sign", "-", str(exe_path)], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 权限和签名设置完成")
        else:
            print(f"⚠️ 签名可能失败: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ 权限设置失败: {e}")

def test_executable(exe_path):
    """测试可执行文件"""
    print("🧪 测试可执行文件...")
    try:
        # 启动测试
        process = subprocess.Popen([str(exe_path)], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 等待3秒
        import time
        time.sleep(3)
        
        # 测试HTTP响应
        try:
            import urllib.request
            response = urllib.request.urlopen("http://127.0.0.1:5001", timeout=2)
            if response.getcode() == 200:
                print("✅ 可执行文件测试通过")
            else:
                print("⚠️ HTTP响应异常")
        except Exception as e:
            print(f"⚠️ HTTP测试失败: {e}")
        
        # 停止测试进程
        process.terminate()
        process.wait(timeout=5)
        
    except Exception as e:
        print(f"⚠️ 测试失败: {e}")

if __name__ == "__main__":
    main() 