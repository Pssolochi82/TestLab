from app.app import app


def test_index_route_ok():
    client = app.test_client()
    r = client.get("/")
    assert r.status_code == 200
    assert b"TestLab" in r.data


def test_login_fail_then_success():
    client = app.test_client()
    # falha
    r = client.post(
        "/login", data={"username": "x", "password": "y"}, follow_redirects=True
    )
    assert b"Credenciais" in r.data  # evita problemas de acentos no Windows

   
def test_login_invalido_mostra_mensagem():
    client = app.test_client()
    r = client.post("/login", data={"username": "admin", "password": "errada"}, follow_redirects=True)
    assert r.status_code == 200
    # evita problemas de encoding/acentos no Windows: procura um fragmento estável
    assert b"Credenciais" in r.data

    # sucesso
    r = client.post(
        "/login",
        data={"username": "admin", "password": "123456"},
        follow_redirects=True,
    )
    assert b"Login efetuado" in r.data
