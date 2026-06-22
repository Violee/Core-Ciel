from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.modules.selenium.browser.salvar import salvar_rdo
import time


# ==================================================
# SET INPUT (ANGULAR / DOCKER SAFE)
# ==================================================
def set_input_js(driver, element, value):
    driver.execute_script("""
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
    """, element, value)


# ==================================================
# OBTÉM DIA DA SEMANA
# ==================================================
def obter_dia_semana(driver, timeout=30):
    wait = WebDriverWait(driver, timeout)
    el = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//td//span[contains(text(), 'Feira') or contains(text(), 'Sábado') or contains(text(), 'Domingo')]"
            )
        )
    )
    dia = el.text.strip()
    print(f"📅 Dia da semana detectado: {dia}")
    return dia


# ==================================================
# DEFINE HORÁRIOS
# ==================================================
def definir_horarios(dia_semana):
    dia = dia_semana.lower()

    if "sábado" in dia or "sabado" in dia or "domingo" in dia:
        return "07:00", "16:00", "12:00", "13:00"

    return "07:00", "18:00", "12:00", "13:00"


# ==================================================
# PREENCHER HORÁRIOS (FIX REAL)
# ==================================================
def preencher_horarios(driver, timeout=30):
    wait = WebDriverWait(driver, timeout)

    dia = obter_dia_semana(driver)
    entrada, saida, i_ini, i_fim = definir_horarios(dia)

    print(
        f"⏰ Horários definidos → Entrada: {entrada}, "
        f"Saída: {saida}, Intervalo: {i_ini}-{i_fim}"
    )

    campo_entrada = wait.until(EC.presence_of_element_located((By.NAME, "expedienteInicio")))
    campo_saida = wait.until(EC.presence_of_element_located((By.NAME, "expedienteFim")))
    campo_i_ini = wait.until(EC.presence_of_element_located((By.NAME, "intervaloInicio")))
    campo_i_fim = wait.until(EC.presence_of_element_located((By.NAME, "intervaloFim")))

    set_input_js(driver, campo_entrada, entrada)
    set_input_js(driver, campo_saida, saida)
    set_input_js(driver, campo_i_ini, i_ini)
    set_input_js(driver, campo_i_fim, i_fim)

    time.sleep(0.3)

    print("✅ Horários aplicados no frontend")

    # 🔥 REGRA 1 — SALVAR RDO APÓS PREENCHER HORÁRIO
    salvar_rdo(driver)

