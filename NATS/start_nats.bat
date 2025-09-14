@echo off
title Iniciando NATS Server
echo.

:: Caminho para o executável do NATS e o arquivo de configuração
set NATS_EXE=C:\nats\nats-server-v2.11.2-windows-amd64\nats-server.exe
set NATS_CONFIG=C:\nats\nats-server-v2.11.2-windows-amd64\nats.conf

:: Iniciar o NATS Server
echo Iniciando NATS Server com configuracao personalizada...
start cmd /k "%NATS_EXE% -c %NATS_CONFIG% 

echo.
echo NATS Server iniciado em uma nova janela.
exit
