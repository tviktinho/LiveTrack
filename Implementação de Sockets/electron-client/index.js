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

    win.loadURL('http://192.168.100.105:8000'); // Endereço do Flask

    // Add event listeners for marking points and user clicks
    win.webContents.on('did-finish-load', () => {
        win.webContents.executeJavaScript(`
            document.getElementById('markPointButton').addEventListener('click', () => {
                const lat = prompt("Enter latitude:");
                const lon = prompt("Enter longitude:");
                if (lat && lon) {
                    fetch('/mark_point', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ lat, lon })
                    });
                }
            });

            const userList = document.getElementById('userList');
            userList.addEventListener('click', (event) => {
                const userId = event.target.dataset.userId;
                if (userId) {
                    // Logic to zoom in on the user's location on the map
                    const userLocation = getUserLocation(userId); // Implement this function to get the user's location
                    if (userLocation) {
                        map.setView(userLocation, 15); // Zoom level 15
                    }
                }
            });
        `);
    });
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
