from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ..utils.digitar import digitar_como_humano

LOGIN_URL = "https://web.diariodeobra.app/#/login?idioma=pt"
SUCESSO_ROTA = "#/app/obras"   # 🔒 rota obrigatória após login

def fazer_login(driver, email, senha, timeout=30):
    wait = WebDriverWait(driver, timeout)

    # Abre página de login
    driver.get(LOGIN_URL)

    # Aguarda campos
    campo_email = wait.until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    campo_senha = wait.until(
        EC.presence_of_element_located((By.NAME, "password"))
    )

    # Digitação humana
    digitar_como_humano(campo_email, email)
    digitar_como_humano(campo_senha, senha)

    # Botão entrar
    botao = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )

    # Clique via JS (mais confiável em SPA)
    driver.execute_script("arguments[0].click();", botao)

    # ==========================
    # VALIDAÇÃO REAL DO LOGIN
    # ==========================
    try:
        wait.until(lambda d: SUCESSO_ROTA in d.current_url)
        return True
    except TimeoutException:
        return False
