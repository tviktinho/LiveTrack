import sys
import json
import asyncio
import requests
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

NATS_SERVER = "nats://35.238.213.13:4222"
userName = sys.argv[1] if len(sys.argv) > 1 else "usuario-desconhecido"
nats_client = NATS()

async def connect_nats():
    """Conecta ao servidor NATS e se inscreve para receber atualizações."""
    try:
        await nats_client.connect(servers=[NATS_SERVER])
        print("[NATS] Conectado com sucesso!")

        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                if data.get("username") != userName:
                    print(f"[NATS] Recebido: {data['username']} está em {data['lat']}, {data['lon']}")
            except Exception as e:
                print(f"[NATS] Erro ao processar mensagem recebida: {e}")

        await nats_client.subscribe("locations", cb=message_handler)

    except ErrNoServers as e:
        print("[NATS] Erro: Não foi possível conectar ao NATS Server.")
        raise e

def get_ip_location():
    """Obtém a localização baseada no IP."""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        data = response.json()
        if data.get('status') == 'success':
            return str(data['lat']), str(data['lon'])
        else:
            return "0.0", "0.0"
    except Exception as e:
        print(f"[ERRO] Falha ao obter localização via IP: {e}")
        return "0.0", "0.0"

async def send_data_nats():
    """Envia dados de localização para o NATS periodicamente."""
    while True:
        try:
            if not nats_client.is_connected:
                print("[NATS] Reconectando...")
                await connect_nats()

            lat, lon = get_ip_location()
            message = json.dumps({"username": userName, "lat": lat, "lon": lon})

            await nats_client.publish("locations", message.encode())
            print(f"[NATS] Enviado: {message}")

        except (ErrConnectionClosed, ErrTimeout) as e:
            print(f"[NATS] Conexão perdida ou timeout: {e}")
            await asyncio.sleep(2)  # Aguarda um pouco antes de tentar reconectar
            continue

        except Exception as e:
            print(f"[NATS] Erro inesperado ao enviar dados: {e}")

        await asyncio.sleep(5)

async def main():
    print(f"[INFO] Iniciando cliente como '{userName}'...")
    try:
        await connect_nats()
        await send_data_nats()
    except Exception as e:
        print(f"[FATAL] Cliente encerrado devido a erro: {e}")

if __name__ == "__main__":
    asyncio.run(main())
