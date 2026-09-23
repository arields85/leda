@echo off
rem Levanta el PostgreSQL local instalado con scoop. No lo registra como
rem servicio: arranca solo cuando se ejecuta este archivo.
setlocal
chcp 65001 >nul

set "PGBIN=%USERPROFILE%\scoop\apps\postgresql\current\bin"
set "PGDATA=%USERPROFILE%\scoop\persist\postgresql\data"
set "PGLOG=%USERPROFILE%\scoop\persist\postgresql\postgres.log"

if not exist "%PGBIN%\pg_ctl.exe" (
    echo PostgreSQL no está instalado en %PGBIN%.
    echo Instalación: scoop install postgresql
    goto fin
)

"%PGBIN%\pg_ctl.exe" -D "%PGDATA%" status >nul 2>&1
if %errorlevel%==0 (
    echo PostgreSQL ya estaba corriendo.
    goto listo
)

echo Levantando PostgreSQL...
"%PGBIN%\pg_ctl.exe" -D "%PGDATA%" -l "%PGLOG%" start -w -t 60
if errorlevel 1 (
    echo PostgreSQL no arrancó. Detalle en el registro: %PGLOG%
    goto fin
)

:listo
"%PGBIN%\pg_isready.exe" -h localhost -p 5432

:fin
pause
