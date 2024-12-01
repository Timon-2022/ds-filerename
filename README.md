# 🤖 Ollama File Renamer

## Overview

Automate intelligent file renaming using AI-powered content analysis with Ollama (local LLM).

## 📝 Description

A Python script that leverages AI (Ollama) to automatically rename files based on their content, transforming generic filenames into descriptive, meaningful names. Ideal for developers, writers, and knowledge workers managing large document collections.

## Features

- 🧠 **AI-Powered Naming**: Uses Ollama's language models to generate intelligent, context-aware filenames
- 🔍 **Content Analysis**: Reads file content to suggest appropriate, descriptive names
- 📂 **Batch Processing**: Handles renaming multiple files in a single operation
- 🛡️ **Robust Error Handling**: Gracefully manages file system complexities
- 🚦 **Flexible Modes**: Supports both sequential and parallel renaming
- 🗄️ **Preservation**: Moves original files to an "old" directory for backup

## Use Cases

- Many "new 512.txt" files
- Software development project file management
- Research document organization
- Code repository cleanup
- Technical documentation standardization

## Prerequisites

- Python 3.8+
- Ollama
- Ollama model (qwen2.5-coder:7b, llama 3.2, etc)

## Installation

```bash
git clone git@github.com:octrow/ollama-rename-files.git
cd ollama-rename-files
pip install -r requirements.txt
```

## Usage

### Basic Renaming (recommend for ordinary PC)
```bash
python rename_files.py "/path/to/your/directory"
```

### Parallel Processing
```bash
python rename_files.py "/path/to/your/directory" -p 10
```

## Configuration

- Customize renaming patterns
- Modify AI model selection
- Adjust logging preferences

## Example

Before:
- `new 125.txt`

After:
- `issue-fix-backend-data-processing-optimization.txt`

## 🤖 How It Works

1. Scans files matching a pattern (e.g., "новый *.txt")
2. Uses Ollama AI to analyze file content
3. Generates a descriptive filename
4. Renames file and archives original

## 🔍 Naming Convention

`<Type> - <Action> - <Component> - <Short Description>.<Extension>`

- **Type:** task, issue, doc, snippet, review, idea
- **Action:** create, fix, update, review, discuss, complete
- **Component:** backend, frontend, database, etc.

## 🌟 Contributing

Contributions welcome! Easy :)