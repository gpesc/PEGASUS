@echo off
setlocal
cd /d "%~dp0"
echo Use o mesmo Python com que o Pegasus funciona.
python build_windows.py
if errorlevel 1 goto falha
echo.
echo Pronto: dist\Pegasus.exe
pause
exit /b 0
:falha
echo.
echo Falha. Copie a mensagem acima para diagnostico.
pause
exit /b 1
