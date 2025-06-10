import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import os
import time
from datetime import datetime
from pathlib import Path
import sys
import re

# Informações de doação
DOACOES = {
    "PIX (CPF - Enio Rocha)": "10689169663",
    "BTC": "bc1qua6c3dqka9kqt73a3xgfperl6jmffsefcr0g7n",
    "SOL": "BaT6BPZo5bGvFTf5vPZyoa2YAw3QUi55e19pR6K9bBtz",
    "ETH/BASE/ARB/EVM": "0x12e69a0D9571676F3e95007b99Ce02B207adB4b0"
}

# Informações de contato
CONTATOS = {
    "WhatsApp": "34992374363",
    "Email": "enioxt@gmail.com",
    "GitHub": "https://github.com/enioxt"
}

# Constantes para nomes de diretórios e scripts
PYTHON_DIR_NAME = "python_embutido"
SOURCE_DIR_NAME = "codigo_fonte"
CORE_SCRIPT_NAME = "nucleo_processador_videos.py"

# Determinar o diretório base da aplicação
try:
    if getattr(sys, 'frozen', False):
        INSTALL_BASE_DIR = Path(sys.executable).parent
    else:
        INSTALL_BASE_DIR = Path(__file__).resolve().parent
except NameError:
    INSTALL_BASE_DIR = Path(".").resolve()

