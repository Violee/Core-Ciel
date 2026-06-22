from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..utils.digitar import digitar_como_humano
import time
import os

RELATORIOS_URL = (
    "https://web.diariodeobra.app/"
)

# ==================================================
# ABRIR LISTA DE RELATÓRIOS
# ==================================================
def abrir_relatorios(driver, timeout=30):
    wait = WebDriverWait(driver, timeout)

    print(f"🌐 Navegando para: {RELATORIOS_URL}")
    driver.get(RELATORIOS_URL)

    print("⏳ Aguardando carregamento da página de relatórios...")
    try:
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//th[contains(text(),'Data')]")
            )
        )
        print("✅ Página de relatórios carregada")
    except Exception as e:
        print(f"❌ Elemento esperado não encontrado: {str(e)}")
        print(f"📄 Título da página: {driver.title}")
        print(f"📄 URL atual: {driver.current_url}")
        print("📄 Procurando por elementos de tabela...")
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"📄 Tabelas encontradas: {len(tables)}")
        if tables:
            headers = tables[0].find_elements(By.TAG_NAME, "th")
            print(f"📄 Cabeçalhos da primeira tabela: {[h.text for h in headers]}")
        raise


# ==================================================
# ABRIR OU CRIAR RELATÓRIO
# ==================================================
def abrir_ou_criar_relatorio(driver, data_alvo, timeout=30):
    wait = WebDriverWait(driver, timeout)

    # ==================================================
    # 1. VERIFICAR SE O RDO JÁ EXISTE
    # ==================================================
    linhas_data = driver.find_elements(
        By.XPATH,
        "//tr[contains(@class,'top-border')]"
        "/a[contains(@class,'td')][1]"
    )
    print(f"✅ Encontradas {len(linhas_data)} linhas de data")

    for el in linhas_data:
        if el.text.strip() == data_alvo:
            print(f"📄 RDO {data_alvo} já existe → abrindo")
            driver.execute_script("arguments[0].click();", el)
            time.sleep(0.6)
            return "aberto"

    print(f"➕ RDO {data_alvo} não existe → criando")

    # ==================================================
    # 2. ADICIONAR → ADICIONAR RELATÓRIO
    # ==================================================
    try:
        botao_adicionar = wait.until(
            EC.element_to_be_clickable((By.ID, "btn-adicionar"))
        )
        print("✅ Botão adicionar encontrado")
        driver.execute_script("arguments[0].click();", botao_adicionar)
        time.sleep(0.3)
    except Exception as e:
        print(f"❌ Erro ao clicar no botão adicionar: {str(e)}")
        raise

    try:
        botao_add_relatorio = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Adicionar Relatório')]")
            )
        )
        print("✅ Botão adicionar relatório encontrado")
        driver.execute_script("arguments[0].click();", botao_add_relatorio)
        time.sleep(0.4)
    except Exception as e:
        print(f"❌ Erro ao clicar no botão adicionar relatório: {str(e)}")
        raise

    # ==================================================
    # 3. MODAL → CONFIGURAÇÕES INICIAIS
    # ==================================================
    try:
        wait.until(
            EC.visibility_of_element_located(
                (By.ID, "modalAdicionarRelatorio")
            )
        )
        print("✅ Modal adicionar relatório aberto")
    except Exception as e:
        print(f"❌ Erro ao aguardar modal: {str(e)}")
        raise

    # 🔴 DESMARCAR "Copiar informações do último relatório"
    checkbox_copiar = wait.until(
        EC.presence_of_element_located(
            (By.ID, "copiarInformacoes")
        )
    )

    if checkbox_copiar.is_selected():
        driver.execute_script("arguments[0].click();", checkbox_copiar)
        time.sleep(0.3)

    # ==================================================
    # 4. INSERIR DATA (DIGITAÇÃO HUMANA)
    # ==================================================
    campo_data = wait.until(
        EC.element_to_be_clickable(
            (By.ID, "relatorioDataInicio")
        )
    )

    driver.execute_script("arguments[0].focus();", campo_data)

    digitar_como_humano(
        campo_data,
        data_alvo,
        delay_min=0.04,
        delay_max=0.08
    )

    time.sleep(0.3)

    # 🔑 FECHAR CALENDÁRIO
    driver.execute_script("document.body.click();")
    time.sleep(0.3)

    # ==================================================
    # 5. SALVAR
    # ==================================================
    botao_salvar = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//div[@id='modalAdicionarRelatorio']//button[@type='submit']"
            )
        )
    )

    driver.execute_script("arguments[0].click();", botao_salvar)
    time.sleep(0.6)

    print("💾 Relatório criado e aberto")
    return "criado"


