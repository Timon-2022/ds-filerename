#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek智能文件重命名工具 - 可执行文件打包脚本
作者: Timon
版本: 1.0.0
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
        return True
    except ImportError:
        print("❌ PyInstaller 未安装")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("🔧 正在安装 PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller 安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller 安装失败")
        return False

def create_spec_file():
    """创建PyInstaller规格文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_final.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('config.json', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'flask',
        'requests',
        'docx',
        'PyPDF2',
        'openpyxl',
        'pptx',
        'tkinter',
        'asyncio',
        'json',
        'logging',
        'webbrowser',
        'threading',
        'time',
        'os',
        'sys',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DeepSeek智能文件重命名工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico' if os.path.exists('app_icon.ico') else None,
)
'''
    with open('deepseek_rename.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✅ 已创建 PyInstaller 规格文件")

def build_executable():
    """构建可执行文件"""
    print("🚀 开始构建可执行文件...")
    print("📝 这可能需要几分钟时间，请耐心等待...")
    
    try:
        # 使用规格文件构建
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "deepseek_rename.spec"
        ]
        
        subprocess.check_call(cmd)
        print("✅ 可执行文件构建成功！")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False

def create_readme_for_exe():
    """为可执行文件创建说明文档"""
    readme_content = """# DeepSeek智能文件重命名工具 - 可执行版本

## 🚀 使用说明

### 快速开始
1. 双击运行 `DeepSeek智能文件重命名工具.exe`
2. 程序会自动启动并打开浏览器
3. 在网页界面中设置您的DeepSeek API密钥
4. 选择要处理的文件夹，开始智能重命名

### 系统要求
- Windows 10/11 (64位)
- 无需安装Python环境
- 需要稳定的网络连接（用于调用DeepSeek API）

### 功能特色
- 🤖 AI智能文件名生成
- 📁 支持多种文件格式
- ✅ 可选择性重命名
- 🔒 自动备份和日志记录

### 注意事项
1. **首次运行可能较慢**：程序需要解压内置文件
2. **防火墙提示**：请允许程序访问网络
3. **杀毒软件误报**：可能需要添加信任

### API密钥获取
访问 https://platform.deepseek.com/ 注册并获取API密钥

### 技术支持
- 作者：Timon
- 版本：v1.0.0
- 如有问题，请查看程序日志或联系技术支持

---
*此可执行文件包含了完整的运行环境，无需额外安装依赖*
"""
    
    with open('dist/使用说明.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ 已创建使用说明文档")

def cleanup_build_files():
    """清理构建过程中的临时文件"""
    print("🧹 清理临时文件...")
    
    # 删除build目录
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("✅ 已删除 build 目录")
    
    # 删除spec文件
    if os.path.exists('deepseek_rename.spec'):
        os.remove('deepseek_rename.spec')
        print("✅ 已删除规格文件")

def main():
    """主函数"""
    print("=" * 60)
    print("  DeepSeek智能文件重命名工具 - 可执行文件打包")
    print("  作者: Timon")
    print("  版本: v1.0.0")
    print("=" * 60)
    print()
    
    # 检查并安装PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("❌ 无法安装PyInstaller，请手动安装后重试")
            return False
    
    # 检查必要文件
    required_files = [
        'app_final.py',
        'api_final.py', 
        'rename_files_final.py',
        'deepseek_client_final.py',
        'file_extractor_final.py',
        'config.json',
        'templates/index.html',
        'static/styles.css',
        'static/script.js'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file in missing_files:
            print(f"   - {file}")
        print("请确保所有final版本文件都存在")
        return False
    
    print("✅ 所有必要文件检查通过")
    
    # 创建规格文件
    create_spec_file()
    
    # 构建可执行文件
    if not build_executable():
        return False
    
    # 创建使用说明
    if os.path.exists('dist'):
        create_readme_for_exe()
    
    # 显示结果
    print()
    print("🎉 打包完成！")
    print("📁 可执行文件位置: dist/DeepSeek智能文件重命名工具.exe")
    print("📖 使用说明: dist/使用说明.txt")
    print()
    print("📋 分发建议:")
    print("   1. 将整个 dist 文件夹打包为 ZIP")
    print("   2. 文件夹中包含可执行文件和使用说明")
    print("   3. 用户只需解压并运行 .exe 文件")
    print()
    
    # 询问是否清理临时文件
    choice = input("是否清理构建临时文件？(y/n): ").lower().strip()
    if choice in ['y', 'yes', '是']:
        cleanup_build_files()
    
    print("✅ 所有操作完成！")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1) 