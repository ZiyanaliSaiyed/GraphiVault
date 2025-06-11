@echo off
echo.
echo ===============================================
echo    GraphiVault Development Environment Setup
echo ===============================================
echo.

echo [1/5] Checking prerequisites...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

rustc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Rust is not installed or not in PATH
    echo Please install Rust from https://rustup.rs/
    pause
    exit /b 1
)

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org/
    pause
    exit /b 1
)

echo ✓ All prerequisites found!
echo.

echo [2/5] Installing Node.js dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Node.js dependencies
    pause
    exit /b 1
)
echo ✓ Node.js dependencies installed!
echo.

echo [3/5] Installing Python dependencies...
call pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo ✓ Python dependencies installed!
echo.

echo [4/5] Installing Tauri CLI...
call npm install -g @tauri-apps/cli
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Tauri CLI
    pause
    exit /b 1
)
echo ✓ Tauri CLI installed!
echo.

echo [5/5] Verifying setup...
echo Testing frontend build...
call npm run build >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Frontend build test failed - this might be normal for initial setup
) else (
    echo ✓ Frontend builds successfully!
)
echo.

echo ===============================================
echo    Setup Complete! 🎉
echo ===============================================
echo.
echo To start developing:
echo   npm run tauri:dev     - Start full development environment
echo   npm run dev           - Start frontend only
echo   npm run build         - Build for production
echo.
echo For more information, see DEVELOPMENT.md
echo.
pause
