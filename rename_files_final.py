import os
import re
import shutil
import asyncio
import sys
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, Union
import logging

from deepseek_client_final import DeepSeekClient
from file_extractor_final import FileContentExtractor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DeepSeekFileRenamer:
    """基于 DeepSeek API 的智能文件重命名工具"""
    
    def __init__(
        self,
        api_key: str = "",
        base_dir: Union[str, Path] = None,
        analysis_type: str = "summary",
        naming_strategy: str = "ai_suggestion",
        add_date: bool = False,
        custom_prefix: str = "",
        custom_suffix: str = "",
        max_filename_length: int = 100,
        backup_enabled: bool = True,
        exclude_patterns: List[str] = None
    ):
        """
        初始化文件重命名器
        
        Args:
            api_key: DeepSeek API 密钥
            base_dir: 要处理的目录
            analysis_type: 分析类型 ('summary', 'keywords', 'topic')
            naming_strategy: 命名策略 ('ai_suggestion', 'keywords_only', 'topic_date')
            add_date: 是否添加日期
            custom_prefix: 自定义前缀
            custom_suffix: 自定义后缀
            max_filename_length: 最大文件名长度
            backup_enabled: 是否启用备份
            exclude_patterns: 排除的文件模式
        """
        self.api_key = api_key
        self.base_dir = Path(base_dir) if base_dir else None
        self.analysis_type = analysis_type
        self.naming_strategy = naming_strategy
        self.add_date = add_date
        self.custom_prefix = custom_prefix
        self.custom_suffix = custom_suffix
        self.max_filename_length = max_filename_length
        self.backup_enabled = backup_enabled
        self.exclude_patterns = exclude_patterns or []
        
        # 初始化组件
        self.deepseek_client = None
        self.content_extractor = FileContentExtractor()
        
        # 运行时状态
        self.backup_dir = None
        self.operation_log = []
        self.processed_files = []
        
        if api_key:
            self.deepseek_client = DeepSeekClient(api_key)
    
    def set_api_key(self, api_key: str) -> bool:
        """设置 API 密钥并测试连接"""
        try:
            self.api_key = api_key
            self.deepseek_client = DeepSeekClient(api_key)
            return self.deepseek_client.test_connection()
        except Exception as e:
            logger.error(f"设置 API 密钥失败: {str(e)}")
            return False
    
    def set_directory(self, directory: Union[str, Path]) -> bool:
        """设置工作目录"""
        try:
            if not directory or str(directory).strip() == '':
                logger.error("目录路径为空")
                return False
            
            self.base_dir = Path(directory)
            
            if not self.base_dir.exists():
                logger.error(f"目录不存在: {self.base_dir}")
                return False
            
            if not self.base_dir.is_dir():
                logger.error(f"路径不是目录: {self.base_dir}")
                return False
            
            logger.info(f"成功设置工作目录: {self.base_dir}")
            return True
            
        except Exception as e:
            logger.error(f"设置目录失败: {str(e)}")
            return False
    
    def create_backup_directory(self) -> Path:
        """创建备份目录"""
        if not self.base_dir:
            raise ValueError("未设置工作目录")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.base_dir / f"backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        self.backup_dir = backup_dir
        return backup_dir
    
    def backup_file(self, file_path: Path) -> bool:
        """备份文件"""
        if not self.backup_enabled or not self.backup_dir:
            return True
        
        try:
            shutil.copy2(file_path, self.backup_dir)
            return True
        except Exception as e:
            logger.error(f"备份文件失败 {file_path}: {str(e)}")
            return False
    
    def is_excluded_file(self, file_path: Path) -> bool:
        """检查文件是否在排除列表中"""
        file_name = file_path.name.lower()
        
        for pattern in self.exclude_patterns:
            if re.search(pattern.lower(), file_name):
                return True
        
        # 默认排除的文件类型
        excluded_extensions = {'.exe', '.dll', '.so', '.dylib', '.bin', '.zip', '.rar', '.7z'}
        if file_path.suffix.lower() in excluded_extensions:
            return True
        
        return False
    
    def scan_directory(self) -> List[Dict[str, Any]]:
        """扫描目录并返回可处理的文件列表"""
        if not self.base_dir or not self.base_dir.exists():
            return []
        
        files_info = []
        
        for file_path in self.base_dir.rglob('*'):
            if not file_path.is_file():
                continue
            
            if self.is_excluded_file(file_path):
                continue
            
            if not self.content_extractor.is_supported_file(file_path):
                continue
            
            file_info = {
                'path': file_path,
                'name': file_path.name,
                'size': file_path.stat().st_size,
                'type': self.content_extractor.get_file_type(file_path),
                'extension': file_path.suffix,
                'relative_path': file_path.relative_to(self.base_dir)
            }
            
            files_info.append(file_info)
        
        return files_info
    
    def sanitize_filename(self, filename: str, extension: str = "") -> str:
        """清理文件名，确保符合文件系统要求"""
        # 移除或替换不允许的字符
        invalid_chars = r'[<>:"/\\|?*]'
        filename = re.sub(invalid_chars, '_', filename)
        
        # 移除多余的空格和特殊字符
        filename = re.sub(r'\s+', ' ', filename).strip()
        filename = re.sub(r'[._-]+', '_', filename)
        
        # 确保不以点开头或结尾
        filename = filename.strip('.')
        
        # 限制长度
        max_name_length = self.max_filename_length - len(extension)
        if len(filename) > max_name_length:
            filename = filename[:max_name_length].rstrip('_')
        
        # 确保不为空
        if not filename:
            filename = "unnamed_file"
        
        return filename
    
    def generate_filename(self, analysis_result: Dict[str, Any], original_file: Path) -> str:
        """根据分析结果和命名策略生成新文件名"""
        suggested_name = analysis_result.get('suggested_name', '未知文档')
        original_ext = original_file.suffix
        
        # 清理建议的文件名
        clean_name = self.sanitize_filename(suggested_name)
        
        # 应用命名策略
        if self.naming_strategy == "ai_suggestion":
            new_name = clean_name
        elif self.naming_strategy == "keywords_only":
            # 如果是关键词分析，直接使用
            new_name = clean_name
        elif self.naming_strategy == "topic_date":
            # 主题 + 日期
            date_str = datetime.now().strftime('%Y%m%d')
            new_name = f"{clean_name}_{date_str}"
        else:
            new_name = clean_name
        
        # 添加自定义前缀和后缀
        if self.custom_prefix:
            new_name = f"{self.custom_prefix}_{new_name}"
        
        if self.custom_suffix:
            new_name = f"{new_name}_{self.custom_suffix}"
        
        # 如果启用日期添加
        if self.add_date and self.naming_strategy != "topic_date":
            date_str = datetime.now().strftime('%Y%m%d')
            new_name = f"{new_name}_{date_str}"
        
        # 最终清理
        new_name = self.sanitize_filename(new_name, original_ext)
        
        return new_name + original_ext
    
    def resolve_name_conflict(self, target_path: Path, original_path: Path) -> Path:
        """解决文件名冲突"""
        if not target_path.exists() or target_path.samefile(original_path):
            return target_path
        
        base_name = target_path.stem
        extension = target_path.suffix
        parent_dir = target_path.parent
        
        counter = 1
        while True:
            new_name = f"{base_name}_{counter}{extension}"
            new_path = parent_dir / new_name
            
            if not new_path.exists():
                return new_path
            
            counter += 1
            if counter > 1000:  # 避免无限循环
                raise RuntimeError("无法解决文件名冲突")
    
    async def analyze_and_rename_file(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析单个文件并生成重命名建议"""
        file_path = file_info['path']
        result = {
            'original_path': file_path,
            'original_name': file_path.name,
            'success': False,
            'new_name': None,
            'new_path': None,
            'error': None,
            'analysis_result': None,
            'skipped': False
        }
        
        try:
            # 提取文件内容
            logger.info(f"正在分析文件: {file_path.name}")
            extraction_result = self.content_extractor.extract_content(file_path)
            
            if not extraction_result['success']:
                result['error'] = f"内容提取失败: {extraction_result['error']}"
                result['skipped'] = True
                return result
            
            content = extraction_result['content']
            if not content or len(content.strip()) < 10:
                result['error'] = "文件内容过短，跳过分析"
                result['skipped'] = True
                return result
            
            # 调用 DeepSeek API 分析
            if not self.deepseek_client:
                result['error'] = "DeepSeek API 客户端未初始化"
                return result
            
            analysis_result = self.deepseek_client.analyze_content(content, self.analysis_type)
            result['analysis_result'] = analysis_result
            
            if not analysis_result['success']:
                result['error'] = f"AI 分析失败: {analysis_result.get('error', '未知错误')}"
                return result
            
            # 生成新文件名
            new_filename = self.generate_filename(analysis_result, file_path)
            new_path = file_path.parent / new_filename
            
            # 解决冲突
            final_path = self.resolve_name_conflict(new_path, file_path)
            
            result['success'] = True
            result['new_name'] = final_path.name
            result['new_path'] = final_path
            result['suggested_name'] = analysis_result['suggested_name']
            
            logger.info(f"分析完成: {file_path.name} -> {final_path.name}")
            
        except Exception as e:
            result['error'] = f"处理文件时发生错误: {str(e)}"
            logger.error(f"处理文件失败 {file_path}: {str(e)}")
        
        return result
    
    async def batch_analyze_files(self, files_info: List[Dict[str, Any]], max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """批量分析文件"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_semaphore(file_info):
            async with semaphore:
                return await self.analyze_and_rename_file(file_info)
        
        tasks = [analyze_with_semaphore(file_info) for file_info in files_info]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = {
                    'original_path': files_info[i]['path'],
                    'original_name': files_info[i]['name'],
                    'success': False,
                    'error': f"异步处理异常: {str(result)}",
                    'skipped': False
                }
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def execute_rename(self, rename_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行实际的文件重命名操作"""
        stats = {
            'total': len(rename_results),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        if self.backup_enabled:
            self.create_backup_directory()
        
        for result in rename_results:
            if result['skipped'] or not result['success']:
                stats['skipped'] += 1
                continue
            
            original_path = result['original_path']
            new_path = result['new_path']
            
            try:
                # 备份原文件
                if self.backup_enabled:
                    if not self.backup_file(original_path):
                        stats['failed'] += 1
                        stats['errors'].append((original_path.name, "备份失败"))
                        continue
                
                # 执行重命名
                original_path.rename(new_path)
                stats['success'] += 1
                
                # 记录操作日志
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'original_path': str(original_path),
                    'new_path': str(new_path),
                    'success': True
                }
                self.operation_log.append(log_entry)
                
                logger.info(f"重命名成功: {original_path.name} -> {new_path.name}")
                
            except Exception as e:
                stats['failed'] += 1
                error_msg = f"重命名失败: {str(e)}"
                stats['errors'].append((original_path.name, error_msg))
                
                # 记录失败日志
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'original_path': str(original_path),
                    'new_path': str(new_path),
                    'success': False,
                    'error': error_msg
                }
                self.operation_log.append(log_entry)
                
                logger.error(f"重命名失败 {original_path.name}: {str(e)}")
        
        return stats
    
    def save_operation_log(self) -> str:
        """保存操作日志"""
        if not self.operation_log:
            return ""
        
        log_file = self.base_dir / f"rename_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.operation_log, f, ensure_ascii=False, indent=2)
            
            logger.info(f"操作日志已保存到: {log_file}")
            return str(log_file)
        except Exception as e:
            logger.error(f"保存操作日志失败: {str(e)}")
            return ""
    
    async def process_directory(self, execute_rename: bool = False) -> Dict[str, Any]:
        """处理整个目录的主方法"""
        if not self.base_dir:
            return {'error': '未设置工作目录'}
        
        if not self.deepseek_client:
            return {'error': '未设置 DeepSeek API 密钥'}
        
        try:
            # 扫描文件
            logger.info("正在扫描目录...")
            files_info = self.scan_directory()
            
            if not files_info:
                return {'error': '未找到可处理的文件'}
            
            logger.info(f"找到 {len(files_info)} 个可处理的文件")
            
            # 批量分析文件
            logger.info("正在分析文件内容...")
            analysis_results = await self.batch_analyze_files(files_info)
            
            # 统计分析结果
            successful_analyses = [r for r in analysis_results if r['success']]
            failed_analyses = [r for r in analysis_results if not r['success'] and not r['skipped']]
            skipped_analyses = [r for r in analysis_results if r['skipped']]
            
            result = {
                'total_files': len(files_info),
                'analysis_results': analysis_results,
                'successful_analyses': len(successful_analyses),
                'failed_analyses': len(failed_analyses),
                'skipped_analyses': len(skipped_analyses),
                'rename_stats': None
            }
            
            # 如果需要执行重命名
            if execute_rename and successful_analyses:
                logger.info("正在执行文件重命名...")
                rename_stats = self.execute_rename(analysis_results)
                result['rename_stats'] = rename_stats
                
                # 保存操作日志
                log_file = self.save_operation_log()
                if log_file:
                    result['log_file'] = log_file
            
            return result
            
        except Exception as e:
            logger.error(f"处理目录时发生错误: {str(e)}")
            return {'error': f'处理失败: {str(e)}'}
    
    # 为了向后兼容，添加一些旧版本的方法
    def _discover_file_patterns(self) -> List[Tuple[Tuple[str, str], int]]:
        """发现文件模式（向后兼容）"""
        if not self.base_dir or not self.base_dir.exists():
            return []
        
        patterns = Counter()
        for file_path in self.base_dir.iterdir():
            if file_path.is_file():
                prefix_match = re.match(r"^([^.\w]{1,5}|\w{1,5})", file_path.name)
                if prefix_match:
                    prefix = prefix_match.group(1)
                    ext = file_path.suffix.lower()
                    patterns[(prefix, ext)] += 1
        
        return patterns.most_common(5)
    
    async def rename_files(self) -> Tuple[int, int, List[Tuple[str, str]]]:
        """重命名文件（向后兼容）"""
        result = await self.process_directory(execute_rename=True)
        
        if 'error' in result:
            return 0, 0, [(result['error'], "")]
        
        rename_stats = result.get('rename_stats', {})
        success_count = rename_stats.get('success', 0)
        failed_count = rename_stats.get('failed', 0)
        errors = rename_stats.get('errors', [])
        
        return success_count, failed_count, errors

    async def process_selected_files(self, selected_indices: List[int], execute_rename: bool = False) -> Dict:
        """处理选定的文件
        
        Args:
            selected_indices: 选中的文件索引列表
            execute_rename: 是否执行重命名
        """
        if not self.base_dir or not self.deepseek_client:
            return {"error": "未设置工作目录或API密钥"}
        
        # 获取所有文件信息（需要与前端保持一致的顺序）
        files_info = self.scan_directory()
        
        if not files_info:
            return {"error": "目录中没有支持的文件"}
        
        # 根据索引筛选文件
        selected_files_info = []
        for idx in selected_indices:
            if 0 <= idx < len(files_info):
                selected_files_info.append(files_info[idx])
        
        if not selected_files_info:
            return {"error": "没有有效的选中文件"}
        
        logger.info(f"开始处理 {len(selected_files_info)} 个选中的文件...")
        
        # 批量分析选中的文件
        logger.info("正在分析文件内容...")
        analysis_results = await self.batch_analyze_files(selected_files_info)
        
        # 统计分析结果
        successful_analyses = [r for r in analysis_results if r['success']]
        failed_analyses = [r for r in analysis_results if not r['success'] and not r['skipped']]
        skipped_analyses = [r for r in analysis_results if r['skipped']]
        
        result = {
            'total_files': len(selected_files_info),
            'successful_analyses': len(successful_analyses),
            'failed_analyses': len(failed_analyses),
            'skipped_analyses': len(skipped_analyses),
            'results': analysis_results
        }
        
        # 如果需要执行重命名
        if execute_rename and successful_analyses:
            logger.info("正在执行文件重命名...")
            rename_stats = self.execute_rename(analysis_results)
            result['rename_stats'] = rename_stats
            
            # 保存操作日志
            log_file = self.save_operation_log()
            if log_file:
                result['log_file'] = log_file
        
        return result


# 为了向后兼容，保留原来的类名
class InteractiveFileRenamer(DeepSeekFileRenamer):
    """向后兼容的类名"""
    pass 