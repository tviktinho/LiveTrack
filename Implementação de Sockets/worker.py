import json
import asyncio
from nats.aio.client import Client as NATS

NATS_SERVER = "nats://localhost:4222"
ALERT_DISTANCE = 0.01  # Ajuste a distância limite para alertas

nats_client = NATS()
locations = {}

async def process_location(msg):
    """Processa a localização recebida."""
    data = json.loads(msg.data.decode())
    username = data["username"]
    lat, lon = data["lat"], data["lon"]
    print(f"[WORKER] Processando localização de {username}: {lat}, {lon}")

async def start_worker():
    nc = NATS()
    await nc.connect(servers=[NATS_SERVER])
    print("[WORKER] Conectado ao NATS.")

    await nc.subscribe("locations", cb=process_location, queue="location_workers")

    while True:
        await asyncio.sleep(1)
        
async def setup_nats():
    """Conecta ao NATS e escuta atualizações de localização."""
    await nats_client.connect(servers=[NATS_SERVER])
    print("[NATS] Worker conectado para processar alertas.")

    async def message_handler(msg):
        data = json.loads(msg.data.decode())
        username = data["username"]
        lat, lon = float(data["lat"]), float(data["lon"])

        locations[username] = (lat, lon)
        check_proximity(username, lat, lon)

    await nats_client.subscribe("locations", cb=message_handler)

def check_proximity(user, lat, lon):
    """Verifica se há outro usuário perto o suficiente."""
    for other_user, (other_lat, other_lon) in locations.items():
        if other_user != user:
            distance = ((lat - other_lat) ** 2 + (lon - other_lon) ** 2) ** 0.5
            if distance < ALERT_DISTANCE:
                print(f"[ALERTA] {user} está próximo de {other_user}!")        

async def main():
    await setup_nats()
    await asyncio.Future()  # Mantém o worker rodando

if __name__ == "__main__":
    asyncio.run(main())