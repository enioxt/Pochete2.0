# Processador de Vídeo

**Versão: v0.2.0**

Uma ferramenta de interface gráfica (GUI) desenvolvida em Python com Tkinter para processar vídeos usando FFmpeg. Permite dividir vídeos grandes em partes menores com base em um tamanho máximo definido ou extrair segmentos específicos com base em tempos de início e fim.

## Funcionalidades

- **Modo de Processamento Completo**: Divide vídeos grandes em partes menores respeitando um tamanho máximo por arquivo (MB) definido pelo usuário, com uma margem de segurança de 15% para garantir que os arquivos não ultrapassem o limite.
- **Modo de Extração de Segmento**: Extrai segmentos específicos de um vídeo com base em tempos de início e fim fornecidos pelo usuário, aplicando automaticamente uma margem de segurança de 3 segundos.
- **Cancelamento Robusto**: Implementado um botão 'Cancelar' que interrompe corretamente o processo FFmpeg no Windows usando o comando `taskkill /F /PID {pid} /T`, permitindo que os usuários interrompam operações longas de processamento de vídeo.
- **Interface Gráfica Intuitiva**: Interface Tkinter que desabilita campos irrelevantes com base no modo selecionado (completo ou segmento) e gerencia o estado da UI durante o processamento (desabilita campos de entrada e botão 'Iniciar', habilita botão 'Cancelar').
- **Gestão de Estado da UI**: Um método centralizado para gerenciar a habilitação/desabilitação de widgets da UI com base no estado do processamento, redefinindo a UI ao estado inicial após cancelamento ou conclusão.
- **Sincronização Segura**: Uso de `threading.Lock` para acesso seguro ao handle do subprocesso FFmpeg, evitando problemas de concorrência.
- **Confirmação de Fechamento**: Ao tentar fechar a janela durante o processamento, o usuário é questionado se deseja cancelar a operação.
- **Criação Automática de Diretórios**: Garante que os diretórios de saída sejam criados antes da execução do FFmpeg, evitando falhas na gravação de arquivos.
- **Monitoramento de Progresso**: Exibe o progresso do processamento do FFmpeg na interface gráfica.

## Atualizações Recentes (v0.2.0)

- **Resolução de Caminhos FFmpeg/FFprobe**: Corrigidos problemas de 'arquivo não encontrado' instalando uma versão de sistema via `winget`, tornando o script dependente do PATH do sistema.
- **Correção de Bug de Segmentação**: Resolvido erro de `local variable 'part_number' referenced before assignment` ao processar segmentos pequenos como um único arquivo.
- **Margem de Segurança para Tamanho de Arquivo**: Ajustada para 15% abaixo do tamanho máximo estipulado pelo usuário, garantindo que os arquivos gerados fiquem dentro do limite (testado com sucesso para arquivos entre 28 e 36 MB para um limite de 37 MB).
- **Robustez na Interface**: Melhorias na entrada de tempo e no fluxo geral do script, tornando a ferramenta mais confiável.

## Instalação e Uso

Nenhuma instalação de Python, FFmpeg ou dependências é necessária!

1. Baixe o arquivo `Pochete_2.0.exe` da seção [Releases](https://github.com/enioxt/Pochete2.0/releases).
2. Execute o arquivo. Não é necessário instalar nada!
3. Caso o Windows exiba alertas de segurança, clique em "Mais informações" > "Executar assim mesmo".

### Resolvendo Bloqueios de Segurança
Como o aplicativo não possui uma assinatura digital, o Windows pode exibir alertas de segurança:

- **Aviso "Windows Protected Your PC"**: Clique em "Mais informações" e depois em "Executar assim mesmo".
- **SmartScreen ou Antivírus bloqueando**: Adicione o aplicativo às exceções do seu antivírus. Clique com o botão direito no arquivo > Propriedades > Desbloquear (se disponível).
- **Permissões de Administrador**: Em alguns casos, pode ser necessário executar como administrador (clique direito > Executar como administrador).
- **Problemas de Acesso a Pastas**: Certifique-se de que o aplicativo tenha permissões de escrita na pasta onde está sendo executado. Evite executar o aplicativo a partir de pastas protegidas como "Arquivos de Programas".

## Requisitos

- Windows 7 ou superior.
- Nenhuma instalação de Python ou FFmpeg é necessária. O executável já inclui tudo.

## Tecnologias Incluídas
O Pochete 2.0 é um aplicativo standalone que incorpora:

- **Python 3.9**: Linguagem de programação versátil e poderosa. [python.org](https://www.python.org/)
- **Tkinter**: Biblioteca gráfica nativa do Python.
- **FFmpeg**: Ferramenta poderosa para processamento de vídeo e áudio. [ffmpeg.org](https://ffmpeg.org/)
- **PyInstaller**: Empacotador de aplicativos Python. [pyinstaller.org](https://pyinstaller.org/)

## Uso

1. **Seleção de Modo**: Escolha entre 'Vídeo Completo' (para dividir o vídeo inteiro em partes) ou 'Cortar Segmento' (para extrair um segmento específico).
2. **Configurações**:
   - No modo 'Vídeo Completo', defina o tamanho máximo por arquivo (MB).
   - No modo 'Cortar Segmento', insira os tempos de início e fim do segmento desejado.
3. **Seleção de Arquivos**: Escolha o vídeo de entrada e a pasta de saída.
4. **Processamento**: Clique em 'Iniciar Processamento' para começar. Use o botão 'Cancelar Processamento' para interromper a operação a qualquer momento.
5. **Monitoramento**: Acompanhe o progresso na interface gráfica.

## Contribuição

Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias, correções de bugs ou novas funcionalidades.

## Licença

[Insira a licença escolhida aqui, se aplicável]

## Roadmap

Consulte o arquivo [ROADMAP.md](ROADMAP.md) para ver as funcionalidades planejadas e o progresso do desenvolvimento.
