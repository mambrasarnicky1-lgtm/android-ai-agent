// ════════════════════════════════════════════════════
// NOIR SOVEREIGN — MISSION CONTROL JS v21.0 AEGIS
// ════════════════════════════════════════════════════

const API_KEY = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026";
const VPS = ""; // Relative — served from same origin
const HEADERS = { "Authorization": `Bearer ${API_KEY}`, "Content-Type": "application/json" };

let allLogs = [];
let logVisible = true;
let mediaMode = 'screenshots';
let allMediaItems = [];
let pendingEvoCount = 0;

// ── SPA Navigation ──────────────────────────────────
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        const panel = document.getElementById(`panel-${btn.dataset.panel}`);
        if (panel) panel.classList.add('active');
        document.getElementById('panel-title').innerText = btn.title.toUpperCase();
        if (btn.dataset.panel === 'media') refreshMedia();
        if (btn.dataset.panel === 'evolution') renderEvolutions();
        if (btn.dataset.panel === 'logs') renderLogs();
        // Clear badge
        const badge = document.getElementById(`${btn.dataset.panel.replace('evolution','evo').replace('logs','')}-badge`);
        if (badge) { badge.style.display = 'none'; badge.innerText = '0'; }
    });
});

// ── System Clock ────────────────────────────────────
setInterval(() => {
    document.getElementById('sys-time').innerText = new Date().toLocaleTimeString();
}, 1000);

