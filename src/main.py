import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from dotenv import load_dotenv

from src.models.sql import (
    init_db,
    list_services,
    get_service,
    create_service,
    update_service,
    delete_service,
)
from src.auth.local_auth import bootstrap_admin, authenticate
from src.auth.decorators import login_required, admin_required


def create_app():
    load_dotenv()

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

    init_db()
    bootstrap_admin()

    @app.route("/")
    def home():
        return render_template("dashboard.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password") or ""
            user = authenticate(email, password)
            if user:
                session["user_id"] = user["id"]
                session["email"] = user["email"]
                session["role"] = user["role"]
                next_url = request.args.get("next") or url_for("home")
                return redirect(next_url)
            error = "Invalid email or password"
        return render_template("login.html", error=error)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("home"))

    @app.route("/appointments")
    @login_required
    def appointments():
        return render_template("appointments.html")

    @app.route("/services", methods=["GET"])
    @login_required
    def services():
        services_data = list_services()
        return render_template("services.html", services=services_data)

    @app.route("/services/new", methods=["GET", "POST"])
    @admin_required
    def new_service():
        if request.method == "POST":
            name = (request.form.get("name") or "").strip()
            duration_minutes = int(request.form.get("duration_minutes") or 0)
            price_gbp = float(request.form.get("price_gbp") or 0)

            if not name or duration_minutes <= 0 or price_gbp < 0:
                return render_template(
                    "new_service.html",
                    error="Enter a name, a positive duration, and a non negative price.",
                )

            create_service(name, duration_minutes, price_gbp)
            return redirect(url_for("services"))

        return render_template("new_service.html", error=None)

    @app.route("/services/<int:service_id>/edit", methods=["GET", "POST"])
    @admin_required
    def edit_service(service_id: int):
        service = get_service(service_id)
        if service is None:
            return "Service not found", 404

        if request.method == "POST":
            name = (request.form.get("name") or "").strip()
            duration_minutes = int(request.form.get("duration_minutes") or 0)
            price_gbp = float(request.form.get("price_gbp") or 0)

            if not name or duration_minutes <= 0 or price_gbp < 0:
                service["name"] = name
                service["duration_minutes"] = duration_minutes
                service["price_gbp"] = price_gbp
                return render_template(
                    "edit_service.html",
                    service=service,
                    error="Enter a name, a positive duration, and a non negative price.",
                )

            update_service(service_id, name, duration_minutes, price_gbp)
            return redirect(url_for("services"))

        return render_template("edit_service.html", service=service, error=None)

    @app.route("/services/<int:service_id>/delete", methods=["POST"])
    @admin_required
    def remove_service(service_id: int):
        delete_service(service_id)
        return redirect(url_for("services"))

    @app.route("/api/health")
    def api_health():
        return jsonify(status="ok")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
