import sys
import time
import json
import socket
import asyncio
import geocoder
import requests
import threading
import websockets
from nats.aio.client import Client as NATS

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
WEBSOCKET_SERVER = 'ws://127.0.0.1:6955'
NATS_SERVER = "nats://localhost:4222"

userName = sys.argv[1] if len(sys.argv) > 1 else "usuario-desconhecido"
nats_client = NATS()

async def connect_nats():
    """Conecta ao servidor NATS e escuta atualizações de localização."""
    await nats_client.connect(servers=[NATS_SERVER])

    async def message_handler(msg):
        data = json.loads(msg.data.decode())
        print(f"[NATS] {data['username']}: {data['lat']}, {data['lon']}")

    await nats_client.subscribe("locations", cb=message_handler)

def get_real_gps_coordinates():
    """Obtém a localização GPS real do usuário"""
    try:
        response = geocoder.ip('me')        
        if response.ok:
            lat, lon = response.latlng if response.latlng else (None, None)
            if lat is not None and lon is not None:
                return lat, lon
        return "0.0", "0.0"  # Retorna valores padrão se falhar
    except Exception as e:
        print(f"[ERRO] Falha ao obter localização: {e}")
        return "0.0", "0.0"

def get_ip_based_location():
    """Obtém a localização baseada no IP do usuário."""
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        if data['status'] == 'success':
            return float(data['lat']), float(data['lon'])
        return 0.0, 0.0
    except Exception as e:
        print(f"[ERRO] Falha ao obter localização: {e}")
        return 0.0, 0.0

def send_data_tcp(client):
    """Envia dados de localização via TCP."""
    while True:
        lat, lon = get_ip_based_location()
        message = f"{userName},{lat},{lon}"
        try:
            client.send(message.encode('utf-8'))
            print(f"[TCP] Enviado: {message}")
        except Exception as e:
            print(f"[TCP] Erro: {e}")
            break
        time.sleep(15)

async def send_data_websocket():
    """Envia localização via WebSocket."""
    async with websockets.connect(WEBSOCKET_SERVER) as websocket:
        await websocket.send(json.dumps({"type": "register", "username": userName}))
        while True:
            lat, lon = get_real_gps_coordinates()
            await websocket.send(f"{lat},{lon}")
            print(f"[WS] Enviado: {lat}, {lon}")
            await asyncio.sleep(15)

def start_client():
    """Inicia os serviços de TCP, WebSocket e NATS."""
    threading.Thread(target=lambda: asyncio.run(connect_nats()), daemon=True).start()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_HOST, SERVER_PORT))
        print(f"[TCP] Conectado ao servidor {SERVER_HOST}:{SERVER_PORT}")
        threading.Thread(target=send_data_tcp, args=(client,), daemon=True).start()
        asyncio.run(send_data_websocket())
    except Exception as e:
        print(f"[TCP] Erro: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()
