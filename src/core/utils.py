import os
import sys
import json
import getpass
import win32security # PIP INSTALL PYWIN32
from datetime import datetime

# --- LÓGICA DE CAMINHOS RESILIENTE ---
if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Configurações de Pastas de Log e Data
PATH_DIRETORIO_LOG_CENTRAL = os.path.join(BASE_DIR, "logs")
PATH_DATA = os.path.join(BASE_DIR, "data")
LOG_FILE_NAME = "audit_trail.log"
SNAPSHOT_FILE_NAME = "folder_state.json"

for path in [PATH_DIRETORIO_LOG_CENTRAL, PATH_DATA]:
    if not os.path.exists(path):
        os.makedirs(path)

# --- CONFIGURAÇÃO DE AMBIENTE ---
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

def carregar_configuracao():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            env = data.get("APP_ENV", "TEST")
            return env, data.get(env)
    except Exception:
        return "TEST", {
            "PATH_ORIGEM_07": "07_origem",
            "PATH_DESTINO_06": "06_destino"
        }

AMBIENTE, CONTEXTO = carregar_configuracao()

CAMINHO_RAIZ_ORIGEM_07 = os.path.join(CONTEXTO["PATH_ORIGEM_07"])
CAMINHO_RAIZ_DESTINO_06 = os.path.join(CONTEXTO["PATH_DESTINO_06"])

# --- FUNÇÕES UTILITÁRIAS ---
def gerar_nome_inventario_padrao(termo: str) -> str:
    nums = "".join(filter(str.isdigit, termo))
    return f"2{nums[-11:].zfill(11)}"

def get_file_owner(filepath: str) -> str:
    """Descobre o dono do arquivo via Windows Security API."""
    try:
        sd = win32security.GetFileSecurity(filepath, win32security.OWNER_SECURITY_INFORMATION)
        owner_sid = sd.GetSecurityDescriptorOwner()
        name, domain, type = win32security.LookupAccountSid(None, owner_sid)
        return f"{domain}\\{name}"
    except Exception:
        return "UNKNOWN_OWNER"

def audit_log(folder: str, files: list, src: str, dest: str, custom_user=None):
    try:
        username = custom_user if custom_user else getpass.getuser()
    except Exception:
        username = "UNKNOWN"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    files_str = ", ".join(files) if files else "Nenhum arquivo"
    
    log_entry = (
        f"[{timestamp}] [USER: {username}] "
        f"Folder: {folder} | "
        f"{src} -> {dest} | "
        f"Arquivos: [{files_str}]\n"
    )

    log_path = os.path.join(PATH_DIRETORIO_LOG_CENTRAL, LOG_FILE_NAME)
    
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Erro ao salvar log: {e}")

# --- SNAPSHOT MANAGER ---
class SnapshotManager:
    def __init__(self, root_path):
        self.root_path = root_path
        self.snapshot_path = os.path.join(PATH_DATA, SNAPSHOT_FILE_NAME)

    def _get_current_state(self):
        current_files = set()
        if not os.path.exists(self.root_path):
            return current_files
            
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.root_path)
                current_files.add(rel_path)
        return current_files

    def check_changes_and_log(self):
        current_state = self._get_current_state()
        
        if os.path.exists(self.snapshot_path):
            with open(self.snapshot_path, 'r') as f:
                try:
                    old_state = set(json.load(f))
                except:
                    old_state = set()
        else:
            old_state = set()

        added = current_state - old_state
        deleted = old_state - current_state
        
        # --- DETECÇÃO DE MOVIMENTAÇÃO (Crucial para o seu pedido) ---
        moves = []
        # Convertemos para lista para poder modificar os sets originais
        for del_path in list(deleted):
            del_name = os.path.basename(del_path)
            
            # Procura se esse arquivo deletado apareceu nos adicionados (Mover = Delete + Add)
            for add_path in list(added):
                add_name = os.path.basename(add_path)
                
                if del_name == add_name:
                    # ENCONTRAMOS UM MOVIMENTO!
                    moves.append((del_path, add_path))
                    
                    # Remove das listas de "Adicionado" e "Deletado" para não duplicar o log
                    if del_path in deleted: deleted.remove(del_path)
                    if add_path in added: added.remove(add_path)
                    break
        
        # 1. LOGA AS MOVIMENTAÇÕES
        for old_path, new_path in moves:
            full_new_path = os.path.join(self.root_path, new_path)
            owner = get_file_owner(full_new_path) # Conseguimos saber o dono pois o arquivo existe!
            filename = os.path.basename(new_path)
            
            audit_log(
                folder="Movimentação Interna",
                files=[filename],
                src=os.path.dirname(old_path),  # Pasta Antiga
                dest=os.path.dirname(new_path), # Pasta Nova
                custom_user=owner
            )

        # 2. LOGA AS ADIÇÕES RESTANTES
        if added:
            files_by_folder = {}
            for rel_path in added:
                full_path = os.path.join(self.root_path, rel_path)
                folder = os.path.dirname(rel_path)
                filename = os.path.basename(rel_path)
                
                owner = get_file_owner(full_path)
                
                key = (folder, owner)
                if key not in files_by_folder: files_by_folder[key] = []
                files_by_folder[key].append(filename)
            
            for (folder, owner), files in files_by_folder.items():
                audit_log(
                    folder=folder if folder else "Raiz",
                    files=files,
                    src="Externo/Offline",
                    dest=f"{folder}",
                    custom_user=owner
                )

        # 3. LOGA AS REMOÇÕES RESTANTES (Sem dono, infelizmente)
        if deleted:
            files_by_folder = {}
            for rel_path in deleted:
                folder = os.path.dirname(rel_path)
                filename = os.path.basename(rel_path)
                if folder not in files_by_folder: files_by_folder[folder] = []
                files_by_folder[folder].append(filename)

            for folder, files in files_by_folder.items():
                audit_log(
                    folder=folder if folder else "Raiz",
                    files=files,
                    src=f"{folder}",
                    dest="Removido/Deletado",
                    custom_user="UNKNOWN/DELETED"
                )

        self.save_snapshot(current_state)

    def save_snapshot(self, state_set=None):
        if state_set is None:
            state_set = self._get_current_state()
        
        with open(self.snapshot_path, 'w') as f:
            json.dump(list(state_set), f)

monitor = SnapshotManager(CAMINHO_RAIZ_ORIGEM_07)