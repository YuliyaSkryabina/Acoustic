@echo off
chcp 65001 >nul
title Акустик — Проверка расчётов

set "ROOT=%~dp0"
set "VENV=%ROOT%.venv"

echo ╔══════════════════════════════════════════════════════════════╗
echo ║   АКУСТИК — Запуск тестов расчётного ядра (41 тест)        ║
echo ║   Верификация по СП 51.13330.2011 и ГОСТ 31295.2-2005       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

if not exist "%VENV%\Scripts\activate.bat" (
    echo  ОШИБКА: Виртуальное окружение не найдено.
    echo  Сначала запустите УСТАНОВКА.bat
    pause
    exit /b 1
)

call "%VENV%\Scripts\activate.bat"
pip install pytest pytest-asyncio pytest-cov -q

cd "%ROOT%"
echo  Запуск тестов...
echo.
python -m pytest tests\ -v --tb=short

echo.
echo ──────────────────────────────────────────────────
if errorlevel 1 (
    echo  ❌ Некоторые тесты не прошли — см. вывод выше.
) else (
    echo  ✅ Все тесты пройдены успешно!
)
echo.
pause
