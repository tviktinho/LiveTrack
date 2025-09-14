const { app, BrowserWindow, ipcMain } = require('electron');
const { exec } = require('child_process');
const path = require('path');
const { connect } = require('nats');

let clientProcess;
let userName = '';

async function setupNats() {
    try {
        const nc = await connect({ servers: "nats://35.238.213.13:4222" });
        console.log("[NATS] Conectado ao servidor NATS.");

        const sub = nc.subscribe("locations");
        (async () => {
            for await (const msg of sub) {
                const data = JSON.parse(msg.data);
                console.log(`[NATS] ${data.username}: ${data.lat}, ${data.lon}`);
            }
        })();
    } catch (error) {
        console.error("[ERRO] Falha ao conectar ao NATS:", error);
    }
}

function startClient(userName) {
    console.log(`[DEBUG] Iniciando client.py com nome: ${userName}`);
    const clientScript = path.resolve(__dirname, '..', 'client.py');

    clientProcess = exec(`python "${clientScript}" "${userName}"`, (error, stdout, stderr) => {
        if (error) {
            console.error("[ERRO] Falha ao iniciar o cliente:", error.message);
            return;
        }
        console.log("[CLIENTE] Saída:", stdout);
        console.error("[CLIENTE] Erros:", stderr);
    });
}

function askUserName() {
    return new Promise((resolve) => {
        console.log("[DEBUG] Abrindo janela para inserir nome...");

        const inputWindow = new BrowserWindow({
            width: 400,
            height: 200,
            modal: true,
            frame: false,
            alwaysOnTop: true,
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false
            }
        });

        ipcMain.once('set-user-name', (_, name) => {
            console.log(`[DEBUG] Nome recebido: ${name}`);
            userName = name.trim() || "Usuário";
            inputWindow.close();
            resolve(userName);
        });

        inputWindow.loadURL(`data:text/html,
            <body style="text-align:center;font-family:sans-serif;padding:20px;">
                <h3>Digite seu nome:</h3>
                <form id="nameForm">
                    <input type="text" id="userName" style="padding:10px;width:80%;" required />
                    <button type="submit" id="submit" style="margin-top:10px;padding:10px;">Confirmar</button>
                </form>
                <script>
                    const { ipcRenderer } = require('electron');
                    document.getElementById('nameForm').addEventListener('submit', (event) => {
                        event.preventDefault();
                        const name = document.getElementById('userName').value.trim();
                        if (name) {
                            ipcRenderer.send('set-user-name', name);
                        } else {
                            alert("Por favor, insira um nome.");
                        }
                    });
                </script>
            </body>`);
    });
}

async function createWindow() {
    await setupNats();
    userName = await askUserName();
    startClient(userName);

    let win = new BrowserWindow({
        width: 1000,
        height: 700,
        webPreferences: {
            nodeIntegration: true
        }
    });

    //win.loadURL('http://192.168.1.100:8000');
    win.loadURL('http://35.238.213.13:8000');


}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    console.log("[DEBUG] Fechando aplicação...");
    if (process.platform !== 'darwin') {
        if (clientProcess) {
            console.log("[DEBUG] Finalizando cliente...");
            clientProcess.kill();
        }
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