// ── Neural Chart ────────────────────────────────────
const neuralCtx = document.getElementById('neural-chart')?.getContext('2d');
let neuralChart;
if (neuralCtx) {
    neuralChart = new Chart(neuralCtx, {
        type: 'line',
        data: {
            labels: Array(12).fill(''),
            datasets: [{ data: Array(12).fill(0), borderColor: '#00f2ff', borderWidth: 2, fill: true, tension: 0.4, backgroundColor: 'rgba(0,242,255,.07)', pointRadius: 0 }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { x: { display: false }, y: { display: false } }
        }
    });
}

// ── Main Polling Loop ────────────────────────────────
let lastScreenshot = null;
let pingStart = 0;

async function pollDashboard() {
    try {
        pingStart = Date.now();
        const r = await fetch(`${VPS}/api/summary`, { headers: HEADERS });
        const ping = Date.now() - pingStart;
        if (!r.ok) throw new Error("API Error");
        const data = await r.json();

        updateConnection(data.online, ping);
        if (data.agent) updateTelemetry(data.agent.stats || {}, data.agent);
        if (data.logs?.length) ingestLogs(data.logs);
        checkEvolutions(data.commands || []);

    } catch(e) {
        updateConnection(false, 999);
    }
}

function updateConnection(online, ping) {
    const chip = document.getElementById('connection-status');
    const dot = document.getElementById('agent-dot');
    if (online) {
        chip.className = 'status-chip online';
        chip.innerHTML = '<div class="pulse-dot"></div> NEURAL LINK: ACTIVE';
        dot.className = 'status-dot online';
        document.getElementById('hs-status').innerText = 'STABLE';
        document.getElementById('hs-status').className = 'tag-success';
    } else {
        chip.className = 'status-chip offline';
        chip.innerHTML = '<div class="pulse-dot"></div> LINK SEVERED';
        dot.className = 'status-dot offline';
        document.getElementById('hs-status').innerText = 'SEARCHING...';
        document.getElementById('hs-status').className = '';
    }
    document.getElementById('ping-val').innerText = `${ping}ms`;
    document.getElementById('ping-bar').style.width = `${Math.min(ping / 5, 100)}%`;
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

    // Shizuku chip
    const shizuku = stats.shizuku || 'N/A';
    const sz = document.getElementById('shizuku-chip');
    sz.innerHTML = `<i class="fas fa-shield-cat"></i> ${shizuku}`;
    sz.className = shizuku === 'AUTHORIZED' ? 'status-chip online' : 'status-chip neutral';

    // Version chip
    if (stats.version) {
        document.getElementById('agent-ver-chip').innerHTML = `<i class="fas fa-code-branch"></i> ${stats.version}`;
    }

    // Vision Feed
    if (agent.last_screenshot && agent.last_screenshot !== lastScreenshot) {
        lastScreenshot = agent.last_screenshot;
        document.getElementById('vision-img').src = `/api/asset/${lastScreenshot}`;
        document.getElementById('vision-time').innerText = new Date().toLocaleTimeString();
        document.getElementById('vision-status').innerText = 'LIVE FEED';
        addMediaItem({ type: 'screenshot', key: lastScreenshot, ts: Date.now() });
    }

    // Neural chart update
    if (neuralChart) {
        neuralChart.data.datasets[0].data.shift();
        neuralChart.data.datasets[0].data.push(stats.ram || Math.random() * 60 + 20);
        neuralChart.update('none');
    }
}

// ── Log System ───────────────────────────────────────
function ingestLogs(logs) {
    logs.forEach(log => {
        allLogs.push({ ts: new Date().toLocaleTimeString(), level: log.level || 'INFO', msg: log.message || '' });
    });
    if (allLogs.length > 500) allLogs = allLogs.slice(-500);
    if (document.getElementById('panel-logs').classList.contains('active')) renderLogs();
}

function addLog(level, msg) {
    allLogs.push({ ts: new Date().toLocaleTimeString(), level, msg });
    if (document.getElementById('panel-logs').classList.contains('active')) renderLogs();
    // Show badge if not on log panel
    const btn = document.querySelector('[data-panel="logs"]');
    if (!btn?.classList.contains('active') && ['ERROR','WARNING'].includes(level)) {
        const badge = document.getElementById('chat-badge'); // reuse logic
    }
}

function renderLogs() {
    const console_ = document.getElementById('log-console');
    const filter = document.getElementById('log-filter')?.value || 'all';
    const visible = logVisible;
    if (!visible && !logVisible) { console_.innerHTML = '<div style="text-align:center;color:var(--text-dim);padding:2rem;">LOGS HIDDEN — Dashboard Hidden Mode Active</div>'; return; }
    
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
    btn.style.background = logVisible ? '' : 'rgba(239,68,68,.15)';
    btn.style.color = logVisible ? '' : 'var(--danger)';
    btn.style.borderColor = logVisible ? '' : 'var(--danger)';
    addLog('SYSTEM', `Log visibility toggled: ${logVisible ? 'VISIBLE' : 'HIDDEN'}`);
    // Notify APK to suppress logs from being visible in UI
    sendCmd('log_visibility', { visible: logVisible });
}

// ── Command Routing ───────────────────────────────────
async function sendCmd(type, extra = {}) {
    addLog('CMD', `Issuing: ${type.toUpperCase()}`);
    try {
        const r = await fetch(`${VPS}/api/command`, {
            method: 'POST',
            headers: HEADERS,
            body: JSON.stringify({
                target_device: 'REDMI_NOTE_14',
                action: { type, ...extra },
                description: `Dashboard → ${type}`
            })
        });
        const res = await r.json();
        addLog('MESH', `Queued: ${(res.command_id||'').substring(0,8)}`);
        return res;
    } catch(e) {
        addLog('ERROR', `Command failed: ${e.message}`);
    }
}

async function sendShell() {
    const input = document.getElementById('shell-input');
    const cmd = input.value.trim();
    if (!cmd) return;
    input.value = '';
    addLog('CMD', `SHELL: ${cmd}`);
    await sendCmd('shell', { cmd });
}

// ── AI Chat ──────────────────────────────────────────
async function sendChatMsg() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';

    addChatBubble('user', msg);

    // Show typing indicator
    const typingId = 'typing-' + Date.now();
    addChatBubble('ai', '<i class="fas fa-ellipsis" style="animation:pls 1s infinite"></i>', typingId);

    try {
        const r = await fetch(`${VPS}/api/brain/chat`, {
            method: 'POST',
            headers: HEADERS,
            body: JSON.stringify({ message: msg, device_id: 'REDMI_NOTE_14' })
        });
        const data = await r.json();
        document.getElementById(typingId)?.remove();
        addChatBubble('ai', data.response || 'No response from Neural Brain.');

        if (data.autonomous_action) {
            addLog('AI', `Autonomous action triggered: ${data.autonomous_action.type}`);
        }
    } catch(e) {
        document.getElementById(typingId)?.remove();
        addChatBubble('ai', 'Neural Brain offline. Check VPS connection.');
        addLog('ERROR', `Chat relay failed: ${e.message}`);
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
    // Badge notification if not on chat panel
    if (!document.querySelector('[data-panel="chat"]')?.classList.contains('active') && role === 'ai') {
        const badge = document.getElementById('chat-badge');
        if (badge) { badge.style.display = 'grid'; badge.innerText = (parseInt(badge.innerText)||0) + 1; }
    }
}

document.getElementById('chat-input')?.addEventListener('keydown', e => { if (e.key === 'Enter') sendChatMsg(); });

// ── Media Vault ───────────────────────────────────────
let mediaItems = [];

function addMediaItem(item) {
    mediaItems.unshift(item);
    const badge = document.getElementById('media-badge');
    if (badge && !document.querySelector('[data-panel="media"]')?.classList.contains('active')) {
        badge.style.display = 'grid';
        badge.innerText = (parseInt(badge.innerText)||0) + 1;
    }
}

function switchMediaTab(btn, mode) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    mediaMode = mode;
    renderMedia();
}

async function refreshMedia() {
    try {
        const r = await fetch(`${VPS}/api/assets`, { headers: HEADERS });
        const assets = await r.json();
        assets.forEach(a => {
            if (!mediaItems.find(m => m.key === a.key)) {
                const type = a.key.endsWith('.mp3') || a.key.endsWith('.m4a') ? 'audio' : 'screenshot';
                mediaItems.unshift({ type, key: a.key, ts: new Date(a.uploaded).getTime() });
            }
        });
        renderMedia();
    } catch(e) {
        addLog('ERROR', `Media refresh failed: ${e.message}`);
    }
}

