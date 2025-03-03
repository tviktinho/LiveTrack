# **LiveTrack - Sistema de Compartilhamento de Localização em Tempo Real**

## **Visão Geral**
O **LiveTrack** é um sistema distribuído projetado para permitir que um grupo de amigos compartilhe sua localização em tempo real via GPS e visualize as posições no mapa.

A aplicação consiste em um **servidor Flask**, um **cliente Electron** e utiliza **WebSockets e REST API** para comunicação entre as máquinas.

## **Funcionalidades**
✅ **Captura de Localização**: Usuários compartilham sua localização periodicamente.
✅ **Exibição em Tempo Real**: Mapa interativo mostra as localizações dos amigos.
✅ **Conexão via WebSockets e HTTP**: Suporte para comunicação em tempo real.
✅ **Grupos Privados**: Usuários podem compartilhar localização apenas com amigos.
✅ **Suporte para Várias Máquinas**: Cliente pode rodar em qualquer dispositivo na rede.

## **Tecnologias Utilizadas**
- **Backend:** Flask (Python)
- **Frontend:** Electron (JavaScript)
- **Mapa:** OpenLayers ou Leaflet.js
- **Comunicação em Tempo Real:** WebSockets (Socket.io) e HTTP
- **Banco de Dados (futuro):** Firebase ou Redis

## **Instalação e Execução**

### **1. Clonar o repositório**
```sh
git clone https://github.com/seu-usuario/LiveTrack.git
cd LiveTrack
```

### **2. Configurar o Servidor Flask**
#### **Instalar dependências**
```sh
cd flask-server
pip install -r requirements.txt
```

#### **Executar o Servidor Flask**
```sh
python app.py
```
O servidor iniciará em `http://127.0.0.1:5000`.

### **3. Configurar o Cliente Electron**
#### **Instalar dependências**
```sh
cd ../electron-client
npm install
```

#### **Iniciar a Aplicação**
```sh
npm start
```
A interface Electron abrirá mostrando o mapa e os controles.

## **Como Usar**
1. **Abrir a interface Electron**
2. **Clicar em "Compartilhar Localização"** para enviar sua localização ao servidor.
3. **Visualizar o mapa** atualizado em tempo real.

## **Próximos Passos**
📌 **Salvar localizações no Firebase ou Redis** para persistência.
📌 **Criar grupos privados** para compartilhamento entre amigos.
📌 **Adicionar autenticação de usuários**.
📌 **Implementar versão mobile** para Android e iOS.

## **Contribuição**
Se deseja contribuir com o projeto, sinta-se à vontade para abrir um Pull Request ou relatar issues.

## **Licença**
Este projeto está sob a licença MIT.

---

🔗 **Desenvolvido por [Seu Nome]**

