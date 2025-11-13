# INSTALLATION.md — SecureArchive / TitanCrypt Engine

## 1. Overview

This document provides a clear, step‑by‑step installation guide for SecureArchive across Windows, Linux, and macOS.  
SecureArchive operates fully offline and requires only Python 3.12+ and a minimal dependency set.

<br>

## 2. System Requirements

### 2.1. Supported Operating Systems
- Windows 10 / 11
- macOS (Intel & Apple Silicon)
- Linux (Ubuntu, Debian, Arch, Fedora, etc.)

### 2.2. Python Requirements
- Python **3.12+**
- `pip` and `venv` modules installed

### 2.3. Dependencies
Installed automatically via `requirements.txt`:
- PySide6 (GUI)
- cryptography (AES‑GCM, PBKDF2)
- typing_extensions

<br>

## 3. Installation (Windows)

### 3.1. Verify Python installation
```powershell
python --version
pip --version
```

### 3.2. Create virtual environment
```powershell
python -m venv .venv
```

### 3.3. Activate environment
```powershell
.venv\Scripts\activate
```

### 3.4. Install dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.5. Launch the GUI
```powershell
python securearchive_gui.py
```

### 3.6. Launch the CLI
```powershell
python securearchive_main.py --help
```

<br>

## 4. Installation (Linux)

### 4.1. Install Python
```bash
sudo apt install python3 python3-venv python3-pip
```

### 4.2. Create venv
```bash
python3 -m venv .venv
```

### 4.3. Activate
```bash
source .venv/bin/activate
```

### 4.4. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.5. Run GUI
```bash
python securearchive_gui.py
```

<br>

## 5. Installation (macOS)

### 5.1. Install Python via Homebrew
```bash
brew install python
```

### 5.2. Create & activate venv
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 5.3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5.4. Start GUI
```bash
python securearchive_gui.py
```

<br>

## 6. Common Issues & Troubleshooting

### Issue: *ModuleNotFoundError: No module named 'PySide6'*
Cause: Dependencies not installed in venv.  
Fix:
```bash
pip install PySide6
```

### Issue: *ModuleNotFoundError: No module named 'cryptography'*
Fix:
```bash
pip install cryptography
```

### Issue: Permission denied (Linux/macOS)
Fix:
```bash
chmod +x securearchive_main.py
```

### Issue: "SSL Error" during installation (Windows)
Fix:
```powershell
python -m pip install --upgrade pip setuptools wheel
pip install PySide6 cryptography --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

<br>

## 7. Folder Structure after Installation

```
SecureArchive/
│
├── securearchive/
│   ├── engine.py
│   ├── crypto.py
│   ├── fsutil.py
│   ├── i18n.py
│   ├── errors.py
│   └── __init__.py
│
├── securearchive_gui.py
├── securearchive_main.py
├── requirements.txt
└── LICENSE.md
```

<br>

## 8. Uninstallation

### Windows / Linux / macOS
Deactivate and remove the virtual environment:
```bash
deactivate
rm -rf .venv
```

<br>

## 9. Next Steps

After successful installation, you can:

- Create encrypted SecureArchive containers  
- Extract `.secarc` archives  
- Verify container integrity  
- Rotate passwords securely  

For deeper details, refer to:
- **SECURITY.md**
- **ARCHITECTURE.md**
- **CONTAINER_FORMAT.md**
