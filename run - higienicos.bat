@echo off
chcp 65001 > nul

set PASTA_PROJETO=Z:\OPERACOES\13-ALMOXARIFADO\1 - Controle de Higienicos
set NOME_VENV=venv
set ARQUIVO_PY=higienicos.py

cd /d "%PASTA_PROJETO%"

if not exist "%NOME_VENV%\Scripts\activate.bat" (
    echo [ERRO] O ambiente virtual "%NOME_VENV%" não foi encontrado nesta pasta.
    echo Caminho procurado: %PASTA_PROJETO%%NOME_VENV%
    pause
    exit /b
)


if not exist "%ARQUIVO_PY%" (
    echo [ERRO] O arquivo "%ARQUIVO_PY%" não foi encontrado.
    pause
    exit /b
)

echo Ativando o ambiente virtual (%NOME_VENV%)...
call "%NOME_VENV%\Scripts\activate.bat"

echo Executando %ARQUIVO_PY%...
echo --------------------------------------------------
python "%ARQUIVO_PY%"
echo --------------------------------------------------

call deactivate