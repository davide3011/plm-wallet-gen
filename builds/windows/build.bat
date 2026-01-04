@echo off
REM Build script for PLM Wallet Generator Windows executable
REM This creates a single-file .exe with embedded icon

echo ========================================
echo PLM Wallet Generator - Windows Build
echo ========================================
echo.

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo WARNING: Virtual environment is not activated.
    echo It's recommended to activate your venv first:
    echo   From project root: venv\Scripts\activate
    echo.
    choice /C YN /M "Continue anyway"
    if errorlevel 2 exit /b 1
    echo.
)

echo [1/4] Installing build dependencies...
pip install -r requirements-build.txt
if errorlevel 1 (
    echo ERROR: Failed to install build dependencies
    pause
    exit /b 1
)
echo.

echo [2/4] Cleaning previous builds...
cd ..\..
if exist build (
    echo   Removing build\ directory...
    rmdir /s /q build
)
if exist dist (
    echo   Removing dist\ directory...
    rmdir /s /q dist
)
cd builds\windows
echo.

echo [3/4] Building executable with PyInstaller...
echo   This may take a few minutes...
pyinstaller plm-wallet-gen.spec
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo.

echo [4/4] Build complete!
echo.
echo ========================================
echo Executable created at:
echo   ..\..\dist\PLM-Wallet-Generator.exe
echo   (from project root: dist\PLM-Wallet-Generator.exe)
echo.
echo File size: ~50-100 MB (includes all dependencies)
echo.
echo The executable includes:
echo   - GUI application with icon
echo   - All required libraries
echo   - Encrypted wallet support
echo   - Standalone and portable
echo ========================================
echo.

pause