# ==================================================
# ENTRAR EM MODO EDIÇÃO
# ==================================================
def entrar_modo_edicao(driver, timeout=30):
    wait = WebDriverWait(driver, timeout)

    # 1️⃣ Esperar sair da lista e entrar no relatório (URL com ID)
    wait.until(lambda d: "/relatorios/" in d.current_url and not d.current_url.endswith("/relatorios"))

    url_atual = driver.current_url
    print(f"📍 URL do relatório detectada: {url_atual}")

    # 2️⃣ Se já estiver em edição, beleza
    if url_atual.endswith("/editar"):
        print("ℹ️ Já está em modo edição")
        return

    # 3️⃣ Preferir botão Editar (mais seguro que URL)
    try:
        botao_editar = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Editar')]")
            )
        )
        driver.execute_script("arguments[0].click();", botao_editar)
        print("✏️ Entrou em modo edição via botão")
    except:
        # 4️⃣ Fallback seguro via URL (AGORA com ID)
        url_editar = url_atual.rstrip("/") + "/editar"
        print(f"🔁 Indo para modo edição via URL segura: {url_editar}")
        driver.get(url_editar)

    # 5️⃣ Confirma que está em edição
    wait.until(
        EC.presence_of_element_located(
            (By.NAME, "expedienteInicio")
        )
    )

    print("✅ RDO em modo edição confirmado")



# ==================================================
# FLUXO COMPLETO DO RELATÓRIO (ATÉ EDIÇÃO)
# ==================================================

def fluxo_relatorio(driver, data_alvo):
    abrir_relatorios(driver)
    status = abrir_ou_criar_relatorio(driver, data_alvo)
    entrar_modo_edicao(driver)
    return status

# ==================================================
# EXTRAIR ATIVIDADES DA PÁGINA
# ==================================================
def extrair_atividades(driver, pasta_atividades, timeout=30):
    wait = WebDriverWait(driver, timeout)

    # Ajuste os XPath conforme a estrutura da página
    atividades_elements = driver.find_elements(By.XPATH, "//div[contains(@class,'atividade') or contains(@class,'activity')]")

    if not atividades_elements:
        print("Nenhuma atividade encontrada na página")
        return

    for i, el in enumerate(atividades_elements, 1):
        # Extract data - ajuste os XPath
        hora_element = el.find_elements(By.XPATH, ".//span[contains(@class,'hora') or contains(@class,'time')]")
        hora = hora_element[0].text.strip() if hora_element else ""

        texto_element = el.find_elements(By.XPATH, ".//p[contains(@class,'observacao') or contains(@class,'description')]")
        texto = texto_element[0].text.strip() if texto_element else ""

        # Fotos - ajuste para encontrar links ou src
        fotos_elements = el.find_elements(By.XPATH, ".//img")
        fotos = [img.get_attribute("src") for img in fotos_elements if img.get_attribute("src")]

        # Create folder
        pasta = os.path.join(pasta_atividades, f"Atividade {i}")
        os.makedirs(pasta, exist_ok=True)

        # Save atividade.txt
        with open(os.path.join(pasta, "atividade.txt"), "w", encoding="utf-8") as f:
            if hora:
                f.write(f"Horário: {hora}\n\n")
            f.write("Atividade:\n")
            f.write(texto or "Texto não encontrado")
            f.write("\n\n")
            if fotos:
                f.write("Fotos:\n")
                for j, foto in enumerate(fotos, 1):
                    f.write(f"- foto_{j}\n")
                # Download fotos - placeholder
                # for j, url in enumerate(fotos, 1):
                #     baixar_arquivo(url, os.path.join(pasta, f"foto_{j}.jpg"))

        print(f"Atividade {i} extraída")

    print("Extração de atividades concluída")