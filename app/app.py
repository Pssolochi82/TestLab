from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "change-me-dev-key"  # para sessão

USERS = {"admin": "123456"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if USERS.get(username) == password:
            session["user"] = username
            session.setdefault("todos", [])
            flash("Login efetuado com sucesso", "success")
            return redirect(url_for("todo"))
        flash("Credenciais inválidas", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sessão terminada", "info")
    return redirect(url_for("index"))


@app.route("/todo", methods=["GET", "POST"])
def todo():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        item = request.form.get("item", "").strip()
        if item:
            todos = session.get("todos", [])
            todos.append(item)
            # reatribuir para garantir que o Flask grava a mudança (ou usar session.modified = True)
            session["todos"] = todos  # ou: session.modified = True
            flash("Tarefa adicionada", "success")
        # PRG — estabiliza o DOM e evita repost do form
        return redirect(url_for("todo"))

    return render_template(
        "todo.html",
        user=session["user"],
        todos=session.get("todos", []),
    )



if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True)      # pragma: no cover

