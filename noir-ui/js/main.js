const API_URL = ""; // Relative to server
const terminal = document.getElementById('terminal');

function logToTerminal(msg, type="INFO") {
    const line = document.createElement('div');
    line.className = 'terminal-line';
    line.textContent = `[${new Date().toLocaleTimeString()}] [${type}] ${msg}`;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

// --- Chart Initialization ---
const ctxActivity = document.getElementById('activityChart').getContext('2d');
const activityChart = new Chart(ctxActivity, {
    type: 'line',
    data: {
        labels: Array(10).fill(''),
        datasets: [{
            label: 'Activity',
            data: Array(10).fill(0),
            borderColor: '#9d50bb',
            backgroundColor: 'rgba(157, 80, 187, 0.2)',
            fill: true,
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { display: false } }
    }
});

const ctxLatency = document.getElementById('latencyChart').getContext('2d');
const latencyChart = new Chart(ctxLatency, {
    type: 'bar',
    data: {
        labels: Array(10).fill(''),
        datasets: [{
            label: 'Latency',
            data: Array(10).fill(0),
            backgroundColor: '#00d2ff',
            borderRadius: 5
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { display: false } }
    }
});

async function updateDashboard() {
    try {
        const resp = await fetch('/api/summary');
        const data = await resp.json();
        
        // Update Connection Status
        const status = document.getElementById('connection-status');
        if (data.online) {
            status.className = 'status-pill status-online';
            status.innerHTML = '<div class="pulse"></div> LINK ACTIVE';
        } else {
            status.className = 'status-pill status-offline';
            status.innerHTML = 'LINK SEVERED';
        }

        // Update Charts
        activityChart.data.datasets[0].data.shift();
        activityChart.data.datasets[0].data.push(Math.random() * 100); // Dummy for now
        activityChart.update();

        latencyChart.data.datasets[0].data.shift();
        latencyChart.data.datasets[0].data.push(Math.random() * 500); // Dummy for now
        latencyChart.update();

        // Update Mobile Stats
        if (data.agent) {
            const stats = data.agent.stats || {};
            document.getElementById('mobile-stats').innerHTML = `
                <p style="font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem;">${stats.battery || '--'}% <span style="font-size: 1rem; color: var(--text-secondary);">BATTERY</span></p>
                <p style="color: var(--success); font-size: 0.9rem;">+ NEURAL PERSISTENCE ACTIVE</p>
            `;
            
            if (data.agent.last_screenshot) {
                document.getElementById('last-screenshot').src = `/api/asset/${data.agent.last_screenshot}`;
            }
        }

        // Refresh Logs
        if (data.commands) {
            // Only add new lines (simplified for now)
        }
    } catch (e) {
        logToTerminal("Dashboard Update Failed", "ERROR");
    }
}

async function sendCommand(type) {
    logToTerminal(`Issuing command: ${type.toUpperCase()}`);
    try {
        const resp = await fetch('/api/command', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action: {type: type}, description: `Web Command: ${type}`})
        });
        const res = await resp.json();
        logToTerminal(`Command queued: ${res.command_id}`);
    } catch (e) {
        logToTerminal(`Command failed: ${e.message}`, "ERROR");
    }
}

async function sendPCCommand() {
    const cmd = document.getElementById('pc-command').value;
    if (!cmd) return;
    
    logToTerminal(`PC BRIDGE: ${cmd}`);
    try {
        const resp = await fetch('/api/command', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                target_device: "NOIR_PC_MASTER",
                action: {type: "pc_shell", cmd: cmd},
                description: `PC Remote Shell: ${cmd}`
            })
        });
        const res = await resp.json();
        logToTerminal(`PC Command Status: ${res.status}`);
    } catch (e) {
        logToTerminal(`PC Bridge Error: ${e.message}`, "ERROR");
    }
}

// Initial update and periodic refresh
setInterval(updateDashboard, 5000);
updateDashboard();
logToTerminal("NOIR SOVEREIGN ELITE CORE INITIALIZED.");
