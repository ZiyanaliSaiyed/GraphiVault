@echo off
REM GraphiVault Python Package Management Script

echo === GraphiVault Python Package Management ===
echo.

:menu
echo Select an option:
echo 1. Install all required Python packages
echo 2. Update all Python packages
echo 3. Export current packages to requirements.txt
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto update
if "%choice%"=="3" goto export
if "%choice%"=="4" goto end

echo Invalid choice. Please try again.
goto menu

:install
echo.
echo Installing Python packages from requirements.txt...
pip install -r requirements.txt
echo.
goto menu

:update
echo.
echo Updating Python packages...
for /f "delims=" %%i in ('pip freeze ^| findstr /v "^-e"') do (
    for /f "delims==" %%j in ("%%i") do (
        echo Updating %%j...
        pip install -U %%j
    )
)
echo.
goto menu

:export
echo.
echo Exporting current Python packages to requirements.txt...
pip freeze > requirements.txt
echo Exported to requirements.txt
echo.
goto menu

:end
echo.
echo === Package management complete ===
echo.
