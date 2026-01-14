import os
import shutil
import ctypes
import logging
from datetime import datetime
from src.core.utils import CAMINHO_RAIZ_ORIGEM_07, gerar_nome_inventario_padrao, BASE_DIR

# --- Configurações Locais do Script ---
NOME_PASTA_MAQUINA_PADRAO = "CNC_PLC"
PASTAS_MAQUINA_ANTIGAS = ["CNC", "PLC", "CNC + PLC", "CNC_PLC"]
LOG_FILE_NAME = "audit_trail.log"
USUARIO = os.getlogin()

# --- Configuração de Logging Compartilhada ---
def configurar_logging():
    """
    Configura o logger para salvar no mesmo diretório 'logs' que o App de Coleta usa.
    """
    path_logs = os.path.join(BASE_DIR, "logs")
    if not os.path.exists(path_logs):
        os.makedirs(path_logs)
        
    log_file = os.path.join(path_logs, LOG_FILE_NAME)
    
    logger = logging.getLogger("MasterScript")
    logger.setLevel(logging.INFO)
    
    # Evita duplicar handlers se o script for chamado múltiplas vezes
    if not logger.handlers:
        # File Handler (Arquivo)
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] [SCRIPT] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(fh)
        
        # Console Handler (Terminal)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        logger.addHandler(ch)
        
    return logger

logger = configurar_logging()


def obter_data_modificacao(caminho_item: str) -> str:
    """Retorna a data de modificação yyyymmdd."""
    try:
        timestamp = os.path.getmtime(caminho_item)
        return datetime.fromtimestamp(timestamp).strftime('%Y%m%d')
    except Exception as e:
        logger.error(f"Erro ao obter data de {caminho_item}: {e}")
        return datetime.now().strftime('%Y%m%d')

def cria_e_audita_pasta(caminho: str, contexto: str) -> bool:
    """Cria pasta se não existir e loga."""
    try:
        if not os.path.exists(caminho):
            os.makedirs(caminho)
            logger.info(f"[{contexto}] Pasta criada: {caminho}")
            return True
        return True # Já existe
    except Exception as e:
        logger.error(f"[{contexto}] Falha ao criar pasta {caminho}: {e}")
        return False

def reorganizar_pasta_data(caminho_data: str, nome_inventario: str) -> list[str]:
    """
    Verifica e reorganiza o conteúdo DENTRO de uma pasta yyyymmdd existente.
    """
    modificacoes = []
    nome_data = os.path.basename(caminho_data)
    caminho_destino_final = os.path.join(caminho_data, NOME_PASTA_MAQUINA_PADRAO)
    
    # 1. Checar se já existe a subpasta padrão
    subpastas_maquina_existentes = [
        d for d in os.listdir(caminho_data) 
        if os.path.isdir(os.path.join(caminho_data, d)) and d.upper() in [p.upper() for p in PASTAS_MAQUINA_ANTIGAS + [NOME_PASTA_MAQUINA_PADRAO]]
    ]
    
    # Se NENHUMA subpasta de máquina existir, criamos a CNC_PLC
    if not subpastas_maquina_existentes:
        if cria_e_audita_pasta(caminho_destino_final, "MASTER-REORG"):
             modificacoes.append(f"✅ Criada subpasta '{NOME_PASTA_MAQUINA_PADRAO}' dentro de {nome_data}.")
        else:
            modificacoes.append(f"❌ Erro ao criar '{NOME_PASTA_MAQUINA_PADRAO}' em {nome_data}.")
            return modificacoes

    # 2. Mover arquivos e pastas soltas para o CNC_PLC
    itens_movidos = 0
    for nome_item in os.listdir(caminho_data):
        caminho_item = os.path.join(caminho_data, nome_item)
        
        # Ignorar pastas de máquina que já são padrão (antigas e nova)
        if nome_item == NOME_PASTA_MAQUINA_PADRAO or nome_item.upper() in [p.upper() for p in PASTAS_MAQUINA_ANTIGAS]:
            continue
            
        # Se for um item solto (arquivo ou pasta não-padrão)
        if os.path.isfile(caminho_item) or os.path.isdir(caminho_item):
            # Garante que destino existe
            cria_e_audita_pasta(caminho_destino_final, "MASTER-REORG")
            
            shutil.move(caminho_item, caminho_destino_final)
            modificacoes.append(f"Conteúdo '{nome_item}' movido para '{NOME_PASTA_MAQUINA_PADRAO}' em {nome_data}.")
            logger.info(f"[MASTER-REORG]: Movido {nome_item} para {caminho_destino_final}.")
            itens_movidos += 1
    
    if not modificacoes and itens_movidos == 0 and not subpastas_maquina_existentes:
         pass
         
    return modificacoes

