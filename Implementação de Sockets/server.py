import json
import psutil
import random
import socket
import asyncio
import threading
import websockets
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from urllib.parse import urlparse, parse_qs
from nats.aio.client import Client as NATS

# Configuração do servidor
HOST = '0.0.0.0'
PORT = 5000
WEBSOCKET_PORT = 6955
NATS_SERVER = "nats://localhost:4222"

active_tcp_connections = []
websocket_clients = {}
tcp_locations = {}
ws_locations = {}
clients_colors = {}
lock = threading.Lock()
nats_client = NATS()

# Configuração inicial do Flask com CORS habilitado
app = Flask(__name__)
CORS(app)

async def setup_nats():
    """Conecta ao NATS na inicialização do servidor."""
    await nats_client.connect(servers=[NATS_SERVER])
    print("[NATS] Conectado ao servidor NATS.")

async def publish_location_update(username, lat, lon):
    """Publica a localização do cliente no NATS."""
    message = json.dumps({"username": username, "lat": lat, "lon": lon})
    await nats_client.publish("locations", message.encode())

@app.route('/')
def mapa():
    return render_template("map.html")

@app.route('/data')
def data():
    """Retorna as localizações dos clientes."""
    with lock:
        return jsonify({
            "tcp": {user: {"lat": lat, "lon": lon, "color": clients_colors.get(user, "gray")} 
                    for user, (lat, lon) in tcp_locations.items()},
            "websocket": {user: {"lat": lat, "lon": lon, "color": clients_colors.get(user, "blue")} 
                          for user, (lat, lon) in ws_locations.items()}
        })

async def websocket_handler(websocket):
    """Gerencia conexões WebSocket e publica localização no NATS."""
    try:
        data = await websocket.recv()
        message = json.loads(data)
        username = message.get("username", "Desconhecido")

        print(f"[WebSocket] Cliente conectado: {username}")
        websocket_clients[username] = websocket

        while True:
            data = await websocket.recv()
            lat, lon = map(float, data.split(","))
            with lock:
                ws_locations[username] = (lat, lon)
            await publish_location_update(username, lat, lon)

    except websockets.exceptions.ConnectionClosed:
        print(f"[WebSocket] Cliente {username} desconectado.")
    finally:
        ws_locations.pop(username, None)
        websocket_clients.pop(username, None)

async def websocket_server():
    async with websockets.serve(websocket_handler, "0.0.0.0", WEBSOCKET_PORT):
        await asyncio.Future()

def handle_tcp_client(conn, addr):
    """Gerencia conexões TCP e publica localização no NATS."""
    try:
        data = conn.recv(1024).decode('utf-8').strip()
        if not data:
            raise ValueError("Dados vazios recebidos.")

        parts = data.split(",")
        if len(parts) != 3:
            raise ValueError(f"Formato de dados inválido: {data}")

        username, lat, lon = parts
        lat, lon = float(lat), float(lon)

        print(f"[TCP] Cliente conectado: {username} - {lat}, {lon}")
        with lock:
            tcp_locations[username] = (lat, lon)
            clients_colors[username] = random.choice(["red", "blue", "green"])

        asyncio.run(publish_location_update(username, lat, lon))

    except Exception as e:
        print(f"[TCP] Erro com cliente {addr}: {e}")

    finally:
        conn.close()


def start_tcp_server():
    """Inicia o servidor TCP para receber localizações."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVIDOR TCP] Rodando em {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True)
        thread.start()

async def main():
    """Inicia os servidores Flask, TCP e WebSocket, garantindo a conexão com NATS."""
    await setup_nats()
    
    threading.Thread(target=start_tcp_server, daemon=True).start()
    threading.Thread(target=lambda: asyncio.run(websocket_server()), daemon=True).start()

    print("[Flask] Servidor iniciado em http://0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)

if __name__ == "__main__":
    asyncio.run(main())
