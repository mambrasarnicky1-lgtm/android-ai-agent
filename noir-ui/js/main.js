// ════════════════════════════════════════════════════
// NOIR SOVEREIGN — MISSION CONTROL JS v21.0 AEGIS
// ════════════════════════════════════════════════════

const API_KEY = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026";
const VPS = ""; // Relative — served from same origin
const HEADERS = { "Authorization": `Bearer ${API_KEY}`, "Content-Type": "application/json" };

let allLogs = [];
let logVisible = true;
let bypassActive = false;
let mediaMode = 'screenshots';
let mediaItems = [];
let pendingEvoCount = 0;

// ── SPA Navigation ──────────────────────────────────
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        
        btn.classList.add('active');
        const panelId = `panel-${btn.dataset.panel}`;
        const panel = document.getElementById(panelId);
        if (panel) panel.classList.add('active');
        
        document.getElementById('panel-title').innerText = btn.title.toUpperCase();
        
        // Specific panel init
        if (btn.dataset.panel === 'media') refreshMedia();
        if (btn.dataset.panel === 'evolution') renderEvolutions();
        
        // Clear badge
        const badge = document.getElementById(`${btn.dataset.panel.replace('evolution','evo').replace('media','media')}-badge`);
        if (badge) { badge.style.display = 'none'; badge.innerText = '0'; }
    });
});

// ── Bypass Control ──────────────────────────────────
document.getElementById('bypass-btn').onclick = () => {
    bypassActive = true;
    document.getElementById('reconnect-ui').style.display = 'none';
    addLog('SYSTEM', 'Neural Hub access authorized via manual bypass.');
};

// ── System Clock ────────────────────────────────────
setInterval(() => {
    document.getElementById('sys-time').innerText = new Date().toLocaleTimeString();
}, 1000);

// ── Main Polling Loop ────────────────────────────────
let lastScreenshot = null;

async function pollDashboard() {
    try {
        const pingStart = Date.now();
        const r = await fetch(`${VPS}/api/summary`, { headers: HEADERS });
        const ping = Date.now() - pingStart;
        
        if (!r.ok) throw new Error("API Error");
        const data = await r.json();

        updateConnection(data.online, ping);
        
        if (data.agent) {
            updateTelemetry(data.agent.stats || {}, data.agent);
        }
        
        if (data.logs?.length) {
            ingestLogs(data.logs);
        }
        
        checkEvolutions(data.commands || []);

    } catch(e) {
        updateConnection(false, 999);
    }
}

function updateConnection(online, ping) {
    const chip = document.getElementById('connection-status');
    const recon = document.getElementById('reconnect-ui');
    
    if (online) {
        chip.className = 'status-chip online';
        chip.innerHTML = '<div class="pulse-dot"></div> NEURAL LINK: ACTIVE';
        recon.style.display = 'none';
    } else {
        chip.className = 'status-chip offline';
        chip.innerHTML = '<div class="pulse-dot"></div> LINK SEVERED';
        if (!bypassActive) {
            recon.style.display = 'flex';
        }
    }
    
    document.getElementById('ping-val').innerText = `${ping}ms`;
}

function updateTelemetry(stats, agent) {
    const set = (id, val, unit='%') => {
        const el = document.getElementById(id);
        if (el) el.innerText = val != null ? `${val}${unit}` : '--';
    };
    const bar = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.style.width = `${Math.min(val||0, 100)}%`;
    };

    set('bat-val', stats.bat || stats.battery);
    bar('bat-bar', stats.bat || stats.battery);
    set('cpu-val', stats.cpu);
    bar('cpu-bar', stats.cpu);
    set('ram-val', stats.ram);
    bar('ram-bar', stats.ram);

    const shizuku = stats.shizuku || 'N/A';
    document.getElementById('shizuku-chip').innerText = `SHIZUKU: ${shizuku}`;

    if (agent.last_screenshot && agent.last_screenshot !== lastScreenshot) {
        lastScreenshot = agent.last_screenshot;
        const img = document.getElementById('vision-img');
        img.src = `/api/asset/${lastScreenshot}`;
        img.style.opacity = 1;
        document.getElementById('vision-status').innerText = 'LIVE FEED';
        document.getElementById('vision-time').innerText = new Date().toLocaleTimeString();
        addMediaItem({ type: 'screenshot', key: lastScreenshot, ts: Date.now() });
    }
}

// ── Log System ───────────────────────────────────────
function ingestLogs(logs) {
    logs.forEach(log => {
        allLogs.push({ ts: new Date().toLocaleTimeString(), level: log.level || 'INFO', msg: log.message || '' });
    });
    if (allLogs.length > 500) allLogs = allLogs.slice(-500);
    renderLogs();
}

function addLog(level, msg) {
    allLogs.push({ ts: new Date().toLocaleTimeString(), level, msg });
    renderLogs();
}

function renderLogs() {
    const console_ = document.getElementById('log-console');
    const filter = document.getElementById('log-filter').value;
    
    const filtered = filter === 'all' ? allLogs : allLogs.filter(l => l.level === filter);
    
    console_.innerHTML = filtered.map(l => 
        `<div class="log-entry">
            <span class="log-ts">[${l.ts}]</span>
            <span class="log-lvl-${l.level}">${l.level}:</span>
            <span class="log-msg">${l.msg}</span>
        </div>`
    ).join('');
    console_.scrollTop = console_.scrollHeight;
}

