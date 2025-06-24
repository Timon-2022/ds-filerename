@echo off
chcp 65001 >nul
title DeepSeek智能文件重命名工具 - 打包可执行文件

echo.
echo ============================================
echo   DeepSeek智能文件重命名工具 - 打包工具
echo   作者: Timon
echo ============================================
echo.
echo 🚀 开始打包可执行文件...
echo 📝 这将创建一个独立的 .exe 文件
echo ⏳ 请耐心等待，可能需要几分钟...
echo.

:: 使用Python运行打包脚本
& "C:\Program Files\Python311\python.exe" build_exe.py

echo.
echo 👋 打包完成！
pause 