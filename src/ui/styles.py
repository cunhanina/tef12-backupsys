import customtkinter as ctk

# Paleta Oficial Bosch Digital
BOSCH_COLORS = {
    "blue": "#007BC0",            # Ação Primária
    "blue_hover": "#005A8C",      # Hover do botão
    "text_primary": "#000000",    # Títulos e Dados
    "text_secondary": "#525F6B",  # Labels e suporte
    "background_white": "#FFFFFF",
    "background_light": "#F2F4F5",# Background de inputs e frames
    "border_sutil": "#D1D3D4",    # Bordas de inputs
    "danger": "#ED0007",          # Erros
    "success": "#18837E"          # Sucesso
}

def get_fonts():
    return {
        "title": ctk.CTkFont(family="Bosch Sans", size=26, weight="bold"),
        "subtitle": ctk.CTkFont(family="Bosch Sans", size=15, weight="bold"),
        "small": ctk.CTkFont(family="Bosch Sans", size=13, weight="bold"),
        "log": ctk.CTkFont(family="Consolas", size=12)
    }