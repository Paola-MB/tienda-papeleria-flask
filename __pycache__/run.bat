@echo off
set FLASK_APP=run.py
echo FLASK_APP establecido a %FLASK_APP%

echo.
echo Inicializando la base de datos (solo la primera vez)...
flask db init

echo.
echo Generando la migración...
flask db migrate -m "Añadir campo email_confirmado a Usuario"

echo.
echo Aplicando la migración a la base de datos...
flask db upgrade

echo.
echo Proceso de migración finalizado.
pause
