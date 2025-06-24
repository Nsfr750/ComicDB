@echo off
setlocal enabledelayedexpansion

:: Imposta la directory di lavoro alla radice del progetto
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

:: Installa il pacchetto in modalità sviluppo
echo Installing package in development mode...
pip install -e .

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install package in development mode
    exit /b %ERRORLEVEL%
)

:: Crea la directory di output se non esiste
if not exist "_build\html" mkdir "_build\html"

:: Funzione per verificare se un comando esiste
:command_exists
where /q %1 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    exit /b 0
) else (
    exit /b 1
)

:: Verifica se sphinx-build è installato
echo Checking for sphinx-build...
call :command_exists sphinx-build
if %ERRORLEVEL% NEQ 0 (
    echo sphinx-build not found. Installing Sphinx...
    pip install -r docs/requirements-docs.txt
    
    call :command_exists sphinx-build
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install Sphinx. Please install it manually.
        exit /b 1
    )
)

echo.
echo Compiling English documentation...
python -m sphinx -b html -D language=en docs _build\html\en

if %ERRORLEVEL% NEQ 0 (
    echo Error compiling English documentation
    exit /b %ERRORLEVEL%
)

echo.
echo Compiling Italian documentation...
python -m sphinx -b html -D language=it docs _build\html\it

if %ERRORLEVEL% NEQ 0 (
    echo Error compiling Italian documentation
    exit /b %ERRORLEVEL%
)

echo.
echo Documentation built successfully!

:: Verifica se esiste il file index.html in inglese
if exist "_build\html\en\index.html" (
    echo Opening English documentation in default browser...
    start "" "_build\html\en\index.html"
) else if exist "_build\html\it\index.html" (
    echo English documentation not found. Opening Italian documentation...
    start "" "_build\html\it\index.html"
) else (
    echo Documentation files not found. Please check the build output for errors.
)

exit /b 0
