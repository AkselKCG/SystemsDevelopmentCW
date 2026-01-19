from flask import Flask, render_template

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/appointments")
def appointments():
    return render_template("appointments.html")

@app.route("/services")
def services():
    return render_template("services.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
