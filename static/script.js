// 全局状态管理
const AppState = {
    hasApiKey: false,
    hasDirectory: false,
    currentConfig: {},
    scannedFiles: [],
    previewResults: []
};

// 工具函数
const Utils = {
    // 显示加载状态
    showLoading(text = '正在处理...') {
        const overlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');
        loadingText.textContent = text;
        overlay.style.display = 'flex';
    },

    // 隐藏加载状态
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = 'none';
    },

    // 显示消息提示
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fas ${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        container.appendChild(toast);
        
        // 自动移除
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    },

    getToastIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    },

    // 格式化文件大小
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // 更新按钮状态
    updateButtonStates() {
        const scanBtn = document.getElementById('scan-files-btn');
        const previewBtn = document.getElementById('preview-btn');
        const executeBtn = document.getElementById('execute-btn');

        // 扫描按钮：需要API密钥和目录
        scanBtn.disabled = !(AppState.hasApiKey && AppState.hasDirectory);

        // 预览按钮：需要扫描到文件
        previewBtn.disabled = AppState.scannedFiles.length === 0;

        // 执行按钮：需要预览结果且有选中的文件
        const selectedFiles = this.getSelectedFiles();
        executeBtn.disabled = AppState.previewResults.length === 0 || selectedFiles.length === 0;
    },

    // 获取选中的文件
    getSelectedFiles() {
        const checkboxes = document.querySelectorAll('.file-select:checked');
        return Array.from(checkboxes).map(cb => parseInt(cb.dataset.index));
    },

    // 全选/全不选
    selectAllFiles(select) {
        const checkboxes = document.querySelectorAll('.file-select');
        checkboxes.forEach(cb => {
            cb.checked = select;
        });
        this.updateButtonStates();
    },

    // 反选
    toggleSelection() {
        const checkboxes = document.querySelectorAll('.file-select');
        checkboxes.forEach(cb => {
            cb.checked = !cb.checked;
        });
        this.updateButtonStates();
    }
};

// API 调用函数
const API = {
    async call(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`API call failed: ${url}`, error);
            throw error;
        }
    },

    async setApiKey(apiKey) {
        return await this.call('/set_api_key', {
            method: 'POST',
            body: JSON.stringify({ api_key: apiKey })
        });
    },

    async setDirectory(directory) {
        return await this.call('/set_directory', {
            method: 'POST',
            body: JSON.stringify({ directory })
          });
    },

    async scanFiles() {
        return await this.call('/scan_files');
    },

    async setConfig(config) {
        return await this.call('/set_config', {
            method: 'POST',
            body: JSON.stringify(config)
        });
    },

    async previewRename() {
        return await this.call('/preview_rename', {
            method: 'POST'
        });
    },

    async executeRename(selectedFiles = []) {
        return await this.call('/execute_rename', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                selected_files: selectedFiles
            })
        });
    },

    async getConfig() {
        return await this.call('/get_config');
    },

    async chooseDirectory() {
        return await this.call('/choose_directory', {
            method: 'POST'
        });
    }
};

