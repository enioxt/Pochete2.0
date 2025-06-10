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

# Classe para o campo de entrada de tempo com máscara e placeholder
class InfoWindow(tk.Toplevel):
    def __init__(self, parent, title, data):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(expand=True, fill=tk.BOTH)
        main_frame.columnconfigure(1, weight=0) # Não expandir a coluna das caixas de texto
        main_frame.columnconfigure(4, weight=1) # Adicionar uma coluna "espaçadora" que se expande

        row_num = 0
        for key, value in data.items():
            ttk.Label(main_frame, text=f"{key}:", font=('TkDefaultFont', 10, 'bold')).grid(row=row_num, column=0, sticky=tk.W, pady=(5, 0), columnspan=2)
            
            entry_frame = ttk.Frame(main_frame)
            entry_frame.grid(row=row_num + 1, column=0, columnspan=3, sticky=tk.EW, pady=(0, 10))
            entry_frame.columnconfigure(0, weight=1)

            entry = ttk.Entry(entry_frame, width=50)
            entry.insert(0, value)
            entry.config(state='readonly')
            entry.grid(row=0, column=0, sticky=tk.EW)

            copy_button = ttk.Button(entry_frame, text="Copiar", command=lambda v=value, b=entry: self.copy_to_clipboard(v, b))
            copy_button.grid(row=0, column=1, sticky=tk.W, padx=(5,0))
            
            row_num += 2

        close_button = ttk.Button(main_frame, text="Fechar", command=self.destroy)
        close_button.grid(row=row_num, column=0, columnspan=3, pady=(15,0))
        
        self.update_idletasks()
        self.center_window()

    def copy_to_clipboard(self, text, button):
        self.clipboard_clear()
        self.clipboard_append(text)
        original_bg = button.cget("background")
        button.config(style="Copiado.TEntry")
        self.after(1500, lambda: button.config(style="TEntry"))

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
        # Ignora teclas que não produzem caracteres (Shift, Ctrl, etc.)
        # Impede que a função seja acionada por teclas não imprimíveis (exceto Backspace)
        if e.keysym not in ['BackSpace'] and (len(e.char) == 0 or not e.char.isprintable()):
            return

        current_text = super().get()
        # Mantém apenas os dígitos
        just_digits = "".join(filter(str.isdigit, current_text))

        # Limita a 6 dígitos
        just_digits = just_digits[:6]

        # Formata o texto com os dois-pontos
        formatted_text = ""
        if len(just_digits) > 0:
            formatted_text = just_digits[:2]
        if len(just_digits) > 2:
            formatted_text += ':' + just_digits[2:4]
        if len(just_digits) > 4:
            formatted_text += ':' + just_digits[4:6]

        # Atualiza o widget de forma controlada para evitar loops
        self.unbind("<KeyRelease>")
        self.delete(0, "end")
        self.insert(0, formatted_text)
        self.icursor(len(formatted_text)) # Posiciona o cursor no final
        self.bind("<KeyRelease>", self._on_key_release)

        if len(formatted_text) == 8 and self.next_widget:
            self.next_widget.focus_set()
            self.next_widget._clear_placeholder()

    def get(self):
        val = super().get()
        return val if val != self.placeholder else "00:00:00"

# Definir o diretório base para a instalação de forma robusta
if getattr(sys, 'frozen', False):
    # O aplicativo está congelado (executável)
    # Para builds --onefile, o caminho está em sys._MEIPASS
    # Para builds --onedir, o caminho é o pai do executável
    INSTALL_BASE_DIR = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(sys.executable).parent
else:
    # O aplicativo está rodando como um script .py
    INSTALL_BASE_DIR = Path(__file__).parent

