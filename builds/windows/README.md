# Windows Build Guide - PLM Wallet Generator

This directory contains scripts and configurations to build a standalone Windows executable (.exe) for the PLM Wallet Generator.

**Note**: This build process must be run **on Windows** to create Windows executables.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Build Process](#build-process)
- [Build Output](#build-output)
- [Troubleshooting](#troubleshooting)
- [Distribution](#distribution)
- [Security Notes](#security-notes)

## Prerequisites

| Requirement | Details |
|------------|---------|
| **Operating System** | Windows 10 or Windows 11 |
| **Python Version** | 3.8 or higher |
| **Virtual Environment** | Activated |
| **Dependencies** | `pip install -r requirements.txt` |

## Build Process

### Option 1: Automated Build (Recommended)

1. **Activate the virtual environment**:
   ```powershell
   # PowerShell
   .\venv\Scripts\Activate.ps1

   # Command Prompt (cmd)
   venv\Scripts\activate
   ```

2. **Navigate and run**:
   ```bash
   cd builds\windows
   .\build.bat
   ```

3. **Wait** (2-5 minutes)

4. **Get executable**: `../../dist/PLM-Wallet-Generator.exe`

### Option 2: Manual Build

For advanced users who want more control:

1. **Navigate to this directory**:
   ```bash
   cd builds\windows
   ```

2. **Install PyInstaller**:
   ```bash
   pip install -r requirements-build.txt
   ```

3. **Clean previous builds** (optional but recommended):
   ```bash
   # Navigate to project root
   cd ..\..
   rmdir /s /q build
   rmdir /s /q dist
   cd builds\windows
   ```

4. **Run PyInstaller**:
   ```bash
   pyinstaller plm-wallet-gen.spec
   ```

5. **The executable will be created at**:
   ```
   ../../dist/PLM-Wallet-Generator.exe
   ```

## Build Output

### What You Get

| Property | Details |
|----------|---------|
| **Filename** | `PLM-Wallet-Generator.exe` |
| **Size** | ~50 MB (includes all dependencies) |
| **Type** | Standalone executable (no installation required) |
| **Portability** | Fully portable - copy and run |

### Build Artifacts

The build process creates the following directory structure (at project root):

```
plm-wallet-gen/
├── build/              # Temporary build files (can be deleted)
└── dist/               # Contains the final executable
    └── PLM-Wallet-Generator.exe
```

## Troubleshooting

### Common Errors

**Error: "ModuleNotFoundError"**
- **Fix**: Add missing module to `hiddenimports` in `plm-wallet-gen.spec`
  ```python
  hiddenimports=[
      'gui.app',
      'missing_module_name',  # Add here
  ],
  ```

**Error: "Failed to execute script"**
- **Fix**: Enable console to see error
  1. Change `console=False` to `console=True` in spec file
  2. Rebuild and run to see error message
  3. Fix issue, restore `console=False`

**Error: "Icon file not found"**
- **Fix**: Verify icon exists: `dir ..\..\src\gui\icons\icon.ico`

**Error: "Permission Denied"**
- **Fix**: Close running app, delete manually:
  ```bash
  cd ..\..
  rmdir /s /q build dist
  ```

**Virtual Environment Not Activated**
- **Fix**: Activate venv and verify:
  ```bash
  .\venv\Scripts\Activate.ps1
  python --version
  ```

## Distribution

### Testing Checklist

Before distributing:
- Executable launches without errors
- Icon displays correctly (Explorer, taskbar, window)
- Generate/save/load wallet functions work
- All GUI features respond

### User Requirements

**None.** The executable is fully standalone:
- No Python required
- No dependencies required
- No installation required
- Portable (USB ready)

## Security Notes

**IMPORTANT**: The executable is **NOT digitally signed**

**What this means**:
- Windows SmartScreen will show a security warning
- Users must click "More info" → "Run anyway"
- This is normal for unsigned executables

**For end users**:
- Download only from official sources
- Run antivirus scan if concerned
- The app is safe (source code is open and auditable)

## Advanced Configuration

Edit `plm-wallet-gen.spec` to customize build:

| Parameter | Purpose |
|-----------|---------|
| `name` | Executable filename |
| `icon` | Icon file path |
| `console` | Show/hide console |
| `upx` | Enable compression |

See [PyInstaller documentation](https://pyinstaller.org/en/stable/) for advanced options.