def padronizar_inventario(caminho_inventario: str) -> list[str]:
    """Padroniza uma única pasta de inventário, usando a data de modificação como destino."""
    
    nome_inventario = os.path.basename(caminho_inventario)
    modificacoes_inventario = []
    
    logger.info(f"--- INICIANDO MASTER - Inventário: {nome_inventario} ---")

    try:
        for nome_item in os.listdir(caminho_inventario):
            caminho_item = os.path.join(caminho_inventario, nome_item)
            
            # 1. Pasta de Data (yyyyMMdd) - Apenas Reorganizar Internamente
            if os.path.isdir(caminho_item) and len(nome_item) == 8 and nome_item.isdigit():
                modificacoes_inventario.extend(reorganizar_pasta_data(caminho_item, nome_inventario))
                continue
            
            # 2. Itens Soltos (Arquivos, CNC/PLC Antigos, Outras Pastas)
            # Determinar data de modificação (Destino Dinâmico)
            data_modificacao = obter_data_modificacao(caminho_item)
            caminho_data_destino = os.path.join(caminho_inventario, data_modificacao)
            caminho_destino_final = os.path.join(caminho_data_destino, NOME_PASTA_MAQUINA_PADRAO)
            
            # Cria a estrutura de destino
            if not cria_e_audita_pasta(caminho_destino_final, "MASTER-CREATE"):
                 modificacoes_inventario.append(f"❌ Erro ao criar estrutura de destino: {caminho_destino_final}")
                 continue
            
            if os.path.isfile(caminho_item):
                # Arquivo solto
                shutil.move(caminho_item, caminho_destino_final)
                modificacoes_inventario.append(f"Arquivo solto '{nome_item}' movido para o padrão ({data_modificacao}).")
                logger.info(f"[MASTER-MOVED]: Arquivo solto '{nome_item}' movido para {data_modificacao}.")

            elif os.path.isdir(caminho_item):
                
                # Pastas de tipo de máquina soltas
                if nome_item.upper() in [p.upper() for p in PASTAS_MAQUINA_ANTIGAS]: 
                    msg = f"Conteúdo de '{nome_item.upper()}' movido para o padrão ({data_modificacao}) e pasta antiga removida."
                    modificacoes_inventario.append(msg)
                    
                    for item_interno in os.listdir(caminho_item):
                        shutil.move(os.path.join(caminho_item, item_interno), caminho_destino_final)
                    
                    try:
                        os.rmdir(caminho_item)
                    except OSError:
                        logger.warning(f"Não foi possível remover a pasta {nome_item}, pode não estar vazia.")
                        
                    logger.info(f"[MASTER-MOVED]: Conteúdo de '{nome_item}' movido e pasta removida.")

                # Qualquer outra pasta solta (ex: 'Temp', 'Scripts')
                else:
                      modificacoes_inventario.append(f"Pasta solta '{nome_item}' movida para o padrão ({data_modificacao}).")
                      shutil.move(caminho_item, caminho_destino_final)
                      logger.info(f"[MASTER-MOVED]: '{nome_item}' movida para {data_modificacao}.")

    except Exception as e:
        erro_msg = f"❌ ERRO CRÍTICO no Inventário {nome_inventario}: {e}"
        logger.error(f"[MASTER-CRITICAL]: {erro_msg}", exc_info=True)
        modificacoes_inventario.append(erro_msg)
    
    logger.info(f"--- FIM DA MASTER - Inventário: {nome_inventario} ---")
    
    return [f"**{nome_inventario}**: {mod}" for mod in modificacoes_inventario]

