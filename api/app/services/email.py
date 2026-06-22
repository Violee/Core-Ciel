import json
from datetime import datetime, timedelta
from pathlib import Path

ATRASO_MAX_DIAS = 5
INTERVALO_EMAIL_HORAS = 6

RESPONSAVEIS_FILE = Path("/app/app/core/managers.json")
NOTIFICACOES_CC_FILE = Path("/app/app/core/copy_email.json")  
RDO_GERAL_FILE = Path("/data/logs/rdo_geral/rdo_geral.json")
EMAIL_STATE_FILE = Path("/data/logs/email/email_state.json")

TEMPLATE_EMAIL_FILE = Path("/data/logs/email/email_rdo_atraso.html")

def carregar_json(caminho: Path, default):
    if not caminho.exists():
        return default

    with open(caminho, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list) and data and "conteudo" in data[0]:
        return data[0]["conteudo"]

    return data


def salvar_json(caminho: Path, conteudo):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(conteudo, f, ensure_ascii=False, indent=2)


def parse_data(data_str):
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except Exception:
        return None


def pode_enviar(email, email_state):
    ultimo = email_state.get(email, {}).get("ultimo_envio")
    if not ultimo:
        return True

    ultimo_dt = datetime.fromisoformat(ultimo)
    return datetime.now() - ultimo_dt >= timedelta(hours=INTERVALO_EMAIL_HORAS)


def montar_cc(nome_resp, obra_id, email_obra, notificacoes_cc):
    cc = set()

    if email_obra:
        cc.add(email_obra)

    cc.update(
        notificacoes_cc.get("por_responsavel", {})
        .get(nome_resp, {})
        .get("cc", [])
    )

    cc.update(
        notificacoes_cc.get("por_obra", {})
        .get(obra_id, {})
        .get("cc", [])
    )

    cc.update(notificacoes_cc.get("global", {}).get("cc", []))

    return list(cc)

def carregar_template():
    if not TEMPLATE_EMAIL_FILE.exists():
        return None
    return TEMPLATE_EMAIL_FILE.read_text(encoding="utf-8")

def montar_html(template, dados):
    html = template
    for chave, valor in dados.items():
        html = html.replace(f"{{{{{chave}}}}}", str(valor))
    return html

def executar_email_brain():
    responsaveis_cfg = carregar_json(RESPONSAVEIS_FILE, {})
    notificacoes_cc = carregar_json(NOTIFICACOES_CC_FILE, {})
    rdos = carregar_json(RDO_GERAL_FILE, {})
    email_state = carregar_json(EMAIL_STATE_FILE, {})

    template_html = carregar_template()
    hoje = datetime.now()

    emails = []

    for obra_id, cfg_obra in responsaveis_cfg.items():
        nome_obra = cfg_obra.get("obra")
        email_obra = cfg_obra.get("email_obra")
        responsaveis = cfg_obra.get("responsaveis", {})

        for nome_resp, cfg_resp in responsaveis.items():

            if cfg_resp.get("ignorar") is True:
                continue

            email_resp = cfg_resp.get("email")
            if not email_resp:
                continue

            rdos_resp = [
                rdo for rdo in rdos.values()
                if rdo.get("descricao")
                and nome_resp in rdo.get("descricao", "")
                and rdo.get("status") == "Aprovado"
            ]

            if rdos_resp:
                rdos_resp.sort(
                    key=lambda r: parse_data(r.get("data")) or datetime.min,
                    reverse=True
                )
                ultimo_aprovado = parse_data(rdos_resp[0].get("data"))
            else:
                ultimo_aprovado = None

            dias_atraso = (
                (hoje - ultimo_aprovado).days
                if ultimo_aprovado
                else ATRASO_MAX_DIAS + 1
            )

            if dias_atraso <= ATRASO_MAX_DIAS:
                continue

            if not pode_enviar(email_resp, email_state):
                continue

            cc_final = montar_cc(
                nome_resp,
                obra_id,
                email_obra,
                notificacoes_cc
            )

            dados_template = {
                "NOME_RESPONSAVEL": nome_resp,
                "ULTIMO_RDO": (
                    ultimo_aprovado.strftime("%d/%m/%Y")
                    if ultimo_aprovado else "Nenhum"
                ),
                "DIAS_ATRASO": dias_atraso,
                "OBRA": nome_obra
            }

            body = (
                montar_html(template_html, dados_template)
                if template_html
                else f"Atraso de RDO — {nome_obra}"
            )

            emails.append({
                "to": email_resp,
                "cc": cc_final,
                "subject": f"RDO em atraso – {nome_obra}",
                "body": body
            })

            email_state[email_resp] = {
                "ultimo_envio": datetime.now().isoformat()
            }

    salvar_json(EMAIL_STATE_FILE, email_state)

    return {
        "enviar_email": bool(emails),
        "total_emails": len(emails),
        "emails": emails
    }
