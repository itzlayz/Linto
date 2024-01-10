@echo off

cls
color 9

echo 1 - Linto with flet app
echo 2 - Linto with web manager
echo Anything else - Linto without managers
echo.

set /p choice=Choose option: 
cls

if "%choice%"== "1" (
    echo Starting linto with flet app.
    echo.

    python -m linto --no-web --flet
) else if "%choice%"== "2" (
    echo Starting linto web manager.
    echo.
    
    python -m linto
) else (
    echo Starting linto without managers.
    echo.

    python -m linto --no-web
)