import os
import sys
import json
from datetime import datetime

# --- LÓGICA DE CAMINHOS RESILIENTE ---
# Detecta se está rodando como script ou como executável (.exe)
if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
<<<<<<< HEAD
=======
    # Ajusta para subir dois níveis a partir de src/core/ para a raiz do projeto
>>>>>>> 0da70c54e8b4dc6b08a9c23c946615227fcbbc4f
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Configurações de Pastas de Log
PATH_DIRETORIO_LOG_CENTRAL = os.path.join(BASE_DIR, "logs")
LOG_FILE_NAME = "audit_trail.log"

# Garante que a pasta de logs exista
if not os.path.exists(PATH_DIRETORIO_LOG_CENTRAL):
    os.makedirs(PATH_DIRETORIO_LOG_CENTRAL)

# --- CONFIGURAÇÃO DE AMBIENTE ---
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

def carregar_configuracao():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            env = data.get("APP_ENV", "TEST")
            return env, data.get(env)
    except Exception:
        # Fallback para testes locais caso o config.json suma
        return "TEST", {
            "PATH_ORIGEM_07": "07_origem",
            "PATH_DESTINO_06": "06_destino"
        }

AMBIENTE, CONTEXTO = carregar_configuracao()

# Exportação dos caminhos globais
CAMINHO_RAIZ_ORIGEM_07 = os.path.join(BASE_DIR, CONTEXTO["PATH_ORIGEM_07"])
CAMINHO_RAIZ_DESTINO_06 = os.path.join(BASE_DIR, CONTEXTO["PATH_DESTINO_06"])

# --- FUNÇÕES UTILITÁRIAS ---
def gerar_nome_inventario_padrao(termo: str) -> str:
    """Padroniza o inventário para o formato Bosch (12 dígitos iniciando com 2)."""
    nums = "".join(filter(str.isdigit, termo))
    return f"2{nums[-11:].zfill(11)}"

def audit_log(mensagem: str):
    """Registra eventos no arquivo de log centralizado."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = os.path.join(PATH_DIRETORIO_LOG_CENTRAL, LOG_FILE_NAME)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{AMBIENTE}] {mensagem}\n")