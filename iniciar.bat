@echo off
chcp 65001 >nul 2>&1
:: ══════════════════════════════════════════════════════════
::  Video Cutter — Launcher Windows
::  Detecta e instala Python automaticamente se necessário
::  Duplo clique para iniciar
:: ══════════════════════════════════════════════════════════

set PORT=8765
set DIR=%~dp0
set URL=http://localhost:%PORT%
set PYTHON=

echo.
echo ══════════════════════════════════════
echo   Video Cutter — Iniciando...
echo ══════════════════════════════════════
echo.

:: ── Encerra servidor antigo na porta ─────────────────────
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%PORT% " 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: ── Detecta Python ────────────────────────────────────────
for %%c in (python python3 py) do (
    %%c --version >nul 2>&1 && set PYTHON=%%c && goto :python_found
)

:: ── Instala Python via winget (Windows 10+) ───────────────
echo Python nao encontrado. Tentando instalar...
winget --version >nul 2>&1
if %errorlevel%==0 (
    echo Instalando Python via winget...
    winget install -e --id Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
    for %%c in (python python3 py) do (
        %%c --version >nul 2>&1 && set PYTHON=%%c && goto :python_found
    )
)

:: ── Tenta instalar via Microsoft Store ───────────────────
echo Tentando Microsoft Store...
start ms-windows-store://pdp/?ProductId=9NCVDN91XZQP
echo.
echo O Python esta sendo instalado via Microsoft Store.
echo Apos a instalacao, feche esta janela e clique em iniciar.bat novamente.
echo.
echo Se preferir instalar manualmente: https://python.org/downloads
echo.
pause
exit /b 1

:python_found
echo [OK] Python encontrado:
%PYTHON% --version
echo.

:: ── Inicia servidor Python ────────────────────────────────
echo Iniciando servidor local na porta %PORT%...
start /B %PYTHON% "%DIR%_server_win.py"
timeout /t 2 /nobreak >nul

:: ── Verifica se subiu ────────────────────────────────────
netstat -ano | findstr ":%PORT% " >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Servidor nao iniciou. Tente rodar como Administrador.
    echo.
    pause
    exit /b 1
)

echo [OK] Servidor rodando em %URL%
echo.

:: ── Abre navegador ───────────────────────────────────────
start "" "%URL%"

echo ══════════════════════════════════════
echo   Acesse: %URL%
echo   Feche esta janela para encerrar.
echo ══════════════════════════════════════
echo.
pause

:: ── Encerra servidor ao fechar ───────────────────────────
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%PORT% " 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo Servidor encerrado.
