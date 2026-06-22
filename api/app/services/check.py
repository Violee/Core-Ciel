import json
import re
from pathlib import Path
from datetime import datetime

RESPONSAVEIS_FILE = Path("/app/app/core/managers.json")
RDO_GERAL_FILE = Path("/data/logs/rdo_geral/rdo_geral.json")

HISTORICO_FILE = Path("/data/logs/telegram/monitoramento_geral.txt")
HISTORICO_FILE.parent.mkdir(parents=True, exist_ok=True)

def extrair_rp(descricao: str):
    if not descricao:
        return None
    m = re.search(r"RP:\s*(.+)$", descricao)
    return m.group(1).strip() if m else None

def parse_data(data_str: str):
    return datetime.strptime(data_str, "%d/%m/%Y").date()

def carregar_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def ler_historico(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

def salvar_historico(path: Path, texto: str):
    path.write_text(texto, encoding="utf-8")

def check():
    responsaveis_data = carregar_json(RESPONSAVEIS_FILE)
    rdo_data = carregar_json(RDO_GERAL_FILE)

    if isinstance(rdo_data, list):
        rdo_data = rdo_data[0]

    rdos = rdo_data.get("conteudo", {})
    hoje = datetime.now().date()

    atrasados = []
    em_dia = []

    for obra_info in responsaveis_data.values():
        responsaveis = obra_info.get("responsaveis", {})

        for nome_rp, dados_rp in responsaveis.items():
            if dados_rp.get("ignorar") is True:
                continue

            aprovados = [
                rdo for rdo in rdos.values()
                if rdo.get("status") == "Aprovado"
                and extrair_rp(rdo.get("descricao")) == nome_rp
            ]

            if not aprovados:
                atrasados.append(f"{nome_rp} — — (sem aprovação)")
                continue

            ultimo = max(aprovados, key=lambda r: parse_data(r["data"]))
            dias = (hoje - parse_data(ultimo["data"])).days

            linha = f"{nome_rp} — {ultimo['data']} ({dias} dias)"

            if dias > 5:
                atrasados.append(linha)
            else:
                em_dia.append(linha)

    linhas = ["📊 Monitoramento — Último RDO Aprovado\n"]

    if atrasados:
        linhas.append("🔴 Atrasados\n")
        linhas.extend(atrasados)
        linhas.append("")

    if em_dia:
        linhas.append("✅ Em dia\n")
        linhas.extend(em_dia)

    mensagem = "\n".join(linhas)

    historico = ler_historico(HISTORICO_FILE)
    mudou = mensagem.strip() != historico.strip()

    if mudou:
        salvar_historico(HISTORICO_FILE, mensagem)

    return {
        "changed": mudou,
        "text": mensagem
    }
