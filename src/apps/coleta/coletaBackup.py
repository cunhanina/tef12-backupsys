import os, threading, shutil
from datetime import datetime
import customtkinter as ctk
from PIL import Image
from src.core.utils import CAMINHO_RAIZ_ORIGEM_07, gerar_nome_inventario_padrao, BASE_DIR
from src.ui.styles import BOSCH_COLORS, get_fonts
from src.ui.components import ConfirmationModal

class ColetaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("TEF12 - Coleta de Backup")
        # Blindagem do fundo da janela principal
        self.configure(fg_color=BOSCH_COLORS["background_white"])
        
        self.fonts = get_fonts()
        self.assets, self._resize_timer = {}, None
        self.selected_files = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self._setup_ui()
        self.after(50, self._init_app)

    def _init_app(self):
        self._load_branding()
        self.state('zoomed')
        self.deiconify()

    def _load_branding(self):
        img_dir = os.path.join(BASE_DIR, "assets", "images")
        try:
            self.assets["sg"] = Image.open(os.path.join(img_dir, "supergraph.png"))
            self.assets["logo"] = Image.open(os.path.join(img_dir, "logo_bosch.png"))
            self._render_branding()
        except: pass

    def _handle_resize(self, _):
        if self._resize_timer: self.after_cancel(self._resize_timer)
        self._resize_timer = self.after(100, self._render_branding)

    def _render_branding(self):
        if not self.assets: return
        w = self.winfo_width()
        # Supergraph: Forçando preenchimento horizontal total
        self.sg_bar.configure(image=ctk.CTkImage(self.assets["sg"], size=(w, 12)))
        asp = self.assets["logo"].width / self.assets["logo"].height
        self.logo_label.configure(image=ctk.CTkImage(self.assets["logo"], size=(int(60*asp), 60)))

    def _setup_ui(self):
        # 1. Supergraph (Sticky EW para preenchimento total)
        self.sg_bar = ctk.CTkLabel(self, text="", height=12, fg_color="transparent")
        self.sg_bar.grid(row=0, column=0, sticky="ew")
        
        # 2. Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=1, column=0, sticky="ew", padx=80, pady=30)
        
        t_box = ctk.CTkFrame(header, fg_color="transparent")
        t_box.pack(side="left")
        ctk.CTkLabel(t_box, text="TEF12", font=self.fonts["title"], text_color=BOSCH_COLORS["blue"]).pack(side="left")
        ctk.CTkLabel(t_box, text=" | Coleta de Backup", font=self.fonts["title"], text_color=BOSCH_COLORS["text_primary"]).pack(side="left", padx=5)
        self.logo_label = ctk.CTkLabel(header, text="")
        self.logo_label.pack(side="right")

        # 3. Form Container
        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.grid(row=2, column=0, sticky="nsew", padx=80)
        
        ctk.CTkLabel(cont, text="Nº INVENTÁRIO", font=self.fonts["small"], text_color=BOSCH_COLORS["text_secondary"]).pack(anchor="w")
        self.ent_inv = ctk.CTkEntry(cont, height=50, corner_radius=0, 
                                     border_color=BOSCH_COLORS["border_sutil"],
                                     fg_color=BOSCH_COLORS["background_light"],
                                     text_color=BOSCH_COLORS["text_primary"])
        self.ent_inv.pack(fill="x", pady=(5,25))
        
        # Checkboxes blindadas
        cb_f = ctk.CTkFrame(cont, fg_color="transparent")
        cb_f.pack(fill="x", pady=10)
        cb_style = {"font": self.fonts["small"], "text_color": BOSCH_COLORS["text_primary"], 
                    "fg_color": BOSCH_COLORS["blue"], "border_color": BOSCH_COLORS["blue"], "corner_radius": 0}
        
        self.cb_cnc = ctk.CTkCheckBox(cb_f, text="CNC", **cb_style); self.cb_cnc.pack(side="left", padx=(0, 30))
        self.cb_plc = ctk.CTkCheckBox(cb_f, text="PLC", **cb_style); self.cb_plc.pack(side="left")

        # Botão Selecionar (Estilo Outlined)
        ctk.CTkButton(cont, text="+ SELECIONAR ARQUIVOS", height=45, corner_radius=0, 
                      fg_color="transparent", border_width=1, border_color=BOSCH_COLORS["blue"],
                      text_color=BOSCH_COLORS["blue"], hover_color=BOSCH_COLORS["background_light"],
                      command=self._select_files).pack(pady=20, anchor="w")

        self.scroll = ctk.CTkScrollableFrame(cont, height=300, corner_radius=0, 
                                             fg_color=BOSCH_COLORS["background_light"],
                                             border_color=BOSCH_COLORS["border_sutil"], border_width=1)
        self.scroll.pack(fill="both", expand=True)

        # Action Area Estática
        self.action_area = ctk.CTkFrame(cont, height=100, fg_color="transparent")
        self.action_area.pack(fill="x", pady=40)
        self.action_area.pack_propagate(False)

        self.btn_run = ctk.CTkButton(self.action_area, text="EXECUTAR COLETA", height=70, corner_radius=0, 
                                      fg_color=BOSCH_COLORS["blue"], text_color="white",
                                      font=self.fonts["subtitle"], command=self._on_submit)
        self.btn_run.pack(fill="both")

        self.prog_f = ctk.CTkFrame(self.action_area, fg_color="transparent")
        self.bar = ctk.CTkProgressBar(self.prog_f, height=15, progress_color=BOSCH_COLORS["blue"], corner_radius=0)
        self.bar.pack(fill="x", pady=10); self.bar.set(0)
        self.lbl_st = ctk.CTkLabel(self.prog_f, text="", font=self.fonts["log"], text_color=BOSCH_COLORS["text_secondary"])
        self.lbl_st.pack()

    def _select_files(self):
        f = ctk.filedialog.askopenfilenames()
        if f:
            self.selected_files.extend(f)
            for w in self.scroll.winfo_children(): w.destroy()
            for x in self.selected_files:
                ctk.CTkLabel(self.scroll, text=f"📄 {os.path.basename(x)}", 
                             text_color=BOSCH_COLORS["text_primary"]).pack(anchor="w", padx=10)

    def _on_submit(self):
        inv = self.ent_inv.get().strip()
        if not inv or not self.selected_files: return
        info = {"Inventário": inv, "Total de Arquivos": str(len(self.selected_files))}
        ConfirmationModal(self, "Revisão de Coleta", info, self._start_process, self.fonts)

    def _start_process(self):
        self.btn_run.pack_forget(); self.prog_f.pack(fill="both")
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            inv = gerar_nome_inventario_padrao(self.ent_inv.get())
            ts = [os.path.getmtime(f) for f in self.selected_files]
            dt = datetime.fromtimestamp(max(ts)).strftime("%Y%m%d")
            dest = os.path.join(CAMINHO_RAIZ_ORIGEM_07, inv, dt)
            os.makedirs(dest, exist_ok=True)
            
            for i, f in enumerate(self.selected_files, 1):
                self.after(0, lambda v=i/len(self.selected_files): self.bar.set(v))
                shutil.copy2(f, dest)
            
            self.after(0, lambda: self.lbl_st.configure(text="Sucesso!", text_color=BOSCH_COLORS["success"]))
            self.after(3000, self._reset_ui)
        except Exception as e:
            self.after(0, lambda: self.lbl_st.configure(text=f"Erro: {e}", text_color=BOSCH_COLORS["danger"]))

    def _reset_ui(self):
        self.prog_f.pack_forget(); self.btn_run.pack(fill="both")
        self.selected_files.clear(); [w.destroy() for w in self.scroll.winfo_children()]
        self.ent_inv.delete(0, 'end'); self.bar.set(0)

if __name__ == "__main__":
    app = ColetaApp()
    app.bind("<Configure>", app._handle_resize)
    app.mainloop()