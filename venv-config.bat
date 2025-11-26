@echo off
IF NOT EXIST ".venv\Scripts\activate.bat" (
    echo Ambiente virtual '.venv' não encontrado. Criando ambiente virtual...
    python -m venv .venv
    IF %ERRORLEVEL% NEQ 0 (
        echo Falha ao criar o ambiente virtual. Certifique-se de que o Python está instalado corretamente.
        pause
        exit /b %ERRORLEVEL%
    )
) ELSE (
    echo Ambiente virtual '.venv' já existe.
)


echo Ativando o ambiente virtual...
call .venv\Scripts\activate.bat
python.exe -m pip install --upgrade pip

IF %ERRORLEVEL% NEQ 0 (
    echo Falha ao ativar o ambiente virtual.
    pause
    exit /b %ERRORLEVEL%
)

IF EXIST "requirements.txt" (
    echo Instalando dependências do requirements.txt...
    pip install -r requirements.txt
    IF %ERRORLEVEL% NEQ 0 (
        echo Falha ao instalar as dependências. Verifique o arquivo requirements.txt.
        pause
        exit /b %ERRORLEVEL%
    )
) ELSE (
    echo Arquivo requirements.txt não encontrado. Pulando a instalação de dependências.
)
echo Ambiente virtual ativado e dependências instaladas com sucesso.
pause
