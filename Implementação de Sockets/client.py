import sys
import time
import json
import ipinfo
import socket
import asyncio
import geocoder
import requests
import threading
import websockets



#ipinfo.io/[IP address]?token=058ff7f8b2eac9

# Configuração do servidor
SERVER_HOST = '3.145.211.37'
SERVER_PORT = 5000
WEBSOCKET_SERVER = 'ws://3.145.211.37:6955'

access_token = '058ff7f8b2eac9'


cached_location = None
last_request_time = 0
userName = "usuario-desconhecido"
if len(sys.argv) > 1:
    userName = sys.argv[1]
websocket_client = None  # Mantém uma única conexão WebSocket ativa

#TCP
def get_ip_based_location():
    global cached_location, last_request_time
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        if data['status'] == 'success':
            cached_location = f"{data['lat']},{data['lon']}"
            last_request_time = time.time()
            return cached_location
        return "0.0,0.0"
    except Exception as e:
        print(f"[ERRO] Falha ao obter localização: {e}")
        return "0.0,0.0"

#WEB SOCKET
def get_real_gps_coordinates():
    global cached_location, last_request_time
    try:
        response = geocoder.ip('me')        
        if response.ok:
            lat, lon = response.latlng if response.latlng else (None, None)
            if lat is not None and lon is not None:
                cached_location = f"{lat},{lon}"
                last_request_time = time.time()
                return cached_location
        return "0.0,0.0"
    except Exception as e:
        print(f"[ERRO] Falha ao obter localização: {e}")
        return "0.0..0.0"

def send_data_tcp(client):
    """Envia dados de localização via TCP"""
    while True:
        gps_data = get_ip_based_location()
        try:
            if client.fileno() == -1:
                print("[ERRO] Conexão TCP fechada.")
                break
            # Enviar nome do usuário junto com a localização
            message = f"{userName},{gps_data}"
            client.send(message.encode('utf-8'))
            print(f"[ENVIADO TCP] {message}")
        except Exception as e:
            print(f"[ERRO] Falha ao enviar dados TCP: {e}")
            break
        time.sleep(15)

async def send_data_websocket():
    """Envia e recebe dados via WebSocket"""
    global websocket_client

    if websocket_client is not None:
        print("[INFO] WebSocket já está ativo. Ignorando nova conexão.")
        return

    try:
        async with websockets.connect(WEBSOCKET_SERVER) as websocket:
            websocket_client = websocket  # Armazena a conexão ativa
            await websocket.send(json.dumps({"type": "register", "username": userName}))
            print("[WEBSOCKET] Conectado ao servidor")

            send_task = asyncio.create_task(send_location_updates(websocket))

            try:
                while True:
                    data = await websocket.recv()
                    message = json.loads(data)
                    if message["type"] == "location_update":
                        client_id = message["client_id"]
                        lat, lon = message["lat"], message["lon"]
                        print(f"[{client_id}]: {lat},{lon}")
                    elif message["type"] == "mark_point":
                        mark_point_on_map(message["lat"], message["lon"])
            except Exception as e:
                print(f"[ERRO] Falha ao receber dados: {e}")
                send_task.cancel()
    except Exception as e:
        print(f"[ERRO] WebSocket desconectado: {e}")
    finally:
        websocket_client = None  # Reseta a conexão ao desconectar

async def send_location_updates(websocket):
    """Envia atualizações de localização periodicamente"""
    try:
        while True:
            gps_data_ws = get_real_gps_coordinates()
            await websocket.send(gps_data_ws)
            print(f"[ENVIADO WS] {gps_data_ws}")
            await asyncio.sleep(15)
    except asyncio.CancelledError:
        print("[INFO] Tarefa de envio de localização cancelada.")

def start_websocket_thread():
    """Garante que apenas um WebSocket seja iniciado"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_data_websocket())

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_HOST, SERVER_PORT))
        print(f"[CONECTADO] Cliente conectado ao servidor {SERVER_HOST}:{SERVER_PORT}")

        thread_send_tcp = threading.Thread(target=send_data_tcp, args=(client,))
        thread_send_tcp.start()

        # Executa WebSocket apenas se não estiver ativo
        if websocket_client is None:
            thread_ws = threading.Thread(target=start_websocket_thread, daemon=True)
            thread_ws.start()
        else:
            print("[INFO] WebSocket já rodando. Ignorando nova inicialização.")

        thread_send_tcp.join()
    except Exception as e:
        print(f"[ERRO] Não foi possível conectar ao servidor: {e}")
    finally:
        client.close()

def mark_point_on_map(lat, lon):
    """Marca um ponto no mapa"""
    print(f"[MARCAR PONTO] Latitude: {lat}, Longitude: {lon}")

if __name__ == "__main__":
    start_client()
