import socket
import threading

# Configurações do servidor
HOST = '0.0.0.0'  # Permite conexões de qualquer IP
PORT = 5000
clientes = []  # Lista de clientes conectados

# Função para lidar com clientes
def handle_client(conn, addr):
    print(f"[NOVA CONEXÃO] Cliente {addr} conectado.")
    clientes.append(conn)
    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            print(f"[LOCALIZAÇÃO RECEBIDA] {addr}: {data}")
            broadcast(data, conn)
    except:
        pass
    finally:
        print(f"[DESCONECTADO] Cliente {addr} saiu.")
        clientes.remove(conn)
        conn.close()

# Função para enviar mensagens a todos os clientes conectados
def broadcast(message, sender):
    for client in clientes:
        if client != sender:
            try:
                client.send(message.encode('utf-8'))
            except:
                clientes.remove(client)

# Inicialização do servidor
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVIDOR RODANDO] Aguardando conexões em {HOST}:{PORT}...")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
