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

# Configuração do servidor
HOST = '0.0.0.0'
PORT = 5000
WEBSOCKET_PORT = 6955

active_tcp_connections = []
active_ws_connections = {}
websocket_clients = {}
clients_locations = {}
tcp_locations = {}
ws_locations = {}
clients_colors = {}
websocket_counter = 0
lock = threading.Lock()

# Cores para os marcadores do mapa
COLOR_LIST = [
    "red", "blue", "green", "purple", "orange", "darkred", "lightred",
    "beige", "darkblue", "darkgreen", "cadetblue", "darkpurple"
]

# Configuração inicial do Flask com CORS habilitado
app = Flask(__name__)
CORS(app)

#Desabilitar o cache no Flask
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Rota principal que carrega o mapa HTML
@app.route('/')
def mapa():
    return render_template("map.html")

# Rota para obter dados atualizados das localizações dos clientes
@app.route('/data')
def data():
    """Retorna as localizações dos clientes TCP e WebSocket separadamente."""
    with lock:
        print("[DEBUG] Dados no servidor:", tcp_locations, ws_locations)
        data = {
            "tcp": {client_id: {"lat": lat, "lon": lon, "color": clients_colors.get(client_id, "gray"), "name": client_id}
                    for client_id, (lat, lon) in tcp_locations.items()},
            "websocket": {client_id: {"lat": lat, "lon": lon, "color": clients_colors.get(client_id, "blue"), "name": client_id}
                      for client_id, (lat, lon) in ws_locations.items()}
        }
    return jsonify(data)

# Rota para atualizar a localização de um cliente via POST
@app.route("/update_location", methods=["POST"])
def update_location():
    data = request.json
    return jsonify({"message": "Localização atualizada com sucesso!"}), 200

# Rota para marcar pontos no mapa via POST
@app.route("/mark_point", methods=["POST"])
def mark_point():
    """Endpoint para marcar um ponto no mapa."""
    data = request.json
    lat = data.get("lat")
    lon = data.get("lon")
    asyncio.run(broadcast_marked_point(lat, lon))
    return jsonify({"message": "Ponto marcado com sucesso!"}), 200

# Função assíncrona para notificar todos os clientes WebSocket sobre um novo ponto marcado
async def broadcast_marked_point(lat, lon):
    """Envia a localização marcada para todos os clientes WebSocket."""
    for ws_client_id, ws in websocket_clients.items():
        try:
            message = {
                "type": "mark_point",
                "lat": lat,
                "lon": lon
            }
            await ws.send(json.dumps(message))
        except Exception as e:
            print(f"[ERRO] Falha ao enviar para {ws_client_id}: {e}")

# Função para verificar se a porta está disponível
def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("0.0.0.0", port)) != 0

# Garante que as portas estão disponíveis antes de iniciar os servidores
def ensure_ports_available():
    ports = [PORT, WEBSOCKET_PORT, 8000]
    unavailable_ports = [port for port in ports if not is_port_available(port)]
    if unavailable_ports:
        print("[ERRO] As seguintes portas estão em uso:", unavailable_ports)
        return False
    return True

# Handler para conexões WebSocket
async def websocket_handler(websocket):
    global websocket_counter
    client_id = f"CLIENTE {websocket_counter}"
    websocket_counter += 1

    # Receber o primeiro pacote para capturar o nome de usuário
    try:
        data = await websocket.recv()
        message = json.loads(data)
        if message.get("type") == "register":
            username = message.get("username", "Desconhecido")
        else:
            username = "Desconhecido"
    except:
        username = "Desconhecido"

    print(f"[WebSocket] Novo cliente conectado [{client_id}]: {username}")
    websocket_clients[username] = websocket

    # Mantenha a conexão aberta aguardando mensagens ou o fechamento
    try:
        async for msg in websocket:
            # Aqui você pode processar mensagens adicionais, se necessário
            print(f"[WebSocket] Mensagem recebida de {username}: {msg}")
    except Exception as e:
        print(f"[WebSocket] Erro na conexão com {username}: {e}")
    finally:
        print(f"[WebSocket] Conexão encerrada com {username}")
        websocket_clients.pop(username, None)

# Inicia o servidor WebSocket
async def websocket_server():
    async with websockets.serve(websocket_handler, "0.0.0.0", WEBSOCKET_PORT):
        await asyncio.Future()

# Função para iniciar o servidor WebSocket
def start_websocket_server():
    try:
        asyncio.run(websocket_server())
    except Exception as e:
        print(f"Erro ao iniciar WebSocket: {e}")

# Função para iniciar o servidor TCP
def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVIDOR TCP] Rodando em {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True)
        thread.start()

# Handler para conexões TCP, processando dados recebidos
def handle_tcp_client(conn, addr):
    print(f"[NOVA CONEXÃO TCP] {addr} conectado.")
    try:
        # Primeiro pacote recebido deve conter o nome do usuário
        first_data = conn.recv(1024).decode('utf-8')
        if not first_data:
            conn.close()
            return
        parts = first_data.split(",")
        if len(parts) < 3:
            conn.close()
            return

        user_name = parts[0]  # Obtém o nome do usuário
        lat, lon = float(parts[1]), float(parts[2])
        
        client_id = f"{user_name}"  # Agora o ID do cliente será o nome dele
        print(f"[NOVO CLIENTE TCP] {client_id} conectado.")

        active_tcp_connections.append(client_id)
        clients_colors[client_id] = random.choice(COLOR_LIST)
        tcp_locations[client_id] = (lat, lon)  # Salva localização inicial

        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            parts = data.split(",")
            if len(parts) < 3:
                continue  # Ignora pacotes inválidos
            
            lat, lon = float(parts[1]), float(parts[2])  # Ignora o nome e mantém a localização
            tcp_locations[client_id] = (lat, lon)

    except Exception as e:
        print(f"[ERRO] Falha ao processar cliente TCP: {e}")
    finally:
        print(f"[DESCONECTADO TCP] {client_id}")
        active_tcp_connections.remove(client_id)
        tcp_locations.pop(client_id, None)
        clients_colors.pop(client_id, None)
        conn.close()

# Ponto de entrada principal
if __name__ == "__main__":
    if ensure_ports_available():
        threading.Thread(target=start_websocket_server, daemon=True).start()
        threading.Thread(target=start_tcp_server, daemon=True).start()
        app.run(host="0.0.0.0", port=8000, debug=False)
