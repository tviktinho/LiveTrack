import time
import threading
import socket
import asyncio
import websockets
import requests

# Configuração do servidor
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
WEBSOCKET_SERVER = 'ws://localhost:6790'

cached_location = None
last_request_time = 0

def get_ip_based_location():
    global cached_location, last_request_time
    current_time = time.time()
    if cached_location and (current_time - last_request_time < 3600):
        return cached_location
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        if data['status'] == 'success':
            cached_location = f"{data['lat']},{data['lon']}"
            last_request_time = current_time
            return cached_location
        else:
            return "0.0,0.0"
    except Exception as e:
        print(f"[ERRO] Falha ao obter localização: {e}")
        return "0.0,0.0"

def send_data_tcp(client):
    while True:
        gps_data = get_ip_based_location()
        try:
            client.send(gps_data.encode('utf-8'))
            print(f"[ENVIADO TCP] {gps_data}")
        except Exception as e:
            print(f"[ERRO] Falha ao enviar dados TCP: {e}")
            break
        time.sleep(5)

async def send_data_websocket():
    while True:
        gps_data = get_ip_based_location()
        try:
            async with websockets.connect(WEBSOCKET_SERVER) as websocket:
                await websocket.send(gps_data)
                print(f"[ENVIADO WS] {gps_data}")
        except Exception as e:
            print(f"[ERRO] Falha ao enviar dados WebSocket: {e}")
        await asyncio.sleep(5)

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_HOST, SERVER_PORT))
        print(f"[CONECTADO] Cliente conectado ao servidor {SERVER_HOST}:{SERVER_PORT}")
        
        thread_send_tcp = threading.Thread(target=send_data_tcp, args=(client,))
        thread_send_tcp.start()
        
        asyncio.run(send_data_websocket())
        
        thread_send_tcp.join()
    except Exception as e:
        print(f"[ERRO] Não foi possível conectar ao servidor: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()