# DeepSeek 智能文件重命名工具 v1.0.0

> 基于DeepSeek API的智能文件重命名工具，支持多种文件格式的内容分析和智能重命名
> 
> **作者**: Timon  
> **版本**: 1.0.0 Final

## 🌟 功能特色

- 🤖 **AI智能分析** - 使用DeepSeek API分析文件内容并生成语义化文件名
- 📁 **多格式支持** - 支持txt、md、doc、docx、pdf、xlsx、xls、pptx、ppt等格式
- 🖥️ **现代化界面** - 美观的Web图形界面，支持中文
- ✅ **选择性重命名** - 支持选择特定文件进行重命名，避免误操作
- ⚡ **批量处理** - 异步处理，支持批量文件重命名
- 🔒 **安全备份** - 自动备份原文件名，可恢复
- 🎯 **智能冲突处理** - 自动处理文件名冲突

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+ (推荐使用 Python 3.11)
- **操作系统**: Windows 10/11
- **DeepSeek API密钥**: 需要有效的DeepSeek API密钥

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd ollama-rename-files
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动应用**
   ```bash
   # 方式1：使用批处理文件（推荐）
   双击运行 "启动应用.bat"
   
   # 方式2：使用Python命令
   python app_final.py
   ```

4. **访问界面**
   - 浏览器会自动打开：http://localhost:5000
   - 如未自动打开，请手动访问上述地址

## 📖 使用指南

### 基本使用流程

1. **设置API密钥**
   - 在配置面板中输入您的DeepSeek API密钥
   - 点击"设置API密钥"按钮保存

2. **选择工作目录**
   - 点击"选择目录"按钮选择要处理的文件夹
   - 或手动输入完整的目录路径

3. **配置重命名规则**
   - 选择分析类型：摘要、关键词、主题
   - 设置文件名前缀、后缀（可选）
   - 启用/禁用日期后缀和备份功能

4. **扫描文件**
   - 点击"开始扫描"查看目录中的可处理文件

5. **预览重命名**
   - 点击"预览重命名"查看AI分析结果
   - 查看建议的新文件名

6. **选择文件**
   - 使用复选框选择要重命名的文件
   - 使用"全选"、"全不选"、"反选"按钮快速控制

7. **执行重命名**
   - 点击"执行重命名"完成操作
   - 查看操作结果和统计信息

### 高级功能

- **选择性重命名**: 可以选择部分文件进行重命名，避免处理不需要的文件
- **批量控制**: 提供全选、全不选、反选功能，快速管理文件选择
- **冲突处理**: 自动检测并处理文件名冲突，确保重命名安全
- **操作日志**: 自动保存重命名操作日志，便于追踪和恢复

## 🔧 配置说明

### 配置文件 (config.json)

项目使用 `config.json` 文件管理所有配置，包括：

- **API配置**: DeepSeek API相关设置
- **文件处理**: 支持的文件格式和处理规则
- **界面设置**: UI语言和主题配置
- **服务器设置**: 本地服务器端口和主机配置

### 环境变量

可以通过环境变量覆盖部分配置：

- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `SERVER_PORT`: 服务器端口（默认5000）
- `SERVER_HOST`: 服务器主机（默认127.0.0.1）

## 📁 项目结构

```
ollama-rename-files/
├── 核心模块 (final版本)
│   ├── app_final.py              # 应用启动入口
│   ├── api_final.py              # Flask Web API
│   ├── rename_files_final.py     # 文件重命名核心逻辑
│   ├── deepseek_client_final.py  # DeepSeek API客户端
│   └── file_extractor_final.py   # 文件内容提取器
├── 前端资源
│   ├── templates/
│   │   └── index.html            # 主页面模板
│   └── static/
│       ├── styles.css            # 样式文件
│       └── script.js             # 前端逻辑
├── 配置文件
│   ├── config.json               # 项目配置
│   └── requirements.txt          # Python依赖
├── 启动脚本
│   └── 启动应用.bat              # Windows启动脚本
└── 文档
    ├── README_final.md           # 使用说明
    └── development_log.md        # 开发日志
```

## 🛠️ 技术架构

### 后端技术栈

- **Python 3.11+**: 主要开发语言
- **Flask**: Web框架，提供API服务
- **DeepSeek API**: AI内容分析服务
- **asyncio**: 异步处理，提高性能
- **文件处理库**: 
  - `python-docx`: Word文档处理
  - `PyPDF2`: PDF文档处理
  - `openpyxl`: Excel文档处理
  - `python-pptx`: PowerPoint文档处理

### 前端技术栈

- **HTML5 + CSS3 + JavaScript**: 基础前端技术
- **响应式设计**: 适配不同屏幕尺寸
- **现代浏览器API**: 文件系统访问等
- **Font Awesome**: 图标库

## 📋 API文档

### 主要API端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 主页面 |
| `/set_api_key` | POST | 设置DeepSeek API密钥 |
| `/choose_directory` | POST | 选择工作目录 |
| `/set_directory` | POST | 设置工作目录 |
| `/scan_files` | GET | 扫描目录文件 |
| `/set_config` | POST | 保存配置 |
| `/preview_rename` | POST | 预览重命名结果 |
| `/execute_rename` | POST | 执行文件重命名 |
| `/get_config` | GET | 获取当前配置 |

## 🔍 故障排除

### 常见问题

1. **服务器无法启动**
   - 检查Python环境是否正确安装
   - 确认依赖包已正确安装
   - 检查端口5000是否被占用

2. **API密钥验证失败**
   - 确认DeepSeek API密钥有效性
   - 检查网络连接
   - 验证API配额是否充足

3. **文件分析失败**
   - 检查文件格式是否支持
   - 确认文件没有损坏
   - 验证文件大小是否超限

4. **重命名操作失败**
   - 检查文件是否被其他程序占用
   - 确认目标目录有写入权限
   - 验证新文件名的合法性

### 日志查看

- **应用日志**: 在终端/命令提示符中查看实时日志
- **操作日志**: 每次重命名操作会生成JSON格式的详细日志
- **错误信息**: 界面会显示详细的错误提示

## 🤝 贡献指南

欢迎提交Issues和Pull Requests来改进项目：

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- **作者**: Timon
- **项目**: DeepSeek智能文件重命名工具
- **版本**: v1.0.0

---

⭐ 如果这个项目对您有帮助，请给个Star支持一下！ 