import json
import psutil
import random
import socket
import asyncio
import threading
import websockets
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Configuração do servidor
HOST = '0.0.0.0'
PORT = 5000
WEBSOCKET_PORT = 6790
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

@app.route('/')
def mapa():
    return render_template("map.html")

@app.route('/data')
def data():
    """Retorna as localizações dos clientes como JSON para atualizar o mapa."""
    with lock:
        print("[DEBUG] Dados no servidor:", clients_locations)
        data = {client_id: {"lat": lat, "lon": lon, "color": clients_colors[client_id]}
                for client_id, (lat, lon) in clients_locations.items()}
    return jsonify(data)

@app.route("/update_location", methods=["POST"])
def update_location():
    data = request.json
    return jsonify({"message": "Localização atualizada com sucesso!"}), 200

@app.route("/shutdown")
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    return "Servidor encerrado"

def handle_client(conn, addr):
    """Recebe dados do cliente e armazena a localização."""
    print(f"[NOVA CONEXÃO] {addr} conectado.")

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

def start_tcp_server():
    """Servidor TCP para receber dados de localização"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVIDOR TCP] Rodando em {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

def is_port_in_use(port):
    """Verifica se a porta já está em uso."""
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return True
    return False

if is_port_in_use(WEBSOCKET_PORT):
    print(f"⚠️ A porta {WEBSOCKET_PORT} já está em uso. Finalize o processo antes de iniciar o servidor.")
    
async def websocket_handler(websocket):
    try:
        while True:
            with lock:
                data = {
                    client_id: {"lat": lat, "lon": lon, "color": clients_colors.get(client_id, "gray")}
                    for client_id, (lat, lon) in clients_locations.items()
                }
            await websocket.send(json.dumps(data))
            await asyncio.sleep(5)
            await websocket.ping()
            await asyncio.sleep(30)
    except websockets.exceptions.ConnectionClosed:
        print("[WebSocket] Cliente desconectado.")
    except websockets.exceptions.ConnectionClosedOK:
        print("[WebSocket] Conexão encerrada pelo cliente.")
    except websockets.exceptions.ConnectionClosedError:
        print("[WebSocket] Conexão fechada inesperadamente.")

async def websocket_server():
    async with websockets.serve(websocket_handler, "0.0.0.0", WEBSOCKET_PORT):
        await asyncio.Future()

def start_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(websocket_server())
    except Exception as e:
        print(f"Erro ao iniciar WebSocket: {e}")
    finally:
        loop.close()

if __name__ == "__main__":
    threading.Thread(target=start_websocket_server, daemon=True).start()
    threading.Thread(target=start_tcp_server, daemon=True).start()
    app.run(host="0.0.0.0", port=8000, debug=True)
