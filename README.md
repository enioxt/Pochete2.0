# POCHETE 2.0 - PROCESSADOR DE VÍDEOS

## DESCRIÇÃO
O Pochete 2.0 é uma ferramenta com interface gráfica para processamento de vídeos que permite:
- Processar vídeos completos ou extrair segmentos específicos
- Dividir vídeos grandes em partes menores com tamanho máximo configurável
- Recodificar vídeos com configurações otimizadas
- Interface amigável para facilitar o uso

## REQUISITOS
- Windows 7 ou superior
- Python 3.6 ou superior (instalado automaticamente se necessário)
- Bibliotecas Python: tkinter, tqdm, colorama (instaladas automaticamente)
- FFmpeg e FFprobe (incluídos no instalador)

## INSTALAÇÃO
Para instalar o Pochete 2.0 no Windows:
1. Baixe o arquivo do instalador "Instalador_Pochete2.0.exe".
   Você pode encontrá-lo na seção "Releases" do repositório do projeto no GitHub:
   [https://github.com/enioxt/Pochete2.0/releases/](https://github.com/enioxt/Pochete2.0/releases/)
   (Se o link direto para o arquivo .exe estiver disponível na página principal do repositório, você também pode usá-lo).
2. Execute o arquivo "Instalador_Pochete2.0.exe" que você baixou.
3. Siga as instruções apresentadas pelo assistente de instalação.
   - O instalador verificará automaticamente se o Python e as dependências necessárias (Tkinter, Colorama, TQDM) já estão presentes em seu sistema.
   - Caso alguma dessas dependências não seja encontrada, o instalador oferecerá a opção de baixá-las e instalá-las para você.
4. Após a conclusão da instalação, você poderá iniciar o Pochete 2.0 através do atalho criado no Menu Iniciar ou na Área de Trabalho (se você tiver escolhido criar um).

## INSTRUÇÕES DE USO
### 1. INICIALIZAÇÃO:
- Inicie o aplicativo através do ícone no Menu Iniciar ou na Área de Trabalho
- A interface gráfica será carregada automaticamente

### 2. UTILIZAÇÃO DA INTERFACE:
- Selecione o vídeo de origem clicando no botão "Selecionar Vídeo"
- Escolha o modo de processamento (vídeo completo ou segmento específico)
- Se escolher um segmento, informe os tempos de início e fim
- Defina o tamanho máximo por parte (em MB) no campo apropriado
- Clique em "Processar Vídeo" para iniciar o processamento
- Acompanhe o progresso através da barra de progresso

### 3. RESULTADOS:
- Os vídeos processados serão salvos na pasta "saida" dentro da pasta de instalação
- Cada vídeo terá sua própria pasta com o nome do projeto
- Se o vídeo for dividido em partes, cada parte terá numeração sequencial
- Ao finalizar, o aplicativo mostrará uma mensagem de conclusão

## MODOS DE PROCESSAMENTO

### 1. PROCESSAMENTO DE VÍDEO COMPLETO
Este modo é ideal para situações como:
- Quando você precisa fazer upload de um vídeo grande em plataformas que limitam o tamanho do arquivo
- Para compartilhar vídeos extensos via e-mail ou mensageiros que têm restrições de tamanho
- Para armazenar vídeos em dispositivos com sistemas de arquivos que limitam o tamanho máximo de arquivo
- Para facilitar o download em conexões instáveis, permitindo baixar partes separadamente
- Para distribuir conteúdo em mídias físicas com capacidade limitada (pen drives, DVDs)

### 2. EXTRAÇÃO DE SEGMENTOS
Este modo é perfeito para:
- Extrair apenas as partes relevantes de uma gravação longa
- Compartilhar momentos específicos de um vídeo sem enviar o arquivo completo
- Criar clipes curtos para redes sociais ou apresentações
- Remover seções desnecessárias ou indesejadas de um vídeo
- Dividir um vídeo longo em capítulos ou seções temáticas

## DICAS
- Para extrair um segmento, você pode informar o tempo nos formatos:
  * Segundos (ex: 90)
  * MM:SS (ex: 01:30)
  * HH:MM:SS (ex: 00:01:30)
- O programa adiciona automaticamente uma margem de segurança nas extrações
- Arquivos temporários são limpos automaticamente após o processamento
- Você pode verificar informações sobre o vídeo original na interface
- Para vídeos muito grandes, recomenda-se definir um tamanho máximo por parte adequado ao meio de compartilhamento
- A qualidade do vídeo é preservada durante o processamento, mantendo as características do original

## SUPORTE
Em caso de problemas, verifique:
- Se o Python está corretamente instalado (execute o arquivo "instalar_dependencias.bat")
- Se os vídeos estão em formatos compatíveis (MP4, AVI, MOV, etc.)
- Se há espaço suficiente no disco para os arquivos processados
- Se o FFmpeg e FFprobe estão corretamente instalados

## NOTA SOBRE PYTHON E DEPENDÊNCIAS
O Pochete 2.0 utiliza Python e algumas bibliotecas adicionais para funcionar.

**O que é Python e por que é necessário?**
Python é uma linguagem de programação popular, segura e versátil, usada por muitos aplicativos,
incluindo o Pochete 2.0. Ele fornece as ferramentas básicas para que o programa
funcione corretamente. Se o Python não estiver instalado em seu sistema, o instalador
do Pochete 2.0 oferecerá a opção de baixá-lo e instalá-lo automaticamente.

**É seguro instalar o Python?**
Sim, o Python é um software de código aberto amplamente utilizado e seguro.
O instalador do Pochete 2.0, se necessário, fará o download do Python diretamente
do site oficial (python.org), garantindo que você obtenha uma versão autêntica e segura.

**O que são as dependências (Tkinter, Colorama, TQDM)?**
São bibliotecas (conjuntos de código) que adicionam funcionalidades específicas ao
Pochete 2.0:
- Tkinter: Utilizada para criar a interface gráfica do programa.
- Colorama: Permite o uso de cores em mensagens no console (usado internamente).
- TQDM: Usada para exibir barras de progresso durante o processamento dos vídeos.
Essas dependências também são instaladas automaticamente pelo instalador se não
estiverem presentes e a opção de instalação for selecionada.

## COMPILANDO O INSTALADOR (PARA DESENVOLVEDORES)

Se você deseja modificar o instalador ou compilá-lo a partir do código-fonte, siga estas etapas:

### Requisitos para Compilação:
1.  **Inno Setup:** Você precisará ter o Inno Setup instalado. O Inno Setup é uma ferramenta gratuita para criar instaladores para programas Windows.
    *   **Download:** Você pode baixá-lo em [jrsoftware.org](https://jrsoftware.org/isinfo.php).
    *   **Instalação:** Siga as instruções do instalador do próprio Inno Setup.

### Passos para Compilar:
1.  **Clone o Repositório:** Certifique-se de ter uma cópia local de todos os arquivos do projeto Pochete 2.0, incluindo:
    *   `pochete_instalador_completo.iss` (o script principal do Inno Setup)
    *   `gui_processador_videos.py`
    *   A pasta `ffmpeg/` com `ffmpeg.exe` e `ffprobe.exe`
    *   `LEIAME.TXT`
    *   `CHANGELOG.md`
    *   `requirements.txt`
    *   `favicon.ico`
    Todos esses arquivos devem estar na mesma estrutura de pastas que no repositório.

2.  **Abra o Script no Inno Setup:**
    *   Inicie o "Inno Setup Compiler".
    *   Vá em `File > Open` (Arquivo > Abrir).
    *   Navegue até a pasta onde você clonou o repositório Pochete 2.0 e selecione o arquivo `pochete_instalador_completo.iss`.

3.  **Compile o Script:**
    *   Com o script aberto, você pode compilá-lo de duas maneiras:
        *   Pressionando `F9`.
        *   Clicando em `Build > Compile` (Construir > Compilar) no menu.
    *   O Inno Setup processará o script. Se não houver erros, ele criará o arquivo `Instalador_Pochete2.0.exe` na subpasta `output/` (relativa à localização do arquivo `.iss`).

4.  **Verifique a Saída:**
    *   Após a compilação bem-sucedida, você encontrará o `Instalador_Pochete2.0.exe` na pasta `output/`. Este é o instalador que você pode distribuir.

### Observações:
*   O script `pochete_instalador_completo.iss` está configurado para buscar os arquivos fonte (`gui_processador_videos.py`, `ffmpeg/`, etc.) em caminhos relativos à sua própria localização. Portanto, é crucial manter a estrutura de pastas do projeto.
*   Qualquer modificação nos arquivos fonte (como `gui_processador_videos.py`) exigirá uma nova compilação do instalador para que as alterações sejam incluídas.

## DOAÇÕES
Se você gosta deste aplicativo e deseja apoiar seu desenvolvimento,
considere fazer uma doação através do botão disponível na interface.

## CONTATO
- **Criador:** Enio Rocha
- **Email:** [eniodind@protonmail.com](mailto:eniodind@protonmail.com)
- **LinkedIn:** [Enio Rocha](https://www.linkedin.com/in/enio-rocha-138a01225?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)
- **WhatsApp:** [+55 34 99237-4363](https://wa.me/5534992374363)

---
Desenvolvido por Enio Rocha
[https://github.com/enioxt](https://github.com/enioxt)
