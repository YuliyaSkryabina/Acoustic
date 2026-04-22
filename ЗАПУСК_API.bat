@echo off
chcp 65001 >nul
title Акустик — Сервер расчётов (API)

set "ROOT=%~dp0"
set "VENV=%ROOT%.venv"

echo ╔══════════════════════════════════════════════════════════════╗
echo ║   АКУСТИК — Запуск сервера расчётов                         ║
echo ║   Адрес: http://localhost:8765                              ║
echo ║   Документация API: http://localhost:8765/docs              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Проверка виртуального окружения
if not exist "%VENV%\Scripts\activate.bat" (
    echo  ОШИБКА: Виртуальное окружение не найдено.
    echo  Сначала запустите УСТАНОВКА.bat
    echo.
    pause
    exit /b 1
)

call "%VENV%\Scripts\activate.bat"

echo  Запуск API-сервера...
echo  Для остановки нажмите Ctrl+C
echo.

cd "%ROOT%"
python -m uvicorn api.main:app --host 0.0.0.0 --port 8765 --reload

pause
