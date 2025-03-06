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

# Iniciar Flask
app = Flask(__name__)
CORS(app)

@app.route('/')
def mapa():
    return render_template("map.html")

@app.route('/data')
def data():
    """Retorna as localizações dos clientes TCP e WebSocket separadamente."""
    with lock:
        print("[DEBUG] Dados no servidor:", tcp_locations, ws_locations)
        data = {
            "tcp": {client_id: {"lat": lat, "lon": lon, "color": clients_colors.get(client_id, "gray")}
                    for client_id, (lat, lon) in tcp_locations.items()},
            "websocket": {client_id: {"lat": lat, "lon": lon, "color": clients_colors.get(client_id, "blue")}
                          for client_id, (lat, lon) in ws_locations.items()}
        }
    return jsonify(data)

@app.route("/update_location", methods=["POST"])
def update_location():
    data = request.json
    return jsonify({"message": "Localização atualizada com sucesso!"}), 200

@app.route("/mark_point", methods=["POST"])
def mark_point():
    """Endpoint para marcar um ponto no mapa."""
    data = request.json
    lat = data.get("lat")
    lon = data.get("lon")
    
    # Broadcast the marked point to all clients
    asyncio.run(broadcast_marked_point(lat, lon))
    
    return jsonify({"message": "Ponto marcado com sucesso!"}), 200

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

def handle_tcp_client(conn, addr):
    """Recebe dados do cliente via TCP e armazena a localização."""
    print(f"[NOVA CONEXÃO TCP] {addr} conectado.")
    client_id = f"TCP-{addr[0]}:{addr[1]}"

    with lock:
        active_tcp_connections.append(client_id)
        if client_id not in clients_colors:
            clients_colors[client_id] = random.choice(COLOR_LIST)

    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            lat, lon = map(float, data.split(","))

            with lock:
                tcp_locations[client_id] = (lat, lon)  # Agora armazena apenas em tcp_locations
            print(f"[LOCALIZAÇÃO RECEBIDA TCP] {client_id}: {lat}, {lon}")
    except:
        print(f"[DESCONECTADO TCP] {client_id} saiu.")
    finally:
        with lock:
            active_tcp_connections.remove(client_id)
            tcp_locations.pop(client_id, None)  # Remover da estrutura correta
            clients_colors.pop(client_id, None)
        conn.close()

async def websocket_handler(websocket):
    global websocket_counter
    client_id = f"CLIENTE {websocket_counter}"
    websocket_counter += 1
    websocket_clients[client_id] = websocket
    active_ws_connections[client_id] = websocket
    print(f"[WebSocket] Novo cliente conectado: {client_id}")
    
    try:
        while True:
            try:
                # Receber dados do cliente
                data = await websocket.recv()
                lat, lon = map(float, data.split(","))
                
                # Atualizar localização do cliente
                with lock:
                    ws_locations[client_id] = (lat, lon)
                print(f"[LOCALIZAÇÃO RECEBIDA WS] {client_id}: {lat},{lon}")
                
                # Broadcast da nova localização para todos os clientes
                await broadcast_location(client_id, lat, lon)
                
                await asyncio.sleep(1)  # Pequeno delay para evitar sobrecarga
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                print(f"[ERRO] Erro ao processar dados do cliente {client_id}: {e}")
                break
                
    except websockets.exceptions.ConnectionClosed:
        print(f"[WebSocket] Cliente {client_id} desconectado.")
    except websockets.exceptions.ConnectionClosedOK:
        print(f"[WebSocket] Conexão encerrada pelo cliente {client_id}.")
    except websockets.exceptions.ConnectionClosedError:
        print(f"[WebSocket] Conexão fechada inesperadamente para cliente {client_id}.")
    finally:
        # Remover o cliente do dicionário quando desconectar
        ws_locations.pop(client_id, None)
        active_ws_connections.pop(client_id, None)
        if client_id in websocket_clients:
            del active_ws_connections[client_id]
            del websocket_clients[client_id]        

def is_port_available(port):
    """Verifica se uma porta está disponível."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        sock.close()
        return True
    except socket.error:
        return False

def ensure_ports_available():
    """Verifica se as portas necessárias estão disponíveis."""
    ports = [PORT, WEBSOCKET_PORT, 8000]
    unavailable_ports = []
    
    for port in ports:
        if not is_port_available(port):
            unavailable_ports.append(port)
    
    if unavailable_ports:
        print("[ERRO] As seguintes portas estão em uso:")
        for port in unavailable_ports:
            print(f"- Porta {port}")
        print("\nPor favor, encerre os processos que estão usando essas portas e tente novamente.")
        return False
    
    return True

async def broadcast_location(sender_id, lat, lon):
    """Envia uma atualização de localização para todos os clientes WebSocket"""
    for ws_client_id, ws in websocket_clients.items():
        try:
            # Envia apenas a localização do cliente que atualizou
            message = {
                "type": "location_update",
                "client_id": sender_id,
                "lat": lat,
                "lon": lon
            }
            await ws.send(json.dumps(message))
        except Exception as e:
            print(f"[ERRO] Falha ao enviar para {ws_client_id}: {e}")

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

def start_tcp_server():
    """Servidor TCP para receber dados de localização"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVIDOR TCP] Rodando em {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True)
        thread.start()

if __name__ == "__main__":
    threading.Thread(target=start_websocket_server, daemon=True).start()
    threading.Thread(target=start_tcp_server, daemon=True).start()
    app.run(host="0.0.0.0", port=8000, debug=True)
