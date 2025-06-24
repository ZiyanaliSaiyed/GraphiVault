@echo off
REM Quick Fix for GraphiVault CryptoController

echo GraphiVault CryptoController Quick Fix
echo =====================================
echo.

set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%..\

echo Running quick fix...
python "%SCRIPT_DIR%quick_fix.py"

echo.
echo Fix complete! Your vault should now work with the test123 password.
echo.

pause
