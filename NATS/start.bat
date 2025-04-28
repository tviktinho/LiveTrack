@echo off
title Iniciando NATS Server
echo.

:: Caminho para o executável do NATS e o arquivo de configuração
set NATS_EXE=C:\Users\Administrator\Documents\GitHub\SistemasDistribuidos_24_2\Sistemas-Distribuidos-2024-2\NATS\nats-server.exe
set NATS_CONFIG=C:\Users\Administrator\Documents\GitHub\SistemasDistribuidos_24_2\Sistemas-Distribuidos-2024-2\NATS\nats.conf

:: Iniciar o NATS Server
echo Iniciando NATS Server com configuracao personalizada...
start cmd /k "%NATS_EXE% -c %NATS_CONFIG%"

echo.
echo NATS Server iniciado em uma nova janela.
exit
