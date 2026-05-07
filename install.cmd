@echo off
rem -----------------------------------------------------------------
rem  GDP Lab — Windows installer
rem  Creates a local virtual environment and installs dependencies.
rem
rem  Usage:  install.cmd
rem
rem  After running, start the dashboard with:
rem      .venv\Scripts\activate
rem      streamlit run app.py
rem -----------------------------------------------------------------
setlocal enabledelayedexpansion

where python >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no PATH. Instale Python 3.11+ e tente novamente.
    exit /b 1
)

if not exist ".venv" (
    echo Criando ambiente virtual em .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar o ambiente virtual.
        exit /b 1
    )
)

call .venv\Scripts\activate
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha na instalacao das dependencias.
    exit /b 1
)

echo.
echo Instalacao concluida.
echo Para rodar:
echo     .venv\Scripts\activate
echo     streamlit run app.py
endlocal
