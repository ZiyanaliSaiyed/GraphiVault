@echo off
REM GraphiVault Status Check Script

echo === GraphiVault Status Check ===
echo.

echo Checking for Node.js and npm...
node --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH.
) else (
    for /f "delims=" %%i in ('node --version') do echo Node.js version: %%i
    for /f "delims=" %%i in ('npm --version') do echo npm version: %%i
)
echo.

echo Checking for Rust and cargo...
rustc --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Rust is not installed or not in PATH.
) else (
    for /f "delims=" %%i in ('rustc --version') do echo Rust version: %%i
    for /f "delims=" %%i in ('cargo --version') do echo Cargo version: %%i
)
echo.

echo Checking for Python...
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
) else (
    for /f "delims=" %%i in ('python --version') do echo Python version: %%i
)
echo.

echo Checking for required directories...
if not exist "src" echo WARNING: src directory not found.
if not exist "src-tauri" echo WARNING: src-tauri directory not found.
if not exist "python_backend" echo WARNING: python_backend directory not found.
if not exist "python_backend\tools\diagnostics" echo WARNING: Diagnostics tools directory not found.
if not exist "python_backend\tools\tests" echo WARNING: Tests directory not found.
echo.

echo Checking npm packages...
if not exist "node_modules" (
    echo WARNING: node_modules directory not found. Dependencies may not be installed.
    echo Run 'npm install' to install dependencies.
) else (
    echo Node modules directory found.
)
echo.

echo Checking Python packages...
pip list > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Unable to check Python packages.
) else (
    for /f "skip=2 tokens=1" %%i in ('pip list') do (
        echo Installed: %%i
    )
)
echo.

echo === Status check complete ===
pause
