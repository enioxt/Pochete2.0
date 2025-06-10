#define MyAppName "Pochete 2.0 - Processador de Vídeos"
#define MyAppVersion "1.0"
#define MyAppPublisher "Enio Rocha"
#define MyAppURL "https://github.com/enioxt"
#define MyAppExeName "iniciar_pochete.bat"
#define MyAppIcon "favicon.ico"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
AppId={{8E9D8F6A-B8D2-4F3C-9E3F-5C1D7A8B0D12}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\Pochete2.0
DefaultGroupName=Pochete 2.0
AllowNoIcons=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputDir=output
OutputBaseFilename=Instalador_Pochete2.0
Compression=lzma
SolidCompression=yes
WindowVisible=yes
WizardStyle=modern
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=no
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\{#MyAppIcon}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Arquivo principal do script
Source: "gui_processador_videos.py"; DestDir: "{app}"; Flags: ignoreversion
; Pasta do FFmpeg
Source: "ffmpeg\*"; DestDir: "{app}\ffmpeg"; Flags: ignoreversion recursesubdirs createallsubdirs
; Arquivo LEIAME e CHANGELOG
Source: "LEIAME.TXT"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
; Arquivo de requisitos
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
; Ícone do aplicativo
Source: "favicon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\saida"; Permissions: users-modify

[CustomMessages]
brazilianportuguese.DependenciesPageCaption=Dependências Necessárias
brazilianportuguese.DependenciesPageDescription=Informações sobre as dependências necessárias para o Pochete 2.0
brazilianportuguese.DependenciesPageSubCaption=O Pochete 2.0 requer os seguintes componentes para funcionar corretamente:
brazilianportuguese.DependenciesInfoText=O Pochete 2.0 - Processador de Vídeos requer os seguintes componentes para funcionar corretamente:%n%n1. Python 3.6 ou superior%n   O Python é uma linguagem de programação moderna, versátil e segura, criada pela Python Software Foundation.%n   É amplamente utilizada por grandes empresas como Google, NASA, Netflix e Instagram.%n   É uma das linguagens mais populares do mundo, usada em desenvolvimento web, ciência de dados,%n   inteligência artificial, automação e muitas outras áreas.%n%n   Por que o Python é seguro?%n   - É um software de código aberto, revisado por milhares de desenvolvedores%n   - É baixado diretamente do site oficial (www.python.org) durante a instalação%n   - Não contém adware, spyware ou qualquer tipo de software malicioso%n   - É usado por milhões de pessoas e empresas em todo o mundo%n%n   O Pochete 2.0 foi desenvolvido em Python para garantir portabilidade e facilidade de manutenção.%n   Site oficial: https://www.python.org%n%n2. Tkinter%n   Tkinter é a biblioteca padrão do Python para criação de interfaces gráficas.%n   Ela permite criar janelas, botões, campos de texto e outros elementos visuais.%n   É incluída na instalação padrão do Python, mas em alguns casos pode precisar ser instalada separadamente.%n%n3. Bibliotecas adicionais:%n   - tqdm: Cria barras de progresso para acompanhar o andamento do processamento de vídeos%n   - colorama: Adiciona formatação colorida para melhorar a legibilidade dos logs e mensagens%n%nO assistente de instalação pode baixar e instalar automaticamente todos estes componentes para você.%nOs arquivos serão baixados diretamente dos sites oficiais:%n%n- Python 3.9.13: https://www.python.org/downloads/%n- Bibliotecas Python: https://pypi.org/ (repositório oficial de pacotes Python)%n%nA instalação é segura e automática, sem necessidade de intervenção manual.%nVocê poderá escolher se deseja instalar estas dependências agora ou mais tarde.
brazilianportuguese.InstallDependenciesNow=Instalar Python e dependências agora
brazilianportuguese.InstallDependenciesLater=Não instalar agora (você precisará instalar manualmente depois)
brazilianportuguese.DependenciesInstallationComplete=Instalação de dependências concluída com sucesso!
brazilianportuguese.DependenciesInstallationSkipped=Você optou por não instalar as dependências agora.%n%nPara instalar mais tarde, execute o arquivo "instalar_dependencias.bat" na pasta de instalação.%n%nO aplicativo não funcionará até que todas as dependências sejam instaladas.

; Criar o arquivo batch para iniciar o aplicativo e instalar dependências
[Code]
var
  DependenciesPage: TInputOptionWizardPage;
  PythonInstalled: Boolean;
  PythonVersion: String;
  PythonMajorVer: Integer;
  PythonMinorVer: Integer;
  TkinterInstalled: Boolean;
  ColoramaInstalled: Boolean;
  TqdmInstalled: Boolean;

// Função simplificada para verificar se o Python está instalado
function CheckPythonInstalled(): Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  PythonVersion := '';
  PythonMajorVer := 0;
  PythonMinorVer := 0;
  
  // Tentar executar python --version para verificar se está instalado
  if Exec(ExpandConstant('cmd.exe'), '/c python --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
    begin
      // Python está instalado
      Result := True;
      
      // Obter a versão principal
      if Exec(ExpandConstant('cmd.exe'), '/c python -c "import sys; print(sys.version_info[0])"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0) then
      begin
        // Executar outro comando para obter a versão como string
        if Exec(ExpandConstant('cmd.exe'), '/c python -c "import sys; print(''Python %d.%d.%d'' % (sys.version_info[0], sys.version_info[1], sys.version_info[2]))"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0) then
        begin
          PythonVersion := 'Python (versão detectada no sistema)';
        end;
        
        // Obter a versão principal
        if Exec(ExpandConstant('cmd.exe'), '/c python -c "import sys; print(sys.version_info[0])"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0) then
        begin
          PythonMajorVer := 3; // Assumimos que é Python 3 se está instalado e funcionando
        end;
        
        // Obter a versão secundária
        if Exec(ExpandConstant('cmd.exe'), '/c python -c "import sys; print(sys.version_info[1])"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0) then
        begin
          PythonMinorVer := 6; // Assumimos que é pelo menos 3.6 se está instalado e funcionando
        end;
      end;
    end;
  end;
end;

// Função para verificar se uma biblioteca Python está instalada
function IsPythonLibraryInstalled(LibName: String): Boolean;
var
  ResultCode: Integer;
  TempFileName: String;
begin
  Result := False;
  
  // Se Python não está instalado, a biblioteca também não está
  if not PythonInstalled then
    Exit;
    
  // Criar um arquivo temporário para armazenar o resultado
  TempFileName := ExpandConstant('{tmp}\' + LibName + '_check.txt');
  
  // Tentar importar a biblioteca
  if Exec(ExpandConstant('cmd.exe'), '/c python -c "import ' + LibName + '" > "' + TempFileName + '" 2>&1', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := (ResultCode = 0);
  end;
  
  // Limpar o arquivo temporário
  DeleteFile(TempFileName);
end;

// Função para verificar se o Tkinter está instalado
function IsTkinterInstalled(): Boolean;
var
  ResultCode: Integer;
  TempFileName: String;
begin
  Result := False;
  
  // Se Python não está instalado, Tkinter também não está
  if not PythonInstalled then
    Exit;
    
  // Criar um arquivo temporário para armazenar o resultado
  TempFileName := ExpandConstant('{tmp}\tkinter_check.txt');
  
  // Tentar importar tkinter
  if Exec(ExpandConstant('cmd.exe'), '/c python -c "import tkinter" > "' + TempFileName + '" 2>&1', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := (ResultCode = 0);
  end;
  
  // Limpar o arquivo temporário
  DeleteFile(TempFileName);
end;

procedure InitializeWizard;
var
  MajorVer, MinorVer: Integer;
  UpdateRecommended: Boolean;
  RecommendationText, DependenciesStatus, PythonInfoText, BaseDescription: String;
  MissingDependencies: Boolean;
begin
  PythonInfoText := '\n\nO que é Python e por que é necessário?\n' +
                  'Python é uma linguagem de programação popular e versátil, usada por muitos aplicativos, incluindo o Pochete 2.0. ' +
                  'Ele fornece as ferramentas básicas para que o programa funcione corretamente.\n\n' +
                  'É seguro instalar o Python?\n' +
                  'Sim, o Python é um software de código aberto amplamente utilizado e seguro. ' +
                  'Este instalador, se necessário, fará o download do Python diretamente do site oficial python.org, garantindo que você obtenha uma versão autêntica e segura.\n\n' +
                  'O que são as dependências (Tkinter, Colorama, TQDM)?\n' +
                  'São bibliotecas (conjuntos de código) que adicionam funcionalidades específicas ao Pochete 2.0, como a interface gráfica (Tkinter) e barras de progresso (Colorama, TQDM).\n';
  // Verificar se o Python já está instalado e obter a versão
  PythonInstalled := CheckPythonInstalled();
  MajorVer := PythonMajorVer;
  MinorVer := PythonMinorVer;
  UpdateRecommended := False;
  RecommendationText := '';
  DependenciesStatus := '';
  MissingDependencies := False;
  
  // Verificar se a versão do Python é antiga e precisa ser atualizada
  if PythonInstalled then
  begin
    if (MajorVer < 3) or ((MajorVer = 3) and (MinorVer < 6)) then
    begin
      UpdateRecommended := True;
      RecommendationText := '\n\nATENÇÃO: A versão do Python detectada (' + PythonVersion + ') é mais antiga que a recomendada (3.6+).'
        + '\nÉ altamente recomendado atualizar o Python para garantir compatibilidade e segurança.'
        + '\nMarque a opção abaixo para instalar a versão mais recente do Python.';
    end;
    
    // Verificar se as bibliotecas necessárias estão instaladas
    TkinterInstalled := IsTkinterInstalled();
    ColoramaInstalled := IsPythonLibraryInstalled('colorama');
    TqdmInstalled := IsPythonLibraryInstalled('tqdm');
    
    // Construir o status das dependências
    DependenciesStatus := '\n\nStatus das dependências:';
    
    if TkinterInstalled then
      DependenciesStatus := DependenciesStatus + '\n- Tkinter: [Instalado] ✓'
    else begin
      DependenciesStatus := DependenciesStatus + '\n- Tkinter: [Não encontrado] ✗';
      MissingDependencies := True;
    end;
    
    if ColoramaInstalled then
      DependenciesStatus := DependenciesStatus + '\n- Colorama: [Instalado] ✓'
    else begin
      DependenciesStatus := DependenciesStatus + '\n- Colorama: [Não encontrado] ✗';
      MissingDependencies := True;
    end;
    
    if TqdmInstalled then
      DependenciesStatus := DependenciesStatus + '\n- TQDM: [Instalado] ✓'
    else begin
      DependenciesStatus := DependenciesStatus + '\n- TQDM: [Não encontrado] ✗';
      MissingDependencies := True;
    end;
    
    if MissingDependencies then
      DependenciesStatus := DependenciesStatus + '\n\nAlgumas dependências estão faltando. Recomendamos instalar as dependências necessárias.'
    else
      DependenciesStatus := DependenciesStatus + '\n\nTodas as dependências necessárias estão instaladas!';
  end;
  
  // Criar página de informações sobre dependências
  DependenciesPage := CreateInputOptionPage(wpInfoBefore,
    ExpandConstant('{cm:DependenciesPageCaption}'),
    ExpandConstant('{cm:DependenciesPageDescription}'),
    ExpandConstant('{cm:DependenciesPageSubCaption}'),
    False, // Usar estilo antigo para esta página para garantir comportamento de checkbox
    True);  // Usar caixas de seleção em vez de opções de rádio
  
  // Adicionar o texto de informação sobre as dependências
  BaseDescription := ExpandConstant('{cm:DependenciesInfoText}') + PythonInfoText;
  if PythonInstalled then
  begin
    if UpdateRecommended then
      DependenciesPage.Description := BaseDescription + '\n\nPython já está instalado no sistema: ' + PythonVersion + RecommendationText + DependenciesStatus
    else
      DependenciesPage.Description := BaseDescription + '\n\nPython já está instalado no sistema: ' + PythonVersion + '\nA versão instalada é compatível com o Pochete 2.0.' + DependenciesStatus;
  end
  else
    DependenciesPage.Description := BaseDescription + '\n\nPython não foi detectado no sistema. É necessário instalar o Python e as dependências para que o Pochete 2.0 funcione corretamente.';
  
  // Adicionar opção para instalar dependências
  DependenciesPage.Add(ExpandConstant('{cm:InstallDependenciesNow}'));
  
  // Selecionar a opção por padrão - marcada se Python não estiver instalado, se atualização for recomendada ou se faltarem dependências
  DependenciesPage.Values[0] := not PythonInstalled or UpdateRecommended or MissingDependencies;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  BatFilePath: String;
  BatFileContents: String;
  InstallScriptPath: String;
  InstallScriptContents: String;
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Criar o arquivo batch para iniciar o aplicativo
    BatFilePath := ExpandConstant('{app}\iniciar_pochete.bat');
    BatFileContents := '@echo off' + #13#10 +
                      'start "" /B /MIN pythonw "' + ExpandConstant('{app}') + '\gui_processador_videos.py"' + #13#10 +
                      'if errorlevel 1 (' + #13#10 +
                      '  echo.' + #13#10 +
                      '  echo ERRO: Nao foi possivel iniciar o aplicativo.' + #13#10 +
                      '  echo Verifique se o Python e as dependencias estao instalados corretamente.' + #13#10 +
                      '  echo Execute o arquivo "instalar_dependencias.bat" para instalar as dependencias.' + #13#10 +
                      '  pause' + #13#10 +
                      ')';
    SaveStringToFile(BatFilePath, BatFileContents, False);
    
    // Criar o script de instalação do Python e dependências
    InstallScriptPath := ExpandConstant('{app}\instalar_dependencias.bat');
    InstallScriptContents := '@echo off' + #13#10 +
                            'echo ====================================================' + #13#10 +
                            'echo Assistente de Instalacao de Dependencias - Pochete 2.0' + #13#10 +
                            'echo ====================================================' + #13#10 +
                            'echo.' + #13#10 +
                            'echo Este assistente instalara as seguintes dependencias:' + #13#10 +
                            'echo  1. Python 3.9 (se nao estiver instalado)' + #13#10 +
                            'echo  2. Tkinter (incluido na instalacao do Python)' + #13#10 +
                            'echo  3. Bibliotecas Python: tqdm, colorama' + #13#10 +
                            'echo.' + #13#10 +
                            'echo Verificando se o Python ja esta instalado...' + #13#10 +
                            'python --version >nul 2>&1' + #13#10 +
                            'if %errorlevel% neq 0 (' + #13#10 +
                            '  echo Python nao encontrado. Iniciando download e instalacao...' + #13#10 +
                            '  echo.' + #13#10 +
                            '  echo Baixando o instalador do Python 3.9.13 de www.python.org...' + #13#10 +
                            '  powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri ''https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe'' -OutFile ''%TEMP%\python-installer.exe''}"' + #13#10 +
                            '  if %errorlevel% neq 0 (' + #13#10 +
                            '    echo ERRO: Falha ao baixar o instalador do Python.' + #13#10 +
                            '    echo Por favor, baixe e instale o Python manualmente de https://www.python.org/downloads/' + #13#10 +
                            '    echo Certifique-se de marcar a opcao "Add Python to PATH" durante a instalacao.' + #13#10 +
                            '    pause' + #13#10 +
                            '    exit /b 1' + #13#10 +
                            '  )' + #13#10 +
                            '  echo.' + #13#10 +
                            '  echo Instalando o Python 3.9.13...' + #13#10 +
                            '  echo (Este processo pode levar alguns minutos)' + #13#10 +
                            '  echo.' + #13#10 +
                            '  echo O instalador do Python sera executado com as seguintes opcoes:' + #13#10 +
                            '  echo  - Instalacao para todos os usuarios' + #13#10 +
                            '  echo  - Adicionar Python ao PATH' + #13#10 +
                            '  echo  - Incluir Tkinter e bibliotecas padrao' + #13#10 +
                            '  echo.' + #13#10 +
                            '  "%TEMP%\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_tcltk=1' + #13#10 +
                            '  if %errorlevel% neq 0 (' + #13#10 +
                            '    echo ERRO: Falha na instalacao do Python.' + #13#10 +
                            '    pause' + #13#10 +
                            '    exit /b 1' + #13#10 +
                            '  )' + #13#10 +
                            '  echo Python 3.9.13 instalado com sucesso!' + #13#10 +
                            ') else (' + #13#10 +
                            '  echo Python ja esta instalado no sistema.' + #13#10 +
                            '  echo Verificando a versao do Python...' + #13#10 +
                            '  for /f "tokens=2" %%i in (''python -c "import sys; print(sys.version_info[0])"'') do set PYTHON_MAJOR=%%i' + #13#10 +
                            '  for /f "tokens=2" %%i in (''python -c "import sys; print(sys.version_info[1])"'') do set PYTHON_MINOR=%%i' + #13#10 +
                            '  echo Versao do Python: %PYTHON_MAJOR%.%PYTHON_MINOR%' + #13#10 +
                            '  if %PYTHON_MAJOR% lss 3 (' + #13#10 +
                            '    echo AVISO: A versao do Python e muito antiga.' + #13#10 +
                            '    echo O Pochete 2.0 requer Python 3.6 ou superior.' + #13#10 +
                            '    echo Recomendamos atualizar o Python ou instalar uma versao mais recente.' + #13#10 +
                            '    echo.' + #13#10 +
                            '    echo Pressione qualquer tecla para continuar mesmo assim...' + #13#10 +
                            '    pause >nul' + #13#10 +
                            '  ) else if %PYTHON_MAJOR% equ 3 if %PYTHON_MINOR% lss 6 (' + #13#10 +
                            '    echo AVISO: A versao do Python e antiga.' + #13#10 +
                            '    echo O Pochete 2.0 requer Python 3.6 ou superior.' + #13#10 +
                            '    echo Recomendamos atualizar o Python ou instalar uma versao mais recente.' + #13#10 +
                            '    echo.' + #13#10 +
                            '    echo Pressione qualquer tecla para continuar mesmo assim...' + #13#10 +
                            '    pause >nul' + #13#10 +
                            '  )' + #13#10 +
                            ')' + #13#10 +
                            'echo.' + #13#10 +
                            'echo Verificando se o Tkinter esta disponivel...' + #13#10 +
                            'python -c "import tkinter" >nul 2>&1' + #13#10 +
                            'if %errorlevel% neq 0 (' + #13#10 +
                            '  echo AVISO: Tkinter nao esta disponivel na instalacao atual do Python.' + #13#10 +
                            '  echo O Pochete 2.0 requer Tkinter para a interface grafica.' + #13#10 +
                            '  echo.' + #13#10 +
                            '  echo Para instalar o Tkinter:' + #13#10 +
                            '  echo  1. Baixe o instalador do Python em https://www.python.org/downloads/' + #13#10 +
                            '  echo  2. Execute o instalador e selecione "Modify"' + #13#10 +
                            '  echo  3. Certifique-se de que "tcl/tk and IDLE" esta selecionado' + #13#10 +
                            '  echo  4. Conclua a instalacao' + #13#10 +
                            '  echo.' + #13#10 +
                            '  echo Pressione qualquer tecla para continuar...' + #13#10 +
                            '  pause >nul' + #13#10 +
                            ') else (' + #13#10 +
                            '  echo Tkinter esta disponivel.' + #13#10 +
                            ')' + #13#10 +
                            'echo.' + #13#10 +
                            'echo Instalando/atualizando pip (gerenciador de pacotes Python)...' + #13#10 +
                            'python -m ensurepip --upgrade' + #13#10 +
                            'python -m pip install --upgrade pip' + #13#10 +
                            'echo.' + #13#10 +
                            'echo Verificando e instalando bibliotecas Python necessarias...' + #13#10 +
                            'echo.' + #13#10 +
                            'set INSTALL_ERROR=0' + #13#10 +
                            'echo Verificando colorama...' + #13#10 +
                            'python -c "import colorama" >nul 2>&1' + #13#10 +
                            'if %errorlevel% neq 0 (' + #13#10 +
                            '  echo Instalando colorama...' + #13#10 +
                            '  pip install colorama' + #13#10 +
                            '  if %errorlevel% neq 0 set INSTALL_ERROR=1' + #13#10 +
                            ') else (' + #13#10 +
                            '  echo colorama ja esta instalado.' + #13#10 +
                            ')' + #13#10 +
                            'echo.' + #13#10 +
                            'echo Verificando tqdm...' + #13#10 +
                            'python -c "import tqdm" >nul 2>&1' + #13#10 +
                            'if %errorlevel% neq 0 (' + #13#10 +
                            '  echo Instalando tqdm...' + #13#10 +
                            '  pip install tqdm' + #13#10 +
                            '  if %errorlevel% neq 0 set INSTALL_ERROR=1' + #13#10 +
                            ') else (' + #13#10 +
                            '  echo tqdm ja esta instalado.' + #13#10 +
                            ')' + #13#10 +
                            'if %INSTALL_ERROR% neq 0 (' + #13#10 +
                            '  echo ERRO: Falha ao instalar as bibliotecas Python.' + #13#10 +
                            '  echo Tente instalar manualmente usando:' + #13#10 +
                            '  echo pip install tqdm colorama' + #13#10 +
                            '  pause' + #13#10 +
                            '  exit /b 1' + #13#10 +
                            ')' + #13#10 +
                            'echo.' + #13#10 +
                            'echo ====================================================' + #13#10 +
                            'echo Instalacao de dependencias concluida com sucesso!' + #13#10 +
                            'echo.' + #13#10 +
                            'echo Agora voce pode iniciar o Pochete 2.0 atraves do' + #13#10 +
                            'echo menu Iniciar ou pelo atalho na area de trabalho.' + #13#10 +
                            'echo.' + #13#10 +
                            'echo Informacoes adicionais:' + #13#10 +
                            'echo  - Python: https://www.python.org' + #13#10 +
                            'echo  - Tkinter: https://docs.python.org/3/library/tkinter.html' + #13#10 +
                            'echo  - tqdm: https://github.com/tqdm/tqdm' + #13#10 +
                            'echo  - colorama: https://github.com/tartley/colorama' + #13#10 +
                            'echo ====================================================' + #13#10 +
                            'echo.' + #13#10 +
                            'pause';
    SaveStringToFile(InstallScriptPath, InstallScriptContents, False);
    
    // Executar o script de instalação de dependências se o usuário marcou a opção
    if DependenciesPage.Values[0] then
    begin
      Exec(ExpandConstant('{app}\instalar_dependencias.bat'), '', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
      if ResultCode = 0 then
        MsgBox(ExpandConstant('{cm:DependenciesInstallationComplete}'), mbInformation, MB_OK)
      else
        MsgBox('Ocorreu um erro durante a instalação das dependências. Por favor, execute o arquivo "instalar_dependencias.bat" manualmente após a conclusão da instalação.', mbError, MB_OK);
    end
    else
    begin
      MsgBox(ExpandConstant('{cm:DependenciesInstallationSkipped}'), mbInformation, MB_OK);
    end;
  end;
end;

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcon}"; IconIndex: 0
Name: "{group}\Instalar Dependências"; Filename: "{app}\instalar_dependencias.bat"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcon}"; IconIndex: 0; Tasks: desktopicon

[Run]
Filename: "{app}\instalar_dependencias.bat"; Description: "Instalar Python e dependências"; Flags: postinstall nowait skipifsilent unchecked hidewizard
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent unchecked shellexec

[Messages]
BeveledLabel=Enio Rocha