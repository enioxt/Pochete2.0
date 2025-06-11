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
import json

# --- Constantes da Aplicação ---
DOACOES = {
    "PIX (CPF - Enio Rocha)": "10689169663",
    "BTC": "bc1qua6c3dqka9kqt73a3xgfperl6jmffsefcr0g7n",
    "SOL": "BaT6BPZo5bGvFTf5vPZyoa2YAw3QUi55e19pR6K9bBtz",
    "ETH/BASE/ARB/EVM": "0x12e69a0D9571676F3e95007b99Ce02B207adB4b0"
}
CONTATOS = {
    "WhatsApp": "34992374363",
    "Email": "enioxt@gmail.com",
    "GitHub": "https://github.com/enioxt"
}

# Determinar o diretório base para a instalação de forma robusta
try:
    if getattr(sys, 'frozen', False):
        # O aplicativo está congelado (executável .exe)
        INSTALL_BASE_DIR = Path(sys.executable).parent
        # Para PyInstaller, os recursos estão em _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            RESOURCES_DIR = Path(sys._MEIPASS)
        else:
            RESOURCES_DIR = INSTALL_BASE_DIR
    else:
        # O aplicativo está rodando como um script .py
        INSTALL_BASE_DIR = Path(__file__).parent
        RESOURCES_DIR = INSTALL_BASE_DIR
except Exception:
    INSTALL_BASE_DIR = Path.cwd()
    RESOURCES_DIR = INSTALL_BASE_DIR

