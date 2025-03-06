const { app, BrowserWindow } = require('electron');
const { exec } = require('child_process');
const path = require('path');

let flaskProcess;

function startFlask() {
    const env = Object.assign({}, process.env, { 'PYTHONIOENCODING': 'utf-8' });
    let startScript = path.resolve(__dirname, '..', 'start_server.bat');
    flaskProcess = exec(`"${startScript}"`, { env, cwd: path.resolve(__dirname, '..') }, (error, stdout, stderr) => {
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

    //win.loadURL('http://15.229.12.108:8000'); // Endereço do Flask
    win.loadURL('http://192.168.100.105:8000'); // Endereço do Flask
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
