const { app, BrowserWindow } = require('electron');
const { exec } = require('child_process');
const path = require('path');

let flaskProcess;

function startFlask() {
    let flaskScript = path.join(__dirname, '..', 'server.py'); // Caminho do Flask
    flaskProcess = exec(`python ${flaskScript}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Erro ao iniciar o Flask: ${error.message}`);
            return;
        }
        console.log(stdout);
        console.error(stderr);
    });
}

function createWindow() {
    let win = new BrowserWindow({
        width: 1000,
        height: 700,
        webPreferences: {
            nodeIntegration: true
        }
    });

    win.loadURL('http://127.0.0.1:8000'); // Endereço do Flask
}

app.whenReady().then(() => {
    startFlask();
    // Aguarda um pouco para o servidor Flask iniciar
    setTimeout(createWindow, 1000);
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        if (flaskProcess) {
            flaskProcess.kill();
        }
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
