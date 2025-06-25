#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建真正的 macOS .app 包
========================
将可执行文件包装成标准的 .app 应用程序包，支持双击启动

运行：
    python3 create_app_bundle.py

生成：
    dist/DeepSeekFileRenamer.app (可双击启动的应用)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

APP_NAME = "DeepSeekFileRenamer"
EXECUTABLE_NAME = "DeepSeekFileRenamer_Final"

def main():
    print("🚀 创建 macOS .app 应用程序包...")
    
    # 检查可执行文件是否存在
    exe_path = Path(f"dist/{EXECUTABLE_NAME}")
    if not exe_path.exists():
        print(f"❌ 找不到可执行文件: {exe_path}")
        print("请先运行 final_build_mac.py 生成可执行文件")
        sys.exit(1)
    
    # 创建 .app 目录结构
    app_path = create_app_structure()
    
    # 拷贝可执行文件
    copy_executable(exe_path, app_path)
    
    # 创建 Info.plist
    create_info_plist(app_path)
    
    # 创建启动脚本
    create_launcher_script(app_path)
    
    # 设置权限和签名
    setup_app_permissions(app_path)
    
    # 测试应用
    test_app(app_path)
    
    print(f"\n🎉 .app 应用程序包创建完成！")
    print(f"📱 应用位置: {app_path}")
    print("📋 使用说明:")
    print("1. 可以双击启动应用")
    print("2. 可以拖拽到 Applications 文件夹")
    print("3. 可以直接拷贝到其他 Mac 设备使用")
    print("4. 首次运行可能需要右键选择'打开'")

def create_app_structure():
    """创建 .app 目录结构"""
    app_path = Path(f"dist/{APP_NAME}.app")
    
    # 删除现有的 .app（如果存在）
    if app_path.exists():
        shutil.rmtree(app_path)
    
    # 创建标准 .app 目录结构
    contents_path = app_path / "Contents"
    macos_path = contents_path / "MacOS"
    resources_path = contents_path / "Resources"
    
    for path in [contents_path, macos_path, resources_path]:
        path.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ 创建 .app 目录结构: {app_path}")
    return app_path

def copy_executable(exe_path, app_path):
    """拷贝可执行文件到 .app 包内"""
    macos_path = app_path / "Contents" / "MacOS"
    target_exe = macos_path / EXECUTABLE_NAME
    
    shutil.copy2(exe_path, target_exe)
    os.chmod(target_exe, 0o755)
    
    print(f"✅ 拷贝可执行文件到: {target_exe}")

def create_info_plist(app_path):
    """创建 Info.plist 文件"""
    plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>DeepSeek 智能文件重命名工具</string>
    <key>CFBundleExecutable</key>
    <string>{APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.deepseek.filerenamer</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>{APP_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>13.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
</dict>
</plist>'''
    
    plist_path = app_path / "Contents" / "Info.plist"
    plist_path.write_text(plist_content, encoding='utf-8')
    
    print(f"✅ 创建 Info.plist: {plist_path}")

def create_launcher_script(app_path):
    """创建启动脚本"""
    launcher_script = f'''#!/bin/bash
# DeepSeek 文件重命名工具启动脚本

# 获取应用程序包路径
APP_PATH="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
EXECUTABLE_PATH="$APP_PATH/{EXECUTABLE_NAME}"

# 启动应用程序
exec "$EXECUTABLE_PATH" "$@"
'''
    
    launcher_path = app_path / "Contents" / "MacOS" / APP_NAME
    launcher_path.write_text(launcher_script, encoding='utf-8')
    os.chmod(launcher_path, 0o755)
    
    print(f"✅ 创建启动脚本: {launcher_path}")

def setup_app_permissions(app_path):
    """设置应用权限和签名"""
    try:
        # 移除隔离属性
        subprocess.run(["xattr", "-dr", "com.apple.quarantine", str(app_path)], 
                      capture_output=True)
        
        # 设置所有文件的执行权限
        macos_path = app_path / "Contents" / "MacOS"
        for file in macos_path.iterdir():
            if file.is_file():
                os.chmod(file, 0o755)
        
        # ad-hoc 签名整个应用包
        result = subprocess.run(["codesign", "--force", "--deep", "--sign", "-", str(app_path)], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 应用签名完成")
        else:
            print(f"⚠️ 签名可能失败: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ 权限设置失败: {e}")

def test_app(app_path):
    """测试应用程序"""
    print("🧪 测试应用程序...")
    try:
        # 尝试启动应用
        process = subprocess.Popen(["open", str(app_path)], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 等待启动
        import time
        time.sleep(5)
        
        # 测试HTTP响应
        try:
            import urllib.request
            response = urllib.request.urlopen("http://127.0.0.1:5001", timeout=3)
            if response.getcode() == 200:
                print("✅ 应用程序测试通过")
                # 停止测试进程
                subprocess.run(["pkill", "-f", EXECUTABLE_NAME], capture_output=True)
            else:
                print("⚠️ HTTP响应异常")
        except Exception as e:
            print(f"⚠️ HTTP测试失败: {e}")
        
    except Exception as e:
        print(f"⚠️ 应用测试失败: {e}")

if __name__ == "__main__":
    main() 