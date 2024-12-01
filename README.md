# 🤖 Ollama File Renamer

Effortlessly rename files using local AI - No tokens, No API, No cost!

## ✨ What is This?

A dead-simple Python script that uses Ollama to automatically rename your files based on their content. Perfect for developers, writers, and anyone drowning in messy file names.

## 🚀 Why Use This?

- **Free:** 100% local AI, no external services
- **Simple:** Just run `python rename_files.py path\to\folder`
- **Smart:** AI understands your file content
- **Safe:** Original files saved in `after-rename-to-delete/` directory
- **Fast:** Works with hundreds of files quickly-ish

## 🔧 Requirements

- Python 3.8+
- [Ollama](https://ollama.com/) (Free, local AI)

## 💾 Installation

```bash
# Clone the repository
git clone https://github.com/octrow/ollama-rename-files.git
cd ollama-rename-files

# Install dependencies
pip install -r requirements.txt

# Pull a small language model
ollama pull qwen2.5-coder:7b
```

## 🖥️ Usage

```bash
# Rename files in current directory
python rename_files.py

# Rename files in specific directory
python rename_files.py "C:\path\to\your\folder"
```

## 🤔 How It Works

1. Finds files starting with "новый" and ending with ".txt"
2. Uses local Ollama AI to read file content
3. Generates a smart, descriptive filename
4. Renames the file
5. Moves original file to `after-rename-to-delete/` folder
6. Logs every single action

## 📋 Naming Convention

Creates filenames like:
- `task-fix-backend-resolve-database-connection-issue.txt`
- `doc-update-project-architecture-notes.md`

## 🛡️ What's Protected?

- Original files are never deleted
- Comprehensive logging
- Error-resistant design
- Works with hundreds of files

## 🤝 Contributing

Found a bug? Want a feature? Pull requests are welcome!
