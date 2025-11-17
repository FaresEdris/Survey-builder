from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.services.user_service import UserService

auth_bp = Blueprint("auth", __name__)

user_service = UserService()

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = user_service.find_by_username(username)

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index")) 

        flash("Invalid username or password")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user_service.add_user(username, password)

        flash("Registration successful. Please login.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for("auth.login"))
