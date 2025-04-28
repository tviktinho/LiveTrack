import sys
import time
import json
import asyncio
import requests
from nats.aio.client import Client as NATS

NATS_SERVER = "nats://localhost:4222"
userName = sys.argv[1] if len(sys.argv) > 1 else "usuario-desconhecido"
nats_client = NATS()

async def connect_nats():
    """Conecta ao servidor NATS e se inscreve para receber atualizações de localização."""
    await nats_client.connect(servers=[NATS_SERVER])
    print("[NATS] Conectado com sucesso!")

    async def message_handler(msg):
        data = json.loads(msg.data.decode())
        if data["username"] != userName:  # Ignora suas próprias mensagens
            print(f"[NATS] {data['username']} está em {data['lat']}, {data['lon']}")

    await nats_client.subscribe("locations", cb=message_handler)

def get_ip_location():
    """Obtém a localização do usuário baseada no IP."""
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        if data['status'] == 'success':
            return str(data['lat']), str(data['lon'])
        else:
            return "0.0", "0.0"
    except Exception as e:
        print(f"[ERRO] Falha ao obter localização via IP: {e}")
        return "0.0", "0.0"

async def send_data_nats():
    """Envia dados de localização real via NATS."""
    await connect_nats()

    while True:
        lat, lon = get_ip_location()
        message = json.dumps({"username": userName, "lat": lat, "lon": lon})

        try:
            await nats_client.publish("locations", message.encode())
            print(f"[NATS] Enviado: {message}")
        except Exception as e:
            print(f"[NATS] Erro ao enviar mensagem: {e}")

        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(send_data_nats())
