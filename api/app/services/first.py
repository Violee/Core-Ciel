import os
import json
import re
import requests # type: ignore
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

DATA_INICIAL = "2025-12-20"
TOKEN = os.getenv("DIARIO_OBRA_TOKEN")

MEDIA_DIR = Path("/data/media/RDO")
RDO_GERAL = Path("/data/logs/rdo_geral/rdo_geral.json")
DOWNLOADED = Path("/data/logs/rdo_geral/downloaded_rdos.json")
RESPONSAVEIS = Path("/app/app/core/managers.json")

API_BASE = "https://apiexterna.diariodeobra.app/v1"
HEADERS = {"Token": TOKEN}

MAX_WORKERS_FOTOS = 32
MAX_WORKERS_RDOS = 5

session = requests.Session()
session.headers.update(HEADERS)

def carregar_json(path, default):
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def salvar_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def caminho_saida_por_data(data_str):
    return MEDIA_DIR / datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")

def baixar_arquivo(url, destino):
    if destino.exists():
        return

    destino.parent.mkdir(parents=True, exist_ok=True)

    r = session.get(url, stream=True, timeout=120)
    r.raise_for_status()

    with open(destino, "wb") as f:
        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)

def baixar_relatorio_api(obra_id, rdo_id):
    url = f"{API_BASE}/obras/{obra_id}/relatorios/{rdo_id}"
    r = session.get(url, timeout=120)
    r.raise_for_status()
    return r.json()

def extrair_responsavel(descricao):
    if not descricao:
        return None
    m = re.search(r"RP:\s*(.+)$", descricao)
    return m.group(1).strip() if m else None

def responsavel_valido(obra_id, responsavel, data_rdo, mapa):
    obra = mapa.get(obra_id)
    if not obra:
        return False

    info = obra.get("responsaveis", {}).get(responsavel)
    if not info:
        return False

    inicio = datetime.strptime(info["inicio"], "%Y-%m-%d").date()
    fim = (
        datetime.strptime(info["fim"], "%Y-%m-%d").date()
        if info.get("fim") else None
    )

    return inicio <= data_rdo and (fim is None or data_rdo <= fim)

def salvar_txt_atividade(pasta, atividade):
    texto = atividade.get("observacao")
    hora_inicio = atividade.get("hora_inicio", "")
    hora_fim = atividade.get("hora_fim", "")
    fotos = atividade.get("fotos", [])

    if not texto and not fotos and not hora_inicio:
        return

    path = pasta / "atividade.txt"

    with open(path, "w", encoding="utf-8") as f:
        if hora_inicio:
            horario = f"{hora_inicio}"
            if hora_fim:
                horario += f" - {hora_fim}"
            f.write(f"Horário: {horario}\n\n")

        f.write("Atividade:\n")
        if texto:
            f.write(texto.strip())
            f.write("\n\n")

        if fotos:
            f.write("Fotos:\n")
            for i, foto in enumerate(fotos, 1):
                nome = foto.get("arquivo", f"foto_{i}")
                f.write(f"- {nome}\n")
            f.write("\n")

def salvar_ocorrencias_txt(pasta_atividades, rel):
    path = pasta_atividades / "ocorrencias.txt"

    comentarios = rel.get("comentarios", [])
    ocorrencias = rel.get("ocorrencias", [])

    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            f.write("COMENTÁRIOS:\n\n")
            f.write("OCORRÊNCIAS:\n")

    with open(path, "r", encoding="utf-8") as f:
        conteudo = f.read()

    with open(path, "a", encoding="utf-8") as f:

        if comentarios:
            pos = conteudo.find("OCORRÊNCIAS:")
            f.seek(pos)

            for c in comentarios:
                desc = c.get("descricao")
                if desc:
                    f.write(f"- {desc.strip()}\n")

            f.write("\n")

        if ocorrencias:
            f.write("\n")
            for o in ocorrencias:
                desc = o.get("descricao")
                if desc:
                    f.write(f"- {desc.strip()}\n")

def processar_relatorio(rel, rdo, responsaveis):
    base_dia = caminho_saida_por_data(rdo["data"])
    pasta_atividades = base_dia / "Atividades"
    pasta_atividades.mkdir(parents=True, exist_ok=True)

    nome_resp = extrair_responsavel(
        rel.get("modeloDeRelatorio", {}).get("descricao", "")
    )

    id_eng = (
        responsaveis
        .get(rdo["obra_id"], {})
        .get("responsaveis", {})
        .get(nome_resp, {})
        .get("id_enginner", "SEM-ID")
    )

    salvar_ocorrencias_txt(pasta_atividades, rel)

    tarefas = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS_FOTOS) as executor:
        for atv in rel.get("atividades", []):
            if not atv.get("item"):
                continue

            pasta = pasta_atividades / f"{atv['item']} - {atv['descricao'].replace('/', '-')}"
            pasta.mkdir(parents=True, exist_ok=True)

            salvar_txt_atividade(pasta, atv)

            for i, foto in enumerate(atv.get("fotos", []), 1):
                ext = foto["arquivo"].split(".")[-1]
                nome = f"{id_eng}-{i:03}.{ext}"
                destino = pasta / nome

                tarefas.append(
                    executor.submit(baixar_arquivo, foto["url"], destino)
                )

        for t in as_completed(tarefas):
            t.result()

def listar_primeira_execucao():
    bruto = carregar_json(RDO_GERAL, [])
    downloaded = carregar_json(DOWNLOADED, {})
    responsaveis = carregar_json(RESPONSAVEIS, {})

    rdos_dict = bruto[0].get("conteudo", {}) if isinstance(bruto, list) else bruto

    data_base = datetime.strptime(DATA_INICIAL, "%Y-%m-%d").date()
    resultado = []

    for rdo in rdos_dict.values():
        try:
            data_rdo = datetime.strptime(rdo["data"], "%d/%m/%Y").date()
        except Exception:
            continue

        if (
            data_rdo < data_base
            or rdo.get("status") != "Aprovado"
            or rdo.get("rdo_id") in downloaded
        ):
            continue

        responsavel = extrair_responsavel(rdo.get("descricao", ""))
        if not responsavel:
            continue

        if not responsavel_valido(
            rdo["obra_id"],
            responsavel,
            data_rdo,
            responsaveis
        ):
            continue

        resultado.append({
            "rdo_id": rdo["rdo_id"],
            "obra_id": rdo["obra_id"],
            "data": rdo["data"]
        })

    return resultado, responsaveis

def processar_rdo(rdo, responsaveis):
    rel = baixar_relatorio_api(rdo["obra_id"], rdo["rdo_id"])
    processar_relatorio(rel, rdo, responsaveis)
    return rdo["rdo_id"], rdo["data"]

def executar_first():
    downloaded = carregar_json(DOWNLOADED, {})
    rdos, responsaveis = listar_primeira_execucao()

    baixados = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS_RDOS) as executor:
        futures = [
            executor.submit(processar_rdo, rdo, responsaveis)
            for rdo in rdos
        ]

        for future in as_completed(futures):
            rdo_id, data = future.result()
            downloaded[rdo_id] = {"data": data}
            # Convert to YYYY-MM-DD
            data_formatada = datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
            baixados.append(data_formatada)

    salvar_json(DOWNLOADED, downloaded)

    return {
        "status": "ok",
        "baixados": baixados,
        "modo": "primeira_execucao"
    }