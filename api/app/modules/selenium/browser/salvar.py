from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# ==================================================
# SALVAR RDO (BOTÃO GLOBAL DO HEADER)
# ==================================================
def salvar_rdo(driver, timeout=40):
    wait = WebDriverWait(driver, timeout)

    print("💾 Clicando no botão SALVAR do RDO...")

    # --------------------------------------------------
    # 1) Garantir que NÃO existe modal aberto
    # --------------------------------------------------
    try:
        wait.until(
            EC.invisibility_of_element_located(
                (By.CLASS_NAME, "modal-dialog")
            )
        )
    except:
        pass

    # --------------------------------------------------
    # 2) Garantir que NÃO existe backdrop ativo
    # --------------------------------------------------
    try:
        wait.until(
            lambda d: len(d.find_elements(By.CLASS_NAME, "modal-backdrop")) == 0
        )
    except:
        pass

    # --------------------------------------------------
    # 3) Localizar botão SALVAR do HEADER
    # --------------------------------------------------
    botao_salvar = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//div[@id='header-menu']//button[@title='Salvar' and contains(@class,'btn-success')]"
            )
        )
    )

    # --------------------------------------------------
    # 4) Garantir que o botão está habilitado
    # --------------------------------------------------
    wait.until(lambda d: botao_salvar.is_enabled())

    # --------------------------------------------------
    # 5) Scroll até o botão (navbar aparece)
    # --------------------------------------------------
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        botao_salvar
    )
    time.sleep(0.3)

    # --------------------------------------------------
    # 6) Clique via JavaScript (mais confiável)
    # --------------------------------------------------
    driver.execute_script("arguments[0].click();", botao_salvar)

    # --------------------------------------------------
    # 7) Aguardar processamento do backend
    # --------------------------------------------------
    time.sleep(2)

    print("✅ RDO salvo com sucesso")
