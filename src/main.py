from flask import Flask, render_template, jsonify, request, redirect, url_for
from dotenv import load_dotenv

from src.models.sql import (
    init_db,
    list_services,
    get_service,
    create_service,
    update_service,
    delete_service,
)


def create_app():
    load_dotenv()

    app = Flask(__name__, template_folder="templates", static_folder="static")
    init_db()

    @app.route("/")
    def home():
        return render_template("dashboard.html")

    @app.route("/appointments")
    def appointments():
        return render_template("appointments.html")

    @app.route("/services", methods=["GET"])
    def services():
        services_data = list_services()
        return render_template("services.html", services=services_data)

    @app.route("/services/new", methods=["GET", "POST"])
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
