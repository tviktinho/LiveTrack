import time
import json
import socket
import asyncio
import geocoder
import requests
import threading
import websockets

# Configuração do servidor
SERVER_HOST = '15.229.12.108'
SERVER_PORT = 5000
WEBSOCKET_SERVER = 'ws://15.229.12.108:6790'

cached_location = None
last_request_time = 0

def get_ip_based_location():
    global cached_location, last_request_time
    current_time = time.time()
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
    
def get_real_gps_coordinates():
    global cached_location, last_request_time
    current_time = time.time()   
    try:
        response = geocoder.ip('me')
        if response.ok:
            lat = response.latlng[0] if response.latlng else None
            lon = response.latlng[1] if response.latlng else None
            
            # Se as coordenadas latitude e longitude estiverem disponíveis
            if lat is not None and lon is not None:
                cached_location = f"{lat},{lon}"
                last_request_time = current_time
                return cached_location
            else:
                return "0.0,0.0"
        else:
            return "0.0,0.0"
    
    except Exception as e:
        print(f"[ERRO] Falha ao obter localização: {e}")
        return "0.0,0.0"

def send_data_tcp(client):
    """Envia dados de localização via TCP"""
    while True:
        gps_data = get_ip_based_location()  # Usa localização baseada no IP
        try:
            client.send(gps_data.encode('utf-8'))
            print(f"[ENVIADO TCP] {gps_data}")
        except Exception as e:
            print(f"[ERRO] Falha ao enviar dados TCP: {e}")
            break
        time.sleep(5)


async def send_data_websocket():
    """ Envia dados via WebSocket e recebe dados de outros clientes """
    while True:
        try:
            async with websockets.connect(WEBSOCKET_SERVER) as websocket:
                print("[WEBSOCKET] Conectado ao servidor")
                
                # Criar uma task para enviar dados
                send_task = asyncio.create_task(send_location_updates(websocket))
                
                # Receber dados de outros clientes
                try:
                    while True:
                        data = await websocket.recv()
                        message = json.loads(data)
                        if message["type"] == "location_update":
                            client_id = message["client_id"]
                            lat = message["lat"]
                            lon = message["lon"]
                            print(f"[{client_id}]: {lat},{lon}")
                except Exception as e:
                    print(f"[ERRO] Falha ao receber dados: {e}")
                    send_task.cancel()
                    
        except Exception as e:
            print(f"[ERRO] WebSocket desconectado: {e}")
            await asyncio.sleep(5)  # Aguarda antes de tentar reconectar

async def send_location_updates(websocket):
    """ Envia atualizações de localização periodicamente """
    try:
        while True:
            gps_data_ws = get_real_gps_coordinates()
            await websocket.send(gps_data_ws)
            print(f"[ENVIADO WS] {gps_data_ws}")
            await asyncio.sleep(5)  # Envia a cada 5 segundos
    except asyncio.CancelledError:
        pass
        
def start_websocket_thread():
    """ Inicia o WebSocket em uma thread separada """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    #loop.run_until_complete(send_data_websocket())        

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_HOST, SERVER_PORT))
        print(f"[CONECTADO] Cliente conectado ao servidor {SERVER_HOST}:{SERVER_PORT}")
        
        thread_send_tcp = threading.Thread(target=send_data_tcp, args=(client,))
        thread_send_tcp.start()
        
        thread_ws = threading.Thread(target=start_websocket_thread, daemon=True)
        thread_ws.start()
        
        asyncio.run(send_data_websocket())
        
        thread_send_tcp.join()
    except Exception as e:
        print(f"[ERRO] Não foi possível conectar ao servidor: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()
