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
   Você pode encontrá-lo na seção "Releases" deste repositório.
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
- Se escolher um segmento, defina o tempo de início e fim
- Defina o nome do projeto (será usado para criar a pasta de saída)
- Defina o tamanho máximo por parte (em MB)
- Clique em "Iniciar Processamento"

### 3. MODOS DE PROCESSAMENTO:
- **Vídeo Completo:** Processa o vídeo inteiro. Se o tamanho final exceder o "Tamanho Máximo por Parte", ele será dividido.
- **Segmento Específico:** Extrai e processa apenas o trecho do vídeo entre o "Tempo de Início" e "Tempo de Fim" especificados. Se o segmento extraído exceder o "Tamanho Máximo por Parte", ele também será dividido.

### 4. ACOMPANHAMENTO:
- O progresso será exibido na área de logs da interface
- Ao final, uma mensagem indicará a conclusão e o local dos arquivos processados (geralmente em `Documentos\Pochete2.0\ProcessadorVideos\saida\[Nome do Projeto]\`)

### 5. DICAS:
- **Formato de Tempo:** Use `HH:MM:SS` (ex: `00:01:30` para 1 minuto e 30 segundos).
- **Nome do Projeto:** Evite caracteres especiais para garantir a compatibilidade com nomes de pastas.
- **Espaço em Disco:** Certifique-se de ter espaço suficiente para os vídeos processados.

## COMO FUNCIONA O PYTHON E AS DEPENDÊNCIAS
O Pochete 2.0 é desenvolvido em Python e utiliza algumas bibliotecas externas para funcionar. O instalador foi projetado para facilitar ao máximo a configuração para o usuário:

1.  **Verificação do Python:**
    *   O instalador primeiro verifica se o Python (versão 3.6 ou superior) já está instalado e acessível no PATH do sistema.
    *   Se uma versão compatível do Python for encontrada, o instalador a utilizará.
    *   Se o Python não for encontrado, ou se uma versão incompatível for detectada, o instalador oferecerá a opção de baixar e instalar uma versão recente do Python 3.x (versão *embeddable* que não interfere com outras instalações de Python no sistema, ou uma instalação completa se o usuário preferir e o instalador for configurado para tal).

2.  **Verificação das Bibliotecas (Tkinter, TQDM, Colorama):**
    *   **Tkinter:** Geralmente vem incluído na instalação padrão do Python e é usado para a interface gráfica.
    *   **TQDM:** Usado para exibir barras de progresso no console (útil durante o desenvolvimento e para logs detalhados).
    *   **Colorama:** Usado para adicionar cores aos textos no console (também mais relevante para desenvolvimento).
    *   O instalador verificará se essas bibliotecas estão disponíveis para o Python que será utilizado.
    *   Caso não estejam, e se o Python estiver sendo gerenciado pelo instalador (ou seja, se o usuário permitiu a instalação/configuração do Python pelo instalador), essas dependências podem ser instaladas automaticamente usando o `pip` (gerenciador de pacotes do Python).

3.  **FFmpeg e FFprobe:**
    *   Essas são ferramentas essenciais para manipulação de vídeo.
    *   O instalador do Pochete 2.0 **inclui** os executáveis `ffmpeg.exe` e `ffprobe.exe` e os copia para a pasta de instalação do aplicativo. O aplicativo é configurado para usar esses executáveis locais, não dependendo de uma instalação separada do FFmpeg no sistema do usuário.

O objetivo é que o usuário final precise apenas executar o instalador e seguir os passos, sem se preocupar com a instalação manual de cada componente.

## COMO COMPILAR O INSTALADOR (PARA DESENVOLVEDORES)
Se você é um desenvolvedor e deseja compilar o instalador `Instalador_Pochete2.0.exe` a partir do script Inno Setup (`pochete_instalador_completo.iss`), siga estes passos:

### Pré-requisitos:
*   **Inno Setup:** Você precisa ter o [Inno Setup](https://jrsoftware.org/isinfo.php) instalado em seu sistema.
*   **Arquivos Fonte do Projeto:** Certifique-se de ter todos os arquivos fonte do Pochete 2.0 em uma pasta no seu computador. Isso inclui:
    *   `gui_processador_videos.py`
    *   `pochete_instalador_completo.iss` (o script do Inno Setup)
    *   `LEIAME.TXT`
    *   `CHANGELOG.md`
    *   `requirements.txt`
    *   A pasta `ffmpeg/` contendo `ffmpeg.exe` e `ffprobe.exe`
    *   O arquivo de ícone, por exemplo, `favicon.ico`
    Todos esses arquivos devem estar na mesma estrutura de pastas que no repositório.

### Passos para Compilar:
1.  **Clone o Repositório (se ainda não o fez):**
    *   Obtenha a versão mais recente do código-fonte.

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
Se você gosta deste aplicativo e deseja apoiar seu desenvolvimento, considere fazer uma doação. Sua contribuição ajuda a manter o projeto ativo e em constante evolução!

Você pode doar através dos seguintes canais:
- **PIX (CPF - Enio Rocha):** `10689169663`
- **Bitcoin (BTC):** `bc1qua6c3dqka9kqt73a3xgfperl6jmffsefcr0g7n`
- **Solana (SOL):** `BaT6BPZo5bGvFTf5vPZyoa2YAw3QUi55e19pR6K9bBtz`
- **ETH/BASE/ARB/EVM:** `0x12e69a0D9571676F3e95007b99Ce02B207adB4b0`

Alternativamente, o botão "💚 Apoie o Projeto" na interface do aplicativo também exibe estas opções.

## 💰 TOKEN DO PROJETO E INTEGRAÇÃO BLOCKCHAIN
O Pochete 2.0, assim como outros projetos do ecossistema EGOS, explora a integração com tecnologias blockchain para promover transparência e novas formas de interação. O token $ETHIK faz parte desta visão.

O token $ETHIK está disponível nas seguintes redes:
- **HyperLiquid:** `0xEFC3c015E0CD02246e6b6CD5faA89e96a71Ec1E4`
- **Solana:** `DsLmsjwXschqEe5EnHFvv1oi5BNGoQin6VDN81Ufpump`
- **Base:** `0x633b346b85c4877ace4d47f7aa72c2a092136cb5`

## CONTATO
- **Criador:** Enio Rocha
- **Email:** [eniodind@protonmail.com](mailto:eniodind@protonmail.com)
- **LinkedIn:** [Enio Rocha](https://www.linkedin.com/in/enio-rocha-138a01225?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)
- **WhatsApp:** [+55 34 99237-4363](https://wa.me/5534992374363)

---
Desenvolvido por Enio Rocha
[https://github.com/enioxt](https://github.com/enioxt)
