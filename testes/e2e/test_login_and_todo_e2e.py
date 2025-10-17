# testes/e2e/test_login_and_todo_e2e.py
import os
import time
import threading
import contextlib

from selenium import webdriver
from selenium.webdriver.common.by import By

# Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

# Edge (fallback)
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.app import app


# ---------- util: artifacts em caso de falha ----------
def save_artifacts(driver, name="page"):
    os.makedirs("artifacts", exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    base = os.path.join("artifacts", f"{name}-{ts}")
    try:
        driver.save_screenshot(base + ".png")
    except Exception:
        pass
    try:
        with open(base + ".html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    except Exception:
        pass
    print(f"[ARTIFACTS] Guardados: {base}.png  {base}.html")


# ---------- servidor flask em thread ----------
@contextlib.contextmanager
def run_server():
    thread = threading.Thread(
        target=app.run,
        kwargs={"port": 5001, "use_reloader": False},
        daemon=True,
    )
    thread.start()
    time.sleep(1.0)
    try:
        yield
    finally:
        # o dev server termina com o processo de testes
        pass


# ---------- criar WebDriver (Chrome → Edge fallback) ----------
def make_driver():
    # Tenta Chrome headless…
    try:
        ch = ChromeOptions()
        ch.add_argument("--headless=new")
        ch.add_argument("--no-sandbox")
        ch.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=ch,
        )
    except Exception:
        # …se falhar (sem net/driver), tenta Edge headless
        ed = EdgeOptions()
        ed.add_argument("--headless=new")
        ed.add_argument("--no-sandbox")
        ed.add_argument("--disable-dev-shm-usage")
        return webdriver.Edge(
            service=EdgeService(EdgeChromiumDriverManager().install()),
            options=ed,
        )


def test_login_and_add_todo_invalid_then_success():
    driver = make_driver()
    wait = WebDriverWait(driver, 10)

    try:
        with run_server():
            driver.get("http://127.0.0.1:5001/")

            # Abrir página de login
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Login"))).click()

            # ---------- 1) Tentativa de login INVÁLIDA ----------
            wait.until(EC.presence_of_element_located((By.NAME, "username"))).clear()
            driver.find_element(By.NAME, "username").send_keys("admin")
            driver.find_element(By.NAME, "password").clear()
            driver.find_element(By.NAME, "password").send_keys("errada")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Continua no login, deve ver flash "Credenciais ..."
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form[method='post']")))
            assert "Credenciais" in driver.page_source

            # ---------- 2) Tentativa de login VÁLIDA ----------
            driver.find_element(By.NAME, "username").clear()
            driver.find_element(By.NAME, "username").send_keys("admin")
            driver.find_element(By.NAME, "password").clear()
            driver.find_element(By.NAME, "password").send_keys("123456")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Esperar pelo redirect /todo e pelo input do formulário
            wait.until(EC.url_contains("/todo"))
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='item']")))

            # ---------- 3) Adicionar uma tarefa ----------
            driver.find_element(By.NAME, "item").send_keys("Estudar Pytest")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # PRG: novo GET /todo → esperar o <li> com o texto
            wait.until(lambda d: any("Estudar Pytest" in el.text for el in d.find_elements(By.TAG_NAME, "li")))
            items = [el.text for el in driver.find_elements(By.TAG_NAME, "li")]
            assert any("Estudar Pytest" in t for t in items)

    except Exception:
        # guarda screenshot + HTML para debugging
        save_artifacts(driver, "test_login_and_todo_invalid_then_success")
        raise
    finally:
        try:
            driver.quit()
        except Exception:
            pass
