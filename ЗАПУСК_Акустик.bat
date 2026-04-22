@echo off
chcp 65001 >nul
title Акустик

set "ROOT=%~dp0"
set "VENV=%ROOT%.venv"

:: Проверка виртуального окружения
if not exist "%VENV%\Scripts\activate.bat" (
    echo  ОШИБКА: Виртуальное окружение не найдено.
    echo  Сначала запустите УСТАНОВКА.bat
    pause
    exit /b 1
)

:: Проверка Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ┌──────────────────────────────────────────────────────────────┐
    echo │  Node.js не найден — запускаем только API-сервер            │
    echo │  Для полного интерфейса установите Node.js 20 LTS            │
    echo │  https://nodejs.org/                                         │
    echo └──────────────────────────────────────────────────────────────┘
    echo.
    call "%VENV%\Scripts\activate.bat"
    cd "%ROOT%"
    echo  API-сервер: http://localhost:8765
    echo  Документация: http://localhost:8765/docs
    echo  Нажмите Ctrl+C для остановки
    echo.
    python -m uvicorn api.main:app --host 0.0.0.0 --port 8765
    pause
    exit /b 0
)

:: Проверка сборки Electron
if not exist "%ROOT%electron\node_modules" (
    echo  ⚠️  Модули Electron не установлены. Выполняется npm install...
    cd "%ROOT%electron"
    npm install -q
)

:: Запуск API-сервера в фоне
echo  Запуск API-сервера в фоновом режиме...
call "%VENV%\Scripts\activate.bat"
cd "%ROOT%"
start "Акустик API" /MIN cmd /c "call \"%VENV%\Scripts\activate.bat\" && python -m uvicorn api.main:app --host 0.0.0.0 --port 8765"

:: Небольшая пауза, чтобы API поднялся
timeout /t 2 /nobreak >nul

:: Запуск Electron
echo  Запуск интерфейса Акустик...
cd "%ROOT%electron"
npm run dev

:: При закрытии Electron — остановить API
taskkill /FI "WindowTitle eq Акустик API*" /F >nul 2>&1
