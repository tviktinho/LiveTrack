
# 🚀 GPS Live Tracker

Sistema distribuído para rastreamento de usuários em tempo real usando **Python**, **Electron** e **NATS**.

---

## 📦 Requisitos
- Python 3.x
- Node.js + npm
- NATS Server instalado

---

## 📁 Estrutura do Projeto

```
Live Tracker/
├── server.py               # Servidor Flask + NATS
├── client.py               # Cliente Python (envio de localização)
├── start_server.bat        # Script para iniciar servidor Flask
├── start_nats.bat          # Script para iniciar somente NATS
├── templates/              # Templates HTML
│   ├── manifest.json
│   └── map.html
└── electron-client/        # Cliente Desktop Electron
    ├── index.js
    ├── package.json
    └── package-lock.json
```

---

## ⚙️ Instalação

### Dependências Python
```bash
pip install flask flask-cors requests nats-py
```

### Dependências Node.js
```bash
cd electron-client
npm install
```

### NATS Server
- Download: [NATS Downloads](https://docs.nats.io/running-a-nats-service/introduction/installation)

---

## 🏃‍♂️ Como Executar

### 1. Iniciar NATS Server
```bash
start_nats.bat
```


### 2. Iniciar Servidor Flask
```bash
start_server.bat
```
ou manualmente:
```bash
python server.py
```

### 3. Iniciar Cliente Electron
```bash
cd electron-client
npm start
```

### 4. Executar Cliente Python (opcional)
```bash
python client.py SeuNomeDeUsuario
```

---

## 🌐 Portas Utilizadas

| Serviço | Porta | Observações |
|:--------|:------|:------------|
| NATS Server (TCP) | 4222 | Comunicação com clientes Python |
| NATS WebSocket | 9222 | Comunicação com navegador (map.html) |
| Flask | 8000 | Servir o frontend |
| NATS Monitoramento | 8222 | Painel de administração NATS |

---

## ❓ Solução de Problemas

- **Verificar portas ocupadas**
```bash
netstat -ano | findstr "4222 9222 8000"
```

- **Matar processos travados**
```bash
taskkill /PID <número do processo> /F
```

- **Avisos de Segurança Electron**
  - São normais em ambiente de desenvolvimento.
  - Serão removidos ao empacotar a aplicação.

