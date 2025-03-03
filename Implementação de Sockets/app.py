from flask import Flask, render_template, jsonify, request
import threading
import time

app = Flask(__name__)

# Simulação de usuários com GPS (dados fictícios)
users = [
    {"name": "João", "lat": -23.5505, "lon": -46.6333},
    {"name": "Maria", "lat": -22.9068, "lon": -43.1729},
    {"name": "Carlos", "lat": -15.8267, "lon": -47.9218},
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/locations")
def get_locations():
    return jsonify(users)

@app.route("/update_location", methods=["POST"])
def update_location():
    data = request.json
    users[data["name"]] = {"name": data["name"], "lat": data["lat"], "lon": data["lon"]}
    return jsonify({"message": "Localização atualizada com sucesso!"}), 200

@app.route("/shutdown")
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    return "Servidor encerrado"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
