@echo off
REM Script para ejecutar comandos de Node.js desde el directorio local del proyecto
REM Esto mantiene todo dentro del entorno del proyecto

set "NODEJS_HOME=%~dp0nodejs-portable"
set "PATH=%NODEJS_HOME%;%PATH%"

REM Ejecutar el comando pasado como argumento
%*