class AppProcessadorVideos(tk.Tk): 
    def __init__(self):
        super().__init__()
        self.style = ttk.Style(self)
        try:
            # Attempt to set a more modern theme if available
            # 'clam', 'alt', 'default', 'classic' are standard ttk themes
            self.style.theme_use('clam') 
        except tk.TclError:
            # Fallback to default if 'clam' is not available or causes issues
            print("INFO: 'clam' theme not available, using default.")
            # self.style.theme_use('default') # Optionally explicitly set default
            
        # Configurar estilos para mensagens coloridas
        self.style.configure("Success.TLabel", foreground="dark green", font=("Segoe UI", 10))
        self.style.configure("Error.TLabel", foreground="dark red", font=("Segoe UI", 10))
        self.style.configure("Warning.TLabel", foreground="#CC7000", font=("Segoe UI", 10))


        self.title("Pochete 2.0 - Processador de Vídeos") 
        
        # Definir o tamanho da janela primeiro
        window_width = 650
        window_height = 550
        self.geometry(f"{window_width}x{window_height}")

        # Centralizar a janela na tela
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        # self.resizable(False, False) 

        self.nome_projeto = tk.StringVar()
        self.caminho_video = tk.StringVar()
        self.tamanho_maximo = tk.IntVar(value=37) 
        self.caminho_pasta_saida = tk.StringVar()
        self.default_output_path = str(INSTALL_BASE_DIR / "saida") # Definir como string
        self.caminho_pasta_saida.set(self.default_output_path) # Inicializar com o padrão
        
        # Novas variáveis para modo de processamento e tempos de segmento
        self.modo_processamento = tk.StringVar(value="completo") # "completo" ou "segmento"
        self.tempo_inicio = tk.StringVar() # Formato HH:MM:SS
        self.tempo_fim = tk.StringVar() # Formato HH:MM:SS
        self.erro_detectado = False
        self.mensagem_erro_ffmpeg = None
        
        # Trace para formatar automaticamente os campos de tempo
        self.tempo_inicio.trace_add("write", self.formatar_tempo_entrada)
        self.tempo_fim.trace_add("write", self.formatar_tempo_entrada)

        self.processo_subprocess = None
        self.processing_lock = threading.Lock()
        self.is_processing = False
        self.pedido_cancelamento = False # Nova flag para controle de cancelamento

        self.criar_widgets()
        
        # Verificar FFmpeg após criar os widgets para que self.log funcione corretamente
        self.verificar_ffmpeg()

    def _tempo_para_segundos(self, tempo_str):
        """Converte uma string de tempo HH:MM:SS para segundos com validação de limites."""
        if not tempo_str or not isinstance(tempo_str, str) or tempo_str.count(':') != 2:
            self.log(f"DEBUG: Formato de tempo inválido (não é string ou ':' incorreto): {tempo_str}", "debug")
            return None
        try:
            parts = tempo_str.split(':')
            if not (len(parts[0]) > 0 and len(parts[1]) > 0 and len(parts[2]) > 0):
                 self.log(f"DEBUG: Componente de tempo vazio detectado: {tempo_str}", "debug")
                 return None
            
            h, m, s = map(int, parts)
            if not (0 <= h and 0 <= m < 60 and 0 <= s < 60):
                self.log(f"DEBUG: Valor de tempo fora do intervalo: H={h}, M={m}, S={s}", "debug")
                return None
            return h * 3600 + m * 60 + s
        except ValueError:
            self.log(f"DEBUG: ValueError ao converter tempo para segundos: {tempo_str}", "debug")
            return None
        except Exception as e:
            self.log(f"DEBUG: Exceção inesperada em _tempo_para_segundos com '{tempo_str}': {e}", "debug")
            return None

    def _segundos_para_tempo(self, segundos_totais):
        """Converte segundos totais para uma string de tempo HHMMSS para nomes de arquivo."""
        if segundos_totais is None:
            # Retorna um valor que não causará erro se usado em cálculos ou formatação
            return "000000" 
        segundos_totais = int(segundos_totais)
        h = segundos_totais // 3600
        m = (segundos_totais % 3600) // 60
        s = segundos_totais % 60
        return f"{h:02d}{m:02d}{s:02d}"

    def _format_time_for_display(self, segundos_totais):
        """Converte segundos totais para uma string de tempo HH:MM:SS para display."""
        if segundos_totais is None:
            return "00:00:00"
        segundos_totais = int(segundos_totais)
        h = segundos_totais // 3600
        m = (segundos_totais % 3600) // 60
        s = segundos_totais % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _sanitize_filename(self, filename_str):
        """Remove caracteres inválidos de uma string para usá-la como nome de arquivo/pasta."""
        if not filename_str:
            return "projeto_sem_nome"
        # Remove caracteres que são problemáticos em nomes de arquivo/pasta em Windows/Linux/Mac
        # Mantém letras, números, espaços, hífens, underscores e pontos.
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', filename_str)
        # Substitui múltiplos espaços por um único espaço, depois remove espaços no início/fim
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        # Substitui espaços restantes por underscore
        sanitized = sanitized.replace(' ', '_')
        # Se após a sanitização a string ficar vazia ou só com pontos/underscores, retorna um padrão
        if not sanitized or all(c in '._' for c in sanitized):
            return "projeto_sanitizado"
        return sanitized

    def criar_widgets(self):
        quadro_principal = ttk.Frame(self, padding=10)  # Reduzido o padding de 15 para 10
        quadro_principal.pack(fill="both", expand=True)

        # --- Seção de Configuração ---
        self.quadro_config = ttk.LabelFrame(quadro_principal, text="Configurações do Processamento", padding=8)  # Reduzido o padding de 10 para 8
        self.quadro_config.pack(fill="x", pady=(0,8))  # Reduzido o pady de 10 para 8

        ttk.Label(self.quadro_config, text="Nome do Projeto:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_nome_projeto = ttk.Entry(self.quadro_config, textvariable=self.nome_projeto, width=50)
        self.entry_nome_projeto.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.quadro_config.grid_columnconfigure(1, weight=1) 

        self.btn_selecionar_video = ttk.Button(self.quadro_config, text="Selecionar Vídeo", command=self.selecionar_video)
        self.btn_selecionar_video.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.lbl_caminho_video = ttk.Label(self.quadro_config, text="Nenhum vídeo selecionado", foreground="grey", wraplength=450)
        self.lbl_caminho_video.grid(row=1, column=1, sticky="w", padx=5, pady=5)


        ttk.Label(self.quadro_config, text="Tamanho Máximo por Parte (MB):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_tamanho_maximo = ttk.Entry(self.quadro_config, textvariable=self.tamanho_maximo, width=10)
        self.entry_tamanho_maximo.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Modo de processamento
        ttk.Label(self.quadro_config, text="Modo de Processamento:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        modo_frame = ttk.Frame(self.quadro_config)
        modo_frame.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        self.radio_completo = ttk.Radiobutton(modo_frame, text="Processar Vídeo Completo", 
                                           variable=self.modo_processamento, value="completo", 
                                           command=self.atualizar_campos_segmento)
        self.radio_completo.pack(anchor="w")
        
        self.radio_segmento = ttk.Radiobutton(modo_frame, text="Extrair Segmento", 
                                          variable=self.modo_processamento, value="segmento", 
                                          command=self.atualizar_campos_segmento)
        self.radio_segmento.pack(anchor="w")
        
        # Tempos de segmento
        self.quadro_segmento = ttk.Frame(self.quadro_config)
        # Não exibe o quadro de segmento inicialmente, será exibido apenas quando o modo segmento for selecionado
        # self.quadro_segmento.grid(row=4, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.quadro_segmento, text="Tempo de Início (HH:MM:SS):").grid(row=0, column=0, sticky="w", padx=3, pady=3)
        self.entry_tempo_inicio = ttk.Entry(self.quadro_segmento, textvariable=self.tempo_inicio, width=10)
        self.entry_tempo_inicio.grid(row=0, column=1, sticky="w", padx=3, pady=3)
        
        ttk.Label(self.quadro_segmento, text="Tempo de Fim (HH:MM:SS):").grid(row=0, column=2, sticky="w", padx=3, pady=3)
        self.entry_tempo_fim = ttk.Entry(self.quadro_segmento, textvariable=self.tempo_fim, width=10)
        self.entry_tempo_fim.grid(row=0, column=3, sticky="w", padx=3, pady=3)
        
        # Configura os campos de segmento como desativados inicialmente
        self.entry_tempo_inicio.config(state=tk.DISABLED)
        self.entry_tempo_fim.config(state=tk.DISABLED)
        
        # Pasta de Saída
        ttk.Label(self.quadro_config, text="Pasta de Saída:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.lbl_caminho_pasta_saida = ttk.Label(self.quadro_config, text=self.default_output_path, foreground="grey", wraplength=350)
        self.lbl_caminho_pasta_saida.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        self.btn_selecionar_pasta_saida = ttk.Button(self.quadro_config, text="Selecionar Pasta", command=self.selecionar_pasta_saida)
        self.btn_selecionar_pasta_saida.grid(row=5, column=2, sticky="e", padx=5, pady=5)
        
        # Botão de Doação
        estilo_doacao = ttk.Style()
        estilo_doacao.configure("Doacao.TButton", font=("Segoe UI", 9, "bold"))
        
        # Frame para o botão de doação no canto superior direito do quadro_config
        frame_doacao = ttk.Frame(self.quadro_config)
        frame_doacao.grid(row=0, column=2, sticky="ne", padx=5, pady=5)
        
        self.btn_doacao = ttk.Button(frame_doacao, text="❤️ Apoiar", style="Doacao.TButton", command=self.mostrar_doacoes)
        self.btn_doacao.pack(padx=0, pady=0)

        # --- Botões de Ação ---
        quadro_acoes = ttk.Frame(quadro_principal, padding=5)
        quadro_acoes.pack(fill="x", pady=(10,10))

        self.btn_processar = ttk.Button(quadro_acoes, text="Iniciar Processamento", command=self.iniciar_processamento, style="Accent.TButton")
        self.btn_processar.pack(side=tk.LEFT, padx=5, pady=5, expand=True)

        self.btn_cancelar = ttk.Button(quadro_acoes, text="Cancelar Processamento", command=self.cancelar_processamento, state=tk.DISABLED)
        self.btn_cancelar.pack(side=tk.RIGHT, padx=5, pady=5, expand=True)

        # --- Seção de Status e Log ---
        status_frame = ttk.LabelFrame(quadro_principal, text="Status e Log", padding=5)
        status_frame.pack(fill="both", expand=True, pady=(0,5))   

        self.progress = ttk.Progressbar(status_frame, length=400, mode='indeterminate')
        self.progress.pack(fill="x", pady=3)
        self.progress['value'] = 0

        self.text_log = tk.Text(status_frame, height=18, wrap="word", borderwidth=1, relief="solid", font=("Consolas", 9)) # Aumentado height e usando fonte monospace
        log_scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.text_log.yview)
        self.text_log['yscrollcommand'] = log_scrollbar.set
        log_scrollbar.pack(side="right", fill="y")
        self.text_log.pack(fill="both", expand=True, pady=3)

        # --- Quadro Inferior para Botão de Doações ---
        quadro_inferior = ttk.Frame(quadro_principal, padding=(0, 2, 0, 0)) # Reduzido padding superior
        quadro_inferior.pack(fill='x', side='bottom', pady=(2,0)) # Reduzido pady

        # Botão de doações com ícone de coração verde
        self.btn_doar = ttk.Button(quadro_inferior, text="💚 Apoie o Projeto (PIX/BTC/ETH/SOL)", command=self.mostrar_doacoes)
        self.btn_doar.pack(pady=(0, 2)) # Reduzido pady

        # Estilo para o botão de processar
        # self.style is initialized in __init__
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=5)

    def configurar_validacao_tempo(self):
        """Configura os validadores e bindings para os campos de tempo"""
        # Registrar função de validação para limitar a 8 caracteres (incluindo os dois pontos)
        vcmd = (self.register(self.validar_entrada_tempo), '%P', '%d', '%i', '%s')
        
        # Aplicar validador aos campos de tempo
        self.entry_tempo_inicio.config(validate="key", validatecommand=vcmd)
        self.entry_tempo_fim.config(validate="key", validatecommand=vcmd)
        
        # Adicionar bindings para teclas especiais
        self.entry_tempo_inicio.bind('<KeyPress>', self.gerenciar_teclas_especiais)
        self.entry_tempo_fim.bind('<KeyPress>', self.gerenciar_teclas_especiais)
        
        # Adicionar trace para formatar automaticamente
        self.tempo_inicio.trace_add("write", self.formatar_tempo_entrada)
        self.tempo_fim.trace_add("write", self.formatar_tempo_entrada)
    
    def validar_entrada_tempo(self, valor_proposto, tipo_acao, indice, valor_anterior):
        """Valida a entrada de tempo, limitando a 8 caracteres (HH:MM:SS) e apenas dígitos e :"""
        # Permitir apagar caracteres
        if tipo_acao == '0':  # Deletar
            return True
            
        # Limitar a 8 caracteres (HH:MM:SS)
        if len(valor_proposto) > 8:
            return False
            
        # Verificar se o novo caractere é válido (dígito ou :)
        if tipo_acao == '1':  # Inserir
            novo_char = valor_proposto[int(indice)]
            if not (novo_char.isdigit() or novo_char == ':'):
                return False
                
        # Limitar a 6 dígitos no total
        digitos = sum(1 for c in valor_proposto if c.isdigit())
        if digitos > 6:
            return False
            
        return True
        
    def gerenciar_teclas_especiais(self, event):
        """Gerencia teclas especiais como backspace para permitir apagar os dois pontos"""
        if event.keysym == 'BackSpace':
            entry = event.widget
            cursor_pos = entry.index(tk.INSERT)
            
            # Se o cursor estiver após um ':', permitir apagá-lo
            if cursor_pos > 0 and entry.get()[cursor_pos-1:cursor_pos] == ':':
                # Obter variável associada ao entry
                var = self.tempo_inicio if entry == self.entry_tempo_inicio else self.tempo_fim
                valor_atual = var.get()
                
                # Remover o ':' e o caractere anterior
                novo_valor = valor_atual[:cursor_pos-2] + valor_atual[cursor_pos:]
                
                # Desativar trace temporariamente
                try:
                    var.trace_remove("write", var.trace_info()[0][1])
                    var.set(novo_valor)
                    entry.icursor(cursor_pos-2)  # Reposicionar o cursor
                    var.trace_add("write", self.formatar_tempo_entrada)
                    return "break"  # Impedir o comportamento padrão
                except (IndexError, tk.TclError) as e:
                    print(f"Erro ao gerenciar backspace: {e}")
        
        return None  # Permitir comportamento padrão para outras teclas
    
    def formatar_tempo_entrada(self, name, index, mode):
        """Formata automaticamente os campos de tempo no formato HH:MM:SS e pula para o próximo campo"""
        # Identifica qual variável está sendo modificada
        if name == str(self.tempo_inicio):
            var = self.tempo_inicio
            entry = self.entry_tempo_inicio
            next_entry = self.entry_tempo_fim  # Próximo campo após tempo_inicio
        else:
            var = self.tempo_fim
            entry = self.entry_tempo_fim
            next_entry = None  # Não há próximo campo após tempo_fim
        
        # Obtém o valor atual
        valor_atual = var.get()
        
        # Remove caracteres não permitidos (apenas dígitos e dois pontos são válidos)
        valor_limpo = ''.join(c for c in valor_atual if c.isdigit() or c == ':')
        if valor_limpo != valor_atual:
            try:
                var.trace_remove("write", var.trace_info()[0][1])
                var.set(valor_limpo)
                var.trace_add("write", self.formatar_tempo_entrada)
                return
            except (IndexError, tk.TclError) as e:
                print(f"Erro ao limpar caracteres inválidos: {e}")
        
        # Obter posição do cursor após possível limpeza
        cursor_pos = entry.index(tk.INSERT)
        
        # Ajustar posição do cursor para casos específicos
        # Se o cursor estiver antes de um ':', mova-o para depois
        if cursor_pos < len(valor_atual) and valor_atual[cursor_pos:cursor_pos+1] == ':':
            entry.icursor(cursor_pos + 1)
        
        # Lógica para inserção automática de dois pontos
        if valor_atual.replace(":", "").isdigit():  # Verifica se contém apenas dígitos e :
            # Caso 1: Usuário digitou 2 dígitos (HH), adicionar :
            if len(valor_atual) == 2 and ":" not in valor_atual:
                try:
                    var.trace_remove("write", var.trace_info()[0][1])
                    var.set(valor_atual + ":")
                    self.after(10, lambda: entry.icursor(3))  # Posiciona o cursor após o HH: com pequeno delay
                    var.trace_add("write", self.formatar_tempo_entrada)
                except (IndexError, tk.TclError) as e:
                    print(f"Erro ao adicionar primeiro dois pontos: {e}")
            
            # Caso 2: Usuário digitou 5 caracteres (HH:MM), adicionar segundo :
            elif len(valor_atual) == 5 and valor_atual.count(":") == 1 and valor_atual[2] == ":":
                try:
                    var.trace_remove("write", var.trace_info()[0][1])
                    var.set(valor_atual + ":")
                    self.after(10, lambda: entry.icursor(6))  # Posiciona o cursor após o HH:MM: com pequeno delay
                    var.trace_add("write", self.formatar_tempo_entrada)
                except (IndexError, tk.TclError) as e:
                    print(f"Erro ao adicionar segundo dois pontos: {e}")
            
            # Caso 3: Formato completo HH:MM:SS, pular para o próximo campo
            elif len(valor_atual) == 8 and valor_atual[2] == ":" and valor_atual[5] == ":":
                # Verificar se é o campo de início e pular para o campo de fim
                if next_entry and name == str(self.tempo_inicio):
                    self.after(50, lambda: next_entry.focus())  # Pequeno delay para evitar problemas
        
        # Se o usuário apagar tudo, limpa o campo
        if not valor_atual:
            return
    
    def atualizar_campos_segmento(self):
        """Atualiza a visibilidade dos campos de tempo de segmento com base no modo de processamento selecionado"""
        if self.modo_processamento.get() == "segmento":
            self.quadro_segmento.grid(row=4, column=0, columnspan=3, sticky="w", padx=5, pady=5)
            self.entry_tempo_inicio.config(state=tk.NORMAL)
            self.entry_tempo_fim.config(state=tk.NORMAL)
        else:
            self.quadro_segmento.grid_remove()  # Esconde o quadro de segmento
            self.tempo_inicio.set("")  # Limpa os valores
            self.tempo_fim.set("")
            self.entry_tempo_inicio.config(state=tk.DISABLED)
            self.entry_tempo_fim.config(state=tk.DISABLED)
    
    def update_ui_for_processing_state(self, is_processing):
        """Atualiza a interface de acordo com o estado do processamento."""
        self.is_processing = is_processing
        input_state = tk.DISABLED if is_processing else tk.NORMAL

        # --- Progress Bar and Overlay on quadro_config ---
        if is_processing:
            if hasattr(self, 'progress'):
                self.progress.start(10)
            
            if hasattr(self, 'quadro_config'): # Ensure quadro_config exists
                if not hasattr(self, 'overlay_on_config_frame'):
                    # Create overlay as a child of quadro_config
                    self.overlay_on_config_frame = ttk.Frame(self.quadro_config, style="Overlay.TFrame")
                    
                    # Configure style for the overlay frame (once)
                    if not hasattr(self, '_overlay_style_configured_config'):
                        self.style.configure("Overlay.TFrame", background="whitesmoke") # Or any other suitable color
                        self._overlay_style_configured_config = True

                    overlay_label_text = "Processando vídeo... Por favor, aguarde."
                    self.overlay_label_on_config = ttk.Label(
                        self.overlay_on_config_frame,
                        text=overlay_label_text,
                        font=("Segoe UI", 12, "bold"),
                        foreground="#0066CC", # Azul mais vibrante
                        background="whitesmoke" # Match frame background
                    )
                    self.overlay_label_on_config.pack(pady=40, padx=20, expand=True, fill="both", anchor="center")
                
                # Place and lift the overlay to cover quadro_config
                self.overlay_on_config_frame.place(x=0, y=0, relwidth=1, relheight=1)
                self.overlay_on_config_frame.lift()
            else:
                self.log("AVISO: self.quadro_config não encontrado para aplicar overlay.", "warning")

        else: # Not processing
            if hasattr(self, 'overlay_on_config_frame'):
                self.overlay_on_config_frame.place_forget()
            
            if hasattr(self, 'progress'):
                self.progress.stop()
                self.progress['value'] = 0

        # --- State of Main Control Buttons (Processar, Cancelar) ---
        if hasattr(self, 'btn_processar'):
            self.btn_processar.config(state=tk.DISABLED if is_processing else tk.NORMAL)
        if hasattr(self, 'btn_cancelar'):
            self.btn_cancelar.config(state=tk.NORMAL if is_processing else tk.DISABLED)

        # --- State of Input Widgets within self.quadro_config ---
        widgets_in_config_frame = [
            getattr(self, 'entry_nome_projeto', None),
            getattr(self, 'entry_tamanho_maximo', None),
            getattr(self, 'btn_selecionar_video', None),
            getattr(self, 'btn_selecionar_pasta_saida', None),
            getattr(self, 'radio_completo', None),
            getattr(self, 'radio_segmento', None),
            getattr(self, 'entry_tempo_inicio', None),
            getattr(self, 'entry_tempo_fim', None)
        ]

        for widget in widgets_in_config_frame:
            if widget:
                try:
                    widget.config(state=input_state)
                except tk.TclError as e:
                    self.log(f"AVISO: Não foi possível configurar o estado do widget {widget}: {e}", "warning")
        
        # --- Specific State for Time Entries when NOT Processing ---
        if not is_processing:
            if hasattr(self, 'atualizar_campos_segmento'):
                self.atualizar_campos_segmento()
    
    def selecionar_pasta_saida(self):
        caminho = filedialog.askdirectory(title="Selecione a Pasta de Saída")
        if caminho:
            self.caminho_pasta_saida.set(caminho)
            self.lbl_caminho_pasta_saida.config(text=caminho, foreground='black')
        else:
            # Se o usuário cancelar, redefinir para o padrão se não houver seleção anterior válida
            # ou manter a seleção atual se já houver uma.
            # Para simplificar, vamos sempre mostrar o valor atual de self.caminho_pasta_saida
            current_path_display = self.caminho_pasta_saida.get()
            if not current_path_display or not Path(current_path_display).is_dir(): # Se inválido ou vazio, volta ao default
                self.caminho_pasta_saida.set(self.default_output_path)
                self.lbl_caminho_pasta_saida.config(text=self.default_output_path, foreground='grey')
            else: # Mantém o caminho válido atual
                 self.lbl_caminho_pasta_saida.config(text=current_path_display, foreground='black')

    def selecionar_video(self):
        caminho = filedialog.askopenfilename(
            title="Selecione um arquivo de vídeo",
            filetypes=[("Arquivos de Vídeo", "*.mp4 *.mkv *.avi *.mov *.flv *.wmv *.mpeg *.mpg *.webm *.3gp"), ("Todos os arquivos", "*.*")]
        )
        if caminho:
            self.caminho_video.set(caminho)
            self.lbl_caminho_video.config(text=os.path.basename(caminho), foreground="black")
        else:
            self.caminho_video.set("")
            self.lbl_caminho_video.config(text="Nenhum vídeo selecionado", foreground="gray")

    def _log_on_main_thread(self, full_message, level_tag):
        self.text_log.config(state=tk.NORMAL)
        self.text_log.insert(tk.END, full_message + "\n", level_tag)
        self.text_log.see(tk.END)
        self.text_log.config(state=tk.DISABLED)
        self.update_idletasks()

    def log(self, message, level="info"):
        """Adiciona uma mensagem ao log de forma thread-safe e rola para o final.
        
        Args:
            message: Texto da mensagem.
            level: Tipo da mensagem ('info', 'success', 'error', 'warning', 'debug').
        """
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Formato com milissegundos
        
        level_map = {
            "info": "INFO:",
            "success": "SUCCESS:",
            "error": "ERRO:",
            "warning": "AVISO:",
            "debug": "DEBUG:"
        }
        prefix = level_map.get(level.lower(), "LOG:")
        full_message = f"{timestamp_str} [{prefix}] {message}"
        
        # Definir tags de cores. É seguro chamar tag_configure múltiplas vezes.
        self.text_log.tag_configure("success", foreground="dark green")
        self.text_log.tag_configure("error", foreground="dark red")
        self.text_log.tag_configure("warning", foreground="#CC7000")
        self.text_log.tag_configure("info", foreground="black") # Cor padrão para info
        self.text_log.tag_configure("debug", foreground="blue") # Cor para debug

        level_tag = level.lower() if level.lower() in ["success", "error", "warning", "debug"] else "info"

        if threading.current_thread() is not threading.main_thread():
            if hasattr(self, 'master') and self.master and self.master.winfo_exists():
                self.master.after(0, lambda: self._log_on_main_thread(full_message, level_tag))
            else:
                # Fallback se a GUI não estiver disponível
                print(full_message)
        else:
            self._log_on_main_thread(full_message, level_tag)

        # Opcionalmente, imprimir no console também, independentemente da thread
        if hasattr(self, 'print_to_console') and self.print_to_console.get():
            print(full_message)

    def obter_duracao_video(self, caminho_video):
        """Obtém a duração do vídeo em segundos usando FFprobe."""
        try:
            # Encontrar o caminho do FFprobe
            caminho_ffprobe = "ffprobe"  # Assumimos que está no PATH
            
            # Comando FFprobe para obter a duração
            comando = [caminho_ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", 
                      "default=noprint_wrappers=1:nokey=1", caminho_video]
            
            # Executar o comando
            resultado = subprocess.run(comando, capture_output=True, text=True)
            
            # Verificar se o comando foi bem-sucedido
            if resultado.returncode == 0 and resultado.stdout.strip():
                # Converter a saída para float (segundos)
                return float(resultado.stdout.strip())
            else:
                self.log(f"AVISO: Não foi possível obter a duração do vídeo: {resultado.stderr}", "warning")
                return None
        except Exception as e:
            self.log(f"AVISO: Erro ao obter duração do vídeo: {str(e)}", "warning")
            return None

    def _calcular_tempo_segmento_por_bitrate(self, caminho_video, tamanho_max_mb):
        """Calcula o tempo de segmento em segundos para atingir tamanho_max_mb com base no bitrate do vídeo."""
        try:
            caminho_ffprobe = "ffprobe"
            # Comando para obter bitrate em bits/segundo
            comando_bitrate = [caminho_ffprobe, "-v", "error", "-select_streams", "v:0", 
                               "-show_entries", "stream=bit_rate", "-of", 
                               "default=noprint_wrappers=1:nokey=1", caminho_video]
            
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            resultado_bitrate = subprocess.run(comando_bitrate, capture_output=True, text=True, check=True, startupinfo=startupinfo)
            bitrate_str = resultado_bitrate.stdout.strip()

            # Variável para armazenar o bitrate de áudio
            audio_bitrate_bps = 0

            # Obter também o bitrate de áudio se disponível
            try:
                comando_audio_bitrate = [caminho_ffprobe, "-v", "error", "-select_streams", "a:0", 
                                        "-show_entries", "stream=bit_rate", "-of", 
                                        "default=noprint_wrappers=1:nokey=1", caminho_video]
                resultado_audio = subprocess.run(comando_audio_bitrate, capture_output=True, text=True, check=True, startupinfo=startupinfo)
                audio_bitrate_str = resultado_audio.stdout.strip()
                if audio_bitrate_str and audio_bitrate_str.lower() != 'n/a':
                    audio_bitrate_bps = float(audio_bitrate_str)
                    self.log(f"INFO: Bitrate de áudio detectado: {audio_bitrate_bps / 1000:.2f} kbps", "info")
            except Exception as e:
                self.log(f"DEBUG: Não foi possível obter bitrate de áudio: {str(e)}", "debug")

            if not bitrate_str or bitrate_str.lower() == 'n/a': # Se ffprobe não retornar bitrate (e.g. imagem) ou for N/A
                # Tenta obter o bitrate do formato geral se o stream específico não tiver
                comando_format_bitrate = [caminho_ffprobe, "-v", "error", "-show_entries", "format=bit_rate", 
                                          "-of", "default=noprint_wrappers=1:nokey=1", caminho_video]
                resultado_format_bitrate = subprocess.run(comando_format_bitrate, capture_output=True, text=True, check=True, startupinfo=startupinfo)
                bitrate_str = resultado_format_bitrate.stdout.strip()
                if not bitrate_str or bitrate_str.lower() == 'n/a':
                    self.log(f"AVISO: Bitrate não disponível para {os.path.basename(caminho_video)}. Usando heurística de 1MB = 8s.", "warning")
                    return tamanho_max_mb * 8 # Heurística mais conservadora que 10s

            bitrate_bps = float(bitrate_str)
            if bitrate_bps <= 0:
                self.log(f"AVISO: Bitrate inválido ({bitrate_bps} bps) para {os.path.basename(caminho_video)}. Usando heurística de 1MB = 8s.", "warning")
                return tamanho_max_mb * 8

            # Tamanho máximo em bits (MB * 1024 * 1024 * 8)
            tamanho_max_bits = tamanho_max_mb * 1024 * 1024 * 8
            
            # Considerar o bitrate total (vídeo + áudio) e aplicar fator de segurança
            bitrate_total = bitrate_bps + audio_bitrate_bps
            
            # Fator de ajuste para compensar overhead do container e outros metadados (0.85 = 15% de margem)
            fator_seguranca = 0.85
            
            # Cálculo de tempo ajustado com margem de segurança
            tempo_segmento_segundos = (tamanho_max_bits / bitrate_total) * fator_seguranca
            
            self.log(f"INFO: Bitrate total detectado: {bitrate_total / 1000000:.2f} Mbps (vídeo: {bitrate_bps / 1000000:.2f} Mbps, áudio: {audio_bitrate_bps / 1000:.2f} kbps)", "info")
            self.log(f"INFO: Tempo de segmento calculado com ajuste de precisão: {tempo_segmento_segundos:.2f}s para {tamanho_max_mb}MB (fator de segurança: {fator_seguranca:.2f})", "info")
            
            return tempo_segmento_segundos
        except subprocess.CalledProcessError as e:
            self.log(f"AVISO: FFprobe falhou ao obter bitrate para {os.path.basename(caminho_video)}: {e.stderr}. Usando heurística de 1MB = 8s.", "warning")
            return tamanho_max_mb * 8
        except ValueError as e:
            self.log(f"AVISO: Erro ao converter bitrate para float ({bitrate_str}): {e}. Usando heurística de 1MB = 8s.", "warning")
            return tamanho_max_mb * 8
        except Exception as e:
            self.log(f"AVISO: Erro inesperado ao calcular tempo de segmento por bitrate para {os.path.basename(caminho_video)}: {str(e)}. Usando heurística de 1MB = 8s.", "warning")
            return tamanho_max_mb * 8
    
    def iniciar_processamento(self):
        """Inicia o processamento do vídeo"""
        # Validação básica
        if not self.nome_projeto.get().strip():
            messagebox.showerror("Erro de Validação", "Por favor, informe um Nome de Projeto.")
            return
        if not self.caminho_video.get() or not os.path.exists(self.caminho_video.get()):
            messagebox.showerror("Erro de Validação", "Por favor, selecione um arquivo de vídeo válido.")
            return
        

        if not self.tamanho_maximo.get() or self.tamanho_maximo.get() <= 0:
            messagebox.showerror("Erro de Validação", "O Tamanho Máximo por Parte deve ser um número positivo.")
            return
            
        # Atualiza a interface para o modo de processamento
        self.update_ui_for_processing_state(True)
        
        # Inicializar variáveis de controle de progresso
        self.tempo_atual_processo = 0
        self.tempo_inicio_processamento = time.time()
        
        # Preparar o comando para o ffmpeg
        try:
            # Criar diretório de saída principal se não existir
            pasta_saida = self.caminho_pasta_saida.get()
            if not os.path.exists(pasta_saida):
                os.makedirs(pasta_saida)
                
            # Nome base para os arquivos de saída
            nome_projeto_original = self.nome_projeto.get().strip()
            nome_projeto_sanitizado = self._sanitize_filename(nome_projeto_original)
            if nome_projeto_original != nome_projeto_sanitizado:
                self.log(f"INFO: Nome do projeto original '{nome_projeto_original}' sanitizado para '{nome_projeto_sanitizado}' para uso em caminhos.", "info")

            # Criar subpasta específica para o projeto dentro da pasta de saída
            pasta_projeto = os.path.join(pasta_saida, nome_projeto_sanitizado)
            if not os.path.exists(pasta_projeto):
                os.makedirs(pasta_projeto)
                self.log(f"INFO: Criada subpasta do projeto: {pasta_projeto}", "info")
            
            # Agora o caminho base para arquivos de saída é dentro da subpasta do projeto
            caminho_saida_base = os.path.join(pasta_projeto, nome_projeto_sanitizado)
            
            # Comando base do ffmpeg
            caminho_ffmpeg = "ffmpeg"
            comando_ffmpeg = [caminho_ffmpeg, "-y", "-i", self.caminho_video.get()]

            # Obter a duração total do vídeo ANTES de decidir o modo
            duracao_total_segundos_video = self.obter_duracao_video(self.caminho_video.get())
            if duracao_total_segundos_video is None:
                self.log("ERRO: Não foi possível determinar a duração do vídeo. Verifique o arquivo e o FFprobe.", "error")
                self.after(100, lambda: self.finalizar_processamento(False, "Falha ao obter duração do vídeo."))
                return
            self.log(f"INFO: Duração total do vídeo: {duracao_total_segundos_video:.2f} segundos", "info")
            self.duracao_total_original = duracao_total_segundos_video # Para cálculos de progresso
            
            # Configurar comando com base no modo de processamento
            tamanho_max_mb = self.tamanho_maximo.get()
            if self.modo_processamento.get() == "segmento":
                self.log("INFO: Modo de processamento: EXTRAÇÃO DE SEGMENTO", "info")
                tempo_inicio_str = self.tempo_inicio.get()
                tempo_fim_str = self.tempo_fim.get()

                # Validações de tempo (já existentes e corretas, mantidas)
                if not tempo_inicio_str or tempo_inicio_str.count(':') != 2:
                    self.log("ERRO: Tempo de início inválido. Use o formato HH:MM:SS.", "error")
                    self.after(100, lambda: self.finalizar_processamento(False, "Tempo de início inválido."))
                    return
                if not tempo_fim_str or tempo_fim_str.count(':') != 2:
                    self.log("ERRO: Tempo de fim inválido. Use o formato HH:MM:SS.", "error")
                    self.after(100, lambda: self.finalizar_processamento(False, "Tempo de fim inválido."))
                    return

                tempo_inicio_seg = self._tempo_para_segundos(tempo_inicio_str)
                tempo_fim_seg = self._tempo_para_segundos(tempo_fim_str)

                if tempo_inicio_seg is None or tempo_fim_seg is None:
                    self.after(100, lambda: self.finalizar_processamento(False, "Formato de tempo inválido."))
                    return

                if tempo_inicio_seg >= duracao_total_segundos_video:
                    msg_erro = f"Tempo de início ({self._format_time_for_display(tempo_inicio_seg)}) está além ou igual à duração do vídeo ({self._format_time_for_display(duracao_total_segundos_video)})."
                    self.log(f"ERRO: {msg_erro}", "error")
                    self.after(100, lambda: self.finalizar_processamento(False, msg_erro))
                    return
                
                if tempo_fim_seg > duracao_total_segundos_video:
                    self.log(f"AVISO: Tempo de fim ({self._format_time_for_display(tempo_fim_seg)}) ajustado para a duração total do vídeo ({self._format_time_for_display(duracao_total_segundos_video)}).", "warning")
                    tempo_fim_seg = duracao_total_segundos_video
                
                if tempo_fim_seg <= tempo_inicio_seg:
                    msg_erro = f"Tempo de fim ({self._format_time_for_display(tempo_fim_seg)}) deve ser maior que o tempo de início ({self._format_time_for_display(tempo_inicio_seg)})."
                    self.log(f"ERRO: {msg_erro}", "error")
                    self.after(100, lambda: self.finalizar_processamento(False, msg_erro))
                    return

                duracao_segmento_seg = tempo_fim_seg - tempo_inicio_seg
                if duracao_segmento_seg <= 0: # Checagem extra
                    msg_erro = "Duração do segmento calculada é zero ou negativa."
                    self.log(f"ERRO: {msg_erro}", "error")
                    self.after(100, lambda: self.finalizar_processamento(False, msg_erro))
                    return
                
                self.duracao_total_original = duracao_segmento_seg # Para barra de progresso no modo segmento

                ts_inicio_fn = self._segundos_para_tempo(tempo_inicio_seg) # HHMMSS
                ts_fim_fn = self._segundos_para_tempo(tempo_fim_seg)       # HHMMSS
                nome_arquivo_segmento_base = f"{caminho_saida_base}_segmento_{ts_inicio_fn}_a_{ts_fim_fn}.mp4"
                
                nome_arquivo_segmento = nome_arquivo_segmento_base
                contador = 1
                while os.path.exists(nome_arquivo_segmento): # Evitar sobrescrever
                    nome_arquivo_segmento = f"{nome_arquivo_segmento_base.rsplit('.', 1)[0]}_{contador}.mp4"
                    contador += 1
                
                self.log(f"INFO: Arquivo de segmento de saída: {os.path.basename(nome_arquivo_segmento)}", "info")
                self.log(f"INFO: Extraindo de {self._format_time_for_display(tempo_inicio_seg)} até {self._format_time_for_display(tempo_fim_seg)} (Duração: {self._format_time_for_display(duracao_segmento_seg)}).", "info")

                # Comando FFmpeg para extrair segmento único.
                # -ss ANTES de -i para seek rápido. -t DEPOIS de -i para duração precisa.
                comando_ffmpeg = [
                    caminho_ffmpeg, "-hide_banner", "-nostats", "-loglevel", "info",
                    "-ss", str(tempo_inicio_seg),
                    "-i", self.caminho_video.get(),
                    "-t", str(duracao_segmento_seg),
                    "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k",
                    "-map", "0", # Mapeia todos os streams (vídeo, áudio, legendas se houver)
                    "-avoid_negative_ts", "make_zero", # Evita timestamps negativos que podem ocorrer com cortes precisos
                    nome_arquivo_segmento
                ]
                # Nota: O -y global (sobrescrever) pode não ser necessário se já estamos gerando nomes únicos.
                # Mas para FFmpeg, -y no início é comum para evitar prompts interativos.

            elif self.modo_processamento.get() == "completo":
                self.log("INFO: Modo de processamento: COMPLETO", "info")
                self.duracao_total_original = duracao_total_segundos_video

                tempo_segmento_calculado = self._calcular_tempo_segmento_por_bitrate(self.caminho_video.get(), tamanho_max_mb)
                
                if tempo_segmento_calculado <= 0:
                    self.log("AVISO: Cálculo de tempo de segmento inválido ou vídeo muito pequeno. Tentando processar como arquivo único.", "warning")
                    # Define um valor alto para forçar o processamento como arquivo único
                    tempo_segmento_calculado = duracao_total_segundos_video + 1 

                if duracao_total_segundos_video <= tempo_segmento_calculado:
                    self.log(f"INFO: Vídeo ({self._format_time_for_display(duracao_total_segundos_video)}) será processado como arquivo único.", "info")
                    nome_arquivo_saida_unico_base = f"{caminho_saida_base}_completo.mp4"
                    
                    nome_arquivo_saida_unico = nome_arquivo_saida_unico_base
                    contador = 1
                    while os.path.exists(nome_arquivo_saida_unico): # Evitar sobrescrever
                        nome_arquivo_saida_unico = f"{nome_arquivo_saida_unico_base.rsplit('.', 1)[0]}_{contador}.mp4"
                        contador += 1

                    self.log(f"INFO: Arquivo de saída: {os.path.basename(nome_arquivo_saida_unico)}", "info")
                    
                    comando_ffmpeg = [
                        caminho_ffmpeg, "-y", "-hide_banner", "-nostats", "-loglevel", "info",
                        "-i", self.caminho_video.get(),
                        "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k",
                        "-map", "0",
                        nome_arquivo_saida_unico
                    ]
                else:
                    self.log(f"INFO: Vídeo ({self._format_time_for_display(duracao_total_segundos_video)}) será dividido em partes de ~{self._format_time_for_display(tempo_segmento_calculado)}.", "info")
                    comando_ffmpeg = [
                        caminho_ffmpeg, "-y", "-hide_banner", "-nostats", "-loglevel", "info",
                        "-i", self.caminho_video.get(),
                        "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k",
                        "-map", "0",
                        "-segment_time", str(int(tempo_segmento_calculado)),
                        "-f", "segment",
                        "-reset_timestamps", "1", # Importante para que cada segmento comece do zero
                        f"{caminho_saida_base}_parte%03d.mp4"
                    ]
            else: # Modo desconhecido
                self.log(f"ERRO: Modo de processamento desconhecido: {self.modo_processamento.get()}", "error")
                self.after(100, lambda: self.finalizar_processamento(False, "Modo de processamento desconhecido."))
                return 
            
            self.log(f"Iniciando processamento do vídeo: {os.path.basename(self.caminho_video.get())}")
            self.log(f"Modo: {self.modo_processamento.get().upper()}")
            self.log(f"Tamanho máximo por parte: {tamanho_max_mb} MB")
            self.log(f"Comando FFmpeg: {' '.join(comando_ffmpeg)}", "info") # Log do comando para depuração
            
            # Iniciar o processo
            self.processo_subprocess = subprocess.Popen(
                comando_ffmpeg,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=False,
                bufsize=0  # Usar buffer padrão em vez de buffer de linha (1)
            )
            
            # Iniciar thread para monitorar a saída do processo
            def monitorar_processo():
                try:
                    if self.processo_subprocess:
                        for linha in iter(self.processo_subprocess.stdout.readline, b''):
                            if not self.processo_subprocess:  # Checa se foi cancelado
                                self.log("DEBUG: Loop de saída interrompido")
                                break
                            self.processar_saida(linha)
                        
                        # Verificar o código de retorno quando o processo terminar
                        return_code = self.processo_subprocess.wait()
                        
                        # Log FFmpeg exit details
                        self.log(f"DEBUG: FFmpeg process finished. Return code: {return_code}", "info")
                        
                        # Check self.erro_detectado which is set in processar_saida
                        current_erro_detectado_status = self.erro_detectado 
                        self.log(f"DEBUG: Status of self.erro_detectado before finalizing: {current_erro_detectado_status}", "info")
                        if current_erro_detectado_status and self.mensagem_erro_ffmpeg:
                            self.log(f"DEBUG: First FFmpeg error message captured: {self.mensagem_erro_ffmpeg}", "info")

                        # Determinar se o processamento foi bem-sucedido
                        sucesso = (return_code == 0 and not current_erro_detectado_status)
                        self.log(f"DEBUG: Calculated success status: {sucesso}", "info")
                        
                        # Finalizar o processamento na thread principal
                        self.after(100, lambda: self.finalizar_processamento(sucesso))
                        
                except Exception as e:
                    self.log(f"ERRO FATAL durante o monitoramento do processo: {str(e)}", "error")
                    # Garantir que o processamento seja finalizado mesmo em caso de erro no monitoramento
                    self.after(100, lambda: self.finalizar_processamento(False, f"Erro interno no monitoramento: {str(e)}"))
            
            # Iniciar thread para monitoramento
            threading.Thread(target=monitorar_processo, daemon=True).start()

        except FileNotFoundError as e:
            mensagem_erro_final = f"Erro: FFmpeg ou arquivo de vídeo não encontrado. Verifique o caminho e as permissões: {str(e)}"
            self.log(mensagem_erro_final, "error")
            self.after(100, lambda: self.finalizar_processamento(False, mensagem_erro_final))
        except PermissionError as e:
            mensagem_erro_final = f"Erro de Permissão: Não foi possível acessar o FFmpeg, o vídeo ou a pasta de saída: {str(e)}"
            self.log(mensagem_erro_final, "error")
            self.after(100, lambda: self.finalizar_processamento(False, mensagem_erro_final))
        except Exception as e:
            self.log(f"ERRO FATAL ao iniciar processo: {str(e)} Type: {type(e)}", "error")
            mensagem_erro_final = f"Erro inesperado ao iniciar o processo FFmpeg: {str(e)}"
            self.after(100, lambda: self.finalizar_processamento(False, mensagem_erro_final))
    
    # A linha abaixo deve ser o início do próximo método, por exemplo, processar_saida
    # Se o método processar_saida foi engolido pela edição anterior, precisará ser restaurado ou verificado.
    # Para este replace, assumimos que o próximo método começa após este comentário.
    def processar_saida(self, linha):
        """Processa uma linha de saída do subprocesso"""
        if linha:
            linha_decodificada = linha.decode('utf-8', errors='replace').strip()
            if linha_decodificada:
                # Verificar se a linha contém informações de progresso do FFmpeg
                # O padrão é algo como: frame=  943 fps= 31 q=29.0 size=    3072kB time=00:00:31.43 bitrate= 800.8kbits/s speed=1.05x
                if 'time=' in linha_decodificada and self.duracao_total_original > 0:
                    try:
                        # Extrair o tempo atual
                        time_index = linha_decodificada.find('time=')
                        if time_index != -1:
                            time_str = linha_decodificada[time_index + 5:].split(' ')[0]
                            # Converter o tempo (formato HH:MM:SS.ss) para segundos
                            if ':' in time_str:
                                h, m, s = time_str.split(':')
                                tempo_segundos = float(h) * 3600 + float(m) * 60 + float(s)
                                self.tempo_atual_processo = tempo_segundos
                                
                                # Calcular porcentagem de progresso
                                porcentagem = min(100, (tempo_segundos / self.duracao_total_original) * 100)
                                
                                # Calcular tempo estimado restante
                                if tempo_segundos > 0 and self.tempo_inicio_processamento:
                                    tempo_decorrido = time.time() - self.tempo_inicio_processamento
                                    velocidade = tempo_segundos / tempo_decorrido  # segundos de vídeo por segundo real
                                    tempo_restante = (self.duracao_total_original - tempo_segundos) / velocidade
                                    minutos_restantes = int(tempo_restante / 60)
                                    segundos_restantes = int(tempo_restante % 60)
                                    
                                    # Atualizar a mensagem de overlay com o progresso
                                    if hasattr(self, 'overlay_label_on_config'):
                                        nova_mensagem = f"Processando vídeo... {porcentagem:.1f}%\n"
                                        nova_mensagem += f"Tempo restante estimado: {minutos_restantes}m {segundos_restantes}s"
                                        self.overlay_label_on_config.configure(text=nova_mensagem)
                                    
                                    # Log do progresso a cada 10%
                                    if int(porcentagem) % 10 == 0 and int(porcentagem) > 0:
                                        self.log(f"INFO: Progresso: {porcentagem:.1f}% - Tempo restante estimado: {minutos_restantes}m {segundos_restantes}s", "info")
                    except Exception as e:
                        self.log(f"DEBUG: Erro ao processar progresso: {str(e)}", "debug")
                
                # Determinar o tipo de mensagem baseado no conteúdo
                tipo_msg = "info"
                termos_erro_ffmpeg = [
                    "error", "corrupt", "no pts found",
                    "could not find tag for codec", "codec not currently supported",
                    "could not write header", "invalid argument", "conversion failed",
                    "erro", "corrompido", "invalid data"
                ]
                
                # Termos que são apenas avisos, não erros críticos
                termos_aviso_ffmpeg = [
                    "non-monotonic dts",
                    "queue input is backward in time"
                ]
                linha_lower = linha_decodificada.lower()
                
                # Lógica para identificar se é um erro relevante do FFmpeg
                is_ffmpeg_error = False
                is_ffmpeg_warning = False
                
                # Verificar se a linha contém um aviso conhecido (não tratado como erro)
                if any(termo in linha_lower for termo in termos_aviso_ffmpeg):
                    is_ffmpeg_warning = True
                    tipo_msg = "warning"
                # Verificar erros apenas se não for um aviso conhecido
                elif any(termo in linha_lower for termo in termos_erro_ffmpeg):
                    # Evitar falsos positivos para "invalid argument" se não for um erro real de escrita/conversão
                    if "invalid argument" in linha_lower and not (
                        "could not write header" in linha_lower or 
                        "conversion failed" in linha_lower or 
                        "unable to find a suitable output format" in linha_lower or
                        "output file #0 does not contain any stream" in linha_lower
                    ):
                        pass # Provavelmente não é um erro fatal isolado, pode ser um aviso
                    else:
                        is_ffmpeg_error = True

                if is_ffmpeg_error:
                    tipo_msg = "error"
                    self.erro_detectado = True
                    if self.mensagem_erro_ffmpeg is None: # Captura a primeira mensagem de erro relevante
                        self.mensagem_erro_ffmpeg = linha_decodificada
                    # Log específico para corrupção, se detectado
                    if "corrupt" in linha_lower or "corrompido" in linha_lower or "invalid data" in linha_lower:
                         self.log("ALERTA: Arquivo de vídeo pode estar corrompido ou inválido (detectado pelo FFmpeg).", "warning") # Mudado para warning para não duplicar o erro geral
                elif "warning" in linha_lower or "aviso" in linha_lower:
                    tipo_msg = "warning"
                elif "success" in linha_lower or "sucesso" in linha_lower or "concluído" in linha_lower:
                    tipo_msg = "success" 
                elif "warning" in linha_decodificada.lower() or "aviso" in linha_decodificada.lower():
                    tipo_msg = "warning"
                elif "success" in linha_decodificada.lower() or "sucesso" in linha_decodificada.lower() or "concluído" in linha_decodificada.lower():
                    tipo_msg = "success"
                    
                self.log(linha_decodificada, tipo_msg)
    
    def cancelar_processamento(self):
        """Solicita o cancelamento do processamento em andamento."""
        with self.processing_lock:
            if self.is_processing and self.processo_subprocess:
                self.log("INFO: Solicitação de cancelamento recebida...", "warning")
                self.pedido_cancelamento = True
                try:
                    # Envia um sinal de terminação. O monitorar_processo lidará com a finalização.
                    if self.processo_subprocess.poll() is None: # Verifica se o processo ainda está rodando
                        self.processo_subprocess.terminate()
                        self.log("INFO: Sinal de terminação enviado ao processo FFmpeg.", "info")
                    else:
                        self.log("INFO: Processo FFmpeg já havia terminado ao tentar cancelar.", "info")
                except Exception as e:
                    self.log(f"ERRO ao tentar enviar sinal de terminação: {str(e)}", "error")
            elif not self.is_processing:
                self.log("INFO: Nenhum processamento em andamento para cancelar.", "info")
    
    def finalizar_processamento(self, sucesso=True, mensagem_final_override=None):
        """Finaliza o processamento, atualiza a interface e informa o usuário."""
        with self.processing_lock: # Garante que a finalização seja atômica
            self.log(f"INFO: Finalizando processamento. Sucesso: {sucesso}, Pedido Cancelamento: {self.pedido_cancelamento}", "info")
            
            final_message = ""
            final_level = "info"

            if self.pedido_cancelamento:
                final_message = mensagem_final_override if mensagem_final_override else "Processamento cancelado pelo usuário."
                final_level = "warning"
                sucesso = False # Cancelamento é uma forma de não sucesso
            elif mensagem_final_override:
                final_message = mensagem_final_override
                final_level = "success" if sucesso else "error"
            elif sucesso:
                final_message = "O processamento do vídeo foi concluído com êxito!"
                final_level = "success"
            else: # Falha no processamento não cancelado
                final_message = "Ocorreu um erro durante o processamento do vídeo."
                if self.mensagem_erro_ffmpeg:
                    final_message += f"\n\nDetalhes do FFmpeg (primeira ocorrência de erro relevante):\n{self.mensagem_erro_ffmpeg}"
                final_message += "\n\nPor favor, verifique a aba 'Log de Processamento' para mais detalhes."
                final_message += "\nSe o erro persistir, o arquivo de vídeo pode estar corrompido, ou pode haver um problema com a configuração do FFmpeg ou com os parâmetros fornecidos."
                final_level = "error"

            self.log(f"{final_level.upper()}: {final_message}", final_level)

            # Limpar estado do processo
            if self.processo_subprocess:
                if self.processo_subprocess.poll() is None: # Se ainda estiver rodando por algum motivo
                    self.log("AVISO: Processo FFmpeg ainda estava ativo na finalização. Tentando kill.", "warning")
                    try:
                        self.processo_subprocess.kill()
                        self.processo_subprocess.wait(timeout=5) # Espera um pouco após o kill
                    except Exception as e:
                        self.log(f"ERRO ao tentar forçar kill na finalização: {e}", "error")
            self.processo_subprocess = None
            self.is_processing = False # Certifica que is_processing é False
            self.erro_detectado = False # Reset para a próxima execução
            self.mensagem_erro_ffmpeg = None # Reset para a próxima execução
            
            self.update_ui_for_processing_state(False) # Garante que a UI está totalmente redefinida
            
            # Mostrar janela de status final personalizada
            self.mostrar_janela_status_final(sucesso, final_message, self.pedido_cancelamento)

            self.pedido_cancelamento = False # Reset da flag para a próxima execução
            


    def mostrar_janela_status_final(self, sucesso, mensagem, cancelado):
        """Mostra uma janela de status final (sucesso, erro, cancelado) usando messagebox."""
        if cancelado:
            title = "🟡 Processamento Cancelado"
            messagebox.showwarning(title, mensagem, parent=self)
        elif sucesso:
            title = "✅ Sucesso no Processamento"
            messagebox.showinfo(title, mensagem, parent=self)
        else:
            title = "❌ Erro no Processamento"
            messagebox.showerror(title, mensagem, parent=self)

    def mostrar_doacoes(self):
        janela_doacao = tk.Toplevel(self)
        janela_doacao.title("💚 Apoie o Desenvolvimento do Pochete 2.0")
        # Definir o tamanho da janela primeiro
        popup_width = 650
        popup_height = 580
        janela_doacao.geometry(f"{popup_width}x{popup_height}")

        # Centralizar a janela de doação em relação à janela principal
        # Obter a posição e tamanho da janela principal
        main_window_x = self.winfo_x()
        main_window_y = self.winfo_y()
        main_window_width = self.winfo_width()
        main_window_height = self.winfo_height()

        # Calcular a posição central para o popup
        center_x = main_window_x + int((main_window_width - popup_width) / 2)
        center_y = main_window_y + int((main_window_height - popup_height) / 2)

        janela_doacao.geometry(f"{popup_width}x{popup_height}+{center_x}+{center_y}")
        janela_doacao.resizable(False, False)
        janela_doacao.transient(self) # Mantém a janela de doação na frente da principal
        janela_doacao.grab_set() # Bloqueia interação com a janela principal

        style = ttk.Style(janela_doacao)
        style.configure("Copy.TButton", font=("Segoe UI", 8))
        style.configure("Link.TButton", font=("Segoe UI", 8), foreground="blue")
        style.configure("Green.TLabel", foreground="dark green", font=("Segoe UI", 11, "bold"))
        # Definir o estilo para Readonly.TEntry no style local da janela de doação
        style.map("Readonly.TEntry",
                  foreground=[('readonly', 'black')],
                  fieldbackground=[('readonly', '#ECECEC')])
        style.configure("Readonly.TEntry", padding=(2, 2, 2, 2))

        # Título principal
        ttk.Label(janela_doacao, text="Sua contribuição ajuda a manter o projeto vivo e evoluindo!", 
                  style="Green.TLabel").pack(pady=(15,10))

        # Seção de doações
        doacoes_frame = ttk.LabelFrame(janela_doacao, text="Opções de Doação - Enio Rocha", padding=10)
        doacoes_frame.pack(fill="x", padx=20, pady=10)
        
        for chave, valor in DOACOES.items():
            item_frame = ttk.Frame(doacoes_frame, padding=5)
            item_frame.pack(fill="x")
            ttk.Label(item_frame, text=chave + " ", width=20, anchor="e").pack(side="left")
            
            # Tratamento especial para o link do GitHub
            if chave == "GitHub":
                entrada = ttk.Entry(item_frame, width=45, style="Readonly.TEntry")
                entrada.insert(0, valor)
                entrada.config(state="readonly")
                entrada.pack(side="left", padx=5)
                
                # Botão para copiar
                ttk.Button(item_frame, text="Copiar", style="Copy.TButton", 
                           command=lambda v=valor: self.copiar_para_clipboard(v, janela_doacao)).pack(side="left", padx=(0,5))
                
                # Botão para abrir no navegador
                ttk.Button(item_frame, text="Abrir", style="Link.TButton", 
                           command=lambda v=valor: self.abrir_url(v)).pack(side="left")
            else:
                entrada = ttk.Entry(item_frame, width=45, style="Readonly.TEntry")
                entrada.insert(0, valor)
                entrada.config(state="readonly")
                entrada.pack(side="left", padx=5)
                ttk.Button(item_frame, text="Copiar", style="Copy.TButton", 
                           command=lambda v=valor: self.copiar_para_clipboard(v, janela_doacao)).pack(side="left")

        # Seção de contatos
        contatos_frame = ttk.LabelFrame(janela_doacao, text="Contatos - Enio Rocha", padding=10)
        contatos_frame.pack(fill="x", padx=20, pady=10)
        
        for chave, valor in CONTATOS.items():
            item_frame = ttk.Frame(contatos_frame, padding=5)
            item_frame.pack(fill="x")
            ttk.Label(item_frame, text=chave + " ", width=20, anchor="e").pack(side="left")
            
            entrada = ttk.Entry(item_frame, width=45, style="Readonly.TEntry")
            entrada.insert(0, valor)
            entrada.config(state="readonly")
            entrada.pack(side="left", padx=5)
            ttk.Button(item_frame, text="Copiar", style="Copy.TButton", 
                       command=lambda v=valor: self.copiar_para_clipboard(v, janela_doacao)).pack(side="left")

        # Mensagem de colaboração
        mensagem_frame = ttk.LabelFrame(janela_doacao, text="Convite à Colaboração", padding=10)
        mensagem_frame.pack(fill="x", padx=20, pady=10)
        
        mensagem = "Você tem ideias para novas ferramentas de processamento de vídeo ou recursos adicionais para o Pochete? "
        mensagem += "Estou sempre aberto a sugestões e parcerias para desenvolver soluções que atendam às necessidades dos usuários."
        mensagem += "\n\nSe você tem conhecimentos em programação, design de interface, ou simplesmente boas ideias, "
        mensagem += "podemos construir algo juntos! Suas contribuições podem ser em forma de código, documentação, testes ou ideias."
        mensagem += "\n\nAlguns exemplos de projetos possíveis:\n"
        mensagem += "- Ferramentas para edição automatizada de vídeos\n"
        mensagem += "- Soluções para compressão inteligente de arquivos de mídia\n"
        mensagem += "- Aplicativos para gerenciamento de coleções de vídeos\n"
        mensagem += "\nEntre em contato através dos canais acima e vamos transformar suas ideias em realidade!"
        
        ttk.Label(mensagem_frame, text=mensagem, wraplength=550, justify="center").pack(pady=5)

        ttk.Label(janela_doacao, text="Muito obrigado pelo seu apoio! 🙏", 
                  font=("Segoe UI", 10, "italic")).pack(pady=(15,10))
        
        # Botão fechar
        ttk.Button(janela_doacao, text="Fechar", command=janela_doacao.destroy).pack(pady=10)

    def verificar_ffmpeg(self):
        """Verifica se o FFmpeg está instalado e acessível."""
        try:
            # Usar startupinfo para suprimir a janela do console no Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True, startupinfo=startupinfo)
            self.log("INFO: FFmpeg detectado com sucesso.", "info")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            error_message = "ERRO: FFmpeg não encontrado ou não está funcionando corretamente. " \
                            "Por favor, instale o FFmpeg e adicione-o ao PATH do sistema para que o aplicativo funcione."
            self.log(error_message, "error")
            # Usar self.after para garantir que a messagebox apareça após a janela principal estar pronta
            self.after(100, lambda: messagebox.showerror("Erro Crítico: FFmpeg Ausente", error_message, parent=self))
            self.after(150, self.destroy) # Fechar a aplicação após o erro
            return False
        except Exception as e:
            error_message = f"ERRO inesperado ao verificar FFmpeg: {str(e)}. " \
                            "Verifique a instalação do FFmpeg e as permissões."
            self.log(error_message, "error")
            self.after(100, lambda: messagebox.showerror("Erro Crítico: FFmpeg Check", error_message, parent=self))
            self.after(150, self.destroy)
            return False

    def copiar_para_clipboard(self, valor, parent_window):
        try:
            self.clipboard_clear()
            self.clipboard_append(valor)
            messagebox.showinfo("Copiado!", f"'{valor}' copiado para a área de transferência!", parent=parent_window)
        except tk.TclError:
            messagebox.showwarning("Erro ao Copiar", "Não foi possível acessar a área de transferência.", parent=parent_window)

    def abrir_url(self, url):
        """Abre a URL no navegador padrão do sistema."""
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Erro ao abrir URL", f"Não foi possível abrir a URL: {str(e)}", parent=self)


    def on_closing(self):
        if self.is_processing:
            if messagebox.askyesno("Processamento em Andamento", 
                                   "Um processamento de vídeo está em andamento. Deseja cancelá-lo e sair?"):
                self.log("INFO: Usuário optou por cancelar o processamento e sair.")
                self.cancelar_processamento()
                # Adiciona um pequeno delay para garantir que o cancelamento seja processado antes de fechar
                self.after(100, self.destroy) 
            else:
                self.log("INFO: Usuário optou por não sair enquanto o processamento está em andamento.")
                # Não faz nada, mantém a janela aberta
        else:
            self.destroy()

if __name__ == "__main__":
    app = AppProcessadorVideos()
    app.protocol("WM_DELETE_WINDOW", app.on_closing) # Lida com o fechamento da janela
    app.mainloop()
