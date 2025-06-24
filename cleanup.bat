@echo off
REM GraphiVault Project Cleanup Script

echo === GraphiVault Project Cleanup ===
echo.

echo Cleaning Python cache files...
REM Clean all pycache directories
for /d /r ".\python_backend" %%i in (__pycache__) do (
  if exist "%%i" (
    echo Removing: %%i
    rd /s /q "%%i"
  )
)

echo Cleaning temporary files...
REM Clean any temp files or backup files
for /r "." %%i in (*.bak *.tmp *.pyc *.log) do (
  if exist "%%i" (
    echo Removing: %%i
    del "%%i"
  )
)

echo.
echo === Cleaning complete ===
pause
