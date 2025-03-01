import socket
import threading
import time
import random

# Configuração do cliente
SERVER_HOST = '127.0.0.1'  # IP do servidor
SERVER_PORT = 5000

import geocoder

def get_real_gps_coordinates():
    """Obtém a localização real baseada no IP."""
    g = geocoder.ip('me')  # Obtém a localização pelo IP
    if g.latlng:
        return f"{g.latlng[0]},{g.latlng[1]}"
    else:
        return "0.000000,0.000000"  # Retorna 0,0 se não conseguir obter


def receive_data(client):
    """Recebe mensagens do servidor."""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"[LOCALIZAÇÃO DE OUTRO CLIENTE] {message}")
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
        time.sleep(5)  # Envia a cada 5 segundos


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
