from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import os
from pathlib import Path


# ==================================================
# CONFIG
# ==================================================
EMAIL = "email"
SENHA = "senha"


# ==================================================
# DRIVER
# ==================================================
def criar_driver():
    options = Options()
    options.add_argument("--headless=new")  # Para rodar sem interface
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


# ==================================================
# EXECUTAR SELENIUM PARA UMA DATA
# ==================================================
def executar_selenium(data_str):
    import sys
    sys.path.insert(0, '/app')
    
    from app.modules.selenium.browser.login import fazer_login
    from app.modules.selenium.browser.relatorio_fluxo import fluxo_relatorio, extrair_atividades
    from app.modules.selenium.browser.upload import upload_atividades
    from app.modules.selenium.browser.hora import preencher_horarios
    
    # data_str é YYYY-MM-DD, converter para dd/mm/YYYY
    dt = datetime.strptime(data_str, "%Y-%m-%d")
    data_alvo = dt.strftime("%d/%m/%Y")
    
    pasta_atividades = f"/data/media/RDO/{data_str}/Atividades"
    
    driver = criar_driver()

    try:
        print(f"🚀 Iniciando automação para {data_alvo}")

        # LOGIN
        if not fazer_login(driver, EMAIL, SENHA):
            print("❌ Login falhou")
            return {"status": "error", "message": "Login falhou"}

        print("✅ Login realizado com sucesso")

        # FLUXO RELATÓRIO
        try:
            status_rdo = fluxo_relatorio(driver, data_alvo)
            print(f"📄 RDO {status_rdo}")
        except Exception as e:
            print(f"❌ Erro no fluxo do relatório: {str(e)}")
            return {"status": "error", "message": f"Erro no fluxo do relatório: {str(e)}"}

        if status_rdo == "aberto":
            try:
                extrair_atividades(driver, pasta_atividades)
                print("📥 Atividades extraídas da RDO existente")
                return {"status": "success", "data": data_str, "action": "extracted"}
            except Exception as e:
                print(f"❌ Erro ao extrair atividades: {str(e)}")
                return {"status": "error", "message": f"Erro ao extrair atividades: {str(e)}"}

        # PREENCHER HORÁRIO
        try:
            preencher_horarios(driver)
            print("⏰ Horário preenchido")
        except Exception as e:
            print(f"⏰ Horário não preenchido: {e}")

        # UPLOAD DE ATIVIDADES
        try:
            upload_atividades(driver, pasta_atividades)
            print("📤 Atividades enviadas com sucesso")
        except Exception as e:
            print(f"❌ Erro ao enviar atividades: {str(e)}")
            return {"status": "error", "message": f"Erro ao enviar atividades: {str(e)}"}

        return {"status": "success", "data": data_str}

    except Exception as e:
        print(f"❌ Erro na automação: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        driver.quit()


# ==================================================
# MAIN (PARA TESTE LOCAL)
# ==================================================
def main():
    # Exemplo
    resultado = executar_selenium("2025-11-29")
    print(resultado)


if __name__ == "__main__":
    main()
