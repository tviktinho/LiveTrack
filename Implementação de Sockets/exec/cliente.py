import time
import asyncio
import websockets
import requests
import tkinter as tk
from tkinter import messagebox
import threading
import webbrowser  # Para abrir no navegador

# Configuração do servidor WebSocket
WEBSOCKET_SERVER = 'ws://localhost:6790'
MAP_URL = "http://192.168.100.105:8000"  # URL do mapa

location_data = {}  # Armazena a localização dos usuários

async def receive_data_websocket():
    """Recebe dados do servidor WebSocket e atualiza as localizações"""
    global location_data
    while True:
        try:
            async with websockets.connect(WEBSOCKET_SERVER) as websocket:
                while True:
                    data = await websocket.recv()
                    print(f"[RECEBIDO WS] {data}")
                    user_id = f"Usuário {len(location_data) + 1}"
                    location_data[user_id] = data
        except Exception as e:
            print(f"[ERRO] Falha ao conectar ao WebSocket: {e}")
        await asyncio.sleep(5)

def start_websocket_thread():
    """Inicia a conexão WebSocket em uma thread separada"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(receive_data_websocket())

def abrir_mapa():
    """Abre o mapa no navegador padrão"""
    webbrowser.open(MAP_URL)

def reconectar():
    """Reconecta ao WebSocket"""
    global location_data
    location_data.clear()
    threading.Thread(target=start_websocket_thread, daemon=True).start()
    messagebox.showinfo("Reconectado", "Conexão ao WebSocket reiniciada.")

def sair():
    """Fecha a aplicação"""
    root.destroy()

# Criando a interface gráfica
root = tk.Tk()
root.title("LiveTrack - Monitoramento de GPS")
root.geometry("400x200")

# Criando os botões
btn_frame = tk.Frame(root)
btn_frame.pack(pady=20)

btn_abrir_mapa = tk.Button(btn_frame, text="Abrir Mapa", command=abrir_mapa, width=20)
btn_abrir_mapa.grid(row=0, column=0, padx=5)

btn_reconectar = tk.Button(btn_frame, text="Reconectar", command=reconectar, width=20)
btn_reconectar.grid(row=1, column=0, padx=5, pady=10)

btn_sair = tk.Button(btn_frame, text="Sair", command=sair, width=20)
btn_sair.grid(row=2, column=0, padx=5, pady=10)

# Iniciando a conexão WebSocket em uma thread separada
threading.Thread(target=start_websocket_thread, daemon=True).start()

# Iniciar a interface gráfica
root.mainloop()
