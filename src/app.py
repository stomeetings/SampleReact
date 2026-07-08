import sqlite3

from flask import Flask, redirect, render_template, request, url_for

from database.db import create_user, get_db, init_db, seed_db

app = Flask(__name__)

with app.app_context():
    init_db()
    seed_db()


@app.route("/")
def index():
    return {"status": "ok"}


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    errors = {}
    if not name:
        errors["name"] = "Name is required"
    if not email:
        errors["email"] = "Email is required"
    if not password:
        errors["password"] = "Password is required"
    elif len(password) < 8:
        errors["password"] = "Password must be at least 8 characters"

    if errors:
        return render_template(
            "register.html", errors=errors, form={"name": name, "email": email}
        )

    try:
        create_user(name, email, password)
    except sqlite3.IntegrityError:
        errors["email"] = "Email already registered"
        return render_template(
            "register.html", errors=errors, form={"name": name, "email": email}
        )

    return redirect(url_for("register_success"))


@app.route("/register/success")
def register_success():
    return render_template("register_success.html")


if __name__ == "__main__":
    app.run(debug=True)