class InfoWindow(tk.Toplevel):
    """Janela de informações para Doações e Contatos."""
    def __init__(self, parent, title, data):
        super().__init__(parent)
        self.parent = parent
        self.title(title)

        # Define o ícone da aplicação
        self.icon_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'favicon.ico'))
        if os.path.exists(self.icon_path):
            self.iconbitmap(self.icon_path)
        
        # Janela com tamanho adequado para mostrar endereços completos
        self.geometry("650x380")
        self.transient(parent)
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()
        
        # Centraliza a janela em relação à janela pai
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

        # Estilo e cores
        bg_color = "#f0f0f0"  # Cinza claro para o fundo
        accent_color = "#4a6ea9"  # Azul para destaque
        
        # Configuração do estilo
        style = ttk.Style(self)
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=bg_color, font=("Segoe UI", 11, "bold"))
        style.configure("TButton", font=("Segoe UI", 9))
        style.configure("Copy.TButton", font=("Segoe UI", 9))
        style.configure("Close.TButton", font=("Segoe UI", 10))

        # Criação do frame principal com padding e cor de fundo
        main_frame = ttk.Frame(self, padding="20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título da janela
        header_label = ttk.Label(main_frame, text=title, style="Header.TLabel")
        header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Separador horizontal após o título
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # Adiciona os dados
        row = 2
        for label, value in data.items():
            # Label com o nome do campo
            ttk.Label(main_frame, text=f"{label}:", style="TLabel").grid(row=row, column=0, sticky="w", pady=8)
            
            # Frame para o valor e botão de cópia
            value_frame = ttk.Frame(main_frame, style="TFrame")
            value_frame.grid(row=row, column=1, sticky="w", pady=8)
            
            # Entry para o valor com estilo melhorado e largura aumentada para endereços blockchain
            entry = ttk.Entry(value_frame, width=55)
            entry.insert(0, value)
            entry.config(state="readonly")
            entry.pack(side=tk.LEFT, padx=(0, 5))
            
            # Botão de cópia com estilo melhorado
            copy_button = ttk.Button(value_frame, text="Copiar", style="Copy.TButton", 
                                    command=lambda e=entry: self.copy_to_clipboard(e.get()))
            copy_button.pack(side=tk.LEFT)
            
            row += 1

        # Separador antes do botão de fechar
        separator2 = ttk.Separator(main_frame, orient="horizontal")
        separator2.grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1

        # Botão de fechar centralizado e com estilo melhorado
        close_frame = ttk.Frame(main_frame, style="TFrame")
        close_frame.grid(row=row, column=0, columnspan=2)
        close_button = ttk.Button(close_frame, text="Fechar", style="Close.TButton", command=self.destroy, width=10)
        close_button.pack(pady=5)

    def copy_to_clipboard(self, text):
        """Copia o texto para a área de transferência e mostra feedback."""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        
        # Feedback visual de cópia bem-sucedida
        messagebox.showinfo("Copiado", "Informação copiada para a área de transferência!", parent=self)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

class TimePickerEntry(ttk.Entry):
    """Um widget de entrada com placeholder e formatação automática para HH:MM:SS."""
    def __init__(self, master=None, placeholder="HH:MM:SS", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = 'grey'
        self.default_fg_color = self['foreground']
        self.next_widget = None

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self.bind("<KeyRelease>", self._on_key_release)

        self._add_placeholder()

    def _add_placeholder(self, e=None):
        if not super().get():
            self.insert(0, self.placeholder)
            self['foreground'] = self.placeholder_color

    def _clear_placeholder(self, e=None):
        if super().get() == self.placeholder:
            self.delete(0, "end")
            self['foreground'] = self.default_fg_color

    def _on_key_release(self, e=None):
        if e.keysym not in ['BackSpace'] and (len(e.char) == 0 or not e.char.isprintable()):
            return

        current_text = super().get()
        just_digits = "".join(filter(str.isdigit, current_text))
        just_digits = just_digits[:6]

        formatted_text = ""
        if len(just_digits) > 0: formatted_text = just_digits[:2]
        if len(just_digits) > 2: formatted_text += ':' + just_digits[2:4]
        if len(just_digits) > 4: formatted_text += ':' + just_digits[4:6]

        self.unbind("<KeyRelease>")
        self.delete(0, "end")
        self.insert(0, formatted_text)
        self.icursor(len(formatted_text))
        self.bind("<KeyRelease>", self._on_key_release)

        if len(formatted_text) == 8 and self.next_widget:
            self.next_widget.focus_set()
            self.next_widget._clear_placeholder()

    def get(self):
        val = super().get()
        return val if val != self.placeholder else ""

class AppProcessadorVideos(tk.Tk): 
    def __init__(self):
        super().__init__()
        # --- Configuração de Estilo e Janela ---
        self._setup_styles()
        self.title("Pochete 2.0 - Processador de Vídeos")
        self._center_window(800, 580)
        self.minsize(800, 580)

        # --- Caminhos e Configurações ---
        # Tenta encontrar o FFmpeg em múltiplos locais possíveis
        ffmpeg_locations = [
            RESOURCES_DIR / "ffmpeg" / "ffmpeg.exe",  # Dentro do diretório de recursos do PyInstaller
            INSTALL_BASE_DIR / "ffmpeg" / "ffmpeg.exe",  # Relativo ao executável
            Path("ffmpeg") / "ffmpeg.exe",  # Relativo ao diretório atual
            Path("ffmpeg.exe"),  # No diretório atual
            Path(os.environ.get("PATH", "")).joinpath("ffmpeg.exe")  # No PATH do sistema
        ]
        
        ffprobe_locations = [
            RESOURCES_DIR / "ffmpeg" / "ffprobe.exe",  # Dentro do diretório de recursos do PyInstaller
            INSTALL_BASE_DIR / "ffmpeg" / "ffprobe.exe",  # Relativo ao executável
            Path("ffmpeg") / "ffprobe.exe",  # Relativo ao diretório atual
            Path("ffprobe.exe"),  # No diretório atual
            Path(os.environ.get("PATH", "")).joinpath("ffprobe.exe")  # No PATH do sistema
        ]
        
        # Encontra o primeiro caminho válido para cada binário
        self.ffmpeg_path = next((path for path in ffmpeg_locations if path.exists()), INSTALL_BASE_DIR / "ffmpeg" / "ffmpeg.exe")
        self.ffprobe_path = next((path for path in ffprobe_locations if path.exists()), INSTALL_BASE_DIR / "ffmpeg" / "ffprobe.exe")
        
        # Configura o diretório de saída
        self.default_output_path = INSTALL_BASE_DIR / 'saida'
        self.default_output_path.mkdir(exist_ok=True)

        # --- Variáveis de Estado ---
        self.processando = False
        self.cancelado = False
        self.sucesso = False
        self.processo_ffmpeg = None
        self.start_time = 0
        self.duracao_total_video_seg = None
        self.processing_lock = threading.Lock()
        self.bitrate_total_video_bps = 0
        self.audio_bitrate_bps = 0

        # --- Variáveis do Tkinter ---
        self.nome_projeto = tk.StringVar()
        self.caminho_video = tk.StringVar()
        self.caminho_pasta_saida = tk.StringVar(value=str(self.default_output_path))
        self.tamanho_maximo = tk.IntVar(value=37)
        self.modo_processamento = tk.StringVar(value="completo")
        self.abrir_pasta_ao_concluir = tk.BooleanVar(value=True)
        
        # --- UI ---
        self.criar_widgets()
        self.verificar_ffmpeg()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_styles(self):
        """Configura os estilos ttk para a aplicação."""
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam') 
        except tk.TclError:
            print("INFO: Tema 'clam' não disponível, usando o padrão.")
        self.style.configure("green.Horizontal.TProgressbar", foreground='#28a745', background='#28a745')

    def _center_window(self, width, height):
        """Centraliza a janela na tela."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - width / 2)
        center_y = int(screen_height/2 - height / 2)
        self.geometry(f'{width}x{height}+{center_x}+{center_y}')
    
    def _set_ui_state(self, processing):
        """Habilita/desabilita os widgets da UI com base no estado de processamento."""
        state = tk.DISABLED if processing else tk.NORMAL

        for widget in self.widgets_to_disable:
            if widget:
                widget.config(state=state)

        # O botão de cancelar tem o comportamento inverso
        self.btn_cancelar.config(state=tk.NORMAL if processing else tk.DISABLED)

    def criar_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.rowconfigure(9, weight=1)
        main_frame.columnconfigure(3, weight=1)

        # --- Linha 0: Nome do Projeto ---
        ttk.Label(main_frame, text="Nome do Projeto:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_nome_projeto = ttk.Entry(main_frame, textvariable=self.nome_projeto, width=60)
        self.entry_nome_projeto.grid(row=0, column=1, sticky=tk.EW, pady=2, columnspan=2)

        # --- Linha 1: Caminho do Vídeo ---
        ttk.Label(main_frame, text="Caminho do Vídeo:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_caminho_video = ttk.Entry(main_frame, textvariable=self.caminho_video, width=60, state='readonly')
        self.entry_caminho_video.grid(row=1, column=1, sticky=tk.EW, pady=2)
        self.btn_selecionar_video = ttk.Button(main_frame, text="Selecionar Vídeo", command=self.selecionar_video)
        self.btn_selecionar_video.grid(row=1, column=2, sticky=tk.W, padx=5)

        # --- Linha 2: Pasta de Saída ---
        ttk.Label(main_frame, text="Pasta de Saída:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_pasta_saida = ttk.Entry(main_frame, textvariable=self.caminho_pasta_saida, width=60, state='readonly')
        self.entry_pasta_saida.grid(row=2, column=1, sticky=tk.EW, pady=2)
        self.btn_selecionar_saida = ttk.Button(main_frame, text="Selecionar Pasta", command=self.selecionar_pasta_saida)
        self.btn_selecionar_saida.grid(row=2, column=2, sticky=tk.W, padx=5)

        # --- Canto Superior Direito: Apoio e Contato ---
        support_frame = ttk.Frame(main_frame)
        support_frame.grid(row=0, column=4, rowspan=3, sticky='ne', padx=5, pady=2)
        self.btn_apoio = ttk.Button(support_frame, text="Apoiar o Projeto", command=self.mostrar_info_doacao)
        self.btn_apoio.pack(fill=tk.X, pady=(0, 5))
        self.btn_contato = ttk.Button(support_frame, text="Contato", command=self.mostrar_info_contato)
        self.btn_contato.pack(fill=tk.X)

        # --- Configurações de Processamento ---
        ttk.Label(main_frame, text="Tamanho Máx. (MB):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.spin_tamanho_max = ttk.Spinbox(main_frame, from_=1, to=1000, textvariable=self.tamanho_maximo, width=5)
        self.spin_tamanho_max.grid(row=3, column=1, sticky=tk.W)

        ttk.Label(main_frame, text="Modo:").grid(row=4, column=0, sticky=tk.W, pady=5)
        modo_frame = ttk.Frame(main_frame)
        modo_frame.grid(row=4, column=1, columnspan=3, sticky=tk.W)
        self.radio_modo_completo = ttk.Radiobutton(modo_frame, text="Vídeo Completo", variable=self.modo_processamento, value="completo", command=self.atualizar_campos_segmento)
        self.radio_modo_completo.pack(side=tk.LEFT, padx=5)
        self.radio_modo_segmento = ttk.Radiobutton(modo_frame, text="Cortar Segmento", variable=self.modo_processamento, value="segmento", command=self.atualizar_campos_segmento)
        self.radio_modo_segmento.pack(side=tk.LEFT, padx=5)

        # --- Frame de Segmento ---
        self.frame_segmento = ttk.Labelframe(main_frame, text="Configuração do Segmento", padding="10")
        self.frame_segmento.grid(row=5, column=0, columnspan=5, sticky=tk.EW, pady=5, padx=5)
        self.lbl_video_duration = ttk.Label(self.frame_segmento, text="Duração do vídeo: N/A", font=('TkDefaultFont', 10, 'bold'))
        self.lbl_video_duration.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        ttk.Label(self.frame_segmento, text="Início:").grid(row=1, column=0, sticky=tk.W)
        self.entry_inicio = TimePickerEntry(self.frame_segmento)
        self.entry_inicio.grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(self.frame_segmento, text="Fim:").grid(row=2, column=0, sticky=tk.W)
        self.entry_fim = TimePickerEntry(self.frame_segmento)
        self.entry_fim.grid(row=2, column=1, sticky=tk.W, padx=5)
        self.entry_inicio.next_widget = self.entry_fim

        # --- Ações, Progresso e Log ---
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=6, column=0, columnspan=4, pady=10)
        self.btn_processar = ttk.Button(action_frame, text="Processar Vídeo", command=self.iniciar_processamento)
        self.btn_processar.pack(side=tk.LEFT, padx=5)
        self.btn_cancelar = ttk.Button(action_frame, text="Cancelar", command=self.cancelar_processamento, state=tk.DISABLED)
        self.btn_cancelar.pack(side=tk.LEFT, padx=5)
        self.check_abrir_pasta = ttk.Checkbutton(action_frame, text="Abrir pasta ao concluir", variable=self.abrir_pasta_ao_concluir)
        self.check_abrir_pasta.pack(side=tk.LEFT, padx=15)

        self.barra_progresso = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate', style="green.Horizontal.TProgressbar")
        self.barra_progresso.grid(row=7, column=0, columnspan=4, sticky=tk.EW, pady=5)
        self.lbl_status_progresso = ttk.Label(main_frame, text="")
        self.lbl_status_progresso.grid(row=8, column=0, columnspan=4, sticky=tk.W)
        
        log_frame = ttk.Labelframe(main_frame, text="Log de Operações", padding="10")
        log_frame.grid(row=9, column=0, columnspan=4, sticky="nsew", pady=5)
        self.log_text = tk.Text(log_frame, height=10, state='disabled', wrap=tk.WORD, font=("Consolas", 9))
        log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text['yscrollcommand'] = log_scrollbar.set
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Configuração de Cores para o Log ---
        self.log_text.tag_config("INFO", foreground="black")
        self.log_text.tag_config("SUCCESS", foreground="#28a745") # Verde
        self.log_text.tag_config("WARN", foreground="#ffc107") # Amarelo/Laranja
        self.log_text.tag_config("ERROR", foreground="#dc3545") # Vermelho
        self.log_text.tag_config("CRITICAL", foreground="#dc3545", font=("TkDefaultFont", 9, "bold"))
        self.log_text.tag_config("FFMPEG", foreground="#6c757d") # Cinza

        self.atualizar_campos_segmento()

        # Lista de widgets para desabilitar durante o processamento
        self.widgets_to_disable = [
            self.entry_nome_projeto, self.entry_caminho_video, self.entry_pasta_saida,
            self.btn_selecionar_video, self.btn_selecionar_saida, self.btn_apoio, self.btn_contato,
            self.spin_tamanho_max, self.radio_modo_completo, self.radio_modo_segmento,
            self.entry_inicio, self.entry_fim, self.btn_processar, self.check_abrir_pasta
        ]

    def log(self, message, level='INFO'):
        """Adiciona uma mensagem ao log de forma segura para threads."""
        if not message: return
        now = datetime.now().strftime('%H:%M:%S')
        level_map = {"INFO": "INFO", "ERROR": "ERRO", "WARN": "AVISO", "FFMPEG": "FFMPEG"}
        formatted_message = f"[{now}] [{level_map.get(level, 'LOG')}]: {message}\n"
        
        def _update_log():
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, formatted_message, level)
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')
        
        # Garante que a atualização da UI ocorra na thread principal
        self.after(0, _update_log)

    def verificar_ffmpeg(self):
        """Verifica se FFmpeg e FFprobe existem nos caminhos definidos."""
        # Tenta encontrar o FFmpeg no sistema
        if not self.ffmpeg_path.exists() or not self.ffprobe_path.exists():
            # Tenta usar o FFmpeg do PATH do sistema
            try:
                # Verifica se o FFmpeg está disponível no PATH
                subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                self.ffmpeg_path = Path("ffmpeg")
                
                # Verifica se o FFprobe está disponível no PATH
                subprocess.run(["ffprobe", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                self.ffprobe_path = Path("ffprobe")
                
                self.log(f"[INFO]: Usando FFmpeg e FFprobe do PATH do sistema", 'INFO')
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                self.log(f"[ERRO]: FFmpeg ou FFprobe não encontrado!\nCaminhos verificados:\n{self.ffmpeg_path}\n{self.ffprobe_path}", 'ERROR')
                messagebox.showerror("Erro Crítico", f"FFmpeg ou FFprobe não encontrado!\nCaminhos verificados:\n{self.ffmpeg_path}\n{self.ffprobe_path}")
                return False
        return True

    def selecionar_video(self):
        caminho = filedialog.askopenfilename(title="Selecione o arquivo de vídeo")
        if not caminho: return
        
        self.caminho_video.set(caminho)
        if not self.nome_projeto.get():
            self.nome_projeto.set(Path(caminho).stem)
        
        self.log(f"Vídeo selecionado: {caminho}")
        self.lbl_video_duration.config(text="Duração: Obtendo...")
        threading.Thread(target=self._obter_e_atualizar_duracao_video, args=(caminho,), daemon=True).start()

    def _obter_e_atualizar_duracao_video(self, video_path):
        """Obtém a duração do vídeo em uma thread e atualiza a UI."""
        duration_seconds = self.get_video_duration_seconds(video_path)
        if duration_seconds is not None:
            self.duracao_total_video_seg = duration_seconds
            h = int(duration_seconds / 3600)
            m = int((duration_seconds % 3600) / 60)
            s = int(duration_seconds % 60)
            duration_str = f"{h:02d}:{m:02d}:{s:02d}"
            self.after(0, lambda: self.lbl_video_duration.config(text=f"Duração: {duration_str}"))
            self.log(f"Duração detectada: {duration_str}")
        else:
            self.after(0, lambda: self.lbl_video_duration.config(text="Duração: N/A"))
            self.log("Não foi possível obter a duração do vídeo.", "WARN")

    def selecionar_pasta_saida(self):
        caminho = filedialog.askdirectory(title="Selecione a pasta para salvar os vídeos")
        if caminho:
            self.caminho_pasta_saida.set(caminho)

    def atualizar_campos_segmento(self):
        """Habilita ou desabilita os campos de segmento com base no modo."""
        is_segment_mode = self.modo_processamento.get() == 'segmento'
        new_state = tk.NORMAL if is_segment_mode else tk.DISABLED
        
        for widget in [self.entry_inicio, self.entry_fim]:
            widget.config(state=new_state)
        
        if not is_segment_mode:
            self.frame_segmento.config(text="Configuração do Segmento (Desativado)")
        else:
            self.frame_segmento.config(text="Configuração do Segmento")
        
        self._atualizar_estado_ui_modo()

    def _atualizar_estado_ui_modo(self):
        modo = self.modo_processamento.get()
        is_segmento = (modo == 'segmento')
        segmento_state = 'normal' if is_segmento else 'disabled'
        for widget in [self.entry_inicio, self.entry_fim]:
            widget.config(state=segmento_state)
        tamanho_state = 'disabled' if is_segmento else 'normal'
        self.spin_tamanho_max.config(state=tamanho_state)

    def parse_time_to_seconds(self, time_str):
        """Converte uma string de tempo 'HH:MM:SS' para segundos."""
        if not time_str or not re.match(r'^\d{2}:\d{2}:\d{2}$', time_str):
            return None
        try:
            h, m, s = map(int, time_str.split(':'))
            return h * 3600 + m * 60 + s
        except (ValueError, TypeError):
            return None

    def validar_entradas(self):
        """Verifica se todas as entradas do usuário são válidas antes de processar."""
        nome_projeto = self.nome_projeto.get().strip()
        if not nome_projeto:
            messagebox.showerror("Erro de Validação", "O nome do projeto não pode estar vazio.")
            return False

        caminho_video = self.caminho_video.get()
        if not caminho_video or not Path(caminho_video).is_file():
            messagebox.showerror("Erro de Validação", "Por favor, selecione um arquivo de vídeo válido.")
            return False

        pasta_saida = self.caminho_pasta_saida.get()
        if not pasta_saida or not Path(pasta_saida).is_dir():
            messagebox.showerror("Erro de Validação", "Por favor, selecione uma pasta de saída válida.")
            return False

        if self.duracao_total_video_seg is None or self.duracao_total_video_seg <= 0:
            messagebox.showerror("Erro de Validação", "Aguarde a obtenção dos dados do vídeo antes de processar.")
            return False

        if self.modo_processamento.get() == "segmento":
            try:
                inicio_s = self.parse_time_to_seconds(self.entry_inicio.get())
                fim_s = self.parse_time_to_seconds(self.entry_fim.get())
                
                if inicio_s >= fim_s:
                    messagebox.showerror("Erro de Validação", "O tempo de início deve ser menor que o tempo de fim.")
                    return False
                
                if self.duracao_total_video_seg and (fim_s > self.duracao_total_video_seg):
                    messagebox.showwarning("Aviso de Validação", f"O tempo de fim ({self.formatar_tempo(fim_s)}) excede a duração do vídeo ({self.formatar_tempo(self.duracao_total_video_seg)}). O corte será limitado à duração total.")

            except ValueError:
                messagebox.showerror("Erro de Validação", "Os tempos de início e/ou fim do segmento são inválidos.")
                return False
        
        return True

    def iniciar_processamento(self):
        """Valida as entradas, atualiza a UI e inicia a thread de processamento."""
        if self.processando:
            messagebox.showwarning("Aguarde", "Um processamento já está em andamento.")
            return

        if not self.validar_entradas():
            return

        self._set_ui_state(True)

        # 1. Inicializa o estado do processo
        self.processando = True
        self.cancelado = False
        self.sucesso = False
        self.processo_ffmpeg = None
        self.start_time = time.time()

        # 2. Limpa o log e atualiza a UI para o estado de processamento
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')
        self._set_ui_state(processing=True)
        self.barra_progresso.config(mode='indeterminate')
        self.barra_progresso.start()
        self.lbl_status_progresso.config(text="Iniciando...")
        # Reseta a cor da fonte do status para o padrão do tema
        self.lbl_status_progresso.config(foreground=self.style.lookup('TLabel', 'foreground'))
        
        # 3. Força a atualização da UI antes de iniciar a thread
        self.update_idletasks()

        # 4. Inicia a thread de processamento
        threading.Thread(target=self._thread_principal_de_processamento, daemon=True).start()

    def _thread_principal_de_processamento(self):
        """Thread principal que roteia e gerencia o processamento."""
        # --- Validações e Preparação ---
        caminho_video = Path(self.caminho_video.get())
        nome_projeto = re.sub(r'[\\/*?"<>|]', "", self.nome_projeto.get().strip())
        if not nome_projeto:
            self.log("Nome do Projeto inválido.", "ERROR")
            self.finalizar_processamento(sucesso=False)
            return

        # Armazena o caminho de saída do projeto atual como um atributo da instância
        self.caminho_saida_projeto_atual = Path(self.caminho_pasta_saida.get()) / nome_projeto
        self.caminho_saida_projeto_atual.mkdir(parents=True, exist_ok=True)
        
        # --- Roteamento para o modo de processamento ---
        comando = []
        duracao_para_progresso = self.duracao_total_video_seg
        
        try:
            if self.modo_processamento.get() == 'completo':
                comando, duracao_para_progresso = self._processar_divisao_video(caminho_video, self.caminho_saida_projeto_atual, nome_projeto)
            elif self.modo_processamento.get() == 'segmento':
                comando, duracao_para_progresso = self._processar_corte_segmento(caminho_video, self.caminho_saida_projeto_atual, nome_projeto)
        except ValueError as e:
            self.log(str(e), "ERROR")
            self.finalizar_processamento(sucesso=False)
            return

        if not comando:
            self.log("Falha ao construir o comando FFmpeg.", "ERROR")
            self.finalizar_processamento(sucesso=False)
            return

        if self.modo_processamento.get() == 'completo':
            ffmpeg_cmd = comando
            total_duration = self.get_video_duration_seconds(caminho_video)
            # Define o caminho do primeiro arquivo para verificação de sucesso
            caminho_saida_verificacao = Path(str(ffmpeg_cmd[-1]).replace('%03d', '001'))
        else: # modo 'segmento'
            ffmpeg_cmd = comando
            inicio_s = self.parse_time_to_seconds(self.entry_inicio.get())
            fim_s = self.parse_time_to_seconds(self.entry_fim.get())
            total_duration = fim_s - inicio_s
            # Define o caminho do arquivo de segmento para verificação
            caminho_saida_verificacao = Path(ffmpeg_cmd[-1])

        if not total_duration:
            raise ValueError("Não foi possível obter a duração para a barra de progresso.")

        self.processo_ffmpeg, mensagem_erro = self.executar_ffmpeg(ffmpeg_cmd, total_duration, caminho_saida_verificacao)

        self.finalizar_processamento(self.processo_ffmpeg, mensagem_erro)
        
    def _calcular_tempo_segmento(self, bitrate_total, max_size_mb):
        """
        Calcula o tempo de segmento em segundos com base no bitrate e no tamanho máximo por arquivo,
        aplicando uma margem de segurança de 15% abaixo do tamanho estipulado.
        """
        if max_size_mb <= 0 or bitrate_total <= 0:
            self.log("[ERRO]: Bitrate ou tamanho máximo inválido. Usando tempo padrão de 1800s.", 'ERROR')
            return 1800
        
        # Converter tamanho máximo de MB para bits (1 MB = 8 * 1024 * 1024 bits)
        max_size_bits = max_size_mb * 8 * 1024 * 1024
        # Aplicar margem de segurança de 15% abaixo
        max_size_bits = max_size_bits * 0.85
        # Calcular tempo de segmento em segundos (tempo = tamanho / bitrate)
        tempo_segmento = max_size_bits / bitrate_total
        self.log(f"[INFO]: Tempo de segmento calculado (margem de 15%): {int(tempo_segmento)}s por parte.", 'INFO')
        return int(tempo_segmento)

    def _processar_divisao_video(self, caminho_video, caminho_saida_projeto, nome_projeto):
        """Constrói o comando para dividir o vídeo com base no tamanho máximo."""
        self.log("Modo 'Vídeo Completo' selecionado.", "INFO")
        
        # CORREÇÃO: Usa o bitrate total do formato do arquivo de entrada para o cálculo.
        # Isso é mais robusto do que assumir um bitrate de áudio de saída fixo, 
        # pois o FFmpeg pode ajustar o bitrate do áudio com base na qualidade da fonte.
        stream_props = self._get_stream_properties(caminho_video)
        output_total_bitrate_bps = stream_props.get('format', 0)

        if not output_total_bitrate_bps:
            raise ValueError("Não foi possível determinar o bitrate do vídeo. O arquivo pode estar corrompido ou não ser um vídeo.")

        self.log(f"Bitrate total detectado (formato): {output_total_bitrate_bps / 1000:.0f} kbps. Usando este valor para o cálculo do segmento.")

        max_size_mb = self.tamanho_maximo.get()
        tempo_segmento = self._calcular_tempo_segmento(output_total_bitrate_bps, max_size_mb)
        
        caminho_saida_template = caminho_saida_projeto / f"{nome_projeto}_parte_%03d.mp4"
        
        # Constrói o comando FFmpeg para dividir o vídeo em segmentos
        comando = [
            str(self.ffmpeg_path),
            "-i", str(caminho_video),
            "-c:v", "copy",                      # Copia o vídeo sem re-encoder
            "-c:a", "aac",                       # Re-encoda o áudio para AAC (compatível com MP4)
            "-b:a", "192k",                      # Define um bitrate de áudio razoável
            "-f", "segment",
            "-segment_time", str(tempo_segmento),
            "-reset_timestamps", "1",
            "-max_interleave_delta", "0",        # Workaround para 'Packets poorly interleaved'
            str(caminho_saida_template)
        ]
        return comando, self.duracao_total_video_seg

    # ==============================================================================
    # == INÍCIO DA SEÇÃO ESTÁVEL - PROCESSAMENTO DE CORTE DE SEGMENTO ==
    # A lógica a seguir para o modo 'Cortar Segmento' está funcionando 
    # corretamente e foi validada. Não modificar sem testes extensivos.
    # ==============================================================================
    def _processar_corte_segmento(self, caminho_video, caminho_saida_projeto, nome_projeto):
        """Constrói o comando para cortar um segmento do vídeo."""
        self.log("Modo 'Cortar Segmento' selecionado.", "INFO")
        inicio_str = self.entry_inicio.get()
        fim_str = self.entry_fim.get()

        inicio_s = self.parse_time_to_seconds(inicio_str)
        fim_s = self.parse_time_to_seconds(fim_str)

        if inicio_s is None or fim_s is None or inicio_s >= fim_s:
            raise ValueError(f"Tempos de início/fim inválidos: Início='{inicio_str}', Fim='{fim_str}'.")

        duracao_corte = fim_s - inicio_s
        
        # Normaliza os caminhos para compatibilidade com Windows
        caminho_video_norm = os.path.normpath(caminho_video)
        nome_arquivo_saida = f"{nome_projeto}_segmento_{inicio_str.replace(':', '')}-{fim_str.replace(':', '')}.mp4"
        caminho_arquivo_saida_norm = os.path.normpath(caminho_saida_projeto / nome_arquivo_saida)

        self.log(f"Preparando para cortar de {inicio_str} a {fim_str} ({duracao_corte}s).", "INFO")
        self.log(f"Arquivo de saída: {caminho_arquivo_saida_norm}", "INFO")

        # Constrói o comando FFmpeg para cortar o segmento. 
        # -ss antes de -i é mais rápido para cópia de stream.
        comando = [
            str(self.ffmpeg_path),
            '-y',
            '-ss', str(inicio_s),
            '-i', str(caminho_video_norm),
            '-t', str(duracao_corte),
            '-c:v', 'copy',                      # Copia o vídeo sem re-encoder
            '-c:a', 'aac',                       # Re-encoda o áudio para AAC (compatível com MP4)
            '-b:a', '192k',                      # Define um bitrate de áudio razoável
            '-avoid_negative_ts', 'make_zero',
            str(caminho_arquivo_saida_norm)
        ]
        return comando, duracao_corte
    # ==============================================================================
    # == FIM DA SEÇÃO ESTÁVEL - PROCESSAMENTO DE CORTE DE SEGMENTO ==
    # ==============================================================================

    def executar_ffmpeg(self, command, total_duration, output_path=None):
        """Executa um comando FFmpeg, monitora o progresso e verifica o sucesso."""
        import os
        # Garantir que o diretório de saída existe
        output_dir = os.path.dirname(output_path) if output_path else os.path.dirname(command[-1])
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.log(f"[INFO]: Diretório de saída {output_dir} criado.", 'INFO')
        
        self.log(f"[FFMPEG]: Executando comando: {' '.join(map(str, command))}", 'INFO')
        
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            encoding='utf-8', 
            errors='replace',
            creationflags=creation_flags
        )
        self.log(f"[DEBUG] Processo FFmpeg criado com PID: {process.pid}", "WARN")
        self.processo_ffmpeg = process

        reader_thread = threading.Thread(target=self._ler_saida_ffmpeg, args=(process, total_duration))
        reader_thread.start()
        reader_thread.join() # Espera a thread de leitura terminar

        return_code = process.wait() # Aguarda o término do processo FFmpeg

        if self.cancelado:
            self.log("Processo FFmpeg foi cancelado.", "WARN")
            return False, "Operação cancelada."

        # LÓGICA DE SUCESSO APRIMORADA:
        # 1. Verifica se o arquivo de saída esperado foi criado e não está vazio.
        # Isso é mais confiável do que o código de saída, que pode ser != 0 para avisos.
        if output_path and output_path.exists() and output_path.stat().st_size > 100: # 100 bytes como sanity check
            self.log(f"Arquivo de saída '{output_path.name}' verificado com sucesso. Operação bem-sucedida.", "SUCCESS")
            return True, None

        # 2. Se a verificação do arquivo falhar ou não for fornecida, recorre ao código de saída.
        if return_code != 0:
            error_message = f"FFmpeg finalizou com código de erro: {return_code}. Verifique o log para detalhes."
            self.log(error_message, "ERROR")
            return False, error_message
        
        self.log("Comando FFmpeg executado com sucesso (verificado pelo código de retorno).", "INFO")
        return True, None

    # ==============================================================================
    # == INÍCIO DA SEÇÃO ESTÁVEL - MONITORAMENTO DE PROGRESSO ==
    # As funções a seguir para ler a saída do FFmpeg e atualizar a UI de 
    # progresso estão funcionando corretamente e foram validadas.
    # Não modificar sem testes extensivos.
    # ==============================================================================
    def _ler_saida_ffmpeg(self, process, total_duration):
        """Lê a saída do stderr do FFmpeg para monitorar o progresso."""
        # Regex mais robusto para capturar tempo no formato HH:MM:SS.ms ou HH:MM:SS
        progress_regex = re.compile(r"time=(\d{1,2}):(\d{2}):(\d{2})[.:](\d{2})?")
        
        # Lê o stream de erro (stderr) onde o FFmpeg envia o progresso
        for line in process.stderr:
            if self.cancelado: break
            
            self.log(line.strip(), "FFMPEG") # Loga a linha para depuração
            match = progress_regex.search(line)
            if match:
                h, m, s, _ = map(lambda x: int(x) if x else 0, match.groups())
                processed_seconds = h * 3600 + m * 60 + s
                percent = min((processed_seconds / total_duration) * 100, 100)
                
                elapsed_seconds = time.time() - self.start_time
                eta_str = "..."
                if percent > 1:
                    total_time = (elapsed_seconds / percent) * 100
                    eta_seconds = total_time - elapsed_seconds
                    if eta_seconds > 0:
                        eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))
                
                elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_seconds))
                self.after(0, self._update_progress_ui, percent, elapsed_str, eta_str)

    def _update_progress_ui(self, percent, elapsed_str, eta_str):
        if not self.processando: return
        self.barra_progresso['value'] = percent
        self.lbl_status_progresso.config(text=f"{percent:.1f}% | Decorrido: {elapsed_str} | Restante: {eta_str}")
    # ==============================================================================
    # == FIM DA SEÇÃO ESTÁVEL - MONITORAMENTO DE PROGRESSO ==
    # ==============================================================================

    def cancelar_processamento(self): 
        if self.processando:
            self.cancelado = True
            self.log(f"Solicitação de cancelamento recebida...", 'WARN')
            self.log(f"[DEBUG] Cancelar clicado. Status: self.processando={self.processando}", "WARN")
            
            if hasattr(self, 'processo_ffmpeg') and self.processo_ffmpeg and self.processo_ffmpeg.poll() is None:
                self.log(f"[DEBUG] self.processo_ffmpeg exists. Poll result: {self.processo_ffmpeg.poll()}", "WARN")
                if sys.platform == 'win32':
                    try:
                        import subprocess
                        subprocess.call(['taskkill', '/F', '/PID', str(self.processo_ffmpeg.pid), '/T'])
                        self.log(f"[LOG]: Processo FFmpeg (PID {self.processo_ffmpeg.pid}) e filhos terminados com taskkill.", 'INFO')
                    except Exception as e:
                        self.log(f"[ERRO]: Falha ao terminar processo com taskkill: {str(e)}", 'ERROR')
                else:
                    self.processo_ffmpeg.kill()
                    self.log(f"[LOG]: Processo FFmpeg terminado com kill().", 'INFO')
            else:
                self.log(f"[DEBUG] self.processo_ffmpeg não existe ou já terminou. Poll result: {self.processo_ffmpeg.poll() if hasattr(self, 'processo_ffmpeg') and self.processo_ffmpeg else 'N/A'}", "WARN")
            
            # Corrigir chamada para o método de atualização da UI
            self._atualizar_estado_ui_modo()
            # Desabilitar o estado de processamento
            self.processando = False

    def finalizar_processamento(self, sucesso, mensagem=None):
        """Finaliza o processo, atualiza a UI e mostra o resultado."""
        self.processando = False
        self.after(0, self._finalizar_ui, sucesso, mensagem)

    def _finalizar_ui(self, sucesso, mensagem=None):
        """Atualiza a UI na thread principal, mostra o resultado e reabilita os controles."""
        # 1. Para a barra de progresso e define o status final com cor
        self.barra_progresso.stop()
        self.barra_progresso['value'] = 100 if sucesso else 0
        if sucesso:
            self.lbl_status_progresso.config(text="Concluído com Sucesso!", foreground="#28a745")
        else:
            self.lbl_status_progresso.config(text="Falhou", foreground="#dc3545")

        # 2. Mostra a mensagem apropriada
        if self.cancelado:
            messagebox.showwarning("Cancelado", "A operação foi cancelada pelo usuário.")
        elif sucesso:
            self.log("Processamento concluído com sucesso. Verifique os arquivos na pasta de saída.", "SUCCESS")
            # REMOVIDO: O popup de sucesso estava aparecendo prematuramente.
            
            if self.abrir_pasta_ao_concluir.get():
                try:
                    caminho_para_abrir = self.caminho_pasta_saida.get()
                    if hasattr(self, 'caminho_saida_projeto_atual') and self.caminho_saida_projeto_atual.exists():
                        caminho_para_abrir = str(self.caminho_saida_projeto_atual)
                    self.log(f"Abrindo pasta de saída: {caminho_para_abrir}", "INFO")
                    if sys.platform == "win32": os.startfile(caminho_para_abrir)
                    elif sys.platform == "darwin": subprocess.Popen(["open", caminho_para_abrir])
                    else: subprocess.Popen(["xdg-open", caminho_para_abrir])
                except Exception as e:
                    self.log(f"Não foi possível abrir a pasta de saída: {e}", "ERROR")
        else:
            erro_msg = mensagem if mensagem else "Ocorreu um erro durante o processamento. Verifique o log."
            messagebox.showerror("Erro", erro_msg)
        
        # 3. Reabilita a UI e redefine o estado de processamento
        self.processando = False
        self._set_ui_state(processing=False)

    def get_video_duration_seconds(self, video_path):
        """Obtém a duração do vídeo em segundos usando ffprobe."""
        video_path_norm = os.path.normpath(video_path)
        command = [str(self.ffprobe_path), '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(video_path_norm)]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
            self.log(f"Erro ao obter duração: {e}", "ERROR")
            return None

    def _get_stream_properties(self, video_path):
        """Usa ffprobe para obter propriedades dos streams de vídeo e áudio em formato JSON."""
        video_path_norm = os.path.normpath(video_path)
        command = [
            str(self.ffprobe_path), 
            '-v', 'quiet', 
            '-print_format', 'json', 
            '-show_format', # CORREÇÃO: Adicionado para obter o bitrate do container.
            '-show_streams', 
            str(video_path_norm)
        ]
        self.log(f"Executando ffprobe para obter propriedades do stream: {' '.join(command)}", "INFO")

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            streams_data = json.loads(result.stdout)
            
            properties = {'video': 0, 'audio': 0, 'format': 0}
            
            # Prioriza o bitrate do formato geral, pois é mais confiável para o cálculo de divisão
            format_bit_rate = streams_data.get('format', {}).get('bit_rate')
            if format_bit_rate and format_bit_rate.isdigit():
                properties['format'] = int(format_bit_rate)

            for stream in streams_data.get('streams', []):
                codec_type = stream.get('codec_type')
                bit_rate_str = stream.get('bit_rate', '0')
                if bit_rate_str.isdigit():
                    bit_rate = int(bit_rate_str)
                    if codec_type == 'video' and bit_rate > properties['video']:
                        properties['video'] = bit_rate
                    elif codec_type == 'audio' and bit_rate > properties['audio']:
                        properties['audio'] = bit_rate
            
            # Fallback para o bitrate do formato se o do stream de vídeo não for encontrado
            if properties['video'] == 0 and properties['format'] > 0:
                self.log("Bitrate do stream de vídeo não encontrado, estimando a partir do bitrate do formato.", "WARN")
                # Estima que o vídeo seja 80% do bitrate total se o áudio também não for encontrado
                audio_bitrate_fallback = properties['audio'] if properties['audio'] > 0 else properties['format'] * 0.20
                properties['video'] = properties['format'] - audio_bitrate_fallback

            return properties
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            self.log(f"Erro ao obter propriedades do stream com ffprobe: {e}", "ERROR")
            return {'video': 0, 'audio': 0, 'format': 0}

    def mostrar_info_doacao(self): InfoWindow(self, "Apoie o Desenvolvimento", DOACOES)
    def mostrar_info_contato(self): InfoWindow(self, "Informações de Contato", CONTATOS)
    
    def on_closing(self):
        if self.processando:
            if messagebox.askyesno("Aviso", "O processamento está em andamento. Deseja cancelar e sair?"):
                self.cancelar_processamento()
                self.after(200, self.destroy) # Dá um tempo para o cancelamento
        else:
            self.destroy()

if __name__ == "__main__":
    # Bloco para capturar erros fatais na inicialização
    try:
        app = AppProcessadorVideos()
        app.mainloop()
    except Exception as e:
        import traceback
        log_path = INSTALL_BASE_DIR / 'pochete_crash_log.txt'
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Erro fatal em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(traceback.format_exc())
        
        # Tenta mostrar uma mensagem de erro gráfica como último recurso
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro Crítico", f"Ocorreu um erro fatal. Um relatório foi salvo em:\n{log_path}")
        except:
            pass
