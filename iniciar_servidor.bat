@echo off
REM Script para iniciar o servidor Flask em Windows
REM Execute este arquivo para abrir o painel em http://127.0.0.1:5050

cd /d "%~dp0"
echo Iniciando servidor Flask...
echo Painel sera acessivel em: http://127.0.0.1:5050
echo.
echo Pressione CTRL+C para parar o servidor
echo.

call env\Scripts\activate.bat
python app.py

pause
