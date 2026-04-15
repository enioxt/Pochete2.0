# Pochete 2.0 — Editor de Vídeo para Delegacias

**Ferramenta web para corte, análise e extração de vídeos — 100% no navegador, sem instalar nada.**

🌐 **Acesse online:** [video.egos.ia.br](https://video.egos.ia.br)

> Os vídeos **nunca saem da sua máquina** — todo o processamento acontece no próprio navegador.
> Não é necessário conta, login, nem conexão com internet após abrir a página.

---

## O que você pode fazer

| Recurso | Como usar |
|---------|-----------|
| ✂️ **Cortar trecho** | Define o início e fim na aba "Cortar" e clica em Exportar |
| 📷 **Capturar quadro** | Pausa o vídeo no momento certo e clica "Capturar Quadro" |
| 🔄 **Girar vídeo** | Seleciona a rotação na aba "Cortar" — preview ao vivo antes de exportar |
| 🎯 **Detectar Movimento** | Encontra automaticamente os momentos com movimento no vídeo |
| ✂️ **Enviar para corte** | Clica em "Enviar para Corte" em qualquer evento detectado — já preenche os horários |

---

## Como usar passo a passo

### 1. Abrir o vídeo

1. Acesse [video.egos.ia.br](https://video.egos.ia.br) no navegador
2. Clique em **"Carregar Vídeo"** ou arraste o arquivo para a área indicada
3. Aguarde o carregamento — o progresso aparece em %

> **Formatos suportados:** MP4, AVI, MOV, MKV, WebM e outros comuns

---

### 2. Encontrar movimento automaticamente

1. Clique na aba **"🎯 Detectar Movimento"**
2. Escolha a sensibilidade:
   - **Baixa** — só captura movimento intenso (pessoas, carros)
   - **Média** — equilíbrio recomendado para a maioria dos casos
   - **Alta** — captura qualquer mínimo deslocamento
3. Clique em **"Analisar Vídeo"**
4. Aguarde — o progresso aparece em tempo real
5. Os eventos aparecem em lista com:
   - Horário de início e fim
   - Miniatura do frame
   - **Intensidade do movimento** (0–100%) — passa o mouse para ver explicação

> **O que é a porcentagem de intensidade?**
> Mede quanto do quadro teve pixels que mudaram entre um frame e outro.
> 10% = pequeno deslocamento numa parte da tela. 80%+ = grande movimentação em quase toda a tela.

---

### 3. Cortar um trecho

#### Opção A — A partir do detector de movimento
1. Na lista de eventos, clique em **"Enviar para Corte"** no evento desejado
2. O sistema já preenche o início e fim automaticamente (com 2 segundos de margem)
3. Confira na aba "Cortar" e clique **"Exportar Corte"**

#### Opção B — Manualmente
1. Clique na aba **"✂️ Cortar"**
2. Use a timeline ou os campos de texto para definir início e fim
3. Clique **"Exportar Corte"** — o arquivo MP4 é baixado automaticamente

---

### 4. Girar vídeo

1. Na aba **"✂️ Cortar"**, encontre o seletor de rotação
2. Escolha: **90° horário**, **90° anti-horário** ou **180°**
3. O preview ao vivo mostra como ficará
4. Clique **"Exportar Corte"** para gerar o arquivo girado

---

### 5. Capturar uma imagem

1. Use a barra de progresso ou as setas do teclado para ir ao frame exato
2. Clique em **"📷 Capturar Quadro"**
3. A imagem PNG é baixada automaticamente

**Atalhos de teclado:**
- `Espaço` — play / pausar
- `←` / `→` — avançar ou voltar frame a frame
- `,` / `.` — pular 5 segundos

---

## Rodar localmente (sem internet)

Se precisar usar sem conexão:

```bash
# Linux / Mac
./iniciar.sh

# Windows
iniciar.bat
```

Ou manualmente:
```bash
python3 server.py
# Acesse: http://localhost:8080
```

> **Atenção:** O servidor local é necessário por questões técnicas do navegador (COOP/COEP headers).
> O processamento continua 100% local — nenhum dado é enviado para fora.

---

## Uso correto de evidências

- Este programa **não altera** o arquivo original — sempre trabalha com uma cópia na memória
- Ao exportar um corte, você recebe um **novo arquivo** — o original permanece intacto
- Para preservar cadeia de custódia: guarde o arquivo original separado antes de qualquer edição

---

## Versão

**v4.0** — Detector de movimento integrado, rotação com preview, player adaptável
