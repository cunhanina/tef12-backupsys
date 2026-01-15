import os
import threading
import shutil
import re
from datetime import datetime
import customtkinter as ctk
from PIL import Image
from tkinterdnd2 import TkinterDnD, DND_FILES

from src.core.utils import (
    CAMINHO_RAIZ_ORIGEM_07, 
    gerar_nome_inventario_padrao, 
    BASE_DIR,
    audit_log,
    monitor # Importante: importar o monitor
)
from src.ui.styles import BOSCH_COLORS, get_fonts
from src.ui.components import ConfirmationModal

class FileRow(ctk.CTkFrame):
    def __init__(self, master, filepath, on_delete_callback, fonts):
        super().__init__(master, fg_color="transparent", height=45)
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        
        self.lbl = ctk.CTkLabel(
            self, 
            text=f"  {self.filename}", 
            text_color=BOSCH_COLORS["text_primary"],
            font=fonts["small"],
            anchor="w"
        )
        self.lbl.pack(side="left", fill="x", expand=True, padx=(5, 10))

        self.btn_del = ctk.CTkButton(
            self, 
            text="✕", 
            width=35, 
            height=35,
            corner_radius=0, 
            fg_color=BOSCH_COLORS["danger"],
            hover_color="#C00005", 
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: on_delete_callback(self)
        )
        self.btn_del.pack(side="right")

class ColetaApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        
        self.withdraw()
        self.title("TEF12 - Coleta de Backup")
        self.configure(fg_color=BOSCH_COLORS["background_white"])
        
        self.fonts = get_fonts()
        self.assets, self._resize_timer = {}, None
        self.selected_files = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        
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
        self.sg_bar.configure(image=ctk.CTkImage(self.assets["sg"], size=(w, 12)))
        asp = self.assets["logo"].width / self.assets["logo"].height
        self.logo_label.configure(image=ctk.CTkImage(self.assets["logo"], size=(int(60*asp), 60)))

    def _setup_ui(self):
        self.sg_bar = ctk.CTkLabel(self, text="", height=12, fg_color="transparent")
        self.sg_bar.grid(row=0, column=0, sticky="ew")
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=1, column=0, sticky="ew", padx=80, pady=30)
        
        t_box = ctk.CTkFrame(header, fg_color="transparent")
        t_box.pack(side="left")
        ctk.CTkLabel(t_box, text="TEF12", font=self.fonts["title"], text_color=BOSCH_COLORS["blue"]).pack(side="left")
        ctk.CTkLabel(t_box, text=" | Coleta de Backup", font=self.fonts["title"], text_color=BOSCH_COLORS["text_primary"]).pack(side="left", padx=5)
        self.logo_label = ctk.CTkLabel(header, text="")
        self.logo_label.pack(side="right")

        self.cont = ctk.CTkFrame(self, fg_color="transparent")
        self.cont.grid(row=2, column=0, sticky="nsew", padx=80, pady=(0, 10))
        
        ctk.CTkLabel(self.cont, text="Nº INVENTÁRIO", font=self.fonts["small"], text_color=BOSCH_COLORS["text_secondary"]).pack(anchor="w")
        self.ent_inv = ctk.CTkEntry(self.cont, height=50, corner_radius=0, 
                                     border_color=BOSCH_COLORS["border_sutil"],
                                     fg_color=BOSCH_COLORS["background_light"],
                                     text_color=BOSCH_COLORS["text_primary"])
        self.ent_inv.pack(fill="x", pady=(5,25))
        
        cb_f = ctk.CTkFrame(self.cont, fg_color="transparent")
        cb_f.pack(fill="x", pady=(0, 20))
        cb_style = {"font": self.fonts["small"], "text_color": BOSCH_COLORS["text_primary"], 
                    "fg_color": BOSCH_COLORS["blue"], "border_color": BOSCH_COLORS["blue"], "corner_radius": 0}
        
        self.cb_cnc = ctk.CTkCheckBox(cb_f, text="CNC", **cb_style); self.cb_cnc.pack(side="left", padx=(0, 30))
        self.cb_plc = ctk.CTkCheckBox(cb_f, text="PLC", **cb_style); self.cb_plc.pack(side="left")

        self.drop_container = ctk.CTkFrame(self.cont, fg_color=BOSCH_COLORS["background_light"], 
                                           border_color=BOSCH_COLORS["blue"], border_width=2, corner_radius=0)
        self.drop_container.pack(fill="both", expand=True, pady=10)
        
        self.drop_container.drop_target_register(DND_FILES)
        self.drop_container.dnd_bind('<<Drop>>', self._on_drop)

        self.empty_state_frame = ctk.CTkFrame(self.drop_container, fg_color="transparent")
        ctk.CTkLabel(self.empty_state_frame, text="⭳", font=("Arial", 40), 
                     text_color=BOSCH_COLORS["blue"]).pack(pady=(0, 10))
        ctk.CTkLabel(self.empty_state_frame, text="Arraste e solte arquivos aqui", 
                     font=self.fonts["subtitle"], text_color=BOSCH_COLORS["text_primary"]).pack()
        ctk.CTkLabel(self.empty_state_frame, text="ou", 
                     font=self.fonts["small"], text_color=BOSCH_COLORS["text_secondary"]).pack(pady=5)
        ctk.CTkButton(self.empty_state_frame, text="SELECIONAR DO COMPUTADOR", 
                      fg_color="transparent", border_width=1, border_color=BOSCH_COLORS["blue"],
                      text_color=BOSCH_COLORS["blue"], hover_color="#E6F2F8", corner_radius=0,
                      command=self._select_files).pack(pady=10)

        self.list_container = ctk.CTkFrame(self.drop_container, fg_color="transparent")
        list_header = ctk.CTkFrame(self.list_container, fg_color="transparent", height=40)
        list_header.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(list_header, text="ARQUIVOS SELECIONADOS", 
                     font=self.fonts["small"], text_color=BOSCH_COLORS["blue"]).pack(side="left")
        ctk.CTkButton(list_header, text="+ ADICIONAR", width=80, height=30, corner_radius=0,
                      fg_color="transparent", border_width=1, border_color=BOSCH_COLORS["blue"],
                      text_color=BOSCH_COLORS["blue"], command=self._select_files).pack(side="right")
        self.scroll = ctk.CTkScrollableFrame(self.list_container, corner_radius=0, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.empty_state_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.footer = ctk.CTkFrame(self, height=100, fg_color="transparent")
        self.footer.grid(row=3, column=0, sticky="ew", padx=80, pady=40)
        self.footer.pack_propagate(False)

        self.btn_run = ctk.CTkButton(self.footer, text="EXECUTAR COLETA", height=70, corner_radius=0, 
                                     fg_color=BOSCH_COLORS["blue"], text_color="white",
                                     font=self.fonts["subtitle"], command=self._on_submit)
        self.btn_run.pack(fill="both")

        self.prog_f = ctk.CTkFrame(self.footer, fg_color="transparent")
        self.bar = ctk.CTkProgressBar(self.prog_f, height=15, progress_color=BOSCH_COLORS["blue"], corner_radius=0)
        self.bar.pack(fill="x", pady=10); self.bar.set(0)
        self.lbl_st = ctk.CTkLabel(self.prog_f, text="", font=self.fonts["log"], text_color=BOSCH_COLORS["text_secondary"])
        self.lbl_st.pack()

    def _update_drop_zone_view(self):
        if not self.selected_files:
            self.list_container.pack_forget()
            self.empty_state_frame.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.empty_state_frame.place_forget()
            self.list_container.pack(fill="both", expand=True)

    def _on_drop(self, event):
        raw_data = event.data
        if '{' in raw_data:
            files = re.findall(r'\{(.*?)\}', raw_data)
        else:
            files = raw_data.split()
        new_files = [f for f in files if os.path.isfile(f)]
        self._add_files(new_files)

    def _add_files(self, file_paths):
        for path in file_paths:
            if path not in self.selected_files:
                self.selected_files.append(path)
                row = FileRow(self.scroll, path, self._remove_file, self.fonts)
                row.pack(fill="x", pady=2)
        self._update_drop_zone_view()

    def _remove_file(self, row_widget):
        path = row_widget.filepath
        if path in self.selected_files:
            self.selected_files.remove(path)
        row_widget.destroy()
        self._update_drop_zone_view()

    def _select_files(self):
        f = ctk.filedialog.askopenfilenames()
        if f:
            self._add_files(f)

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
            
            file_names = [os.path.basename(f) for f in self.selected_files]
            source_dir = os.path.dirname(self.selected_files[0]) if self.selected_files else "Upload Manual"

            for i, f in enumerate(self.selected_files, 1):
                self.after(0, lambda v=i/len(self.selected_files): self.bar.set(v))
                shutil.copy2(f, dest)
            
            # Log de auditoria
            audit_log(
                folder=inv,
                files=file_names,
                src=source_dir,
                dest=dest
            )
            
            # CRÍTICO: Atualizar o snapshot para que esses arquivos não apareçam como "novos" na próxima checagem
            monitor.save_snapshot()
            
            self.after(0, lambda: self.lbl_st.configure(text="Sucesso!", text_color=BOSCH_COLORS["success"]))
            self.after(3000, self._reset_ui)
        except Exception as e:
            self.after(0, lambda: self.lbl_st.configure(text=f"Erro: {e}", text_color=BOSCH_COLORS["danger"]))

    def _reset_ui(self):
        self.prog_f.pack_forget(); self.btn_run.pack(fill="both")
        self.selected_files.clear()
        for w in self.scroll.winfo_children(): w.destroy()
        self.ent_inv.delete(0, 'end'); self.bar.set(0)
        self._update_drop_zone_view()

if __name__ == "__main__":
    app = ColetaApp()
    app.bind("<Configure>", app._handle_resize)
    app.mainloop()