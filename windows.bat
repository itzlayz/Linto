@echo off

cls
color 9

echo 1 - Linto with flet app
echo Anything else - Linto without managers
echo.

set /p choice=Choose option: 
cls

if "%choice%"== "1" (
    echo Starting linto with flet app.
    echo.

    python -m linto --flet
) else (
    echo Starting linto without managers.
    echo.

    python -m linto
)