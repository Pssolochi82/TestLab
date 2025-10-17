from app.app import app

def test_redirect_to_login_when_not_logged_in():
    client = app.test_client()
    r = client.get("/todo", follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]

def test_logout_clears_session_and_redirects():
    client = app.test_client()
    client.post("/login", data={"username": "admin", "password": "123456"})
    r = client.get("/logout", follow_redirects=False)
    assert r.status_code == 302
    assert "/" in r.headers["Location"]

def test_add_todo_post_flow():
    client = app.test_client()
    client.post("/login", data={"username": "admin", "password": "123456"}, follow_redirects=True)
    r = client.post("/todo", data={"item": "Ler documentação"}, follow_redirects=True)
    assert r.status_code == 200
    assert b"Ler documenta" in r.data  # evita issues de acentos

