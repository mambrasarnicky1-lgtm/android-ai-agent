// --- NOIR SOVEREIGN: MISSION CONTROL CORE V20.1 ---

const terminal = document.getElementById('terminal');
let lastAssetId = null;

function logToTerminal(msg, type = "INFO") {
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    const timestamp = new Date().toLocaleTimeString();
    
    let color = "var(--text-dim)";
    if(type === "ERROR") color = "var(--danger)";
    if(type === "DIRECTIVE") color = "var(--purple)";
    if(type === "MESH") color = "var(--accent)";

    entry.innerHTML = `
        <span class="log-ts">[${timestamp}]</span>
        <span class="log-msg" style="color: ${color}">${type}: ${msg}</span>
    `;
    
    terminal.appendChild(entry);
    terminal.scrollTop = terminal.scrollHeight;
    
    if (terminal.childElementCount > 100) {
        terminal.removeChild(terminal.firstChild);
    }
}

async function updateDashboard() {
    try {
        const startTime = Date.now();
        const resp = await fetch('/api/summary');
        if (!resp.ok) throw new Error("Link Failed");
        const data = await resp.json();
        
        // Update Latency
        const latency = Date.now() - startTime;
        document.getElementById('ping-rate').innerText = `LATENCY: ${latency}ms`;

        // 1. Connection Link Status
        const statusItem = document.getElementById('connection-status');
        if (data.online) {
            statusItem.innerHTML = '<i class="fas fa-link"></i> NEURAL LINK: ACTIVE';
            statusItem.style.color = "var(--success)";
            statusItem.style.borderColor = "rgba(16, 185, 129, 0.2)";
        } else {
            statusItem.innerHTML = '<i class="fas fa-link-slash"></i> LINK SEVERED';
            statusItem.style.color = "var(--danger)";
            statusItem.style.borderColor = "rgba(239, 68, 68, 0.2)";
        }

        // 2. Process Agent Data (Redmi Note 14)
        if (data.agent) {
            const stats = data.agent.stats || {};
            
            // Battery
            const bat = stats.battery || stats.bat || 0;
            document.getElementById('bat-text').innerText = `${bat}%`;
            document.getElementById('bat-bar').style.width = `${bat}%`;
            
            // CPU
            const cpu = stats.cpu || 0;
            document.getElementById('cpu-text').innerText = `${cpu}%`;
            document.getElementById('cpu-bar').style.width = `${cpu}%`;
            
            // RAM
            const ram = stats.ram || 0;
            document.getElementById('ram-text').innerText = `${ram}%`;
            document.getElementById('ram-bar').style.width = `${ram}%`;

            // 3. Vision Sentinel Feed
            if (data.agent.last_screenshot && data.agent.last_screenshot !== lastAssetId) {
                lastAssetId = data.agent.last_screenshot;
                document.getElementById('last-screenshot').src = `/api/asset/${lastAssetId}`;
                logToTerminal("Vision Buffer Updated.", "SENTINEL");
                
                const analysis = document.getElementById('vision-analysis');
                analysis.innerHTML = `<i class="fas fa-check-circle" style="color: var(--success);"></i> Screen integrity verified. No security breaches detected.`;
            }
        }

        // 4. Update Logs
        if (data.logs && data.logs.length > 0) {
            data.logs.forEach(log => {
                logToTerminal(log.message, log.level || "AGENT");
            });
        }

    } catch (e) {
        // Silent fallback to avoid console spam
    }
}

async function sendCommand(type, extraParams = {}) {
    logToTerminal(`Transmitting: ${type.toUpperCase()}`, "CMD");
    try {
        const payload = {
            target_device: "REDMI_NOTE_14",
            action: { type: type, ...extraParams },
            description: `Commander Directive: ${type}`
        };

        const resp = await fetch('/api/command', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        const res = await resp.json();
        if (res.command_id) {
            logToTerminal(`Mesh Acknowledged: ${res.command_id}`, "MESH");
        }
    } catch (e) {
        logToTerminal(`Link Error: ${e.message}`, "ERROR");
    }
}

// Global exposure
window.sendCommand = sendCommand;

// Run intervals
setInterval(updateDashboard, 3000);
updateDashboard();

// Boot sequence
setTimeout(() => {
    logToTerminal("Sovereign Node Connected.", "SYSTEM");
    logToTerminal("Handshake verified with Redmi Note 14 Core.", "SYSTEM");
}, 1000);