def executar_master():
    """Percorre a pasta raiz, renomeia as pastas de inventário e padroniza o conteúdo interno."""
    
    logger.info(f"Iniciando Execução Master em: {CAMINHO_RAIZ_ORIGEM_07}")
    
    if not os.path.isdir(CAMINHO_RAIZ_ORIGEM_07):
        erro_path = f"O caminho raiz de origem (07) não existe ou está inacessível. Verifique config.json"
        logger.error(f"[MASTER-FATAL] {erro_path}")
        exibir_aviso_final(False, [erro_path], "Falha no Caminho Raiz")
        return
        
    inventarios_a_processar = []
    pastas_renomeadas = []

    # 1. Primeira Passagem: Renomear todas as pastas para o padrão de 12 caracteres
    for nome_item in os.listdir(CAMINHO_RAIZ_ORIGEM_07):
        caminho_item = os.path.join(CAMINHO_RAIZ_ORIGEM_07, nome_item)
        
        if os.path.isdir(caminho_item):
            try:
                nome_padrao = gerar_nome_inventario_padrao(nome_item)
                
                if nome_item != nome_padrao:
                    caminho_padrao = os.path.join(CAMINHO_RAIZ_ORIGEM_07, nome_padrao)
                    
                    if os.path.exists(caminho_padrao):
                         logger.warning(f"[MASTER-RENAME] Destino {nome_padrao} já existe. Pulando renomeação de {nome_item}.")
                         inventarios_a_processar.append(caminho_item)
                         continue
                         
                    os.rename(caminho_item, caminho_padrao)
                    pastas_renomeadas.append(f"**{nome_item}** -> **{nome_padrao}**")
                    logger.info(f"[MASTER-RENAME]: {nome_item} renomeado para {nome_padrao} | Usuário: {USUARIO}")
                    inventarios_a_processar.append(caminho_padrao)
                else:
                    inventarios_a_processar.append(caminho_item)
            
            except ValueError as e:
                logger.error(f"[MASTER-RENAME] Pulando item '{nome_item}' por erro de validação: {e}")
                
    if not inventarios_a_processar:
        mensagem = f"Nenhuma pasta de inventário válida encontrada em '{CAMINHO_RAIZ_ORIGEM_07}' para processar."
        logger.warning(f"[MASTER-INFO] {mensagem}")
        exibir_aviso_final(True, [mensagem], "Nenhum Inventário Processado")
        return

    # 2. Segunda Passagem: Padronizar o CONTEÚDO interno
    todas_modificacoes = []
    
    if pastas_renomeadas:
        todas_modificacoes.append(f"--- PASTAS DE INVENTÁRIO RENOMEADAS ({len(pastas_renomeadas)}) ---")
        todas_modificacoes.extend(pastas_renomeadas)
        todas_modificacoes.append("-------------------------------------------------")
        
    for caminho_inventario in inventarios_a_processar:
        modificacoes = padronizar_inventario(caminho_inventario)
        
        # Filtra mensagens técnicas demais, mostra só ações reais
        modificacoes_filtradas = [m for m in modificacoes if not ("Estrutura de destino" in m and "Criada" in m)]
        
        if modificacoes_filtradas:
            todas_modificacoes.extend(modificacoes_filtradas)
        
    # --- Aviso Final ---
    if todas_modificacoes:
        exibir_aviso_final(True, todas_modificacoes, f"{len(inventarios_a_processar)} Inventários Processados")
    else:
        exibir_aviso_final(True, [], f"{len(inventarios_a_processar)} Inventários Processados")


def exibir_aviso_final(sucesso: bool, modificacoes: list, titulo_contexto: str):
    """Exibe um pop-up de aviso usando a API nativa do Windows."""
    
    titulo = f"✅ Padronização Concluída ({titulo_contexto})" if sucesso else f"❌ Erro na Padronização ({titulo_contexto})"
    
    if sucesso:
        erros_criticos = [m for m in modificacoes if "ERRO CRÍTICO" in m]
        renomeacoes = [m for m in modificacoes if "->" in m]
        
        if erros_criticos or renomeacoes or any("movido" in m or "removida" in m or "Criada subpasta" in m for m in modificacoes):
            detalhes = []
            if renomeacoes:
                detalhes.append(f"- **{len(renomeacoes)}** Pastas de Inventário Renomeadas.")
            if erros_criticos:
                 detalhes.append(f"- **{len(erros_criticos)}** Erro(s) Crítico(s) (Verifique o log!)")
            
            modificacoes_internas = len(modificacoes) - len(renomeacoes) - len(erros_criticos)
            if modificacoes_internas > 0:
                 detalhes.append(f"- **{modificacoes_internas}** Alterações Internas (arquivos/pastas movidos).")

            detalhes_lista = '\n'.join(detalhes)
            
            mensagem = (
                f"A padronização Master foi concluída.\n\n"
                f"Usuário: {USUARIO}\n"
                f"Resumo:\n{detalhes_lista}\n\n"
                f"Verifique o Log em: logs/{LOG_FILE_NAME}"
            )
            estilo = 0x40 # MB_ICONINFORMATION
        else:
            mensagem = (
                f"A padronização Master foi concluída.\n\n"
                f"Usuário: {USUARIO}\n"
                f"Tudo já estava organizado."
            )
            estilo = 0x40 # MB_ICONINFORMATION
    else:
        mensagem = (
            f"Ocorreu um erro FATAL no início da padronização Master.\n\n"
            f"Usuário: {USUARIO}\n"
            f"Erro:\n{modificacoes[0]}\n\n"
            f"Verifique o Log em: logs/{LOG_FILE_NAME}"
        )
        estilo = 0x10 # MB_ICONERROR

    try:
        ctypes.windll.user32.MessageBoxW(0, mensagem, titulo, estilo)
    except Exception as e:
        print(f"\n--- AVISO POP-UP ---\n{titulo}\n{mensagem}\n")
        logger.error(f"[MASTER-POPUP] Falha ao exibir pop-up: {e}")

# --- Execução Principal ---
if __name__ == "__main__":
    executar_master()