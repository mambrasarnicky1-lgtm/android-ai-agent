-- NOIR AGENT v6 — D1 Database Schema
-- Jalankan: wrangler d1 execute noir-db --file=schema.sql

-- Tabel: Antrian Perintah
CREATE TABLE IF NOT EXISTS commands (
    id          TEXT PRIMARY KEY,
    action      TEXT NOT NULL,
    description TEXT DEFAULT 'Manual',
    status      TEXT DEFAULT 'pending',  -- pending | sent | done | failed
    target_device TEXT,                  -- v16: Target specific agent
    result      TEXT,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at  TEXT
);

-- Tabel: Registrasi Agen
CREATE TABLE IF NOT EXISTS agents (
    device_id       TEXT PRIMARY KEY,
    name            TEXT,
    last_seen       TEXT DEFAULT CURRENT_TIMESTAMP,
    last_screenshot TEXT,
    stats           TEXT -- JSON string for CPU, RAM, Temp
);

-- Tabel: Memori Agen (Key-Value)
CREATE TABLE IF NOT EXISTS memory (
    key         TEXT PRIMARY KEY,
    value       TEXT,
    updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Tabel: Knowledge Mesh (Shared Skills & Intelligence)
CREATE TABLE IF NOT EXISTS knowledge_mesh (
    id          TEXT PRIMARY KEY,
    source_agent TEXT,
    skill_name  TEXT UNIQUE,
    data        TEXT, -- JSON data/binary blob of the skill
    confidence  REAL DEFAULT 1.0,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Tabel: Log Telemetri Agen
CREATE TABLE IF NOT EXISTS logs (
    device_id       TEXT,
    level           TEXT,
    message         TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Index untuk performa query
CREATE INDEX IF NOT EXISTS idx_commands_status ON commands(status, created_at);
CREATE INDEX IF NOT EXISTS idx_mesh_skill ON knowledge_mesh(skill_name);
CREATE INDEX IF NOT EXISTS idx_logs_device ON logs(device_id, created_at);
