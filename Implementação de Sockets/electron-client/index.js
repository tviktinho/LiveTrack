const { app, BrowserWindow } = require('electron');
const { exec } = require('child_process');
const path = require('path');

let flaskProcess;

function startFlask() {
    let flaskScript = path.join(__dirname, '..', 'flask-server', 'app.py'); // Caminho do Flask
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

    win.loadURL('http://192.168.100.105:8000'); // Endereço do Flask
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
