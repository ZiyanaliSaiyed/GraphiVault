@echo off
REM GraphiVault Diagnostics Runner

echo GraphiVault Backend Diagnostics
echo ============================
echo.

REM Set paths
set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%..\
set VAULT_PATH=%SCRIPT_DIR%..\..\test_vault

REM Ensure we're using the correct Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Python not found in PATH. Please install Python or add it to PATH.
  exit /b 1
)

echo Using Python:
python --version
echo.

echo 1. Run Vault Validator
echo 2. Run Backend Tests
echo 3. Run All Diagnostics
echo 4. Fix CryptoController
echo 5. Create Test Vault Stubs
echo 6. Quick Fix and Test
echo 0. Exit
echo.

set /p choice=Enter your choice (0-6): 

if "%choice%"=="1" (
  echo Running Vault Validator...
  python run_diagnostics.py --test-mode validate --vault-path "%VAULT_PATH%" --verbose
) else if "%choice%"=="2" (
  echo Running Backend Tests...
  python run_diagnostics.py --test-mode backend --vault-path "%VAULT_PATH%" --verbose
) else if "%choice%"=="3" (
  echo Running All Diagnostics...
  python run_diagnostics.py --test-mode all --vault-path "%VAULT_PATH%" --verbose
) else if "%choice%"=="4" (
  echo Fixing CryptoController...
  python fix_crypto.py --fix-crypto --verbose
) else if "%choice%"=="5" (
  echo Creating Test Vault Stubs...
  python fix_crypto.py --create-stubs --vault-path "%VAULT_PATH%" --verbose
) else if "%choice%"=="6" (
  echo Quick Fix and Test...
  echo 1. Fixing CryptoController...
  python fix_crypto.py --fix-crypto --verbose
  echo.
  echo 2. Creating Test Vault Stubs...
  python fix_crypto.py --create-stubs --vault-path "%VAULT_PATH%" --verbose
  echo.
  echo 3. Running All Diagnostics...
  python run_diagnostics.py --test-mode all --vault-path "%VAULT_PATH%" --verbose
) else if "%choice%"=="0" (
  echo Exiting...
  exit /b 0
) else (
  echo Invalid choice. Exiting.
  exit /b 1
)

pause
