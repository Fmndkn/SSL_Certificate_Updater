@echo off
REM SSL Certificate Updater - Dependency Installer for Windows
REM Usage: install_dependencies.bat

echo === SSL Certificate Updater - Dependency Installation ===

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is required but not installed.
    echo Please install Python 3.6 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is required but not installed.
    echo Please install pip for Python.
    pause
    exit /b 1
)

echo Installing dependencies from requirements.txt...

REM Install dependencies
pip install -r requirements.txt

REM Verify installation
python -c "import paramiko; print('✓ Paramiko installed successfully')"
python -c "import cryptography; print('✓ Cryptography installed successfully')"

echo.
echo === Dependencies installed successfully! ===
echo.
echo You can now run the script:
echo   python cert_updater.py
echo.
pause