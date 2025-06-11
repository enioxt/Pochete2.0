# POCHETE 2.0 - PROCESSADOR DE VÍDEOS

## DESCRIÇÃO
O Pochete 2.0 é uma ferramenta com interface gráfica para processamento de vídeos que permite:
- Processar vídeos completos ou extrair segmentos específicos.
- Dividir vídeos grandes em partes menores com tamanho máximo configurável.
- Recodificar vídeos com configurações otimizadas.
- Interface amigável e intuitiva.

---

## NOVIDADES (v2.2 - Estabilidade e Controle)
- **Cancelamento Robusto:** Implementado um botão 'Cancelar' que interrompe corretamente o processo FFmpeg no Windows, permitindo que os usuários interrompam operações longas de processamento de vídeo.
- **Controle de Tamanho de Arquivo:** Ajustada a margem de segurança para 15% abaixo do tamanho máximo estipulado pelo usuário, garantindo que os arquivos gerados fiquem dentro do limite (testado com sucesso para arquivos entre 28 e 36 MB para um limite de 37 MB).
- **Criação Automática de Diretórios:** Garante que os diretórios de saída sejam criados antes da execução do FFmpeg, evitando falhas na gravação de arquivos.
- **Interface Adaptativa:** A interface desabilita campos irrelevantes com base no modo selecionado (completo ou segmento) e gerencia o estado durante o processamento.
- **Confirmação de Fechamento:** Ao tentar fechar a janela durante o processamento, o usuário é questionado se deseja cancelar a operação.

---

## REQUISITOS
- Windows 7 ou superior.
- Nenhuma dependência externa é necessária. O executável é autônomo.

## TECNOLOGIAS INCLUÍDAS
O Pochete 2.0 é um aplicativo standalone que incorpora:

### Python
O aplicativo foi desenvolvido em Python 3.9, uma linguagem de programação versátil e poderosa. O executável já inclui todos os módulos Python necessários, não sendo necessário instalar o Python separadamente.
- Site oficial: [python.org](https://www.python.org/)
- Biblioteca Tkinter para a interface gráfica

### FFmpeg
O processamento de vídeo é realizado pelo FFmpeg, uma das ferramentas mais poderosas e versáteis para manipulação de áudio e vídeo. Os binários do FFmpeg (ffmpeg.exe e ffprobe.exe) estão embutidos no executável.
- Site oficial: [ffmpeg.org](https://ffmpeg.org/)
- Versão incluída: FFmpeg 6.0 "Lancôme"

### PyInstaller
O executável standalone foi criado com PyInstaller, que empacota todos os componentes necessários em um único arquivo executável.
- Site oficial: [pyinstaller.org](https://pyinstaller.org/)

---

## INSTALAÇÃO E USO
Nenhuma instalação é necessária!
1. Vá para a seção **[Releases](https://github.com/enioxt/Pochete2.0/releases)** deste repositório.
2. Baixe o arquivo `Pochete_2.0.exe` da versão mais recente.
3. Execute o arquivo. É simples assim!

### Resolvendo Bloqueios de Segurança
Como o aplicativo não possui uma assinatura digital, o Windows pode exibir alertas de segurança:

1. **Aviso "Windows Protected Your PC"**: 
   - Clique em "Mais informações" e depois em "Executar assim mesmo".

2. **SmartScreen ou Antivírus bloqueando**:
   - Adicione o aplicativo às exceções do seu antivírus.
   - Clique com o botão direito no arquivo > Propriedades > Desbloquear (se disponível).

3. **Permissões de Administrador**:
   - Em alguns casos, pode ser necessário executar como administrador (clique direito > Executar como administrador).

4. **Problemas de Acesso a Pastas**:
   - Certifique-se de que o aplicativo tenha permissões de escrita na pasta onde está sendo executado.
   - Evite executar o aplicativo a partir de pastas protegidas como "Arquivos de Programas".

---

## MODOS DE PROCESSAMENTO
- **VÍDEO COMPLETO:** Processa o vídeo inteiro, dividindo-o em partes menores respeitando um tamanho máximo por arquivo (MB) definido pelo usuário, com uma margem de segurança de 15% para garantir que os arquivos não ultrapassem o limite.
- **CORTAR SEGMENTO:** Extrai um trecho específico do vídeo com base em tempos de início e fim fornecidos pelo usuário, aplicando automaticamente uma margem de segurança de 3 segundos.

---

## SUPORTE
Se você gosta deste aplicativo e deseja apoiar seu desenvolvimento, considere fazer uma doação através do botão "Apoiar o Projeto" disponível na interface.

Para problemas, por favor, abra um ticket na seção "Issues" do repositório.

---

Desenvolvido por **Enio Rocha**
[https://github.com/enioxt](https://github.com/enioxt)
