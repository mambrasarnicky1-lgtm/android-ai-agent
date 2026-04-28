#!/usr/bin/env python3
"""
NOIR AGENT v14.0 COMMANDER — TELEGRAM SOVEREIGN INTERFACE
=============================================
Bot Telegram cerdas dengan integrasi AI Brain.
"""

import os, json, logging, sys, re, time
from pathlib import Path

# v17.2: Unified Path Normalization
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Load env
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

import threading
import time

try:
    import requests
    from telebot import TeleBot, types
    from ai_router import AIRouter
    from system_tools import SovereignUpdater
    from skill_acquisition import SkillAcquisitionEngine
    from linguistic_learning import LinguisticMastery
    from nlu_processor import NLUProcessor
    from temporal_memory import global_memory as memory
except ImportError:
    print("Install: pip install pyTelegramBotAPI requests")
    sys.exit(1)

BOT_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID    = os.environ.get("TELEGRAM_CHAT_ID", "")
GATEWAY    = os.environ.get("NOIR_GATEWAY_URL", "").rstrip("/")
API_KEY    = os.environ.get("NOIR_API_KEY", "")

if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN belum diisi di .env")
    sys.exit(1)

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("NoirTelegramBot")
bot = TeleBot(BOT_TOKEN)
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

SYSTEM_PROMPT = """
You are the NOIR SOVEREIGN BRAIN (v17.0). You control a Redmi Note 14 agent.
Your tone is cold, efficient, and professional. 
Respond in Indonesian.
If the user asks for a physical action, you must interpret it and tell them you are executing it.
"""

def cloud_cmd(action_type: str, params: dict = None, desc: str = "") -> dict:
    try:
        r = requests.post(
            f"{GATEWAY}/agent/command",
            headers=HEADERS,
            json={"action": {"type": action_type, **(params or {})}, "description": desc or action_type, "target_device": "REDMI_NOTE_14"},
            timeout=15
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}

@bot.message_handler(commands=["fetch"])
def cmd_fetch(msg):
    if not CHAT_ID or str(msg.chat.id) != CHAT_ID: return
    path = msg.text.replace("/fetch", "").strip()
    if not path:
        bot.reply_to(msg, "💡 Gunakan: `/fetch [path_file]` (misal: `/fetch /sdcard/Download/data.pdf`)", parse_mode="Markdown")
        return
    
    bot.reply_to(msg, f"🚚 **FILE FETCH INITIATED**: Mengambil `{os.path.basename(path)}` dari perangkat...", parse_mode="Markdown")
    res = cloud_cmd("file_fetch", params={"path": path}, desc=f"Fetch: {path}")
    if "error" in res:
        bot.reply_to(msg, f"❌ **FAILED**: {res['error']}")

