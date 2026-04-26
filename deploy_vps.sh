#!/bin/bash
# =====================================================
# NOIR SOVEREIGN VPS DEPLOY SCRIPT v18.0 [OMEGA-FIX]
# Jalankan dari VPS: bash deploy_vps.sh
# =====================================================
set -e

echo "╔══════════════════════════════════════════╗"
echo "║  NOIR VPS DEPLOY v18.0 [CACHE-SAFE]     ║"
echo "╚══════════════════════════════════════════╝"

DEPLOY_DIR="/root/android-ai-agent"
BACKUP_DIR="/root/noir_backup_$(date +%Y%m%d_%H%M%S)"

# ── LANGKAH 1: Backup state penting sebelum deploy ──
echo "[1/6] Membuat backup state..."
mkdir -p "$BACKUP_DIR"
[ -f "$DEPLOY_DIR/noir-ui/index.html" ] && cp "$DEPLOY_DIR/noir-ui/index.html" "$BACKUP_DIR/"
[ -f "$DEPLOY_DIR/.env" ] && cp "$DEPLOY_DIR/.env" "$BACKUP_DIR/"
echo "      Backup disimpan: $BACKUP_DIR"

# ── LANGKAH 2: Stop server lama ──
echo "[2/6] Menghentikan server lama..."
pkill -f "web_server.py" 2>/dev/null || true
pkill -f "brain.py" 2>/dev/null || true
sleep 2
echo "      Server lama dihentikan."

# ── LANGKAH 3: Bersihkan SEMUA cache lama ──
echo "[3/6] Membersihkan cache lama..."
find "$DEPLOY_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$DEPLOY_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$DEPLOY_DIR/noir-ui" -name "*.png" -o -name "*.jpg" -o -name "*.tmp" | xargs rm -f 2>/dev/null || true
echo "      Cache dibersihkan."

# ── LANGKAH 4: Update kode dari git ──
echo "[4/6] Mengambil kode terbaru..."
cd "$DEPLOY_DIR"
git fetch origin
git reset --hard origin/main
echo "      Kode diperbarui ke HEAD terbaru."

# ── LANGKAH 5: Install/Update dependencies Python ──
echo "[5/6] Memperbarui dependencies..."
pip install -q -r noir-vps/requirements.txt 2>/dev/null || true
pip install -q fastapi uvicorn httpx python-dotenv pycryptodome 2>/dev/null || true
echo "      Dependencies diperbarui."

# ── LANGKAH 6: Start server baru sebagai background service ──
echo "[6/6] Menjalankan server baru..."
cd "$DEPLOY_DIR"

# Start web_server.py (Dashboard + Direct Agent Endpoint)
nohup python3 noir-ui/web_server.py > /var/log/noir_server.log 2>&1 &
SVPID=$!
echo "      web_server.py PID: $SVPID"

sleep 3

# Verifikasi server aktif
if curl -sf "http://localhost/health" > /dev/null 2>&1; then
    echo "      [OK] Server aktif di port 80"
elif curl -sf "http://localhost:8000/health" > /dev/null 2>&1; then
    echo "      [OK] Server aktif di port 8000"
else
    echo "      [WARN] Server belum merespons — cek log: tail -f /var/log/noir_server.log"
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  DEPLOY SELESAI — Noir VPS v18.0 AKTIF  ║"
echo "╚══════════════════════════════════════════╝"
echo "  Monitor: tail -f /var/log/noir_server.log"
echo "  Status:  curl http://$(hostname -I | cut -d' ' -f1)/health"
