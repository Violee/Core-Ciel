import os
import json
import re
from datetime import datetime
from pathlib import Path

RDO_GERAL = Path("/data/logs/rdo_geral/rdo_geral.json")
DOWNLOADED = Path("/data/logs/rdo_geral/downloaded_rdos.json")
RESP_ESPERADOS = Path("/app/app/core/managers.json")
STATUS_DIARIO = Path("/data/logs/rdo_geral/status_diario_responsaveis.json")
DIAS_AVISADOS = Path("/data/logs/rdo_geral/dias_avisados.json")

def carregar_json(caminho, default):
    if not os.path.exists(caminho):
        return default
    with open(caminho, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list) and data and "conteudo" in data[0]:
        return data[0]["conteudo"]
    return data


def salvar_json(caminho, data):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extrair_responsavel(descricao=""):
    m = re.search(r"RDO\)\s*-\s*(?:RP:\s*)?(.+)$", descricao)
    return m.group(1).strip() if m else None


def data_rdo_para_chave(data_str):
    return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")

def verify_day():
    rdo_geral = carregar_json(RDO_GERAL, {})
    downloaded = carregar_json(DOWNLOADED, {})
    responsaveis_esperados = carregar_json(RESP_ESPERADOS, {})
    status_diario = carregar_json(STATUS_DIARIO, {})
    dias_avisados = carregar_json(DIAS_AVISADOS, {})

    lista_responsaveis = []

    for obra in responsaveis_esperados.values():
        for nome in obra.get("responsaveis", {}).keys():
            if nome not in lista_responsaveis:
                lista_responsaveis.append(nome)

    aprovados_por_dia = {}

    for rdo_id in downloaded.keys():
        rdo = rdo_geral.get(rdo_id)
        if not rdo:
            continue

        data_chave = data_rdo_para_chave(rdo["data"])
        responsavel = extrair_responsavel(rdo.get("descricao", ""))
        if not responsavel:
            continue

        if data_chave not in aprovados_por_dia:
            aprovados_por_dia[data_chave] = set()

        if rdo.get("status") == "Aprovado":
            aprovados_por_dia[data_chave].add(responsavel)

    dias_prontos_para_avisar = []

    for data_chave, aprovados in aprovados_por_dia.items():
        aprovado = []
        em_andamento = []

        for nome in lista_responsaveis:
            if nome in aprovados:
                aprovado.append(nome)
            else:
                em_andamento.append(nome)

        geral_pronto = len(em_andamento) == 0

        status_diario[data_chave] = {
            "geral_pronto": geral_pronto,
            "aprovado": sorted(aprovado),
            "em_andamento": sorted(em_andamento)
        }

        if geral_pronto and not dias_avisados.get(data_chave):
            dias_prontos_para_avisar.append(data_chave)
            dias_avisados[data_chave] = True

    salvar_json(STATUS_DIARIO, status_diario)
    salvar_json(DIAS_AVISADOS, dias_avisados)

    return {
        "status": "ok",
        "dias_prontos": sorted(dias_prontos_para_avisar)
    }

if __name__ == "__main__":
    result = verify_day()
    print(json.dumps(result, ensure_ascii=False))