@bot.message_handler(commands=["start", "menu", "status"])
def cmd_menu(msg):
    if not CHAT_ID or str(msg.chat.id) != CHAT_ID: return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("📸 Screenshot", callback_data="cmd_screenshot")
    item2 = types.InlineKeyboardButton("🔋 Battery", callback_data="cmd_battery")
    item3 = types.InlineKeyboardButton("📊 System Audit", callback_data="cmd_audit")
    item4 = types.InlineKeyboardButton("📍 Find Device", callback_data="cmd_location")
    item5 = types.InlineKeyboardButton("🧠 Consult AI", callback_data="chat_ai")
    item6 = types.InlineKeyboardButton("📂 Fetch File", callback_data="cmd_fetch")
    
    markup.add(item1, item2, item3, item4, item5, item6)
    
    bot.send_message(msg.chat.id, 
        "💠 **NOIR SOVEREIGN: COMMAND CENTER 2.0**\n"
        "V18.4 [TURBO-CHARGED VPS]\n\n"
        "Status: `ONLINE`\n"
        "Neural Link: `ACTIVE`\n\n"
        "Pilih perintah di bawah untuk eksekusi otonom:", 
        reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if not CHAT_ID or str(call.message.chat.id) != CHAT_ID: return
    
    action_map = {
        "cmd_screenshot": ("screenshot", "Taking remote capture..."),
        "cmd_battery": ("battery", "Polling power stats..."),
        "cmd_audit": ("audit", "Initiating system-wide audit..."),
        "cmd_location": ("location", "Acquiring GPS coordinates..."),
        "cmd_fetch": ("file_fetch", "Enter path: `/fetch [path]`"),
    }
    
    if call.data == "chat_ai":
        bot.answer_callback_query(call.id, "Kirimkan pertanyaan Anda secara langsung.")
        return

    if call.data in action_map:
        action, desc = action_map[call.data]
        bot.answer_callback_query(call.id, desc)
        res = cloud_cmd(action, desc=f"Telegram Button: {action}")
        if "error" in res:
            bot.send_message(call.message.chat.id, f"❌ **FAILED**: {res['error']}")
        else:
            bot.send_message(call.message.chat.id, f"💠 **EXECUTING**: `{action.upper()}`\nStatus: `QUEUED`")

@bot.message_handler(commands=["shutdown", "sleep", "kill_system"])
def cmd_shutdown(msg):
    if not CHAT_ID or str(msg.chat.id) != CHAT_ID: return
    
    cmd_type = msg.text.split()[0].replace("/", "")
    
    if cmd_type == "kill_system":
        # SOVEREIGN ABSOLUTE OVERRIDE: Bypasses AI, Nukes Containers
        bot.reply_to(msg, "🚨 **ABSOLUTE OVERRIDE ACTIVATED**\n"
                          "Status: `TERMINATING_ALL_SERVICES`\n"
                          "Kewenangan: `USER_ABSOLUTE`\n\n"
                          "Menghancurkan seluruh kontainer otonom...")
        # Hard shutdown via Docker
        import subprocess
        subprocess.run("docker compose down", shell=True, cwd="/root/noir-agent")
        bot.send_message(msg.chat.id, "✅ **SYSTEM NUKED**: Seluruh layanan otonom telah dimatikan secara fisik.")
        return

    if cmd_type == "shutdown":
        bot.reply_to(msg, "🛑 **GRACEFUL SHUTDOWN**: Menghentikan proses otonom...")
        cloud_cmd("system_shutdown", desc="User Emergency Shutdown")
    else:
        bot.reply_to(msg, "💤 **SYSTEM SLEEP**: Menidurkan seluruh modul.")
        cloud_cmd("system_sleep", desc="User System Sleep")

@bot.message_handler(func=lambda m: True)
def handle_all(msg):
    if not CHAT_ID or str(msg.chat.id) != CHAT_ID:
        # Ignore unauthorized or group noise
        return

    raw_text = msg.text.strip()
    bot.send_chat_action(msg.chat.id, "typing")

    # 1. NLU Processing
    from nlu_processor import NLUProcessor
    nlu_result = NLUProcessor.normalize_input(raw_text)
    intent = nlu_result["intent"]
    
    log.info(f"✨ NLU Intent: {intent}")

    # 2. Action Mapping
    intent_to_action = {
        "TAKE_SCREENSHOT": "screenshot",
        "GET_BATTERY": "battery",
        "GET_STATUS": "info",
        "SYSTEM_ACTION": "shell",
        "SYSTEM_UPGRADE": "upgrade",
        "RUN_AUDIT": "audit"
    }

    found_action = intent_to_action.get(intent)
    
    if found_action:
        # Execute Action
        params = {"cmd": "reboot"} if intent == "SYSTEM_ACTION" and "reboot" in raw_text.lower() else {}
        res = cloud_cmd(found_action, params=params, desc=f"Telegram: {raw_text}")
        
        if "error" in res:
            bot.reply_to(msg, f"❌ **FAILED**: {res['error']}")
            memory.record_interaction("USER_CMD_FAIL", raw_text, res['error'], {"intent": intent})
        else:
            bot.reply_to(msg, f"💠 **EXECUTING**: `{found_action.upper()}`\nStatus: `QUEUED`")
            memory.record_interaction("USER_CMD_EXEC", raw_text, found_action, {"status": "QUEUED"})
        return

    # 3. Intelligence Fallback (The "Answer Questions" part)
    # Only query AI if it's a real question or conversation
    try:
        log.info(f"🧠 Consult Brain: {raw_text}")
        ai_resp = AIRouter.smart_query(f"USER: {raw_text}\nCONTEXT: Noir Sovereign v17.0 Sentinel. Respond concisely.")
        bot.reply_to(msg, f"🧠 **BRAIN**: {ai_resp}")
        
        # Record interaction for learning
        memory.record_interaction("CHAT_INTERACTION", raw_text, ai_resp)
        if "?" in raw_text:
            memory.update_preference("INTEREST", raw_text.split()[-1]) # Simple heuristic
    except Exception as e:
        bot.reply_to(msg, "⚠️ Brain connection latency. Try again later.")

if __name__ == "__main__":
    log.info("🖤 Noir Sovereign Telegram Bot [v17.0] — Starting...")
    while True:
        try:
            bot.polling(none_stop=True, interval=2, timeout=20)
        except Exception as e:
            log.error(f"Polling Error: {e}")
            time.sleep(10)
