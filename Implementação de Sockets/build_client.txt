SERVER_CONFIG = {
    'host': 'http://192.168.100.105:8000',  # Change this to your server IP
    'port': 5000,
    'ws_port': 6790
}

# 2. Update connection variables
SERVER_HOST = SERVER_CONFIG['host']
SERVER_PORT = SERVER_CONFIG['port']
WEBSOCKET_SERVER = f"ws://{SERVER_CONFIG['host']}:{SERVER_CONFIG['ws_port']}"