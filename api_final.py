from flask import Flask, jsonify, request, render_template
from rename_files import DeepSeekFileRenamer
from pathlib import Path
import asyncio
import logging
import sys
import os

logger = logging.getLogger(__name__)
renamer = None

def create_app():
    global renamer
    
    # 支持PyInstaller打包
    if getattr(sys, 'frozen', False):
        # 运行在PyInstaller打包的环境中
        base_dir = Path(sys._MEIPASS)
    else:
        # 运行在普通Python环境中
        base_dir = Path(__file__).parent
    
    template_dir = base_dir / 'templates'
    static_dir = base_dir / 'static'
    
    app = Flask(__name__, 
                template_folder=str(template_dir), 
                static_folder=str(static_dir))
    renamer = DeepSeekFileRenamer()

    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route('/set_api_key', methods=['POST'])
    def set_api_key():
        """设置 DeepSeek API 密钥"""
        data = request.json
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({"error": "API 密钥不能为空"}), 400
        
        success = renamer.set_api_key(api_key)
        if success:
            return jsonify({"message": "API 密钥设置成功，连接测试通过"})
        else:
            return jsonify({"error": "API 密钥无效或连接失败"}), 400

    @app.route('/set_directory', methods=['POST'])
    def set_directory():
        """设置工作目录"""
        data = request.json
        directory = data.get('directory', '').strip()
        
        if not directory:
            return jsonify({"error": "目录路径不能为空"}), 400
        
        logger.info(f"尝试设置目录: {directory}")
        success = renamer.set_directory(directory)
        if success:
            return jsonify({
                "message": "目录设置成功",
                "directory": str(renamer.base_dir)
            })
        else:
            # 提供更详细的错误信息
            from pathlib import Path
            try:
                path = Path(directory)
                if not path.exists():
                    error_msg = f"目录不存在: {directory}"
                elif not path.is_dir():
                    error_msg = f"路径不是目录: {directory}"
                else:
                    error_msg = f"无法访问目录: {directory}"
            except Exception as e:
                error_msg = f"无效的目录路径: {directory} ({str(e)})"
            
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 400

    @app.route('/scan_files', methods=['GET'])
    def scan_files():
        """扫描目录中的文件"""
        if not renamer.base_dir:
            return jsonify({'error': '请先设置工作目录'}), 400
        
        try:
            files_info = renamer.scan_directory()
            
            # 转换为JSON可序列化的格式
            serializable_files = []
            for file_info in files_info:
                serializable_files.append({
                    'name': file_info['name'],
                    'size': file_info['size'],
                    'type': file_info['type'],
                    'extension': file_info['extension'],
                    'relative_path': str(file_info['relative_path'])
                })
            
            return jsonify({
                'total_files': len(serializable_files),
                'files': serializable_files
            })
        except Exception as e:
            logger.error(f"扫描文件失败: {str(e)}")
            return jsonify({'error': f'扫描文件失败: {str(e)}'}), 500

    @app.route('/set_config', methods=['POST'])
    def set_config():
        """设置重命名配置"""
        data = request.json
        
        try:
            # 更新配置
            renamer.analysis_type = data.get('analysis_type', 'summary')
            renamer.naming_strategy = data.get('naming_strategy', 'ai_suggestion')
            renamer.add_date = data.get('add_date', False)
            renamer.custom_prefix = data.get('custom_prefix', '').strip()
            renamer.custom_suffix = data.get('custom_suffix', '').strip()
            renamer.max_filename_length = int(data.get('max_filename_length', 100))
            renamer.backup_enabled = data.get('backup_enabled', True)
            
            exclude_patterns = data.get('exclude_patterns', [])
            if isinstance(exclude_patterns, list):
                renamer.exclude_patterns = exclude_patterns
            
            return jsonify({"message": "配置设置成功"})
        except Exception as e:
            logger.error(f"设置配置失败: {str(e)}")
            return jsonify({'error': f'设置配置失败: {str(e)}'}), 500

    @app.route('/preview_rename', methods=['POST'])
    def preview_rename():
        """预览重命名结果（不执行实际重命名）"""
        if not renamer.base_dir:
            return jsonify({'error': '请先设置工作目录'}), 400
        
        if not renamer.deepseek_client:
            return jsonify({'error': '请先设置 DeepSeek API 密钥'}), 400
        
        try:
            # 使用异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(renamer.process_directory(execute_rename=False))
            loop.close()
            
            if 'error' in result:
                return jsonify({'error': result['error']}), 500
            
            # 转换为JSON可序列化的格式
            preview_results = []
            for analysis_result in result['analysis_results']:
                preview_result = {
                    'original_name': analysis_result['original_name'],
                    'new_name': analysis_result.get('new_name', ''),
                    'success': analysis_result['success'],
                    'skipped': analysis_result['skipped'],
                    'error': analysis_result.get('error', ''),
                    'suggested_name': analysis_result.get('suggested_name', '')
                }
                preview_results.append(preview_result)
            
            return jsonify({
                'total_files': result['total_files'],
                'successful_analyses': result['successful_analyses'],
                'failed_analyses': result['failed_analyses'],
                'skipped_analyses': result['skipped_analyses'],
                'preview_results': preview_results
            })
            
        except Exception as e:
            logger.error(f"预览重命名失败: {str(e)}")
            return jsonify({'error': f'预览重命名失败: {str(e)}'}), 500

    @app.route('/execute_rename', methods=['POST'])
    def execute_rename():
        """执行文件重命名"""
        if not renamer.base_dir:
            return jsonify({'error': '请先设置工作目录'}), 400
        
        if not renamer.deepseek_client:
            return jsonify({'error': '请先设置 DeepSeek API 密钥'}), 400
        
        try:
            data = request.json or {}
            selected_indices = data.get('selected_files', [])
            
            # 使用异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if selected_indices:
                # 如果指定了选中的文件，只处理这些文件
                result = loop.run_until_complete(renamer.process_selected_files(selected_indices, execute_rename=True))
            else:
                # 否则处理所有文件
                result = loop.run_until_complete(renamer.process_directory(execute_rename=True))
            
            loop.close()
            
            if 'error' in result:
                return jsonify({'error': result['error']}), 500
            
            rename_stats = result.get('rename_stats', {})
            
            return jsonify({
                'total_files': result['total_files'],
                'successful_analyses': result['successful_analyses'],
                'failed_analyses': result['failed_analyses'],
                'skipped_analyses': result['skipped_analyses'],
                'rename_success': rename_stats.get('success', 0),
                'rename_failed': rename_stats.get('failed', 0),
                'rename_skipped': rename_stats.get('skipped', 0),
                'errors': rename_stats.get('errors', []),
                'log_file': result.get('log_file', '')
            })
            
        except Exception as e:
            logger.error(f"执行重命名失败: {str(e)}")
            return jsonify({'error': f'执行重命名失败: {str(e)}'}), 500

    @app.route('/choose_directory', methods=['POST'])
    def choose_directory():
        """选择目录的API端点"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            # 创建隐藏的根窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            root.attributes('-topmost', True)  # 确保对话框在最前面
            
            # 打开文件夹选择对话框
            directory = filedialog.askdirectory(
                title="选择要处理的文件夹",
                initialdir="C:\\"
            )
            
            root.destroy()  # 销毁根窗口
            
            if directory:
                return jsonify({
                    "success": True,
                    "directory": directory,
                    "message": "目录选择成功"
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "用户取消了目录选择"
                }), 400
                
        except ImportError:
            return jsonify({
                "success": False,
                "error": "系统不支持图形界面目录选择，请手动输入路径"
            }), 400
        except Exception as e:
            logger.error(f"目录选择失败: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"目录选择失败: {str(e)}"
            }), 500

    @app.route('/get_config', methods=['GET'])
    def get_config():
        """获取当前配置"""
        return jsonify({
            'analysis_type': renamer.analysis_type,
            'naming_strategy': renamer.naming_strategy,
            'add_date': renamer.add_date,
            'custom_prefix': renamer.custom_prefix,
            'custom_suffix': renamer.custom_suffix,
            'max_filename_length': renamer.max_filename_length,
            'backup_enabled': renamer.backup_enabled,
            'exclude_patterns': renamer.exclude_patterns,
            'has_api_key': bool(renamer.deepseek_client),
            'has_directory': bool(renamer.base_dir),
            'directory': str(renamer.base_dir) if renamer.base_dir else ''
        })

    # 向后兼容的路由
    @app.route('/discover_patterns', methods=['GET'])
    def discover_patterns():
        """发现文件模式（向后兼容）"""
        if not renamer.base_dir:
            return jsonify({'error': '请先设置工作目录'}), 400
        
        try:
            patterns = renamer._discover_file_patterns()
            return jsonify(patterns)
        except Exception as e:
            logger.error(f"发现文件模式失败: {str(e)}")
            return jsonify({'error': f'发现文件模式失败: {str(e)}'}), 500

    @app.route('/rename_files', methods=['POST'])
    def rename_files_route():
        """重命名文件（向后兼容）"""
        return execute_rename()

    return app
