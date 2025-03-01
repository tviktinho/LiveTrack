import socket
import threading

# Configurações do servidor
HOST = '0.0.0.0'  # Permite conexões de qualquer IP
PORT = 5000
clientes = []  # Lista de clientes conectados
next_id = 1  # Próximo ID disponível

# Função para lidar com clientes
def handle_client(conn, addr):
    global next_id
    client_id = next_id
    next_id += 1

    print(f"[NOVA CONEXÃO] Cliente {client_id} ({addr}) conectado.")
    clientes.append((conn, client_id))

    try:
        conn.send(f"{client_id}".encode('utf-8'))  # Envia o ID para o cliente
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            print(f"[LOCALIZAÇÃO RECEBIDA] Cliente {client_id} ({addr}): {data}")
            broadcast(f"Cliente {client_id}: {data}", conn)
    except:
        pass
    finally:
        print(f"[DESCONECTADO] Cliente {client_id} ({addr}) saiu.")
        clientes.remove((conn, client_id))
        conn.close()

# Função para enviar mensagens a todos os clientes conectados
def broadcast(message, sender):
    for client, client_id in clientes:
        if client != sender:
            try:
                client.send(message.encode('utf-8'))
            except:
                clientes.remove((client, client_id))

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