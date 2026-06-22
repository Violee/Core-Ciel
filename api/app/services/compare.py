import json
import os
from datetime import datetime
from pathlib import Path

RDO_ATUAL = Path("/data/logs/rdo_geral/rdo_geral.json")
STATE_FILE = Path("/data/logs/rdo_geral/rdo_state.json")
FIRST_EXEC_FILE = Path("/data/logs/first_exec.json")

LIMITE_DIAS_NOVO = 7

def carregar_json(caminho):
    if not os.path.exists(caminho):
        print("ARQUIVO NÃO EXISTE:", caminho)
        return {}

    with open(caminho, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list) and len(data) > 0:
        item = data[0]
        if isinstance(item, dict) and "conteudo" in item:
            return item["conteudo"]

    if isinstance(data, dict):
        return data

    return {}

def salvar_json(caminho, conteudo):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(conteudo, f, ensure_ascii=False, indent=2)

def data_recente(data_str):
    try:
        data = datetime.strptime(data_str, "%d/%m/%Y")
        return (datetime.now() - data).days <= LIMITE_DIAS_NOVO
    except Exception:
        return False

def controlar_primeira_execucao():
    if not os.path.exists(FIRST_EXEC_FILE):
        salvar_json(FIRST_EXEC_FILE, {
            "first_exec": True,
            "date_first_exec": datetime.now().isoformat()
        })
        return True

    data = carregar_json(FIRST_EXEC_FILE)

    if data.get("first_exec") is True:
        data["first_exec"] = False
        salvar_json(FIRST_EXEC_FILE, data)

    return False

def monitorar():
    first_exec = controlar_primeira_execucao()

    estado_atual = carregar_json(RDO_ATUAL)
    estado_anterior = carregar_json(STATE_FILE)

    print("TOTAL LIDO:", len(estado_atual))

    eventos = []
    novo_estado = {}

    for rdo_id, rdo in estado_atual.items():
        status = rdo.get("status")
        data = rdo.get("data")

        if rdo_id not in estado_anterior:
            if data_recente(data):
                eventos.append({
                    "tipo": "novo",
                    **rdo
                })
        else:
            status_antigo = estado_anterior[rdo_id].get("status")
            if status_antigo != status:
                eventos.append({
                    "tipo": "alterado",
                    "status_anterior": status_antigo,
                    **rdo
                })

        novo_estado[rdo_id] = rdo

    salvar_json(STATE_FILE, novo_estado)

    return {
        "executado_em": datetime.now().isoformat(),
        "first_exec": first_exec,
        "total_rdos_atual": len(estado_atual),
        "total_eventos": len(eventos),
        "eventos": eventos
    }