function filterLogs() { renderLogs(); }
function clearLogs() { allLogs = []; renderLogs(); }

function toggleLogVisibility() {
    logVisible = !logVisible;
    const btn = document.getElementById('log-toggle-btn');
    btn.innerText = logVisible ? 'LOG: VISIBLE' : 'LOG: HIDDEN';
    btn.style.color = logVisible ? '' : 'var(--danger)';
    sendCmd('log_visibility', { visible: logVisible });
}

// ── Command Routing ───────────────────────────────────
async function sendCmd(type, extra = {}) {
    addLog('CMD', `Executing neural command: ${type.toUpperCase()}`);
    try {
        const r = await fetch(`${VPS}/api/command`, {
            method: 'POST',
            headers: HEADERS,
            body: JSON.stringify({
                target_device: 'REDMI_NOTE_14',
                action: { type, ...extra },
                description: `Dashboard manually triggered ${type}`
            })
        });
        const res = await r.json();
        addLog('SYSTEM', `Command queued: ${res.command_id || 'OK'}`);
    } catch(e) {
        addLog('ERROR', `Command failure: ${e.message}`);
    }
}

async function sendShell() {
    const cmd = document.getElementById('shell-input').value;
    if (!cmd) return;
    await sendCmd('shell', { cmd });
    document.getElementById('shell-input').value = '';
}

// ── AI Chat ──────────────────────────────────────────
async function sendChatMsg() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';

    addChatBubble('user', msg);
    
    const typingId = 'typing-' + Date.now();
    addChatBubble('ai', 'Thinking...', typingId);

    try {
        const r = await fetch(`${VPS}/api/brain/chat`, {
            method: 'POST',
            headers: HEADERS,
            body: JSON.stringify({ message: msg, device_id: 'REDMI_NOTE_14' })
        });
        const data = await r.json();
        document.getElementById(typingId).remove();
        addChatBubble('ai', data.response || 'Neural network timed out.');
    } catch(e) {
        document.getElementById(typingId).remove();
        addChatBubble('ai', 'Error: VPS link failed.');
    }
}

function addChatBubble(role, text, id = null) {
    const win = document.getElementById('chat-window');
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    if (id) div.id = id;
    div.innerHTML = `<div class="chat-bubble">${text}</div>`;
    win.appendChild(div);
    win.scrollTop = win.scrollHeight;
}

// ── Media Vault ───────────────────────────────────────
function addMediaItem(item) {
    mediaItems.unshift(item);
    const badge = document.getElementById('media-badge');
    badge.style.display = 'grid';
    badge.innerText = (parseInt(badge.innerText)||0) + 1;
}

function switchMediaTab(btn, mode) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    mediaMode = mode;
    renderMedia();
}

async function refreshMedia() {
    // In a real system, this would fetch from /api/assets
    renderMedia();
}

function renderMedia() {
    const grid = document.getElementById('media-grid');
    const filtered = mediaItems.filter(m => {
        if (mediaMode === 'screenshots') return m.type === 'screenshot';
        if (mediaMode === 'audio') return m.type === 'audio';
        return true;
    });
    
    if (!filtered.length) {
        grid.innerHTML = '<p style="grid-column:1/-1; text-align:center; padding:2rem; opacity:0.5;">No items found in vault.</p>';
        return;
    }

    grid.innerHTML = filtered.map(m => `
        <div class="media-item">
            <img src="/api/asset/${m.key}" alt="Loot">
            <div class="media-item-meta">${m.key.substring(0,12)}...</div>
        </div>
    `).join('');
}

// ── Evolution Engine ──────────────────────────────────
let evoProposals = [
    { id: 'EVO-01', title: 'Neural Stealth V2', body: 'AI suggests hiding process names from HyperOS battery monitor.' },
    { id: 'EVO-02', title: 'Adaptive Polling', body: 'Agent detected low battery; proposing to increase polling interval to 120s.' }
];

function checkEvolutions(cmds) {
    // Mock logic: check if any commands are "evolution" types
}

function renderEvolutions() {
    const list = document.getElementById('evo-list');
    list.innerHTML = evoProposals.map(p => `
        <div class="card" style="border-left:4px solid var(--accent-purple);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem;">
                <h4 style="color:var(--accent-purple); font-size:0.9rem;">${p.title}</h4>
                <span class="status-chip neutral" style="font-size:0.6rem;">PENDING</span>
            </div>
            <p style="font-size:0.8rem; margin-bottom:1.5rem; opacity:0.8;">${p.body}</p>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary" style="background:var(--success); color:#000; font-size:0.65rem;">APPROVE & DEPLOY</button>
                <button class="btn-primary" style="background:transparent; border:1px solid var(--danger); color:var(--danger); font-size:0.65rem;">REJECT</button>
            </div>
        </div>
    `).join('');
}

// ── Initialize ────────────────────────────────────────
pollDashboard();
setInterval(pollDashboard, 5000);
addLog('SYSTEM', 'Noir Sovereign Mission Control V21.0 AEGIS initialized.');
