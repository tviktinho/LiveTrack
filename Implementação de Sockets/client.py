import socket
import threading
import time
import requests

# Configuração do cliente
SERVER_HOST = '127.0.0.1' 
SERVER_PORT = 5000
client_id = None

def get_real_gps_coordinates():
    """Obtém a localização real do sistema operacional."""
    try:
        response = requests.get("https://ipinfo.io/json").json()
        location = response["loc"].split(",")
        latitude, longitude = float(location[0]), float(location[1])
        return f"{latitude},{longitude}"
    except Exception as e:
        print(f"[ERRO] Falha ao obter localização real: {e}")
        return "0.000000,0.000000"

def receive_data(client):
    """Recebe mensagens do servidor."""
    global client_id
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                break
            if client_id is None:
                client_id = message
                print(f"[NOVA CONEXÃO] Cliente ID: {client_id}")
            else:
                print(f"{message}")
        except:
            print("[ERRO] Conexão perdida com o servidor.")
            break

def send_data(client):
    """Envia coordenadas GPS reais periodicamente."""
    while True:
        gps_data = get_real_gps_coordinates()
        try:
            client.send(gps_data.encode('utf-8'))
            print(f"[ENVIADO] {gps_data}")
        except:
            print("[ERRO] Falha ao enviar dados.")
            break
        time.sleep(5)

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_HOST, SERVER_PORT))
        print(f"[CONECTADO] Cliente conectado ao servidor {SERVER_HOST}:{SERVER_PORT}")
        
        thread_receive = threading.Thread(target=receive_data, args=(client,))
        thread_send = threading.Thread(target=send_data, args=(client,))
        
        thread_receive.start()
        thread_send.start()
        
        thread_receive.join()
        thread_send.join()
    except Exception as e:
        print(f"[ERRO] Não foi possível conectar ao servidor: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()