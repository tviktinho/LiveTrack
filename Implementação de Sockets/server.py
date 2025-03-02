import socket
import threading
import json
import random
from flask import Flask, render_template, jsonify

# Configuração do servidor
HOST = '0.0.0.0'
PORT = 5000
clients_locations = {}  # Armazena as localizações dos clientes
clients_colors = {}  # Armazena cores associadas a cada cliente
lock = threading.Lock()

# Cores para os marcadores do mapa
COLOR_LIST = [
    "red", "blue", "green", "purple", "orange", "darkred", "lightred",
    "beige", "darkblue", "darkgreen", "cadetblue", "darkpurple"
]

# Iniciar Flask
app = Flask(__name__)

@app.route('/')
def mapa():
    """Renderiza a página do mapa."""
    return render_template("map.html")

@app.route('/data')
def data():
    """Retorna as localizações dos clientes como JSON para atualizar o mapa."""
    with lock:
        data = {client_id: {"lat": lat, "lon": lon, "color": clients_colors[client_id]}
                for client_id, (lat, lon) in clients_locations.items()}
    return jsonify(data)

@app.route('/clients')
def clients():
    """Retorna a lista de clientes conectados e suas localizações."""
    with lock:
        client_list = [{"id": client_id, "lat": lat, "lon": lon, "color": clients_colors[client_id]}
                       for client_id, (lat, lon) in clients_locations.items()]
    return jsonify(client_list)

def handle_client(conn, addr):
    """Recebe dados do cliente e armazena a localização."""
    print(f"[NOVA CONEXÃO] {addr} conectado.")

    # Gerar um ID único para o cliente
    client_id = f"{addr[0]}:{addr[1]}"
    
    with lock:
        if client_id not in clients_colors:
            clients_colors[client_id] = random.choice(COLOR_LIST)

    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            lat, lon = map(float, data.split(","))
            with lock:
                clients_locations[client_id] = (lat, lon)
            print(f"[LOCALIZAÇÃO RECEBIDA] {client_id}: {lat}, {lon}")
    except:
        print(f"[DESCONECTADO] {client_id} saiu.")
    finally:
        with lock:
            clients_locations.pop(client_id, None)
            clients_colors.pop(client_id, None)
        conn.close()

def start_server():
    """Inicia o servidor para receber conexões."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVIDOR ATIVO] Aguardando conexões em {HOST}:{PORT}...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

# Inicia o servidor e o Flask
if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    app.run(host="0.0.0.0", port=8000, debug=True)
