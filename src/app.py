import os
import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

with app.app_context():
    init_db()
    seed_db()


@app.route("/")
def index():
    return {"status": "ok"}


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("login_success"))

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


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("login_success"))

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    errors = {}
    if not email:
        errors["email"] = "Email is required"
    if not password:
        errors["password"] = "Password is required"

    user = None
    if not errors:
        user = get_user_by_email(email)
        if user is None or not check_password_hash(user["password_hash"], password):
            errors["form"] = "Invalid email or password"

    if errors:
        return render_template("login.html", errors=errors, form={"email": email})

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("login_success"))


@app.route("/login/success")
def login_success():
    return render_template("login_success.html", name=session.get("user_name"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
