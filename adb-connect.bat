@echo off
setlocal enabledelayedexpansion

REM Lấy dòng default route (0.0.0.0)
for /f "tokens=3" %%a in ('route print ^| findstr "0.0.0.0"') do (
set IP=%%a
goto :done
)

:done
echo IP tim duoc: %IP%

REM Connect ADB
adb connect %IP%

pause