// UI 更新函数
const UI = {
    updateApiStatus(success, message = '') {
        const status = document.getElementById('api-status');
        if (success) {
            status.className = 'api-status success';
            status.innerHTML = '<i class="fas fa-check-circle"></i> API 密钥验证成功';
            AppState.hasApiKey = true;
          } else {
            status.className = 'api-status';
            status.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message || '请设置 API 密钥'}`;
            AppState.hasApiKey = false;
        }
        Utils.updateButtonStates();
    },

    updateDirectoryStatus(success, directory = '') {
        const status = document.getElementById('directory-status');
        if (success) {
            status.className = 'directory-status success';
            status.innerHTML = `<i class="fas fa-check-circle"></i> 工作目录：${directory}`;
            AppState.hasDirectory = true;
        } else {
            status.className = 'directory-status';
            status.innerHTML = '<i class="fas fa-info-circle"></i> 请选择工作目录';
            AppState.hasDirectory = false;
        }
        Utils.updateButtonStates();
    },

    displayFiles(files) {
        const container = document.getElementById('files-container');
        const stats = document.getElementById('scan-stats');
        
        if (files.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <p>未找到支持的文件</p>
                </div>
            `;
            stats.textContent = '';
            return;
        }

        stats.textContent = `找到 ${files.length} 个可处理的文件`;
        
        const filesByType = {};
        files.forEach(file => {
            if (!filesByType[file.type]) {
                filesByType[file.type] = [];
            }
            filesByType[file.type].push(file);
        });

        let html = '';
        Object.keys(filesByType).forEach(type => {
            html += `<div class="file-type-group">
                <h4>${type} (${filesByType[type].length} 个文件)</h4>`;
            
            filesByType[type].forEach(file => {
                html += `
                    <div class="file-item">
                        <div class="file-info">
                            <div class="file-name">${file.name}</div>
                            <div class="file-details">
                                ${Utils.formatFileSize(file.size)} • ${file.relative_path}
                            </div>
                        </div>
                        <div class="file-type">${file.extension}</div>
                    </div>
                `;
            });
            html += '</div>';
        });

        container.innerHTML = html;
        AppState.scannedFiles = files;
        Utils.updateButtonStates();
    },

    displayPreview(results) {
        const container = document.getElementById('preview-container');
        
        if (results.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>没有可预览的结果</p>
                </div>
            `;
            return;
        }

        // 添加批量控制按钮
        let html = `
            <div class="batch-controls">
                <button class="btn btn-secondary" onclick="Utils.selectAllFiles(true)">
                    <i class="fas fa-check-square"></i> 全选
                </button>
                <button class="btn btn-secondary" onclick="Utils.selectAllFiles(false)">
                    <i class="fas fa-square"></i> 全不选
                </button>
                <button class="btn btn-secondary" onclick="Utils.toggleSelection()">
                    <i class="fas fa-exchange-alt"></i> 反选
                </button>
            </div>
        `;

        results.forEach((result, index) => {
            const statusClass = result.success ? 'success' : (result.skipped ? 'skipped' : 'error');
            const statusIcon = result.success ? 'fa-check-circle' : (result.skipped ? 'fa-minus-circle' : 'fa-exclamation-circle');
            const isSelectable = result.success && result.new_name;
            
            html += `
                <div class="preview-item ${statusClass}" data-file-index="${index}">
                    ${isSelectable ? `
                        <div class="file-checkbox">
                            <input type="checkbox" id="file-${index}" class="file-select" 
                                   data-index="${index}" ${isSelectable ? 'checked' : ''}>
                            <label for="file-${index}">选择此文件进行重命名</label>
                        </div>
                    ` : ''}
                    <div class="preview-header">
                        <i class="fas ${statusIcon}"></i>
                        <span>${result.success ? '成功' : (result.skipped ? '跳过' : '失败')}</span>
                    </div>
                    <div class="preview-names">
                        <div class="original-name">${result.original_name}</div>
                        <div class="arrow"><i class="fas fa-arrow-right"></i></div>
                        <div class="new-name">${result.new_name || '无变化'}</div>
                    </div>
                    ${result.error ? `<div class="error-message" style="color: #e53e3e; font-size: 12px; margin-top: 8px;">${result.error}</div>` : ''}
                    ${result.suggested_name ? `<div class="suggested-name" style="color: #38a169; font-size: 12px; margin-top: 8px;">AI 建议：${result.suggested_name}</div>` : ''}
                </div>
            `;
        });

        container.innerHTML = html;
        AppState.previewResults = results;
        
        // 绑定复选框事件监听器
        const checkboxes = container.querySelectorAll('.file-select');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                Utils.updateButtonStates();
            });
        });
        
        Utils.updateButtonStates();
    },

    displayResults(data) {
        const panel = document.getElementById('results-panel');
        const container = document.getElementById('results-container');
        
        panel.style.display = 'block';
        
        const html = `
            <div class="result-stats">
                <div class="stat-card">
                    <div class="stat-number">${data.total_files}</div>
                    <div class="stat-label">总文件数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${data.successful_analyses}</div>
                    <div class="stat-label">分析成功</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${data.rename_success || 0}</div>
                    <div class="stat-label">重命名成功</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${data.rename_failed || 0}</div>
                    <div class="stat-label">重命名失败</div>
                </div>
            </div>
            ${data.errors && data.errors.length > 0 ? `
                <div class="error-list">
                    <h4>错误详情：</h4>
                    ${data.errors.map(([file, error]) => `<div class="error-item">${file}: ${error}</div>`).join('')}
                </div>
            ` : ''}
            ${data.log_file ? `
                <div class="log-info">
                    <i class="fas fa-file-alt"></i> 操作日志已保存到：${data.log_file}
                </div>
            ` : ''}
        `;
        
        container.innerHTML = html;
        container.scrollIntoView({ behavior: 'smooth' });
    },

    loadConfig(config) {
        document.getElementById('analysis-type').value = config.analysis_type || 'summary';
        document.getElementById('naming-strategy').value = config.naming_strategy || 'ai_suggestion';
        document.getElementById('custom-prefix').value = config.custom_prefix || '';
        document.getElementById('custom-suffix').value = config.custom_suffix || '';
        document.getElementById('add-date').checked = config.add_date || false;
        document.getElementById('backup-enabled').checked = config.backup_enabled !== false;
        
        if (config.directory) {
            document.getElementById('directory').value = config.directory;
            this.updateDirectoryStatus(true, config.directory);
        }
        
        this.updateApiStatus(config.has_api_key);
        
        AppState.currentConfig = config;
    }
};

// 事件处理函数
const EventHandlers = {
    async handleSetApiKey() {
        const apiKey = document.getElementById('api-key').value.trim();
        
        if (!apiKey) {
            Utils.showToast('请输入 API 密钥', 'error');
            return;
        }

        try {
            Utils.showLoading('验证 API 密钥...');
            const result = await API.setApiKey(apiKey);
            UI.updateApiStatus(true);
            Utils.showToast(result.message, 'success');
            
            // 清空密钥输入框（安全考虑）
            document.getElementById('api-key').value = '';
        } catch (error) {
            UI.updateApiStatus(false, error.message);
            Utils.showToast(`API 密钥设置失败: ${error.message}`, 'error');
        } finally {
            Utils.hideLoading();
        }
    },

    async handleChooseDirectory() {
        try {
            Utils.showLoading('打开文件夹选择对话框...');
            
            // 首先尝试使用后端的tkinter文件夹选择
            try {
                const result = await API.chooseDirectory();
                if (result.success && result.directory) {
                    document.getElementById('directory').value = result.directory;
                    Utils.hideLoading();
                    await this.handleSetDirectory(result.directory);
                    return;
                }
            } catch (apiError) {
                console.log('后端API选择失败，尝试浏览器API:', apiError);
            }
            
            // 如果后端API失败，尝试现代浏览器的文件夹选择API
            if (window.showDirectoryPicker) {
                try {
                    const dirHandle = await window.showDirectoryPicker();
                    // 尝试获取完整路径（如果可能）
                    let directory = dirHandle.name;
                    
                    // 对于现代浏览器API，我们只能获取到文件夹名，提示用户输入完整路径
                    document.getElementById('directory').value = directory;
                    Utils.hideLoading();
                    Utils.showToast('浏览器安全限制，请手动输入完整路径或使用系统文件夹选择', 'warning');
                    document.getElementById('directory').focus();
                    return;
                } catch (browserError) {
                    console.log('浏览器API选择失败:', browserError);
                }
            }
            
            // 如果都失败了，提示手动输入
            Utils.hideLoading();
            Utils.showToast('请手动输入完整的目录路径，例如：C:\\Users\\用户名\\Documents', 'info');
            document.getElementById('directory').focus();
            document.getElementById('directory').placeholder = '例如：C:\\Users\\用户名\\Documents';
            
        } catch (error) {
            Utils.hideLoading();
            console.error('选择目录错误:', error);
            Utils.showToast(`选择目录失败: ${error.message}`, 'error');
        }
    },

    async handleSetDirectory(directory = null) {
        const dir = directory || document.getElementById('directory').value.trim();
        
        if (!dir) {
            Utils.showToast('请输入目录路径', 'error');
          return;
        }

        try {
            Utils.showLoading('设置工作目录...');
            const result = await API.setDirectory(dir);
            UI.updateDirectoryStatus(true, result.directory);
            Utils.showToast(result.message, 'success');
        } catch (error) {
            UI.updateDirectoryStatus(false);
            Utils.showToast(`目录设置失败: ${error.message}`, 'error');
        } finally {
            Utils.hideLoading();
        }
    },

    async handleScanFiles() {
        try {
            Utils.showLoading('扫描文件中...');
            const result = await API.scanFiles();
            UI.displayFiles(result.files);
            Utils.showToast(`扫描完成，找到 ${result.total_files} 个文件`, 'success');
        } catch (error) {
            Utils.showToast(`文件扫描失败: ${error.message}`, 'error');
        } finally {
            Utils.hideLoading();
        }
    },

    async handleSaveConfig() {
        const config = {
            analysis_type: document.getElementById('analysis-type').value,
            naming_strategy: document.getElementById('naming-strategy').value,
            custom_prefix: document.getElementById('custom-prefix').value.trim(),
            custom_suffix: document.getElementById('custom-suffix').value.trim(),
            add_date: document.getElementById('add-date').checked,
            backup_enabled: document.getElementById('backup-enabled').checked,
            max_filename_length: 100,
            exclude_patterns: []
        };

        try {
            Utils.showLoading('保存配置...');
            const result = await API.setConfig(config);
            AppState.currentConfig = { ...AppState.currentConfig, ...config };
            Utils.showToast(result.message, 'success');
        } catch (error) {
            Utils.showToast(`配置保存失败: ${error.message}`, 'error');
        } finally {
            Utils.hideLoading();
        }
    },

    async handlePreviewRename() {
        try {
            Utils.showLoading('AI 分析文件内容中...');
            const result = await API.previewRename();
            UI.displayPreview(result.preview_results);
            Utils.showToast(`预览完成：${result.successful_analyses} 个文件分析成功`, 'success');
        } catch (error) {
            Utils.showToast(`预览失败: ${error.message}`, 'error');
        } finally {
            Utils.hideLoading();
        }
    },

    async handleExecuteRename() {
        if (AppState.previewResults.length === 0) {
            Utils.showToast('请先预览重命名结果', 'warning');
            return;
        }

        const selectedFiles = Utils.getSelectedFiles();
        if (selectedFiles.length === 0) {
            Utils.showToast('请至少选择一个文件进行重命名', 'warning');
            return;
        }

        if (!confirm(`确定要重命名选中的 ${selectedFiles.length} 个文件吗？此操作不可撤销（除非启用了备份）。`)) {
            return;
        }

        try {
            Utils.showLoading('执行文件重命名中...');
            const result = await API.executeRename(selectedFiles);
            UI.displayResults(result);
            Utils.showToast(`重命名完成：${result.rename_success || 0} 个文件成功`, 'success');
            
            // 清空预览结果，需要重新扫描
            AppState.previewResults = [];
            AppState.scannedFiles = [];
            document.getElementById('files-container').innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <p>请重新扫描文件</p>
                </div>
            `;
            document.getElementById('preview-container').innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-magic"></i>
                    <p>点击"预览重命名"查看 AI 分析结果</p>
                </div>
            `;
            Utils.updateButtonStates();
        } catch (error) {
            Utils.showToast(`重命名失败: ${error.message}`, 'error');
        } finally {
            Utils.hideLoading();
        }
    }
};

// 初始化应用
async function initApp() {
    try {
        // 加载当前配置
        const config = await API.getConfig();
        UI.loadConfig(config);
        
        Utils.showToast('应用初始化完成', 'success');
    } catch (error) {
        console.error('应用初始化失败:', error);
        Utils.showToast('应用初始化失败，请刷新页面重试', 'error');
    }
}

// 绑定事件监听器
function bindEventListeners() {
    // API 密钥设置
    document.getElementById('set-api-key-btn').addEventListener('click', () => EventHandlers.handleSetApiKey());
    
    // 目录选择
    document.getElementById('choose-dir-btn').addEventListener('click', () => EventHandlers.handleChooseDirectory());
    
    // 目录输入回车
    document.getElementById('directory').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            EventHandlers.handleSetDirectory();
        }
    });
    
    // API 密钥输入回车
    document.getElementById('api-key').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            EventHandlers.handleSetApiKey();
        }
    });
    
    // 配置保存
    document.getElementById('save-config-btn').addEventListener('click', () => EventHandlers.handleSaveConfig());
    
    // 文件扫描
    document.getElementById('scan-files-btn').addEventListener('click', () => EventHandlers.handleScanFiles());
    
    // 预览重命名
    document.getElementById('preview-btn').addEventListener('click', () => EventHandlers.handlePreviewRename());
    
    // 执行重命名
    document.getElementById('execute-btn').addEventListener('click', () => EventHandlers.handleExecuteRename());
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    bindEventListeners();
    initApp();
});

// 兼容旧版本的函数（如果需要）
async function chooseDirectory() {
    return EventHandlers.handleChooseDirectory();
}