function renderMedia() {
    const grid = document.getElementById('media-grid');
    const filtered = mediaItems.filter(m => {
        if (mediaMode === 'screenshots') return m.type === 'screenshot';
        if (mediaMode === 'audio') return m.type === 'audio';
        return true;
    });

    if (!filtered.length) {
        grid.innerHTML = '<div class="media-empty"><i class="fas fa-photo-film"></i><p>No media in vault yet.<br>Use Capture or Sync Gallery controls.</p></div>';
        return;
    }

    grid.innerHTML = filtered.map(m => {
        const date = new Date(m.ts).toLocaleString();
        if (m.type === 'audio') {
            return `<div class="audio-item" onclick="openAudio('${m.key}')">
                <i class="fas fa-music"></i>
                <div>
                    <div style="font-weight:700;font-size:.8rem;">${m.key}</div>
                    <div style="font-size:.68rem;color:var(--text-dim);">${date}</div>
                </div>
            </div>`;
        }
        return `<div class="media-item" onclick="openImage('/api/asset/${m.key}')">
            <img src="/api/asset/${m.key}" alt="Screenshot" onerror="this.src='https://via.placeholder.com/400x250/06060a/00f2ff?text=LOADING...'">
            <div class="media-item-meta"><span>${m.key.substring(0,14)}...</span><br>${date}</div>
        </div>`;
    }).join('');
}

function openImage(src) {
    const lb = document.getElementById('lightbox');
    const img = document.getElementById('lightbox-img');
    const audio = document.getElementById('lightbox-audio');
    audio.style.display = 'none';
    img.style.display = 'block';
    img.src = src;
    lb.classList.remove('hidden');
}

function openAudio(key) {
    const lb = document.getElementById('lightbox');
    const img = document.getElementById('lightbox-img');
    const audio = document.getElementById('lightbox-audio');
    img.style.display = 'none';
    audio.style.display = 'block';
    audio.src = `/api/asset/${key}`;
    audio.play();
    lb.classList.remove('hidden');
}

function closeLightbox() {
    document.getElementById('lightbox').classList.add('hidden');
    document.getElementById('lightbox-audio').pause();
}

// ── Evolution Proposals ───────────────────────────────
let evoProposals = [];

function checkEvolutions(commands) {
    const evo = commands.filter(c => c.description?.includes('Evolution') && c.status === 'pending');
    if (evo.length > pendingEvoCount) {
        pendingEvoCount = evo.length;
        evo.forEach(e => {
            if (!evoProposals.find(p => p.id === e.id)) {
                evoProposals.unshift({ id: e.id, title: e.description, body: 'AI Agent telah menganalisis pola operasional dan mengajukan evolusi sistem berikut untuk persetujuan Anda.', ts: e.updated_at });
            }
        });
        // Show badge
        const badge = document.getElementById('evo-badge');
        if (badge && !document.querySelector('[data-panel="evolution"]')?.classList.contains('active')) {
            badge.style.display = 'grid';
            badge.innerText = pendingEvoCount;
        }
        renderEvolutions();
    }
}

function renderEvolutions() {
    const list = document.getElementById('evo-list');
    if (!evoProposals.length) {
        list.innerHTML = '<div class="evo-empty"><i class="fas fa-dna"></i><p>Tidak ada proposal aktif saat ini. AI Agent akan mengajukan proposal saat menemukan peluang evolusi baru.</p></div>';
        return;
    }
    list.innerHTML = evoProposals.map(p => `
        <div class="evo-card" id="evo-${p.id}">
            <div class="evo-card-hd">
                <div class="evo-card-title"><i class="fas fa-dna" style="color:var(--accent-purple)"></i> ${p.title}</div>
                <div class="evo-card-ts">${p.ts || '--'}</div>
            </div>
            <div class="evo-card-body">${p.body}</div>
            <div class="evo-actions">
                <button class="evo-btn approve" onclick="approveEvo('${p.id}')"><i class="fas fa-check"></i> Approve & Deploy</button>
                <button class="evo-btn reject" onclick="rejectEvo('${p.id}')"><i class="fas fa-x"></i> Reject</button>
            </div>
        </div>
    `).join('');
}

async function approveEvo(id) {
    addLog('SYSTEM', `Evolution approved: ${id}`);
    await sendCmd('apply_evolution', { evolution_id: id });
    evoProposals = evoProposals.filter(p => p.id !== id);
    renderEvolutions();
    addChatBubble('ai', `Proposal evolusi <strong>${id}</strong> telah disetujui dan dikirim ke sistem untuk implementasi.`);
}

function rejectEvo(id) {
    addLog('SYSTEM', `Evolution rejected: ${id}`);
    evoProposals = evoProposals.filter(p => p.id !== id);
    renderEvolutions();
}

// ── Boot Sequence ─────────────────────────────────────
window.addEventListener('load', () => {
    addLog('SYSTEM', 'NOIR SOVEREIGN MISSION CONTROL v21.0 AEGIS INITIALIZED.');
    addLog('SYSTEM', 'Neural link establishing...');
    addChatBubble('system', 'NOIR AI AGENT ONLINE — V21.0 AEGIS');
    
    // Start polling
    pollDashboard();
    setInterval(pollDashboard, 4000);
    
    // Initial media load
    setTimeout(refreshMedia, 2000);
});
