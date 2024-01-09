@echo off

cls
color 9

echo 1 - Linto with flet app
echo 2 - Linto without managers
echo Anything else - Linto with web manager
echo.

set /p choice=Choose option: 
cls

if "%choice%"== "1" (
    echo Starting linto with flet app.
    echo.

    python -m linto --no-web --flet
) else if "%choice%"== "2" (
    echo Starting linto without managers.
    echo.
    
    python -m linto --no-web
) else (
    echo Starting linto with web.
    echo.
    
    python -m linto
)