class AppProcessadorVideos(tk.Tk): 
    def __init__(self):
        super().__init__()
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam') 
        except tk.TclError:
            print("INFO: 'clam' theme not available, using default.")
        self.style.configure("Copiado.TEntry", fieldbackground="#aeffa8")

        self.title("Pochete 2.0 - Processador de Vídeos")
        window_width = 800
        window_height = 580
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.minsize(800, 580)

        self.ffmpeg_path = INSTALL_BASE_DIR / "ffmpeg" / "ffmpeg.exe"
        self.ffprobe_path = INSTALL_BASE_DIR / "ffmpeg" / "ffprobe.exe"

        self.processando = False
        self.cancelado = False
        self.ffmpeg_process = None

        self.nome_projeto = tk.StringVar()
        self.caminho_video = tk.StringVar()
        self.tamanho_maximo = tk.IntVar(value=37)
        
        default_output_path = INSTALL_BASE_DIR / 'saida'
        os.makedirs(default_output_path, exist_ok=True)
        self.caminho_pasta_saida = tk.StringVar(value=str(default_output_path))
        self.default_output_path = str(default_output_path)

        self.modo_processamento = tk.StringVar(value="completo")

        self.criar_widgets()
        self.verificar_ffmpeg()

    def criar_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=0)  # Coluna dos campos de texto não expande
        main_frame.columnconfigure(2, weight=0)  # Coluna dos botões de seleção não expande
        main_frame.columnconfigure(3, weight=1)  # Coluna de espaçamento que empurra os botões para a direita

        ttk.Label(main_frame, text="Nome do Projeto:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_nome_projeto = ttk.Entry(main_frame, textvariable=self.nome_projeto, width=60)
        self.entry_nome_projeto.grid(row=0, column=1, sticky=tk.W, pady=2, columnspan=2)

        ttk.Label(main_frame, text="Caminho do Vídeo:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_caminho_video = ttk.Entry(main_frame, textvariable=self.caminho_video, width=60)
        self.entry_caminho_video.grid(row=1, column=1, sticky=tk.W, pady=2)
        self.btn_selecionar_video = ttk.Button(main_frame, text="Selecionar Vídeo", command=self.selecionar_video)
        self.btn_selecionar_video.grid(row=1, column=2, sticky=tk.W, padx=5)
        # O rótulo de duração foi movido para o frame de segmento para melhor visibilidade.

        ttk.Label(main_frame, text="Pasta de Saída:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_pasta_saida = ttk.Entry(main_frame, textvariable=self.caminho_pasta_saida, width=60)
        self.entry_pasta_saida.grid(row=2, column=1, sticky=tk.W, pady=2)
        self.btn_selecionar_saida = ttk.Button(main_frame, text="Selecionar Pasta", command=self.selecionar_pasta_saida)
        self.btn_selecionar_saida.grid(row=2, column=2, sticky=tk.W, padx=5)

        # Frame para os botões de apoio e contato no canto superior direito
        support_frame = ttk.Frame(main_frame)
        support_frame.grid(row=0, column=4, rowspan=3, sticky='ne', padx=5, pady=2)

        self.btn_doacao = ttk.Button(support_frame, text="Apoiar o Projeto", command=self.mostrar_info_doacao)
        self.btn_doacao.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        self.btn_contato = ttk.Button(support_frame, text="Contato", command=self.mostrar_info_contato)
        self.btn_contato.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(main_frame, text="Tamanho Máx. (MB):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.spin_tamanho = ttk.Spinbox(main_frame, from_=1, to=100, textvariable=self.tamanho_maximo, width=5)
        self.spin_tamanho.grid(row=3, column=1, sticky=tk.W)

        ttk.Label(main_frame, text="Modo de Processamento:").grid(row=4, column=0, sticky=tk.W, pady=5)
        modo_frame = ttk.Frame(main_frame)
        modo_frame.grid(row=4, column=1, columnspan=3, sticky=tk.W)
        ttk.Radiobutton(modo_frame, text="Vídeo Completo", variable=self.modo_processamento, value="completo", command=self.atualizar_campos_segmento).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(modo_frame, text="Cortar Segmento", variable=self.modo_processamento, value="segmento", command=self.atualizar_campos_segmento).pack(side=tk.LEFT, padx=5)

        self.frame_segmento = ttk.Labelframe(main_frame, text="Configuração do Segmento", padding="10")
        self.frame_segmento.grid(row=5, column=0, columnspan=5, sticky=tk.EW, pady=5, padx=5)
        self.frame_segmento.columnconfigure(1, weight=1)

        self.lbl_video_duration = ttk.Label(self.frame_segmento, text="", font=('TkDefaultFont', 10, 'bold'))
        self.lbl_video_duration.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        ttk.Label(self.frame_segmento, text="Início (HH:MM:SS):").grid(row=1, column=0, sticky=tk.W)
        self.entry_inicio = TimePickerEntry(self.frame_segmento)
        self.entry_inicio.grid(row=1, column=1, sticky=tk.EW, padx=5)
        ttk.Label(self.frame_segmento, text="Fim (HH:MM:SS):").grid(row=2, column=0, sticky=tk.W)
        self.entry_fim = TimePickerEntry(self.frame_segmento)
        self.entry_fim.grid(row=2, column=1, sticky=tk.EW, padx=5)
        self.entry_inicio.next_widget = self.entry_fim

        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=6, column=0, columnspan=4, pady=10)
        self.btn_processar = ttk.Button(action_frame, text="Iniciar Processamento", command=self.iniciar_processamento)
        self.btn_processar.pack(side=tk.LEFT, padx=5)
        self.btn_cancelar = ttk.Button(action_frame, text="Cancelar", command=self.cancelar_processamento, state=tk.DISABLED)
        self.btn_cancelar.pack(side=tk.LEFT, padx=5)

        self.barra_progresso = ttk.Progressbar(main_frame, orient='horizontal', mode='indeterminate')
        self.barra_progresso.grid(row=7, column=0, columnspan=4, sticky=tk.EW, pady=5)
        self.lbl_status_progresso = ttk.Label(main_frame, text="")
        self.lbl_status_progresso.grid(row=8, column=0, columnspan=4, sticky=tk.W)

        log_frame = ttk.Labelframe(main_frame, text="Log de Operações", padding="10")
        log_frame.grid(row=9, column=0, columnspan=4, sticky="nsew", pady=5)
        main_frame.rowconfigure(9, weight=1)
        self.log_text = tk.Text(log_frame, height=10, state='disabled', wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.atualizar_campos_segmento()

    def log(self, message, level='INFO'):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{now}] [{level.upper()}]: {message}\n"
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)

    def verificar_ffmpeg(self):
        if not self.ffmpeg_path.exists():
            self.log("FFmpeg não encontrado! Verifique a instalação.", "ERROR")
            messagebox.showerror("Erro Crítico", f"O executável do FFmpeg não foi encontrado no caminho esperado:\n{self.ffmpeg_path}")
            self.destroy()

    def selecionar_video(self):
        caminho = filedialog.askopenfilename(title="Selecione o arquivo de vídeo")
        if caminho:
            self.caminho_video.set(caminho)
            if not self.nome_projeto.get():
                nome_base = Path(caminho).stem
                self.nome_projeto.set(nome_base)
            self.log(f"Vídeo selecionado: {caminho}")
            threading.Thread(target=self._update_video_duration, args=(caminho,), daemon=True).start()

    def _update_video_duration(self, video_path):
        try:
            command = [
                str(self.ffprobe_path),
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.stdout:
                duration_seconds = float(result.stdout.strip())
                h = int(duration_seconds / 3600)
                m = int((duration_seconds % 3600) / 60)
                s = int(duration_seconds % 60)
                duration_str = f"{h:02d}:{m:02d}:{s:02d}"
                self.after(0, lambda: self.lbl_video_duration.config(text=f"Duração: {duration_str}"))
                self.log(f"Duração detectada: {duration_str}")
            else:
                self.after(0, lambda: self.lbl_video_duration.config(text="Duração: N/A"))
        except Exception as e:
            self.after(0, lambda: self.lbl_video_duration.config(text="Duração: N/A"))
            self.log(f"ERRO ao obter duração do vídeo: {e}", "ERROR")

    def selecionar_pasta_saida(self):
        caminho = filedialog.askdirectory(title="Selecione a pasta para salvar os vídeos")
        if caminho:
            self.caminho_pasta_saida.set(caminho)
            self.log(f"Pasta de saída alterada para: {caminho}")

    def atualizar_campos_segmento(self):
        state = tk.NORMAL if self.modo_processamento.get() == 'segmento' else tk.DISABLED
        for child in self.frame_segmento.winfo_children():
            # TimePickerEntry não tem a opção 'state' como widgets padrão, então tratamos o erro
            try:
                child.config(state=state)
            except tk.TclError:
                # Para o nosso TimePickerEntry, podemos controlar a edição de outra forma se necessário
                # Por enquanto, a desativação visual do Labelframe é suficiente
                pass
        # Habilita/desabilita os próprios campos de entrada
        self.entry_inicio.config(state=state)
        self.entry_fim.config(state=state)

    def iniciar_processamento(self):
        if self.processando:
            messagebox.showwarning("Aviso", "Um processamento já está em andamento.")
            return

        caminho_video = self.caminho_video.get()
        if not caminho_video or not Path(caminho_video).exists():
            messagebox.showerror("Erro", "Caminho do vídeo inválido ou não selecionado.")
            return

        self.processando = True
        self.cancelado = False
        self.btn_processar.config(state=tk.DISABLED)
        self.btn_cancelar.config(state=tk.NORMAL)
        self.barra_progresso.start()
        self.lbl_status_progresso.config(text="Iniciando processamento...")

        threading.Thread(target=self._executar_processamento, daemon=True).start()

    def _executar_processamento(self):
        nome_base = self.nome_projeto.get() or Path(self.caminho_video.get()).stem
        pasta_saida = Path(self.caminho_pasta_saida.get()) / nome_base
        os.makedirs(pasta_saida, exist_ok=True)

        comando = [str(self.ffmpeg_path), '-i', self.caminho_video.get(), '-y']

        if self.modo_processamento.get() == 'completo':
            tamanho_max_bytes = self.tamanho_maximo.get() * 1024 * 1024
            comando.extend([
                '-fs', str(tamanho_max_bytes),
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
                str(pasta_saida / f"{nome_base}_completo.mp4")
            ])
        else:
            comando.extend([
                '-ss', self.entry_inicio.get(),
                '-to', self.entry_fim.get(),
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
                str(pasta_saida / f"{nome_base}_segmento.mp4")
            ])

        self.log(f"Comando FFmpeg: {' '.join(comando)}")

        try:
            self.ffmpeg_process = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW, text=True, encoding='utf-8', errors='replace'
            )
            for line in iter(self.ffmpeg_process.stdout.readline, ''):
                if self.cancelado: break
                self.log(line.strip(), 'FFMPEG')
            self.ffmpeg_process.wait()
            self.finalizar_processamento(not self.cancelado and self.ffmpeg_process.returncode == 0)
        except Exception as e:
            self.log(f"Erro ao executar FFmpeg: {e}", "ERROR")
            self.finalizar_processamento(False)

    def cancelar_processamento(self):
        if self.processando and self.ffmpeg_process and self.ffmpeg_process.poll() is None:
            self.log("Solicitação de cancelamento recebida. Encerrando FFmpeg...", "INFO")
            self.cancelado = True
            try:
                self.ffmpeg_process.kill()
                self.log("Processo FFmpeg encerrado.", "INFO")
            except Exception as e:
                self.log(f"Erro ao tentar cancelar o processo: {e}", "ERROR")
        else:
            self.log("Nenhuma operação para cancelar.", "INFO")

    def finalizar_processamento(self, success):
        self.processando = False
        self.ffmpeg_process = None
        self.btn_processar.config(state=tk.NORMAL)
        self.btn_cancelar.config(state=tk.DISABLED)
        self.barra_progresso.stop()
        self.lbl_status_progresso.config(text="")

        if success:
            self.log("Processamento concluído com sucesso.", "INFO")
            caminho_saida = self.caminho_pasta_saida.get()
            messagebox.showinfo("Sucesso", "O vídeo foi processado com sucesso!")
            try:
                if sys.platform == "win32": os.startfile(caminho_saida)
                elif sys.platform == "darwin": subprocess.Popen(["open", caminho_saida])
                else: subprocess.Popen(["xdg-open", caminho_saida])
                self.log(f"Abrindo a pasta de saída: {caminho_saida}", "INFO")
            except Exception as e:
                self.log(f"Não foi possível abrir a pasta de saída: {e}", "ERROR")
                messagebox.showwarning("Aviso", f"Não foi possível abrir a pasta de saída.\nCaminho: {caminho_saida}")
        elif self.cancelado:
            self.log("Processamento cancelado pelo usuário.", "INFO")
            messagebox.showwarning("Cancelado", "A operação foi cancelada.")
        else:
            self.log("O processamento falhou.", "ERROR")
            messagebox.showerror("Erro", "Ocorreu um erro durante o processamento. Verifique o log.")

    def mostrar_info_doacao(self):
        InfoWindow(self, "Apoie o Desenvolvimento", DOACOES)

    def mostrar_info_contato(self):
        InfoWindow(self, "Informações de Contato", CONTATOS)

    def on_closing(self):
        if self.processando:
            if messagebox.askyesno("Aviso", "O processamento está em andamento. Deseja cancelar e sair?"):
                self.cancelar_processamento()
                self.after(100, self.destroy)
        else:
            self.destroy()

if __name__ == "__main__":
    log_path = INSTALL_BASE_DIR / 'pochete_crash_log.txt'
    try:
        app = AppProcessadorVideos()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        import traceback
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Ocorreu um erro fatal em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(traceback.format_exc())
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro Crítico", f"Ocorreu um erro fatal. Um relatório foi salvo em:\n{log_path}")
        except: pass
