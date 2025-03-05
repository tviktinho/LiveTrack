# GPS Live Tracker

## Requisitos
- Python 3.x
- Node.js e npm

## Arquivos Necessários
```
Implementação de Sockets/
├── server.py              # Servidor principal
├── client.py             # Cliente Python
├── start_server.bat      # Script para iniciar o servidor
├── templates/            # Arquivos de template
│   ├── manifest.json
│   └── map.html
└── electron-client/      # Cliente Electron
    ├── index.js
    ├── package.json
    └── package-lock.json
```

## Instalação

1. Instale as dependências Python:
```bash
pip install flask flask-cors psutil websockets
```

2. Na pasta electron-client, instale as dependências Node.js:
```bash
cd electron-client
npm install
```

## Como Executar

### Servidor
1. Execute o arquivo `start_server.bat` ou
2. Execute diretamente: `python server.py`

### Cliente Electron
1. Na pasta electron-client:
```bash
npm start
```

### Cliente Python
1. Execute:
```bash
python client.py
```

## Portas Utilizadas
- 5000: Servidor TCP
- 6790: WebSocket
- 8000: Servidor Flask

Certifique-se de que estas portas estão disponíveis antes de executar o servidor.

## Solução de Problemas

Se receber mensagens sobre portas em uso:
1. Feche qualquer aplicação que possa estar usando as portas 5000, 6790 ou 8000
2. Use o Task Manager para identificar e fechar processos que possam estar usando essas portas
3. Ou execute no CMD: `netstat -ano | findstr "5000 6790 8000"` para ver quais processos estão usando as portas
