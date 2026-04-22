@echo off
chcp 65001 >nul
title Акустик — Первоначальная установка

echo ╔══════════════════════════════════════════════════════════════╗
echo ║          АКУСТИК — Установка и настройка                    ║
echo ║          Расчёт уровней звука (СП 51, СанПиН)               ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Определяем папку скрипта (корень проекта)
set "ROOT=%~dp0"
set "VENV=%ROOT%.venv"

:: ─── Проверка Python ───────────────────────────────────────────
echo [1/5] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ОШИБКА: Python не найден!
    echo  Скачайте и установите Python 3.10+ с сайта: https://www.python.org/downloads/
    echo  При установке ОБЯЗАТЕЛЬНО поставьте галочку "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYVER=%%i
echo  ✅ Найден: %PYVER%
echo.

:: ─── Создание виртуального окружения ──────────────────────────
echo [2/5] Создание виртуального окружения Python...
if exist "%VENV%" (
    echo  ℹ️  Виртуальное окружение уже существует, пропускаю...
) else (
    python -m venv "%VENV%"
    if errorlevel 1 (
        echo  ОШИБКА при создании виртуального окружения!
        pause
        exit /b 1
    )
    echo  ✅ Создано: .venv
)
echo.

:: ─── Установка Python-зависимостей ────────────────────────────
echo [3/5] Установка Python-зависимостей (может занять 2-5 минут)...
echo  Устанавливаются: fastapi, uvicorn, numpy, scipy, matplotlib,
echo  shapely, geopandas, python-docx, reportlab, mcp...
echo.
call "%VENV%\Scripts\activate.bat"
pip install --upgrade pip -q
pip install -r "%ROOT%requirements.txt" -q
if errorlevel 1 (
    echo.
    echo  ОШИБКА при установке зависимостей!
    echo  Проверьте подключение к интернету и повторите попытку.
    pause
    exit /b 1
)
echo  ✅ Python-зависимости установлены
echo.

:: ─── Проверка Node.js (для Electron UI) ───────────────────────
echo [4/5] Проверка Node.js (для графического интерфейса)...
node --version >nul 2>&1
if errorlevel 1 (
    echo  ⚠️  Node.js не найден.
    echo     Графический интерфейс (Electron) недоступен.
    echo     Расчётный API и CLI работают без Node.js.
    echo     Скачать Node.js: https://nodejs.org/  (версия 20 LTS)
    echo.
) else (
    for /f "tokens=*" %%i in ('node --version') do set NODEVER=%%i
    echo  ✅ Найден Node.js %NODEVER%
    echo.
    echo [5/5] Установка Node.js-зависимостей для Electron...
    cd "%ROOT%electron"
    npm install -q
    if errorlevel 1 (
        echo  ⚠️  Ошибка npm install. Графический интерфейс недоступен.
    ) else (
        echo  ✅ Node.js-зависимости установлены
    )
    cd "%ROOT%"
)
echo.

:: ─── Итог ─────────────────────────────────────────────────────
echo ╔══════════════════════════════════════════════════════════════╗
echo ║   ✅ УСТАНОВКА ЗАВЕРШЕНА                                    ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                              ║
echo ║   Для запуска используйте:                                   ║
echo ║                                                              ║
echo ║   ЗАПУСК_API.bat       — запуск сервера расчётов            ║
echo ║   ЗАПУСК_Акустик.bat   — полный запуск с интерфейсом       ║
echo ║   ТЕСТЫ.bat            — проверка корректности расчётов     ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
