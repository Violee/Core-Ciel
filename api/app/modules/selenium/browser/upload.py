import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.modules.selenium.browser.salvar import salvar_rdo


# ==================================================
# FUNÇÃO PRINCIPAL
# ==================================================
def upload_atividades(driver, pasta_atividades, timeout=60):
    wait = WebDriverWait(driver, timeout)

    print("📤 Iniciando upload de atividades")

    pastas = [
        p for p in os.listdir(pasta_atividades)
        if os.path.isdir(os.path.join(pasta_atividades, p))
    ]

    if not pastas:
        print("⚠️ Nenhuma atividade encontrada")
        return

    for idx, nome_tarefa in enumerate(pastas, start=1):
        caminho_tarefa = os.path.join(pasta_atividades, nome_tarefa)
        print(f"\n📂 Processando tarefa {idx}/{len(pastas)}: {nome_tarefa}")

        abrir_modal_lista_tarefas(driver, wait)
        garantir_tarefa_por_vez(driver, wait)
        selecionar_etapa(driver, wait)
        selecionar_tarefa(driver, wait, nome_tarefa)
        preencher_comentario(driver, wait, caminho_tarefa)

        total_fotos = upload_fotos_em_lotes(driver, wait, caminho_tarefa)
        salvar_atividade(driver, wait, total_fotos)

        # 🔥 REGRA 2 — SALVAR RDO APÓS CADA ATIVIDADE
        salvar_rdo(driver)

        print("✅ Tarefa concluída e RDO salvo")

    # 🔥 REGRA 3 — SALVAR RDO APÓS A ÚLTIMA ATIVIDADE (EXPLÍCITO)
    print("📌 Todas as atividades processadas")
    salvar_rdo(driver)
    print("💾 RDO salvo após última atividade")


# ==================================================
# MODAL
# ==================================================
def abrir_modal_lista_tarefas(driver, wait):
    botao_add = wait.until(
        EC.element_to_be_clickable((By.ID, "dropdownListaTaredas"))
    )
    driver.execute_script("arguments[0].click();", botao_add)

    botao_lista = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(.,'Atividade - lista de tarefas')]")
        )
    )
    driver.execute_script("arguments[0].click();", botao_lista)

    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//h4[contains(normalize-space(),'Adicionar atividade')]")
        )
    )


def garantir_tarefa_por_vez(driver, wait):
    radio = wait.until(EC.presence_of_element_located((By.ID, "adicionarUnico")))
    marcado = driver.execute_script("return arguments[0].checked;", radio)
    if not marcado:
        driver.execute_script("arguments[0].click();", radio)
        time.sleep(0.3)


# ==================================================
# ETAPA / TAREFA
# ==================================================
def selecionar_etapa(driver, wait):
    dropdown = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//label[normalize-space()='Etapa *']/following::button[1]")
        )
    )
    dropdown.click()

    opcao = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//label[contains(.,'Rodoanel Norte')]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opcao)
    opcao.click()


def selecionar_tarefa(driver, wait, nome_pasta):
    codigo = nome_pasta.split(" - ")[0].strip()

    dropdown = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//label[contains(text(),'Tarefa')]/following::button[1]")
        )
    )
    dropdown.click()

    tarefa = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//label[contains(normalize-space(),'{codigo}')]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tarefa)
    tarefa.click()


# ==================================================
# COMENTÁRIO
# ==================================================
def preencher_comentario(driver, wait, pasta_tarefa):
    caminho = os.path.join(pasta_tarefa, "atividade.txt")
    if not os.path.exists(caminho):
        return

    with open(caminho, "r", encoding="utf-8") as f:
        texto = f.read().strip()

    if not texto:
        return

    campo = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//textarea[@name='observacao']"))
    )
    campo.clear()
    campo.send_keys(texto)


# ==================================================
# UPLOAD – VERDADE ABSOLUTA
# ==================================================
def get_photo_count(driver):
    try:
        h6 = driver.find_element(By.XPATH, "//h6[contains(text(),'Fotos (')]")
        text = h6.text
        import re
        match = re.search(r'Fotos \((\d+)\)', text)
        return int(match.group(1)) if match else 0
    except:
        return 0


def aguardar_upload_finalizado(driver, wait, total=None):
    print("⏳ Aguardando upload REAL finalizar...")
    wait.until(
        lambda d: d.execute_script("""
            return document.querySelectorAll('.box.loader').length === 0 &&
                   document.querySelectorAll('.progress-bar.upload').length === 0;
        """) and (total is None or get_photo_count(d) == total)
    )
    print("✅ Upload finalizado no backend")


def upload_fotos_em_lotes(driver, wait, pasta_tarefa):
    imagens = sorted([
        os.path.abspath(os.path.join(pasta_tarefa, f))
        for f in os.listdir(pasta_tarefa)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ])

    if not imagens:
        print("ℹ️ Sem fotos")
        return 0

    total = len(imagens)
    LIMITE = 50
    enviadas = 0

    print(f"📸 Total de fotos: {total}")

    while enviadas < total:
        lote = imagens[enviadas:enviadas + LIMITE]

        input_file = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@type='file' and @accept='image/*']")
            )
        )

        driver.execute_script("arguments[0].value = '';", input_file)
        input_file.send_keys("\n".join(lote))
        enviadas += len(lote)

        print(f"📤 Lote enviado: {len(lote)} | Progresso: {enviadas}/{total}")

        time.sleep(0.5)
        aguardar_upload_finalizado(driver, wait)

    return total


# ==================================================
# SALVAR ATIVIDADE (MODAL)
# ==================================================
def salvar_atividade(driver, wait, total_fotos=None):
    aguardar_upload_finalizado(driver, wait, total_fotos)

    print("💾 Tentando salvar atividade...")

    for _ in range(10):
        botoes = driver.find_elements(
            By.XPATH,
            "//div[@id='AtividadesListaTarefasForm']//button[@type='submit' and @title='Salvar']"
        )

        if not botoes:
            time.sleep(1)
            continue

        botao = botoes[0]
        driver.execute_script("arguments[0].scrollIntoView(true);", botao)

        if driver.execute_script("return arguments[0].hasAttribute('disabled');", botao):
            time.sleep(1)
            continue

        driver.execute_script("arguments[0].click();", botao)

        wait.until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "modal-dialog"))
        )

        time.sleep(2)
        print("✅ Atividade salva")
        return

    raise Exception("❌ Falhou ao salvar atividade")
