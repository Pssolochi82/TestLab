import threading
import time
import contextlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from app.app import app


@contextlib.contextmanager
def run_server():
thread = threading.Thread(target=app.run, kwargs={"port": 5001}, daemon=True)
thread.start()
time.sleep(1.0)
try:
yield
finally:
# Flask em modo dev termina com o processo de testes
pass


def test_login_and_add_todo():
with run_server():
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get("http://127.0.0.1:5001/")


# Ir para login
driver.find_element(By.LINK_TEXT, "Login").click()
driver.find_element(By.NAME, "username").send_keys("admin")
driver.find_element(By.NAME, "password").send_keys("123456")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


# Adicionar tarefa
driver.find_element(By.NAME, "item").send_keys("Estudar Pytest")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


# Verificar lista
items = driver.find_elements(By.TAG_NAME, "li")
assert any("Estudar Pytest" in i.text for i in items)
driver.quit()