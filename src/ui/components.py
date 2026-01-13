import customtkinter as ctk
import os
from src.ui.styles import BOSCH_COLORS

class ConfirmationModal(ctk.CTkToplevel):
    """Componente unificado de revisão para Coleta e Gestão."""
    def __init__(self, master, title, info_dict, on_confirm, fonts):
        super().__init__(master)
        self.title(title)
        self.attributes("-topmost", True)
        self.configure(fg_color=BOSCH_COLORS["background_white"])
        self.resizable(False, False)
        self.on_confirm = on_confirm
        self.fonts = fonts
        
        # UI Setup
        ctk.CTkLabel(self, text="", height=4, fg_color=BOSCH_COLORS["blue"]).pack(fill="x")
        ctk.CTkLabel(self, text=title.upper(), font=fonts["title"], text_color=BOSCH_COLORS["blue"]).pack(pady=20)
        
        box = ctk.CTkFrame(self, fg_color=BOSCH_COLORS["background_light"], corner_radius=0)
        box.pack(fill="x", padx=40, pady=10)
        
        for lbl, val in info_dict.items():
            r = ctk.CTkFrame(box, fg_color="transparent")
            r.pack(fill="x", padx=15, pady=5)
            ctk.CTkLabel(r, text=lbl, font=fonts["small"], text_color=BOSCH_COLORS["text_secondary"]).pack(side="left")
            ctk.CTkLabel(r, text=val, font=fonts["subtitle"], text_color=BOSCH_COLORS["text_primary"]).pack(side="right")
            
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", side="bottom", pady=30, padx=40)
        ctk.CTkButton(btns, text="Voltar", width=120, height=40, corner_radius=0, fg_color="transparent", border_width=1, border_color=BOSCH_COLORS["border_sutil"], text_color=BOSCH_COLORS["text_primary"], command=self.destroy).pack(side="left")
        ctk.CTkButton(btns, text="Confirmar", width=240, height=40, corner_radius=0, fg_color=BOSCH_COLORS["blue"], command=self._handle_confirm).pack(side="right")

        self.withdraw(); self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width()//2) - 270
        y = master.winfo_y() + (master.winfo_height()//2) - 250
        self.geometry(f"540x500+{x}+{y}"); self.deiconify(); self.grab_set()

    def _handle_confirm(self):
        self.destroy()
        self.on_confirm()   