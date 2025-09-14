import os
import json
import asyncio
import threading
from flask import Flask, render_template, jsonify, send_from_directory
from flask_cors import CORS
from nats.aio.client import Client as NATS

NATS_SERVER = "nats://35.238.213.13:4222"
nats_client = NATS()

app = Flask(__name__)
CORS(app)

@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.path.dirname(__file__), 'manifest.json')

@app.route('/')
def mapa():
    return render_template("map.html")

async def setup_nats():
    """Conecta ao NATS."""
    await nats_client.connect(servers=[NATS_SERVER])
    print("[NATS] Servidor conectado.")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_nats())
    
    threading.Thread(
        target=app.run,
        kwargs={"host": "0.0.0.0", "port": 8000, "debug": False},
        daemon=True 
    ).start()
    
    loop.run_forever()
