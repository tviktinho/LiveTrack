import json
import random
import socket
import asyncio
import threading
import websockets
from flask import Flask, render_template, jsonify
from flask_cors import CORS

# Configuração do servidor
HOST = '0.0.0.0'
PORT = 5000
WEBSOCKET_PORT = 6789
clients_locations = {}
clients_colors = {}
lock = threading.Lock()

# Cores para os marcadores do mapa
COLOR_LIST = [
    "red", "blue", "green", "purple", "orange", "darkred", "lightred",
    "beige", "darkblue", "darkgreen", "cadetblue", "darkpurple"
]

# Iniciar Flask
app = Flask(__name__)
CORS(app)

@app.route('/map')
def mapa():
    return render_template("map.html")

@app.route('/data')
def data():
    """Retorna as localizações dos clientes como JSON para atualizar o mapa."""
    with lock:
        print("[DEBUG] Dados no servidor:", clients_locations)  # <-- Adicionado para verificar no terminal
        data = {client_id: {"lat": lat, "lon": lon, "color": clients_colors[client_id]}
                for client_id, (lat, lon) in clients_locations.items()}
    return jsonify(data)


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
            print(f"[LOCALIZAÇÃO RECEBIDA] {client_id}: {lat}, {lon}")  # <-- Verifique se os dados chegam aqui
    except:
        print(f"[DESCONECTADO] {client_id} saiu.")
    finally:
        with lock:
            clients_locations.pop(client_id, None)
            clients_colors.pop(client_id, None)
        conn.close()


def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

async def websocket_handler(websocket, path):
    while True:
        with lock:
            data = json.dumps(clients_locations)
        await websocket.send(data)
        await asyncio.sleep(5)

def start_websocket_server():
    asyncio.run(websockets.serve(websocket_handler, "0.0.0.0", WEBSOCKET_PORT, create_protocol=None))

if __name__ == "__main__":
    threading.Thread(target=start_websocket_server, daemon=True).start()
    threading.Thread(target=start_tcp_server, daemon=True).start()
    app.run(host="0.0.0.0", port=8000, debug=True)