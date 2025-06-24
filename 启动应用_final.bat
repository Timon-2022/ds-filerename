@echo off
chcp 65001 >nul
title DeepSeek 智能文件重命名工具 v1.0.0 Final

echo.
echo ============================================
echo   DeepSeek 智能文件重命名工具 v1.0.0 Final
echo   作者: Timon
echo ============================================
echo.
echo 🚀 启动应用...
echo 📝 浏览器将自动打开 http://localhost:5000
echo ⏹️  按 Ctrl+C 停止服务器
echo.

:: 使用最终版本的应用文件
& "C:\Program Files\Python311\python.exe" app_final.py

echo.
echo 👋 程序已退出
pause 