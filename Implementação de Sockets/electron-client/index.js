const { app, BrowserWindow, ipcMain } = require('electron');
const { exec } = require('child_process');
const path = require('path');

let flaskProcess;
let clientProcess;
let userName = '';

function startFlask() {
    console.log("[DEBUG] Iniciando Flask...");
    const env = Object.assign({}, process.env, { 'PYTHONIOENCODING': 'utf-8' });
    let startScript = path.resolve(__dirname, '..', 'start_server.bat');
    flaskProcess = exec(`"${startScript}"`, { env, cwd: path.resolve(__dirname, '..') }, (error, stdout, stderr) => {
        if (error) {
            console.error("[ERRO] Falha ao iniciar o Flask:", error.message);
            return;
        }
        console.log("[FLASK] Saída:", stdout);
        console.error("[FLASK] Erros:", stderr);
    });
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
                contextIsolation: false // Permite o uso do ipcRenderer diretamente
            }
        });

        // Registrar o evento antes da criação da janela
        ipcMain.once('set-user-name', (_, name) => {
            console.log(`[DEBUG] Nome recebido: ${name}`);
            userName = name.trim() || "Usuário"; // Nome padrão se vazio
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
                        event.preventDefault(); // Impede o recarregamento da janela
                        const name = document.getElementById('userName').value.trim();
                        console.log("[DEBUG] Nome digitado:", name);
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
    console.log("[DEBUG] Criando janela principal...");
    userName = await askUserName();
    console.log(`[DEBUG] Nome definido: ${userName}`);
    startClient(userName);

    let win = new BrowserWindow({
        width: 1000,
        height: 700,
        webPreferences: {
            nodeIntegration: true
        }
    });

    console.log("[DEBUG] Carregando pagina Flask...");
    win.loadURL('http://192.168.1.103:8000');
}

app.whenReady().then(() => {
    console.log("[DEBUG] Aplicacao Electron iniciada.");
    startFlask();
    setTimeout(createWindow, 1000);
});

app.on('window-all-closed', () => {
    console.log("[DEBUG] Fechando aplicacao...");
    if (process.platform !== 'darwin') {
        if (flaskProcess) {
            console.log("[DEBUG] Finalizando Flask...");
            flaskProcess.kill();
        }
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
