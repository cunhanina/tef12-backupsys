<<<<<<< HEAD
=======
"""
TEF12 - Gestão de Backup (Full Interface Restore)
-----------------------------------------------
Funcionalidades Restauradas:
- Sistema de Abas (Movimentação e Auditoria).
- Verificação explícita de 07 e 06.
- Blindagem total contra temas externos.
"""

>>>>>>> 0da70c54e8b4dc6b08a9c23c946615227fcbbc4f
import os
import threading
import shutil
import re
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox

from src.core.utils import (
    CAMINHO_RAIZ_ORIGEM_07, 
    CAMINHO_RAIZ_DESTINO_06, 
    PATH_DIRETORIO_LOG_CENTRAL,
    LOG_FILE_NAME,
    gerar_nome_inventario_padrao, 
    BASE_DIR,
    audit_log
)
from src.ui.styles import BOSCH_COLORS, get_fonts
from src.ui.components import ConfirmationModal

class ManagementApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.withdraw()
        
        # Blindagem de Fundo
        self.configure(fg_color=BOSCH_COLORS["background_white"])
        self.title("TEF12 - Gestão de Backup")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.fonts = get_fonts()
        self.assets: dict = {}
        self._resize_timer = None
        
        # Estados
        self.c_orig = self.c_dest = self.data_found = None
        
        self._initialize_ui()
        self.after(50, self._async_init)

    def _async_init(self) -> None:
        self._load_branding()
        self.state('zoomed')
        self.deiconify()

    def _load_branding(self) -> None:
        img_dir = os.path.join(BASE_DIR, "assets", "images")
        try:
            self.assets["sg"] = Image.open(os.path.join(img_dir, "supergraph.png"))
            self.assets["logo"] = Image.open(os.path.join(img_dir, "logo_bosch.png"))
            self._render_branding()
        except: pass

    def _handle_resize(self, _event=None) -> None:
        if self._resize_timer: self.after_cancel(self._resize_timer)
        self._resize_timer = self.after(100, self._render_branding)

    def _render_branding(self) -> None:
        if not self.assets: return
        w = self.winfo_width()
        self.sg_bar.configure(image=ctk.CTkImage(self.assets["sg"], size=(w, 12)))
        asp = self.assets["logo"].width / self.assets["logo"].height
        self.logo_label.configure(image=ctk.CTkImage(self.assets["logo"], size=(int(60*asp), 60)))

    def _initialize_ui(self) -> None:
        # 1. Supergraph
        self.sg_bar = ctk.CTkLabel(self, text="", height=12, fg_color="transparent")
        self.sg_bar.grid(row=0, column=0, sticky="ew")
        
        # 2. Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=1, column=0, sticky="ew", padx=80, pady=(30, 10))
        
        t_box = ctk.CTkFrame(header, fg_color="transparent"); t_box.pack(side="left")
        ctk.CTkLabel(t_box, text="TEF12", font=self.fonts["title"], text_color=BOSCH_COLORS["blue"]).pack(side="left")
        ctk.CTkLabel(t_box, text=" | Gerenciamento", font=self.fonts["title"], text_color=BOSCH_COLORS["text_primary"]).pack(side="left", padx=5)
        self.logo_label = ctk.CTkLabel(header, text=""); self.logo_label.pack(side="right")

        # 3. NAVEGAÇÃO POR ABAS (Underline BDS)
        self.nav_cont = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_cont.grid(row=2, column=0, sticky="nsew", padx=80)
        
        self.tab_bar = ctk.CTkFrame(self.nav_cont, fg_color="transparent")
        self.tab_bar.pack(fill="x")
        
        btn_args = {"width": 180, "height": 45, "fg_color": "transparent", "corner_radius": 0, "font": self.fonts["subtitle"]}
        
        self.btn_move_tab = ctk.CTkButton(self.tab_bar, text="MOVIMENTAÇÃO", text_color=BOSCH_COLORS["blue"], 
                                         hover_color=BOSCH_COLORS["background_light"], command=lambda: self._switch("MOVE"), **btn_args)
        self.btn_move_tab.pack(side="left")
        
        self.btn_log_tab = ctk.CTkButton(self.tab_bar, text="AUDITORIA", text_color=BOSCH_COLORS["text_secondary"], 
                                        hover_color=BOSCH_COLORS["background_light"], command=lambda: self._switch("LOGS"), **btn_args)
        self.btn_log_tab.pack(side="left")

        line = ctk.CTkFrame(self.nav_cont, height=2, fg_color=BOSCH_COLORS["border_sutil"])
        line.pack(fill="x")
        self.indicator = ctk.CTkFrame(line, height=2, width=180, fg_color=BOSCH_COLORS["blue"])
        self.indicator.place(x=0, y=0)

        # Content Views
        self.v_move = ctk.CTkFrame(self.nav_cont, fg_color="transparent")
        self.v_move.pack(fill="both", expand=True)
        self.v_logs = ctk.CTkFrame(self.nav_cont, fg_color="transparent")

        self._build_move_view()
        self._build_logs_view()

    def _switch(self, target: str) -> None:
        """Gerencia a troca de abas e o indicador visual."""
        if target == "MOVE":
            self.v_logs.pack_forget(); self.v_move.pack(fill="both", expand=True)
            self.indicator.place(x=0, y=0)
            self.btn_move_tab.configure(text_color=BOSCH_COLORS["blue"])
            self.btn_log_tab.configure(text_color=BOSCH_COLORS["text_secondary"])
        else:
            self.v_move.pack_forget(); self.v_logs.pack(fill="both", expand=True)
            self.indicator.place(x=180, y=0)
            self.btn_log_tab.configure(text_color=BOSCH_COLORS["blue"])
            self.btn_move_tab.configure(text_color=BOSCH_COLORS["text_secondary"])
            self._refresh_logs()

    def _build_move_view(self) -> None:
        """Interface da aba de movimentação."""
        m = self.v_move
        ctk.CTkLabel(m, text="PESQUISAR INVENTÁRIO", font=self.fonts["small"], text_color=BOSCH_COLORS["text_secondary"]).pack(anchor="w", pady=(30, 0))
        
        row = ctk.CTkFrame(m, fg_color="transparent"); row.pack(fill="x", pady=10)
        self.ent_inv = ctk.CTkEntry(row, height=55, corner_radius=0, border_color=BOSCH_COLORS["border_sutil"], 
                                     fg_color=BOSCH_COLORS["background_light"], text_color=BOSCH_COLORS["text_primary"])
        self.ent_inv.pack(side="left", fill="x", expand=True)
        
        ctk.CTkButton(row, text="VERIFICAR", width=180, height=55, corner_radius=0, fg_color=BOSCH_COLORS["blue"], command=self._on_verify).pack(side="right", padx=(20, 0))

        # Cards de Status
        self.lbl_07 = ctk.CTkLabel(m, text="• ORIGEM (07): Pendente", font=self.fonts["subtitle"], text_color=BOSCH_COLORS["text_secondary"], anchor="w")
        self.lbl_07.pack(fill="x", pady=(20, 5))
        
        self.lbl_06 = ctk.CTkLabel(m, text="• DESTINO (06): -", font=self.fonts["subtitle"], text_color=BOSCH_COLORS["text_secondary"], anchor="w")
        self.lbl_06.pack(fill="x", pady=5)

        # Botão de Execução
        self.action_area = ctk.CTkFrame(m, height=100, fg_color="transparent"); self.action_area.pack(fill="x", side="bottom", pady=40); self.action_area.pack_propagate(False)
        self.btn_exec = ctk.CTkButton(self.action_area, text="EXECUTAR TRANSFERÊNCIA DEFINITIVA", height=80, state="disabled", 
                                      fg_color=BOSCH_COLORS["blue"], text_color="white", text_color_disabled="#D1D3D4",
                                      font=self.fonts["subtitle"], corner_radius=0, command=self._on_submit)
        self.btn_exec.pack(fill="both")

        self.prog_f = ctk.CTkFrame(self.action_area, fg_color="transparent")
        self.bar = ctk.CTkProgressBar(self.prog_f, height=18, progress_color=BOSCH_COLORS["blue"], corner_radius=0); self.bar.pack(fill="x", pady=15); self.bar.set(0)

    def _build_logs_view(self) -> None:
        """Interface da aba de auditoria."""
        m = self.v_logs
        header = ctk.CTkFrame(m, fg_color="transparent"); header.pack(fill="x", pady=(20, 10))
        ctk.CTkLabel(header, text="HISTÓRICO DE AUDITORIA", font=self.fonts["small"], text_color=BOSCH_COLORS["text_secondary"]).pack(side="left")
        ctk.CTkButton(header, text="ATUALIZAR 🔄", width=120, height=35, fg_color="transparent", border_width=1, border_color=BOSCH_COLORS["blue"], text_color=BOSCH_COLORS["blue"], command=self._refresh_logs).pack(side="right")
        
        self.txt_log = ctk.CTkTextbox(m, font=self.fonts["log"], border_width=1, corner_radius=0, fg_color=BOSCH_COLORS["background_light"], text_color=BOSCH_COLORS["text_primary"])
        self.txt_log.pack(fill="both", expand=True, pady=(0, 20))

    def _on_verify(self) -> None:
        inv = self.ent_inv.get().strip()
        if not inv: return
        
        inv_std = gerar_nome_inventario_padrao(inv)
        self.c_orig = self.data_found = None

        # Verificação 07
        try:
            matches = [os.path.join(CAMINHO_RAIZ_ORIGEM_07, s) for s in os.listdir(CAMINHO_RAIZ_ORIGEM_07) if inv in s]
            if matches:
                self.c_orig = matches[0]
                dates = [d for d in os.listdir(self.c_orig) if re.match(r'^\d{8}$', d)]
                if dates:
                    self.data_found = max(dates)
                    self.lbl_07.configure(text=f"✅ ORIGEM (07): {os.path.basename(self.c_orig)} | {self.data_found}", text_color="#18837E")
                    self.btn_exec.configure(state="normal")
                else:
                    self.lbl_07.configure(text="⚠️ ORIGEM (07): Pasta sem data válida.", text_color="#B38600")
            else:
                self.lbl_07.configure(text="❌ ORIGEM (07): Não encontrado.", text_color=BOSCH_COLORS["danger"])
        except: self.lbl_07.configure(text="❌ ORIGEM (07): Falha de conexão.", text_color=BOSCH_COLORS["danger"])

        # Verificação 06
        self.c_dest = os.path.join(CAMINHO_RAIZ_DESTINO_06, inv_std)
        status_06 = "📂 REDE 06: Inventário já existente." if os.path.exists(self.c_dest) else f"🆕 REDE 06: Nova estrutura ({inv_std})."
        self.lbl_06.configure(text=status_06, text_color=BOSCH_COLORS["blue"])

    def _on_submit(self) -> None:
        info = {"Inventário": os.path.basename(self.c_orig), "Data": self.data_found, "Fluxo": "07 → 06"}
        ConfirmationModal(self, "Revisão de Gestão", info, self._start_move, self.fonts)

    def _start_move(self) -> None:
        self.btn_exec.pack_forget(); self.prog_f.pack(fill="both")
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self) -> None:
        try:
            src = os.path.join(self.c_orig, self.data_found)
            os.makedirs(self.c_dest, exist_ok=True)
            shutil.move(src, self.c_dest)
            if not os.listdir(self.c_orig): os.rmdir(self.c_orig)
            audit_log(f"[GESTÃO] {os.path.basename(self.c_orig)} movido para 06")
            self.after(0, lambda: (self.bar.set(1.0), messagebox.showinfo("Sucesso", "Backup movido com sucesso!")))
            self.after(2000, self._reset_ui)
        except Exception as e: self.after(0, lambda: messagebox.showerror("Erro", str(e)))

    def _refresh_logs(self) -> None:
        p = os.path.join(PATH_DIRETORIO_LOG_CENTRAL, LOG_FILE_NAME)
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                c = "".join(f.readlines()[-100:])
                self.txt_log.configure(state="normal"); self.txt_log.delete("1.0", "end"); self.txt_log.insert("1.0", c); self.txt_log.configure(state="disabled")

    def _reset_ui(self) -> None:
        self.prog_f.pack_forget(); self.btn_exec.pack(fill="both")
        self.btn_exec.configure(state="disabled"); self.ent_inv.delete(0, 'end')
        self.lbl_07.configure(text="• ORIGEM (07): Pendente", text_color=BOSCH_COLORS["text_secondary"])

if __name__ == "__main__":
    app = ManagementApp()
    app.bind("<Configure>", app._handle_resize)
    app.mainloop()