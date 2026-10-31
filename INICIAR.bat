@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title MegaRaw OBS Companion

set "PYRUN=python"
where python >nul 2>nul
if errorlevel 1 (
  where py >nul 2>nul
  if errorlevel 1 (
    echo ERRO: Python 3 nao encontrado no PATH.
    echo Instale Python 3 e habilite a opcao Add Python to PATH.
    pause
    exit /b 1
  )
  set "PYRUN=py -3"
)

:menu
cls
echo =======================================================
echo   MegaRaw OBS Companion v1.4.0  -  NAO OFICIAL
echo =======================================================
echo.
echo  1 - DEMONSTRACAO (sem login)
echo  2 - LIVE 5 segundos (recomendado)
echo  3 - LIVE 3 segundos (rapido)
echo  4 - LIVE 10 segundos (conservador)
echo  5 - LIVE 15 segundos (conservador)
echo  6 - LIVE 2 segundos (EXPERIMENTAL / risco 429)
echo  7 - Reconfigurar conta RetroAchievements
 echo  0 - Sair
 echo.
choice /c 12345670 /n /m "Escolha uma opcao: "
if errorlevel 8 goto fim
if errorlevel 7 goto reset
if errorlevel 6 goto dois
if errorlevel 5 goto quinze
if errorlevel 4 goto dez
if errorlevel 3 goto tres
if errorlevel 2 goto cinco
if errorlevel 1 goto demo

:demo
%PYRUN% "%~dp0mega_raw_obs.py" --demo
goto retorno
:cinco
%PYRUN% "%~dp0mega_raw_obs.py" --interval 5
goto retorno
:tres
%PYRUN% "%~dp0mega_raw_obs.py" --interval 3
goto retorno
:dez
%PYRUN% "%~dp0mega_raw_obs.py" --interval 10
goto retorno
:quinze
%PYRUN% "%~dp0mega_raw_obs.py" --interval 15
goto retorno
:dois
%PYRUN% "%~dp0mega_raw_obs.py" --interval 2
goto retorno
:reset
%PYRUN% "%~dp0mega_raw_obs.py" --reset
goto retorno
:retorno
echo.
echo O programa foi encerrado. Aperte uma tecla para voltar ao menu.
pause >nul
goto menu
:fim
endlocal
