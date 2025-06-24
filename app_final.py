#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek 智能文件重命名工具 - 最终版本
基于DeepSeek API的智能文件重命名工具，支持多种文件格式的内容分析和智能重命名

作者: Timon
版本: 1.0.0 Final
"""

import os
import sys
import logging
import webbrowser
import time
import threading
from pathlib import Path

# 支持PyInstaller打包
if getattr(sys, 'frozen', False):
    # 运行在PyInstaller打包的环境中
    BASE_DIR = Path(sys._MEIPASS)
    IS_FROZEN = True
else:
    # 运行在普通Python环境中
    BASE_DIR = Path(__file__).parent
    IS_FROZEN = False

# 添加项目根目录到系统路径
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# 设置模板和静态文件路径
TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

# 导入Flask和其他依赖
try:
    from flask import Flask
    from api_final import create_app
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有必要的依赖包")
    if not IS_FROZEN:
        print("运行: pip install -r requirements.txt")
    sys.exit(1)

def setup_logging():
    """设置日志"""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def open_browser(url, delay=3):
    """延迟打开浏览器"""
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
        except Exception as e:
            logging.warning(f"无法自动打开浏览器: {e}")
            print(f"📝 请手动访问: {url}")
    
    thread = threading.Thread(target=_open, daemon=True)
    thread.start()

def main():
    """主函数"""
    # 设置控制台编码
    if os.name == 'nt':  # Windows
        os.system('chcp 65001 >nul')
    
    print("🚀 启动 DeepSeek 智能文件重命名工具...")
    
    # 设置日志
    setup_logging()
    
    # 检查必要文件
    required_files = [
        TEMPLATE_DIR / 'index.html',
        STATIC_DIR / 'styles.css',
        STATIC_DIR / 'script.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(str(file_path))
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file in missing_files:
            print(f"   - {file}")
        if IS_FROZEN:
            print("可执行文件可能损坏，请重新下载")
        else:
            print("请检查项目文件完整性")
        
        # 在打包环境中避免使用input()
        if not IS_FROZEN:
            input("按回车键退出...")
        else:
            time.sleep(3)
        return
    
    try:
        # 创建Flask应用
        print("⏳ 正在启动服务器...")
        app = create_app()
        
        # 设置服务器参数
        host = '127.0.0.1'
        port = 5000
        
        # 检查端口是否可用
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"⚠️ 端口 {port} 已被占用，尝试其他端口...")
            port = 5001
        
        url = f"http://{host}:{port}"
        
        # 自动打开浏览器
        print("🖥️  正在打开图形界面...")
        open_browser(url)
        
        # 启动Flask服务器
        app.run(
            host=host,
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        logging.error(f"启动失败: {e}")
        print(f"❌ 启动失败: {e}")
        if IS_FROZEN:
            print("如果问题持续存在，请联系技术支持")
        
        # 在打包环境中避免使用input()
        if not IS_FROZEN:
            input("按回车键退出...")
        else:
            time.sleep(3)

if __name__ == '__main__':
    main()
